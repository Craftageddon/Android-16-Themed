"""Distinct bounded ledger/source/state-mask check; not the final whole-goal audit."""
from pathlib import Path, PurePosixPath
import collections, copy, hashlib, json, re
import xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json

BASE = ROOT/'iterations/20-semantic-review'
OUT = ROOT/'iterations/22-native-contract-review'
A = '{http://schemas.android.com/apk/res/android}'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (OUT/'complete-assets.zip').exists()
    before = read_json(BASE/'semantic-family-ledger.json'); original = {r['familyId']: r for r in before}
    for d in read_json(ROOT/'iterations/21-native-workflows/semantic-review-delta.json'):
        original[d['familyId']]['decision'] = d['decision']
    after = read_json(OUT/'semantic-family-ledger.json'); latest = {r['familyId']: r for r in after}
    delta = read_json(OUT/'semantic-review-delta.json'); changed = {d['familyId']: d for d in delta}
    assert len(latest) == len(after) == len(original) == 10926 and len(changed) == len(delta) == 898
    assert sum(len(r['evidence']) for r in after) == 16559
    for key, old in original.items():
        new = latest[key]
        assert old['baselineFamily'] == new['baselineFamily'] and old['evidence'] == new['evidence']
        if key in changed:
            assert old['decision'] == 'OPEN' and new['decision'] == changed[key]['decision']
            assert not changed[key]['artworkComplete']
        else: assert old == new, key
    assert sum(r['decision']=='OPEN' for r in after) == 9655
    sources = read_json(OUT/'source/objects-manifest.json'); saved = {r['gitBlobSha1']: r for r in sources}
    assert len(saved) == len(sources) == 1273
    for r in sources:
        data = (OUT/r['object']).read_bytes()
        assert sha(OUT/r['object']) == r['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == r['gitBlobSha1']
    reviews = read_json(OUT/'native-contract-review.json'); states = levels = 0; variants = 0
    for r in reviews:
        assert r['familyId'] in changed and not r['nativeDropInApproval'] and not r['forgeArtworkCompletion']
        assert len(r['variants']) == len(original[r['familyId']]['evidence'])
        for v in r['variants']:
            variants += 1; raw = (OUT/v['nativeSourceObject']).read_bytes()
            prior = BASE/'source/objects'/v['gitBlobSha1'][:2]/v['gitBlobSha1'][2:]
            assert raw == prior.read_bytes()
            root = ET.fromstring(raw)
            assert all(n.tag not in {'path', 'vector', 'shape', 'gradient', 'solid', 'stroke'} for n in root.iter())
            selectors = [n for n in root.iter() if n.tag in {'selector', 'animated-selector'}]
            assert len(selectors) == len(v['selectors'])
            for node, table in zip(selectors, v['selectors']):
                items = [n for n in node if n.tag == 'item']; bits = table['stateAttributes']; choices = {}
                assert table['caseCount'] == len(table['cases']) == 2**len(bits)
                for case in table['cases']:
                    mask = sum(1 << bits.index(key) for key in case['trueStates'])
                    assert mask not in choices
                    matches = []
                    for i, item in enumerate(items):
                        yes = no = 0
                        for key, value in item.attrib.items():
                            if key in bits:
                                if value == 'true': yes |= 1 << bits.index(key)
                                else: no |= 1 << bits.index(key)
                        if (mask & yes) == yes and not (mask & no): matches.append(i)
                    assert case['allMatchingItems'] == matches
                    assert case['firstMatchingItem'] == (matches[0] if matches else None)
                    choices[mask] = case['firstMatchingItem']; states += 1
                assert len(choices) == 2**len(bits)
            for node, table in zip(root.iter('level-list'), v['levels']):
                if not table['literalRanges']: continue
                ranges = [(int(n.get(A+'minLevel','0')), int(n.get(A+'maxLevel','0'))) for n in node if n.tag=='item']
                assert [list(x) for x in ranges] == table['ranges']
                for case in table['boundaryCases']:
                    choices = [i for i,(lo,hi) in enumerate(ranges) if lo <= case['level'] <= hi]
                    assert case['allMatchingItems'] == choices
                    assert case['firstMatchingItem'] == (choices[0] if choices else None); levels += 1
    assert variants == 919
    # Independent path-parent check, without importing the new scope resolver.
    declarations = read_json(OUT/'resource-declarations.json')
    for d in declarations:
        parent = PurePosixPath(d['path']).parent
        assert parent.name == d['qualifier'], d
        resource_root = parent.parent
        while re.fullmatch(r'flag\(.+\)', resource_root.name): resource_root = resource_root.parent
        assert str(resource_root) == d['resourceRoot'], d
    checkbox = [d for d in declarations if d['project']=='frameworks/base' and d['path']=='core/res/res/drawable/btn_checkbox_checked_mtrl.xml']
    assert len(checkbox) == 1 and checkbox[0]['resourceRoot']=='core/res/res' and checkbox[0]['type']=='drawable'
    # Reference grammar regression is tested against concrete accepted values,
    # including a literal URL that the old substring scan could misclassify.
    from build_resource_graph_v22 import references
    probes = {'@*android:color/white': ('@','android','color','white'),
              '@+id/control': ('@',None,'+id','control'), '?android:colorControlNormal': ('?','android','attr','colorControlNormal'),
              '?attr/colorAccent': ('?',None,'attr','colorAccent'), '@null': ('@',None,None,'null')}
    for value, expected in probes.items():
        actual = list(references(value)); assert len(actual) == 1
        assert tuple(actual[0][k] for k in ['sig','pkg','type','name']) == expected
    for value in ['https://example.invalid/?colorAccent=yes', 'Literal @drawable/icon text', '"@drawable/literal"']:
        assert not list(references(value))
    assert not read_json(OUT/'unresolved-path-parameters.json')
    motion = read_json(OUT/'vector-motion-contracts.json'); targets = [t for r in motion for t in r['targets']]
    assert len(motion) == 254 and len(targets) == 1149
    assert all(t['targetPresentInEveryResolvedVectorCandidate'] and not t['animationPending'] for t in targets)
    morphs = [a for t in targets for a in t['animators'] if 'pathData' in a['properties']]
    assert len(morphs) == 527 and all(a['bothEndpointsExplicitAndResolved'] and a['allResolvedEndpointsSameSignature'] for a in morphs)
    assert not read_json(OUT/'vector-motion-pending.json')
    parser = read_json(OUT/'verification/evidence/androidx-path-parser-checks.json')
    native = read_json(OUT/'verification/evidence/native-flag-scope-checks.json')
    assert parser['result'] == native['result'] == 'PASS' and parser['pairChecks'] == 130816
    assert native['resourceFilesCompiled'] == 8 and len(native['cases']) == 2
    assert all(c['flaggedAvdInLinkedTable'] == (c['flag']=='true') and c['unflaggedBaseAnimatorInLinkedTable'] for c in native['cases'])
    preserved_art = read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    assert len(preserved_art) == 472 and all(sha(ROOT/r['source']) == r['sha256'] for r in preserved_art)
    archives = {'iterations/20-semantic-review/complete-assets.zip': '734f7b39c1a546fe770e64622a9652bcff431cb85867a200532155d8f4e0ce92',
                'iterations/21-native-workflows/complete-assets.zip': 'c72087abc409ea5611d850547d72cf745292b0b4b7d5222f5e5f2f29e3563cf3'}
    for file, expected in archives.items(): assert sha(ROOT/file) == expected
    report = {'date': '2026-10-26', 'result': 'PASS', 'components': 898,
              'familyRecordsConserved': 10926, 'fileVariantsConserved': 16559,
              'preservedContracts': len(reviews), 'exactSourceVariantsChecked': variants,
              'sourceObjectsHashVerified': len(sources), 'selectorBitmaskCases': states,
              'levelBoundaryCases': levels, 'resourceDeclarationScopesChecked': len(declarations),
              'referenceGrammarRegressionCases': len(probes)+3,
              'avdTargetBindings': len(targets), 'explicitMorphAnimators': len(morphs),
              'realAndroidxPairChecks': parser['pairChecks'], 'nativeFlagCompileLinkCases': 2,
              'earlierMastersPreserved': len(preserved_art), 'earlierArchiveHashesPreserved': archives,
              'openFamilyDecisions': 9655, 'newVisualAssets': 0,
              'checkpointScope': '898 native routing/motion preservation decisions, corrected source reference graph and complete acquired AVD structural dependency review. No artwork/native/device completion claim.',
              'v1Scope': 'Full corpus conserved; each preserved qualifier meets the explicit reference-only/neutral-motion policy, source states/IDs/geometry/timing stay native, and leaf artwork/owners/workflows remain separately gated.',
              'v2Method': 'Distinct ledger/source-byte and state-bitmask verification, resource-path provenance, actual AndroidX parser/canMorph execution, actual SDK37 original-resource compilation/linking/table inspection with read-only flag true/false, parameterized path resolution, prior master/archive hashes.',
              'fullPinnedSoongBuild': 'NOT RUN', 'androidDeviceExecution': 'NOT RUN',
              'finalWholeGoalDoubleCheck': 'NOT RUN - full scope remains unfinished',
              'wholeGoalComplete': False}
    write_json(OUT/'verification/evidence/contract-checks.json', report)
    write_json(OUT/'verification/evidence/technical.json', report); print(json.dumps(report))


if __name__ == '__main__': main()
