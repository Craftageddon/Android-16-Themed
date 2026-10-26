"""Audit every acquired AVD's exact target and path-morph dependencies.

Candidate sets deliberately retain qualifiers/overlays; this is not Android's
runtime resource matcher or proof that every source candidate is installed.
"""
from pathlib import Path
import collections, hashlib, itertools, json, re, shutil
import xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json
from build_resource_graph_v22 import scope

BASE = ROOT/'iterations/20-semantic-review'
OUT = ROOT/'iterations/22-native-contract-review'
A = '{http://schemas.android.com/apk/res/android}'
AA = '{http://schemas.android.com/aapt}'
REF = re.compile(r'@(?:(?P<pkg>[\w.]+):)?(?P<type>[\w]+)/(?P<name>[\w.]+)$')
COMMAND = re.compile(r'[a-df-zA-DF-Z]')
FLOAT = re.compile(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?\d*))(?:[eE][-+]?\d+)?')
CAPABILITIES = {
    'group': {'rotation', 'pivotX', 'pivotY', 'scaleX', 'scaleY', 'translateX', 'translateY'},
    'path': {'pathData', 'fillColor', 'fillAlpha', 'strokeColor', 'strokeAlpha',
             'strokeWidth', 'trimPathStart', 'trimPathEnd', 'trimPathOffset'},
    'clip-path': {'pathData'}, 'vector': {'alpha'},
}


def signature(path):
    """Android-style command blocks, including implicit parameter repetitions.

    A trailing empty non-close block can occur in acquired upstream resources.
    Retain that block; do not call this a native path syntax/geometry acceptance.
    """
    matches = list(COMMAND.finditer(path)); result = []
    assert matches and not path[:matches[0].start()].strip(), path[:100]
    for i, m in enumerate(matches):
        command = m.group(); assert command in 'MmZzLlHhVvCcSsQqTtAa', command
        text = path[m.end():matches[i+1].start() if i+1 < len(matches) else len(path)]
        numbers = list(FLOAT.finditer(text)); rest = FLOAT.sub('', text)
        assert not rest.replace(',', '').strip(), (command, rest)
        result.append([command, len(numbers)])
    return result


class Audit:
    def __init__(self):
        self.declarations = read_json(OUT/'resource-declarations.json')
        self.index = collections.defaultdict(list)
        for d in self.declarations:
            self.index[(d['project'], d['resourceRoot'], d['type'], d['name'])].append(d)
        self.features = {x['gitBlobSha1']: x for x in read_json(BASE/'content-evidence.json')}
        supporting = read_json(OUT/'source/supporting-interpolators.json') if (OUT/'source/supporting-interpolators.json').exists() else []
        self.features.update({x['gitBlobSha1']: x for x in supporting})
        self.objects = {}; self.paths = {}; self.unresolved = []

    def source(self, d):
        sha = d['gitBlobSha1']; p = BASE/'source/objects'/sha[:2]/sha[2:]
        if not p.exists(): p = OUT/'source/objects'/sha[:2]/sha[2:]
        data = p.read_bytes(); assert hashlib.sha256(data).hexdigest() == d['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == sha
        dst = OUT/'source/objects'/sha[:2]/sha[2:]; dst.parent.mkdir(parents=True, exist_ok=True)
        if p.resolve() != dst.resolve(): shutil.copy2(p, dst)
        self.objects[sha] = {'gitBlobSha1': sha, 'sha256': d['sha256'],
                             'object': dst.relative_to(OUT).as_posix()}
        return data

    def refs(self, value, context):
        m = REF.fullmatch(value or '')
        if not m:
            return [], 'Not a concrete resource reference'
        pkg, typ, name = m.group('pkg', 'type', 'name')
        if pkg not in {None, 'android'}:
            return [], 'Explicit external package needs effective module mapping'
        project = 'frameworks/base' if pkg == 'android' else context['project']
        root = 'core/res/res' if pkg == 'android' else context['resourceRoot']
        candidates = self.index.get((project, root, typ, name), [])
        return candidates, 'Exact declaration candidates' if candidates else 'External library/generated/unindexed declaration'

    def values(self, value, context, visited=()):
        if value is None: return [], ['Omitted endpoint: native current-property/keyframe semantics retained']
        if value.startswith('@'):
            key = (context['project'], context['resourceRoot'], value)
            if key in visited: return [], ['Reference cycle retained for owner review']
            candidates, reason = self.refs(value, context); result = []; pending = []
            if not candidates: return [], [reason+': '+value]
            for d in candidates:
                self.source(d)
                if d.get('value') is None:
                    pending.append('Declaration is not a scalar path value: '+d['path']); continue
                vals, notes = self.values(d['value'].strip(), d, visited+(key,))
                result.extend(vals); pending.extend(notes)
            return sorted(set(result)), sorted(set(pending))
        if value.startswith('?'): return [], ['Runtime theme attribute retained: '+value]
        # Android quoted string values quote the content, not the SVG grammar.
        if len(value) >= 2 and value[0] == value[-1] == '"': value = value[1:-1]
        return [value], []

    def path_values(self, value, context):
        values, pending = self.values(value, context); ids = []
        for val in values:
            key = hashlib.sha256(val.encode('utf8')).hexdigest()
            if key not in self.paths:
                try:
                    sig = signature(val); result = {'value': val, 'signature': sig, 'parsedCommandBlocks': True}
                except (AssertionError, ValueError) as e:
                    result = {'value': val, 'signature': None, 'parsedCommandBlocks': False,
                              'parseNote': str(e)[:300]}
                self.paths[key] = {'pathSha256': key, **result}
            ids.append(key)
        return {'rawValue': value, 'pathValueIds': ids, 'pending': pending}

    def trees(self, reference, context, visited=()):
        candidates, reason = self.refs(reference, context); result = []; pending = []
        if not candidates: return [], [reason+': '+str(reference)]
        for d in candidates:
            key = (d['project'], d['path'], d.get('type'), d.get('name'))
            if key in visited: pending.append('Reference cycle: '+d['path']); continue
            if d.get('value') is not None:
                self.source(d)
                value = d['value'].strip()
                if value.startswith('@'):
                    sub, notes = self.trees(value, d, visited+(key,)); result.extend(sub); pending.extend(notes)
                else: pending.append('Non-tree alias declaration: '+d['path'])
            else:
                data = self.source(d)
                if self.features[d['gitBlobSha1']]['contentClass'] == 'XML': result.append((ET.fromstring(data), d))
                else: pending.append('Non-XML declaration: '+d['path'])
        return result, pending

    def run_avd(self, f):
        feature = self.features[f['gitBlobSha1']]; root_path, qualifier = scope(f)
        context = {**f, 'resourceRoot': root_path, 'qualifier': qualifier, 'sha256': feature['sha256']}
        root = ET.fromstring(self.source(context)); vectors = []; pending = []
        for attr in root.findall(AA+'attr'):
            if attr.get('name') in {'android:drawable', 'drawable'}:
                vectors.extend((n, context) for n in attr if n.tag == 'vector')
        if root.get(A+'drawable'):
            trees, notes = self.trees(root.get(A+'drawable'), context); pending.extend(notes)
            for tree, source in trees:
                if tree.tag == 'vector': vectors.append((tree, source))
                else: pending.append('Vector reference resolves to '+tree.tag+': '+source['path'])
        targets = []
        for target_index, target in enumerate(root.findall('target')):
            name = target.get(A+'name'); animators = []; animation_notes = []
            for attr in target.findall(AA+'attr'):
                if attr.get('name') in {'android:animation', 'animation'}:
                    animators.extend((n, context) for n in attr)
            if target.get(A+'animation'):
                trees, notes = self.trees(target.get(A+'animation'), context)
                animators.extend(trees); animation_notes.extend(notes)
            animated = []
            for tree, source in animators:
                for node in tree.iter():
                    if node.tag not in {'objectAnimator', 'propertyValuesHolder'}: continue
                    xy = [node.get(A+k) for k in ['propertyXName', 'propertyYName'] if node.get(A+k)]
                    properties = xy or ([node.get(A+'propertyName')] if node.get(A+'propertyName') else [])
                    record = {'animationProject': source['project'], 'animationPath': source['path'],
                              'animationBlob': source['gitBlobSha1'], 'element': node.tag,
                              'properties': properties, 'attributes': dict(node.attrib)}
                    if 'pathData' in properties:
                        fields = [self.path_values(node.get(A+k), source) for k in ['valueFrom', 'valueTo']]
                        for frame in node.findall('keyframe'):
                            fields.append(self.path_values(frame.get(A+'value'), source))
                        ids = sorted({i for field in fields for i in field['pathValueIds']})
                        sigs = {json.dumps(self.paths[i]['signature']) for i in ids if self.paths[i]['signature'] is not None}
                        record.update(pathEndpoints=fields, resolvedPathValueIds=ids,
                                      endpointSignatureKinds=len(sigs),
                                      allResolvedEndpointsSameSignature=len(sigs) <= 1 and all(self.paths[i]['parsedCommandBlocks'] for i in ids),
                                      bothEndpointsExplicitAndResolved=all(field['rawValue'] is not None and field['pathValueIds'] and not field['pending'] for field in fields[:2]),
                                      endpointInterpretation='Command-block structure only; qualifiers remain a candidate set, omitted values use native current-property semantics. No Android execution or interpolated-geometry acceptance.')
                    elif node.get(A+'pathData'):
                        record['motionTraversalPath'] = self.path_values(node.get(A+'pathData'), source)
                    animated.append(record)
            vector_checks = []
            for vector, source in vectors:
                found = [n for n in vector.iter() if n.get(A+'name') == name]
                check = {'vectorProject': source['project'], 'vectorPath': source['path'],
                         'vectorQualifier': source['qualifier'], 'vectorBlob': source['gitBlobSha1'],
                         'name': name, 'matchingNodes': len(found), 'nodeTypes': [n.tag for n in found],
                         'properties': []}
                for n in found:
                    for animator in animated:
                        for prop in animator['properties']:
                            p = {'nodeType': n.tag, 'property': prop,
                                 'standardTargetProperty': prop in CAPABILITIES.get(n.tag, set())}
                            if prop == 'pathData':
                                baseline = self.path_values(n.get(A+'pathData'), source)
                                p['basePath'] = baseline
                                base_sigs = {json.dumps(self.paths[i]['signature']) for i in baseline['pathValueIds'] if self.paths[i]['signature'] is not None}
                                anim_sigs = {json.dumps(self.paths[i]['signature']) for i in animator.get('resolvedPathValueIds', []) if self.paths[i]['signature'] is not None}
                                p['baseAndEndpointSignatureKinds'] = len(base_sigs | anim_sigs)
                                p['candidateSignatureAgreement'] = bool(base_sigs) and len(base_sigs | anim_sigs) == 1
                                p['baseSignatureRequiredForImplicitEndpoint'] = not animator.get('bothEndpointsExplicitAndResolved', False)
                                if not p['candidateSignatureAgreement'] and not p['baseSignatureRequiredForImplicitEndpoint']:
                                    p['reviewedInterpretation'] = 'Both morph endpoints explicitly define compatible animation geometry. The static base uses a different command representation; retain both base and explicit endpoints. A base/endpoint difference alone is not reported as a broken native morph.'
                            check['properties'].append(p)
                vector_checks.append(check)
            targets.append({'index': target_index, 'name': name,
                            'animationReference': target.get(A+'animation'),
                            'animationPending': animation_notes, 'animators': animated,
                            'vectorCandidateChecks': vector_checks,
                            'targetPresentInEveryResolvedVectorCandidate': bool(vector_checks) and all(v['matchingNodes'] == 1 for v in vector_checks)})
        return {'project': f['project'], 'path': f['path'], 'qualifier': qualifier,
                'gitBlobSha1': f['gitBlobSha1'], 'sha256': feature['sha256'],
                'resourceRoot': root_path, 'vectorReference': root.get(A+'drawable'),
                'resolvedVectorCandidates': len(vectors), 'vectorPending': pending, 'targets': targets,
                'dropInApproval': False, 'effectiveRuntimeQualifierSelection': 'NOT EVALUATED'}


def main():
    assert not (OUT/'complete-assets.zip').exists()
    audit = Audit(); files = read_json(BASE/'baseline/resource-files.json')
    avds = [f for f in files if audit.features[f['gitBlobSha1']].get('xmlRoot') == 'animated-vector']
    records = [audit.run_avd(f) for f in avds]
    write_json(OUT/'vector-motion-contracts.json', records)
    write_json(OUT/'morph-path-values.json', sorted(audit.paths.values(), key=lambda x: x['pathSha256']))
    manifest = {r['gitBlobSha1']: r for r in read_json(OUT/'source/objects-manifest.json')}
    manifest.update(audit.objects); write_json(OUT/'source/objects-manifest.json', sorted(manifest.values(), key=lambda x: x['gitBlobSha1']))
    targets = [t for r in records for t in r['targets']]
    morphs = [a for t in targets for a in t['animators'] if 'pathData' in a['properties']]
    properties = [p for t in targets for v in t['vectorCandidateChecks'] for p in v['properties']]
    issues = []
    for r in records:
        for t in r['targets']:
            reasons = []
            if not t['targetPresentInEveryResolvedVectorCandidate']: reasons.append('Target absent, duplicated or not resolved in the retained vector candidate set')
            if t['animationPending']: reasons.append('Some animation references require external/effective-module resolution')
            if any(not p['standardTargetProperty'] for v in t['vectorCandidateChecks'] for p in v['properties']): reasons.append('Nonstandard target/property pair requires source-owner review')
            if any(not p.get('candidateSignatureAgreement', True) and p.get('baseSignatureRequiredForImplicitEndpoint', True) for v in t['vectorCandidateChecks'] for p in v['properties']): reasons.append('Implicit base versus endpoint path-command signatures require owner review')
            if any(not a.get('allResolvedEndpointsSameSignature', True) for a in t['animators']): reasons.append('Morph endpoint signatures diverge across retained candidates')
            if reasons: issues.append({'project': r['project'], 'path': r['path'], 'target': t['name'], 'reasons': reasons})
    summary = {'date': '2026-10-26', 'animatedVectorSourceVariants': len(records),
               'targetBindings': len(targets),
               'targetsPresentExactlyOnceInEveryResolvedVectorCandidate': sum(t['targetPresentInEveryResolvedVectorCandidate'] for t in targets),
               'propertyCandidateChecks': len(properties),
               'standardTargetPropertyChecks': sum(p['standardTargetProperty'] for p in properties),
               'morphAnimators': len(morphs), 'distinctPathValues': len(audit.paths),
               'pathCommandParseExceptions': sum(not p['parsedCommandBlocks'] for p in audit.paths.values()),
               'morphEndpointCandidateSignatureAgreement': sum(a['allResolvedEndpointsSameSignature'] for a in morphs),
               'reviewedExplicitEndpointBaseSignatureDifferences': sum(not p.get('candidateSignatureAgreement', True) and not p.get('baseSignatureRequiredForImplicitEndpoint', True) for p in properties),
               'pendingTargetRecords': len(issues), 'nativePathInterpolationOrRendering': 'NOT RUN',
               'sourceObjectRecordsNowSaved': len(manifest),
               'scope': 'All acquired animated-vector variants, including inline vectors/animators. Complete per-file project/resource-root lookup, all declaration candidates retained. Structural target/property/path command review; not a replacement-art approval or an effective build/runtime resource match.'}
    write_json(OUT/'vector-motion-summary.json', summary); write_json(OUT/'vector-motion-pending.json', issues)
    print(json.dumps(summary))


if __name__ == '__main__': main()
