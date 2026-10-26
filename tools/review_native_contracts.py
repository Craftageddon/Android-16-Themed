"""Content-backed preservation review of routing and neutral native motion.

This deliberately leaves inline artwork, palette declarations, path morph data,
custom classes/properties and unrecognized structures OPEN. A preserved wrapper
does not approve its referenced artwork, the effective overlay, or a Forge drop-in.
"""
from pathlib import Path
import collections, copy, hashlib, itertools, json, re, shutil
import xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json

BASE = ROOT / 'iterations/20-semantic-review'
OUT = ROOT / 'iterations/22-native-contract-review'
A = '{http://schemas.android.com/apk/res/android}'
AA = '{http://schemas.android.com/aapt}'
MOTION_KINDS = {'anim', 'animator', 'transition'}
ROUTING_ROOTS = {
    'selector', 'animated-selector', 'layer-list', 'inset', 'animation-list',
    'animated-vector', 'level-list', 'rotate', 'animated-rotate', 'transition',
    'bitmap', 'nine-patch', 'pointer-icon', 'adaptive-icon',
}
ROUTING_NODES = ROUTING_ROOTS | {'item', 'target', 'background', 'foreground',
                                 'monochrome', 'scale', 'clip'}
MOTION_NODES = {
    'set', 'alpha', 'translate', 'scale', 'rotate', 'extend', 'objectAnimator',
    'animator', 'selector', 'item', 'propertyValuesHolder', 'keyframe',
    'pathInterpolator', 'accelerateDecelerateInterpolator',
    'accelerateInterpolator', 'anticipateInterpolator',
    'anticipateOvershootInterpolator', 'bounceInterpolator', 'cycleInterpolator',
    'decelerateInterpolator', 'linearInterpolator', 'overshootInterpolator',
    'slide', 'fade', 'transitionSet', 'explode', 'changeBounds',
    'changeTransform', 'changeClipBounds', 'changeImageTransform', 'layoutAnimation',
    AA + 'attr',
}
PROPERTIES = {
    'alpha', 'transitionAlpha', 'scaleX', 'scaleY', 'translateX', 'translateY',
    'translationX', 'translationY', 'translationZ', 'x', 'y', 'rotation',
    'rotationX', 'rotationY', 'elevation', 'trimPathStart', 'trimPathEnd',
    'trimPathOffset', 'fillAlpha', 'strokeAlpha', 'strokeWidth',
}
ROLES = {
    'selector': 'Ordered first-match routing: preserve all state predicates, item order and unmatched behavior.',
    'animated-selector': 'State/transition routing: preserve item IDs, from/to IDs, reversible flags and transition resources.',
    'layer-list': 'Composition contract: preserve layer order, IDs, gravity, size, relative/absolute insets and padding mode.',
    'inset': 'Geometry/reference contract: preserve native inset units and child drawable identity.',
    'animation-list': 'Frame protocol: preserve ordered drawable frames, per-frame durations and oneshot policy.',
    'animated-vector': 'Target binding contract: preserve vector identity, target names and animator references; leaf geometry is separately gated.',
    'level-list': 'Level routing: preserve ordered inclusive min/max ranges, overlaps, gaps and unmatched behavior.',
    'rotate': 'Native rotation wrapper: preserve pivots, angles and level behavior around the referenced visual.',
    'animated-rotate': 'Native repeated rotation: preserve pivots, frame duration/count and referenced visual.',
    'transition': 'Native cross-fade composition: preserve layer order, IDs and padding policy.',
    'bitmap': 'Native sampling wrapper: preserve source, tiling, density/mirroring and dithering behavior.',
    'nine-patch': 'Stretch wrapper: preserve source, mirroring and dithering; source stretch/content bands remain separate obligations.',
    'pointer-icon': 'Input contract: preserve bitmap identity and exact cursor hotspot coordinates; the cursor leaf is separately reviewed.',
    'adaptive-icon': 'System mask/layer contract: preserve foreground/background/monochrome identities; never substitute a full static composition.',
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def local(name):
    return name.split('}')[-1]


def tree_record(node):
    return {'tag': node.tag, 'attributes': dict(node.attrib),
            'text': (node.text or '').strip(), 'children': [tree_record(c) for c in node]}


def classify(root, kind):
    nodes = list(root.iter())
    if any((n.text or '').strip() for n in nodes):
        return None, 'Literal node text requires a dedicated value/content review.'
    if kind in MOTION_KINDS:
        if any(n.tag not in MOTION_NODES for n in nodes):
            return None, 'Inline visual geometry, custom transition class or unrecognized motion node.'
        for n in nodes:
            for key, value in n.attrib.items():
                name = local(key)
                if name in {'propertyName', 'propertyXName', 'propertyYName'} and value not in PROPERTIES:
                    return None, 'Path morph or custom/owner-defined property requires its own target review.'
                if value.startswith('#') or name in {'fillColor', 'strokeColor', 'tint', 'color', 'background', 'class'}:
                    return None, 'Palette/background or custom class requires a visual/owner-specific review.'
                if name == 'pathData' and n.tag != 'pathInterpolator':
                    # ObjectAnimator motion paths also stay open here: do not confuse
                    # traversal geometry with a standalone icon or a timing curve.
                    return None, 'Explicit motion/path geometry requires a dedicated target review.'
                if n.tag == AA + 'attr' and value not in {'android:interpolator', 'interpolator'}:
                    return None, 'Non-interpolator bundled resource requires a dedicated review.'
        return 'PRESERVE_NEUTRAL_NATIVE_MOTION', 'Native transform, opacity, trim/width or timing behavior; contains no artwork paths or color animation. Preserve it byte-for-byte and style the linked native visual separately.'
    if root.tag not in ROUTING_ROOTS:
        return None, 'Outside the explicit reference-wrapper review.'
    if any(n.tag not in ROUTING_NODES for n in nodes):
        return None, 'Inline artwork, geometry, bundled animation or custom drawable requires a dedicated review.'
    for n in nodes:
        for key, value in n.attrib.items():
            name = local(key)
            if value.startswith('#') or name in {'color', 'tint', 'alpha', 'fillColor', 'strokeColor', 'class'}:
                return None, 'Inline palette, opacity or custom drawable requires a visual/owner-specific review.'
            if name.startswith('state_') and value not in {'true', 'false'}:
                return None, 'Nonliteral state predicate requires source-owner review.'
    return 'PRESERVE_NATIVE_REFERENCE_CONTRACT', ROLES[root.tag]


def selector_tables(root):
    tables = []
    for node in root.iter():
        if node.tag not in {'selector', 'animated-selector'}:
            continue
        items = [n for n in node if n.tag == 'item']
        bits = sorted({key for n in items for key in n.attrib if local(key).startswith('state_')})
        assert len(bits) <= 14, 'Bound the explicit state-space review rather than silently sampling.'
        cases = []; hits = collections.Counter()
        for values in itertools.product([False, True], repeat=len(bits)):
            state = dict(zip(bits, values)); matching = []
            for index, item in enumerate(items):
                if all(state[k] == (v == 'true') for k, v in item.attrib.items() if k in bits):
                    matching.append(index)
            chosen = matching[0] if matching else None
            if chosen is not None: hits[chosen] += 1
            cases.append({'trueStates': [b for b in bits if state[b]], 'firstMatchingItem': chosen,
                          'allMatchingItems': matching})
        ids = [n.get(A+'id') for n in items if n.get(A+'id')]
        transitions = [dict(n.attrib) for n in node if n.tag == 'transition']
        endpoints = []
        for t in transitions:
            for key in ['fromId', 'toId']:
                value = t.get(A+key)
                # @+id and @id name the same identity.
                canon = lambda s: s.replace('@+id/', '@id/') if s else s
                endpoints.append({'attribute': key, 'value': value,
                                  'declaredInThisSelector': canon(value) in {canon(i) for i in ids}})
        tables.append({'stateAttributes': bits, 'orderedItems': [dict(n.attrib) for n in items],
                       'cases': cases, 'caseCount': len(cases), 'caseSha256': digest(cases),
                       'unmatchedCases': sum(c['firstMatchingItem'] is None for c in cases),
                       'neverChosenItemIndices': [i for i in range(len(items)) if not hits[i]],
                       'transitionAttributes': transitions, 'transitionEndpointChecks': endpoints,
                       'interpretation': 'First-match routing only. Custom state domains are retained, not guessed; this table does not map a state name to ember activation.'})
    return tables


def level_tables(root):
    tables = []
    for node in root.iter('level-list'):
        items = [dict(n.attrib) for n in node if n.tag == 'item']; ranges = []
        literal = True
        for n in items:
            lo = n.get(A+'minLevel', '0'); hi = n.get(A+'maxLevel', '0')
            if not lo.lstrip('-').isdigit() or not hi.lstrip('-').isdigit():
                literal = False; break
            ranges.append((int(lo), int(hi)))
        record = {'orderedItems': items, 'literalRanges': literal}
        if literal:
            # Native level usually spans 0..10000. Also retain out-of-band
            # boundaries; these are not rewritten or clamped by this review.
            probes = {0, 10000}
            for lo, hi in ranges: probes.update([lo-1, lo, lo+1, hi-1, hi, hi+1])
            cases = []
            for value in sorted(probes):
                matching = [i for i, (lo, hi) in enumerate(ranges) if lo <= value <= hi]
                cases.append({'level': value, 'firstMatchingItem': matching[0] if matching else None,
                              'allMatchingItems': matching})
            record.update(ranges=ranges, boundaryCases=cases, caseSha256=digest(cases))
        else:
            record['interpretation'] = 'Referenced bounds preserved literally; effective value/overlay selection is not asserted.'
        tables.append(record)
    return tables


def main():
    assert not (OUT/'complete-assets.zip').exists(), 'Never rewrite a published checkpoint.'
    ledger = read_json(BASE/'semantic-family-ledger.json')
    for delta in read_json(ROOT/'iterations/21-native-workflows/semantic-review-delta.json'):
        row = next(r for r in ledger if r['familyId'] == delta['familyId'])
        assert row['decision'] == delta['previousDecision']; row['decision'] = delta['decision']
    assert len(ledger) == 10926 and sum(len(x['evidence']) for x in ledger) == 16559
    before = sum(x['decision'] == 'OPEN' for x in ledger); assert before == 10553
    graph = read_json(OUT/'resource-reference-graph.json'); declarations = read_json(OUT/'resource-declarations.json')
    by_file = collections.defaultdict(list); family_of_file = {}
    for row in ledger:
        for v in row['evidence']: family_of_file[(row['baselineFamily']['project'], v['path'])] = row['familyId']
    for use in graph: by_file[(use['project'], use['path'])].append(use)
    decisions = []; review = []; excluded = []; objects = {}; total_cases = 0
    for row in ledger:
        if row['decision'] != 'OPEN': continue
        b = row['baselineFamily']; kind = b['kind']
        if kind not in MOTION_KINDS and not all(v.get('xmlRoot') in ROUTING_ROOTS for v in row['evidence']):
            continue
        variants = []; failures = []
        for v in row['evidence']:
            sha = v['gitBlobSha1']; source = BASE/'source/objects'/sha[:2]/sha[2:]
            data = source.read_bytes(); assert hashlib.sha256(data).hexdigest() == v['sha256']
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == sha
            root = ET.fromstring(data); decision, rationale = classify(root, kind)
            if decision is None: failures.append({'path': v['path'], 'reason': rationale}); continue
            dependencies = []
            for use in by_file[(b['project'], v['path'])]:
                candidates = []
                for index in use['candidates']:
                    d = declarations[index]
                    candidates.append({'declarationIndex': index, 'project': d['project'],
                                       'path': d['path'], 'type': d['type'], 'name': d['name'],
                                       'qualifier': d['qualifier'], 'gitBlobSha1': d['gitBlobSha1'],
                                       'sha256': d['sha256'],
                                       'familyId': family_of_file.get((d['project'], d['path']))})
                dependencies.append({'element': use['element'], 'attribute': use['attribute'],
                                     'reference': use['reference'], 'resolution': use['resolution'],
                                     'candidates': candidates})
            tables = selector_tables(root); total_cases += sum(t['caseCount'] for t in tables)
            record = {'project': b['project'], **v, 'decision': decision, 'rationale': rationale,
                      'preservedTree': tree_record(root), 'preservedTreeSha256': digest(tree_record(root)),
                      'selectors': tables, 'levels': level_tables(root), 'dependencies': dependencies,
                      'nativeSourceObject': 'source/objects/'+sha[:2]+'/'+sha[2:]}
            variants.append(record)
        # The family decision is atomic across all qualifiers, never inferred
        # from the first/example variant or a deduplicated descriptor context.
        if failures:
            excluded.append({'familyId': row['familyId'], 'source': b, 'failures': failures}); continue
        assert len(variants) == len(row['evidence'])
        types = sorted({v['decision'] for v in variants}); assert len(types) == 1
        decision = types[0]
        for v in variants:
            sha = v['gitBlobSha1']; source = BASE/'source/objects'/sha[:2]/sha[2:]
            destination = OUT/v['nativeSourceObject']; destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination); objects[sha] = {'gitBlobSha1': sha, 'sha256': v['sha256'], 'object': v['nativeSourceObject']}
        record = {'familyId': row['familyId'], 'source': b, 'decision': decision, 'variants': variants,
                  'treatment': 'Retain exact native XML bytes and behavior. Referenced artwork, colors, runtime themes and effective module/overlay selection stay separately gated.',
                  'nativeDropInApproval': False, 'forgeArtworkCompletion': False,
                  'sourceModification': 'NONE', 'targetRuntimeAcceptance': 'NOT RUN'}
        review.append(record)
        delta = {'familyId': row['familyId'], 'previousDecision': 'OPEN', 'decision': decision,
                 'source': b, 'variantCount': len(variants), 'reviewRecordSha256': digest(record),
                 'treatment': record['treatment'], 'artworkComplete': False,
                 'requiredOwnerWork': 'Preserve this native contract while binding separately reviewed visual leaves; no state-domain activation or effective runtime overlay is inferred.'}
        decisions.append(delta); row['decision'] = decision; row['requiredAction'] = delta['requiredOwnerWork']
        row['rationale'] = 'Exact content/tree, source hashes, each qualifier, ordered state/level rules and reference declarations reviewed; preserve native contract without authoring a duplicate drawing.'
    write_json(OUT/'native-contract-review.json', review)
    write_json(OUT/'semantic-review-delta.json', decisions)
    write_json(OUT/'dedicated-review-still-required.json', excluded)
    write_json(OUT/'source/objects-manifest.json', sorted(objects.values(), key=lambda x: x['gitBlobSha1']))
    write_json(OUT/'semantic-family-ledger.json', ledger)
    counts = collections.Counter(x['decision'] for x in ledger)
    summary = {'date': '2026-10-26', 'familyRecords': len(ledger), 'sourceFileVariants': 16559,
               'previousOpenFamilyDecisions': before, 'newContractPreservationDecisions': len(decisions),
               'contractDecisions': dict(collections.Counter(x['decision'] for x in decisions)),
               'reviewedVariants': sum(len(x['variants']) for x in review), 'savedSourceObjects': len(objects),
               'exhaustiveSelectorCasesInCandidateScan': total_cases,
               'openFamilyDecisions': counts['OPEN'], 'allDecisions': dict(counts),
               'visualAssetsAuthoredInThisPass': 0, 'nativeResourcesChangedInThisPass': 0,
               'semanticDecisionsAreArtworkCompletion': False,
               'workflowAdaptationsAuthoredPreviously': ['W-01', 'W-02'],
               'workflowAdaptationsStillUnauthored': ['W-03', 'W-04', 'W-05', 'W-06', 'W-07'],
               'wholeSemanticReviewFinished': False, 'fullGoalComplete': False,
               'finalWholeGoalDoubleCheck': 'NOT RUN - full scope remains unfinished',
               'scope': 'Preserve only reference-only native structures and standard neutral motion whose full variant content meets the stated contract review. Inline visuals/palette/morph paths/custom owners remain open. Dependency declarations are candidates, not runtime qualifier/overlay evaluation.'}
    write_json(OUT/'semantic-review-progress.json', summary); print(json.dumps(summary))


if __name__ == '__main__': main()
