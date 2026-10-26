"""Compile/link the actual flagged DocumentsUI AVD and native base dependencies."""
from pathlib import Path
import collections, hashlib, json, shutil, subprocess
from audit_os_resource_coverage import ROOT, read_json, write_json

BASE = ROOT/'iterations/20-semantic-review'
OUT = ROOT/'iterations/22-native-contract-review'
SDK = Path(r'C:\Users\spencerm\AppData\Local\Android\Sdk')
AAPT = SDK/'build-tools/37.0.0/aapt2.exe'
ANDROID = SDK/'platforms/android-37.0/android.jar'
PROJECT = 'packages/apps/DocumentsUI'
ENTRY = 'res/flag(com.android.documentsui.flags.use_material3)/drawable/progress_indeterminate_horizontal_material_trimmed_m3.xml'
FLAG = 'com.android.documentsui.flags.use_material3'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    declarations = read_json(OUT/'resource-declarations.json'); graph = read_json(OUT/'resource-reference-graph.json')
    by_file = collections.defaultdict(list); sources = {}
    for d in declarations:
        if d['project'] == PROJECT: sources[d['path']] = d
    for u in graph: by_file[(u['project'], u['path'])].append(u)
    pending = [ENTRY]; seen = set(); unresolved = []
    while pending:
        path = pending.pop()
        if path in seen: continue
        seen.add(path)
        for use in by_file[(PROJECT, path)]:
            ref = use['reference']
            if ref['pkg'] is None and ref['sig'] == '@' and ref['type'] not in {'id', '+id'} and ref['name'] not in {'null', 'empty'}:
                if not use['candidates']: unresolved.append(use)
                for i in use['candidates']:
                    d = declarations[i]
                    assert d['project'] == PROJECT
                    pending.append(d['path'])
    assert not unresolved, unresolved
    work = ROOT/'build-work/f22'; work.mkdir(parents=True, exist_ok=True)
    receipts = []
    for path in sorted(seen):
        d = sources[path]; sha = d['gitBlobSha1']; src = BASE/'source/objects'/sha[:2]/sha[2:]
        if not src.exists(): src = OUT/'source/objects'/sha[:2]/sha[2:]
        data = src.read_bytes(); assert hashlib.sha256(data).hexdigest() == d['sha256']
        dest = work/path; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        receipts.append({'path': path, 'gitBlobSha1': sha, 'sha256': d['sha256']})
    manifest = work/'AndroidManifest.xml'
    manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.craftageddon.contractreview"><uses-sdk android:minSdkVersion="33" android:targetSdkVersion="37"/><application/></manifest>\n', encoding='utf8')
    def run(args):
        args = [x.relative_to(work) if isinstance(x, Path) and x.is_relative_to(work) else x for x in args]
        result = subprocess.run([str(x) for x in args], cwd=work, capture_output=True, text=True, encoding='utf8', errors='replace')
        assert result.returncode == 0, 'Exit '+str(result.returncode)+' for '+str(args)+'\n'+result.stdout+'\n'+result.stderr
        return result.stdout+result.stderr
    evidence = OUT/'verification/evidence'; evidence.mkdir(parents=True, exist_ok=True)
    cases = []
    for enabled in [True, False]:
        label = 'enabled' if enabled else 'disabled'; value = str(enabled).lower()
        compiled = work/('compiled-'+label); compiled.mkdir(exist_ok=True); linked = work/('flag-'+label+'.ap_')
        # Soong compiles the explicit resource list, including flag directories.
        # The SDK directory scanner omits those directories on this host.
        log = run([AAPT, 'compile', '--feature-flags', FLAG+':ro='+value, '-o', compiled, *[work/path for path in sorted(seen)]])
        flats = sorted(compiled.rglob('*.flat')); assert flats
        log += run([AAPT, 'link', '-I', ANDROID, '--manifest', manifest, '--feature-flags', FLAG+':ro='+value, '-o', linked, *flats])
        dump = run([AAPT, 'dump', 'resources', linked]); (evidence/('flag-'+label+'-resource-table.txt')).write_text(dump, encoding='utf8')
        (evidence/('flag-'+label+'-compile.txt')).write_text(log, encoding='utf8')
        avd_present = 'drawable/progress_indeterminate_horizontal_material_trimmed_m3' in dump
        base_anim_present = 'anim/progress_indeterminate_horizontal_rect1' in dump
        assert avd_present == enabled and base_anim_present, dump
        cases.append({'flag': value, 'testFlagReadOnly': True, 'flaggedAvdInLinkedTable': avd_present,
                      'unflaggedBaseAnimatorInLinkedTable': base_anim_present,
                      'linkedResourceBankSha256': hashlib.sha256(linked.read_bytes()).hexdigest()})
    report = {'date': '2026-10-26', 'result': 'PASS', 'actualPinnedSources': receipts,
              'resourceFilesCompiled': len(receipts), 'sdkApi': 37, 'cases': cases,
              'aapt2Sha256': hashlib.sha256(AAPT.read_bytes()).hexdigest(),
              'sdkJarSha256': hashlib.sha256(ANDROID.read_bytes()).hexdigest(),
              'scope': 'Actual source resource compile/link and table inspection with native feature flag true/false. A flag directory shares unflagged animator/interpolator dependencies within the resource root.',
              'toolingObservation': 'Sandboxed Windows SDK37 aapt2 exited3221225477 without diagnostics. The source compiler/linker is run outside the sandbox using explicit original resource files, relative paths and directory output; the directory scanner omitted flagged paths. Read-only true/false values are controlled test inputs, not claims about the installed product flag state.',
              'fullPinnedDocumentsUiSoongBuild': 'NOT RUN', 'androidExecution': 'NOT RUN',
              'installableApplicationProduced': False, 'hardwareActions': 'NONE'}
    write_json(evidence/'native-flag-scope-checks.json', report); print(json.dumps({k:v for k,v in report.items() if k != 'actualPinnedSources'}))


if __name__ == '__main__': main()
