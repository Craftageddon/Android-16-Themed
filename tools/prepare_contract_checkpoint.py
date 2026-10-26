"""Document the898 preservation decisions without shrinking the full goal."""
from pathlib import Path
import collections, hashlib, json, shutil, xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json

BASE = ROOT/'iterations/20-semantic-review'
OUT = ROOT/'iterations/22-native-contract-review'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    ledger = read_json(OUT/'semantic-family-ledger.json'); by_id = {r['familyId']: r for r in ledger}
    file_family = {(r['baselineFamily']['project'], v['path']): r['familyId'] for r in ledger for v in r['evidence']}
    preserved = read_json(OUT/'native-contract-review.json'); queue = []; all_ids = set(); indirect = collections.defaultdict(set)
    for r in preserved:
        refs = []; dependencies = set()
        for v in r['variants']:
            for dep in v['dependencies']:
                ids = sorted({d['familyId'] for d in dep['candidates'] if d.get('familyId')})
                dependencies.update(ids); refs.append({'sourcePath': v['path'], 'reference': dep['reference'],
                                                       'resolution': dep['resolution'], 'candidateFamilyIds': ids})
        indirect[r['familyId']] = dependencies
        queue.append({'familyId': r['familyId'], 'preserveDecision': r['decision'],
                      'source': r['source'], 'directReferences': refs})
    for q in queue:
        todo = list(indirect[q['familyId']]); seen = set(); open_ids = set()
        while todo:
            target = todo.pop()
            if target in seen: continue
            seen.add(target)
            if target in indirect: todo.extend(indirect[target])
            else: open_ids.add(target)
        q['dependentFamiliesOutsideThisPreservationPass'] = [{'familyId': i, 'decision': by_id[i]['decision'],
                                                            'source': by_id[i]['baselineFamily']} for i in sorted(open_ids)]
        all_ids.update(open_ids)
    write_json(OUT/'preserved-contract-dependency-queue.json', queue)
    supporting = read_json(OUT/'source/supporting-interpolators.json'); timing = []
    allowed = {'pathInterpolator', 'decelerateInterpolator', 'accelerateInterpolator', 'linearInterpolator',
               'accelerateDecelerateInterpolator', 'anticipateInterpolator', 'anticipateOvershootInterpolator',
               'bounceInterpolator', 'cycleInterpolator', 'overshootInterpolator'}
    for r in supporting:
        data = (OUT/r['object']).read_bytes(); node = ET.fromstring(data)
        assert node.tag in allowed and not list(node)
        assert not any(v.startswith('#') for v in node.attrib.values())
        timing.append({**r, 'nativeRoot': node.tag, 'attributes': dict(node.attrib),
                       'decision': 'PRESERVE_NATIVE_TIMING_CURVE',
                       'rationale': 'Exact native easing/cycle parameters are timing data, not visible artwork or a source-domain activation policy. Preserve unchanged; reduced motion/emission remains an owner gate.'})
    write_json(OUT/'supporting-timing-contract-review.json', timing)
    # Include every saved original in the exact-byte manifest, including timing
    # dependencies whose original XML is not itself an AVD target/animator.
    known = {r['gitBlobSha1']: r for r in read_json(BASE/'content-evidence.json')}
    known.update({r['gitBlobSha1']: r for r in supporting}); objects = []
    for p in sorted((OUT/'source/objects').glob('*/*')):
        blob = p.parent.name+p.name; data = p.read_bytes()
        assert blob in known and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blob
        sha = hashlib.sha256(data).hexdigest(); assert sha == known[blob]['sha256']
        objects.append({'gitBlobSha1': blob, 'sha256': sha, 'bytes': len(data), 'object': p.relative_to(OUT).as_posix()})
    write_json(OUT/'source/objects-manifest.json', objects)
    licenses = []
    for r in read_json(BASE/'auxiliary-source-files.json'):
        if r['kind'] != 'upstream-license': continue
        src = BASE/r['object']; target = OUT/'source/licenses'/r['project'].replace('/', '__')/r['path']
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == r['sha256']
        licenses.append({**r, 'saved': target.relative_to(OUT).as_posix()})
    write_json(OUT/'source/licenses-manifest.json', licenses)
    shutil.copy2(ROOT/'iterations/19-os-resource-audit/source-projects.json', OUT/'source/source-projects.json')
    owner = next(r for r in read_json(ROOT/'iterations/19-os-resource-audit/source-evidence.json') if r['project']=='packages/apps/DocumentsUI' and r['path']=='Android.bp')
    target = OUT/'source/owner-contracts/DocumentsUI-Android.bp'; target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((ROOT/'iterations/19-os-resource-audit'/owner['saved']).read_bytes())
    assert hashlib.sha256(target.read_bytes()).hexdigest() == owner['sha256']
    write_json(OUT/'source/owner-contracts/manifest.json', [{**owner, 'saved': target.relative_to(OUT).as_posix()}])
    progress = read_json(OUT/'semantic-review-progress.json')
    baseline_status = collections.defaultdict(collections.Counter)
    for r in ledger: baseline_status[r['baselineFamily']['status']][r['decision']] += 1
    progress.update(savedSourceObjects=len(objects), supportingTimingSourceFiles=len(supporting),
                    reviewedBaselineStatusDecisions={k: dict(v) for k,v in baseline_status.items()},
                    dependentFamiliesOutsideThisPreservationPass=len(all_ids),
                    dependencyFamiliesAreConfirmedNewDrawings=False,
                    supportingTimingCurvesAddedToOriginalArtFamilyCount=False,
                    referenceGraphAmendment='The separate22 graph corrects the historical20 resource-root/type/reference index, preserves feature-flag conditions as metadata, and retains all declaration candidates. Original source bytes and signed20/21 archives remain unchanged.')
    write_json(OUT/'semantic-review-progress.json', progress)
    shutil.copy2(BASE/'signing-public-key.pem', OUT/'signing-public-key.pem')
    (OUT/'README.md').write_text('''# Forge22 native contract review

This checkpoint records898 content-backed preservation decisions:639 native reference/state wrappers and259 neutral motion resources, covering919 source variants. It authors no new visual assets and changes no native resource bytes. Referenced artwork remains a separate obligation.

The full goal remains active:10926 original source families and16559 file variants are conserved.9655 family decisions remain OPEN; that is a review count, not9655 confirmed missing drawings. W03 setup, W04 updater, W05 gallery, W06 magnification and W07 boot/charger/recovery adaptations remain unauthored. W01/W02 source/art handoffs were published in Forge21; their full native/device acceptance remains pending. Reuse/app-owner bindings and additional discovered art still need their recorded gates.

## What changed

- `native-contract-review.json.gz` contains exact ordered XML trees, source hashes, state truth tables, level boundaries and dependency candidates for every preserved family/qualifier.
- `semantic-review-delta.json.gz` and `semantic-family-ledger.json.gz` retain the full scope and record only the bounded decisions made here.
- `resource-reference-graph.json.gz` and `resource-declarations.json.gz` supersede the historical20 graph. The old first-res-directory lookup incorrectly indexed core/res/res and resource roots without a literal res component.22 uses the actual resource folder; flag(...) conditions stay inside their resource root and are recorded without choosing the product flag state. Array types, metadata-only declarations, private/+id/short-theme references and scalar reference matching are corrected.
- `vector-motion-contracts.json.gz` audits all254 acquired AVD variants:1149 named targets,2890 standard target/property checks and527 morph animators. All named targets resolve in the retained candidate sets, and all527 explicit endpoint sets have matching command signatures. Six static-base/explicit-endpoint differences are documented; neither geometry is silently rewritten. This is structural evidence, not native interpolation/rendering or drop-in art approval.
-79 pinned supporting interpolator files are acquired and reviewed as unchanged timing data. They do not inflate the original art inventory.
- The real cached AndroidX1.18.0 parser checks504 source paths plus7 tokenizer probes and all130816 unordered/self pairs. The SDK37 check compiles/links eight actual DocumentsUI resources with controlled read-only true/false flags, proving flagged AVDs share base animator/interpolator dependencies. Neither check executes Android or evaluates the installed product.

## Use and reproduce

Restore the signed ZIP from distribution/Restore-Archive.ps1, verify complete-assets.zip.sha256 and the detached signature against the separately pinned public identity. Full local ZIP delivery is also provided. Source/XML and reports are editable; there is no installable application in this checkpoint.

From the repository, run the tools in this order with Python3, the existing JDK, SDK37 and the recorded cached AndroidX dependency: fetch_native_interpolators.py; build_resource_graph_v22.py; review_native_contracts.py; audit_vector_motion_contracts.py; check_morph_paths_androidx.py; check_native_flag_scope.py; prepare_contract_checkpoint.py; verify_native_contract_review.py. Network acquisition reads pinned public files only. Builders refuse to rewrite a packaged checkpoint; use a new checkpoint directory for a new iteration. The SDK tool needs host execution outside the Windows sandbox in this environment; sandboxed aapt2 exits3221225477. Explicit file compilation includes flag directories that --dir scanning omitted.

Cold steel, separate neutral lighting masks, native English text and source-domain activation remain the design rules. This preservation pass introduces no emission/color mapping. Focus is not interpreted as activation. Main and all earlier signed checkpoints are preserved. No install, flashing, hardware action or device settings change occurs.

V1/V2 refer only to this bounded source/contract checkpoint. Full pinned Soong builds, Android/device execution, performance/accessibility acceptance and the final independent whole-goal double-check are NOT RUN. The goal is not complete.
''', encoding='utf8')
    (OUT/'REVIEW.md').write_text('''# Contract decisions and remaining gates

Preserve routing, dimensions/hotspots, IDs, frame timing, target names, transform/opacity/trim behavior and native qualifier/flag conditions. Do not replace these resources with a flattened icon. The content policy excludes inline vector/shape artwork, palette/opacity-bearing drawable wrappers, path morph data, custom classes and custom properties from blanket preservation decisions. A family closes only if every source qualifier meets the policy. State tables retain custom state namespaces and first-match order; no checkbox/name-based glow assumption is introduced.

The dependency queue names the actual candidate resource families outside this preservation pass. OPEN leaves, colors, styles, artwork, opaque external libraries, runtime theme attributes, effective product/overlay selection and native owner bridges are not approved by preservation of a parent wrapper. The queue is source evidence, not a complete installed-app inventory.

898 decisions include639 of the original7048 unassigned visual families and259 native state/motion families. The full10926-family ledger is retained. The original210 reuse candidate review,16 named gaps and20 app/component source roles remain represented, with their native gates intact. W03-W07, broader native layouts/tokens/bitmaps/vectors/Lottie/procedural owners, newly discovered artwork, full native acceptance and the final independent whole-goal double-check remain required.

The historical20 graph is retained as historical evidence.22 corrects8577 per-file scopes, adds79 supporting timing files, and resolves158 parameterized path uses. The graph does not evaluate Soong resource merging, runtime configurations, product flags or overlays. Static-base versus explicit path endpoints are preserved as separate geometry; six differences alone are not native morph failures. All named AVD target/property records are structurally accounted for, while native rendering is NOT RUN.

Verification uses distinct evidence layers: independent source/ledger/state-bitset checks; the actual AndroidX parser/canMorph implementation; actual SDK37 compilation/linking/table inspection for both read-only flag values; source hashes and historical archive/master preservation. No evidence layer is presented as Android/device execution. V3 and final whole-goal completion remain open.
''', encoding='utf8')
    print(json.dumps({'sourceObjects': len(objects), 'timingFiles': len(timing), 'dependencyFamilies': len(all_ids), 'openFamilyDecisions': progress['openFamilyDecisions']}))


if __name__ == '__main__': main()
