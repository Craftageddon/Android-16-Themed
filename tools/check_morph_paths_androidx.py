"""Compare path-command records with the real installed AndroidX implementation.

Host-only parser/canMorph execution, not Android Path interpolation/rendering and
not a claim about the effective pinned framework implementation or ROM build.
"""
from pathlib import Path
import base64, hashlib, json, os, subprocess, zipfile
from audit_os_resource_coverage import ROOT, read_json, write_json
from audit_vector_motion_contracts import signature

OUT = ROOT/'iterations/22-native-contract-review'
CACHE = Path(r'C:\Users\spencerm\Documents\Codex\2026-08-31\us\android-motion\.gradle-user\caches\modules-2\files-2.1\androidx.core\core\1.18.0\ff046a9f2725d94c2eaaa82e08674bb761c17792\core-1.18.0.aar')
SDK = Path(r'C:\Users\spencerm\AppData\Local\Android\Sdk\platforms\android-37.0\android.jar')
JDK = Path(r'C:\Program Files\Android\Android Studio\jbr\bin')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'complete-assets.zip').exists()
    work = ROOT/'build-work/contract22'; work.mkdir(parents=True, exist_ok=True)
    core = work/'core.jar'
    with zipfile.ZipFile(CACHE) as z: assert z.testzip() is None; core.write_bytes(z.read('classes.jar'))
    records = read_json(OUT/'morph-path-values.json')
    assert all(r['parsedCommandBlocks'] for r in records)
    edges = ['M1e-3,2E+2 L.5-.6z', 'M0,0 1,1Z', 'M0 0 L1 1 L2 2z',
             'm0 0l1 1z', 'M0 0A1 2 30 0 1 4 5z', 'M0 0 C1 2 3 4 5 6c',
             'M0,0L1.2.3-.4.5Z']
    inputs = [{'id': r['pathSha256'], 'value': r['value'], 'signature': r['signature']} for r in records]
    inputs += [{'id': 'synthetic-'+str(i), 'value': v, 'signature': signature(v)} for i, v in enumerate(edges)]
    fixture = work/'path-contract-input.tsv'
    fixture.write_text(''.join(r['id']+'\t'+base64.b64encode(r['value'].encode()).decode()+'\t'+','.join(c+str(n) for c,n in r['signature'])+'\n' for r in inputs), encoding='utf8')
    source = ROOT/'tools/PathContractCheck.java'; classes = work/'classes'; classes.mkdir(exist_ok=True)
    cp = os.pathsep.join([str(core), str(SDK)])
    compile_job = subprocess.run([str(JDK/'javac.exe'), '-encoding', 'UTF-8', '-cp', cp, '-d', str(classes), str(source)], capture_output=True, text=True)
    assert compile_job.returncode == 0, compile_job.stderr
    run_job = subprocess.run([str(JDK/'java.exe'), '-cp', os.pathsep.join([str(classes), cp]), 'PathContractCheck', str(fixture)], capture_output=True, text=True)
    evidence = OUT/'verification/evidence'; evidence.mkdir(parents=True, exist_ok=True)
    (evidence/'androidx-path-parser-output.txt').write_text(run_job.stdout+run_job.stderr, encoding='utf8')
    assert run_job.returncode == 0, run_job.stdout+run_job.stderr
    checks = json.loads(run_job.stdout.strip().splitlines()[-1]); assert checks['failures'] == 0
    report = {'date': '2026-10-26', 'result': 'PASS', **checks,
              'acquiredSourcePaths': len(records), 'syntheticTokenizerCases': len(edges),
              'androidxCoreVersion': '1.18.0', 'androidxAarSha256': sha(CACHE),
              'classesJarSha256': sha(core), 'sdk37JarSha256': sha(SDK),
              'javaRunnerSha256': sha(source), 'inputFixtureSha256': sha(fixture),
              'libraryOrigin': 'Existing read-only Gradle cache; not claimed as the official pinned framework implementation.',
              'method': 'Actual AndroidX PathParser.createNodesFromPathData compares all command types/parameter counts with the separately authored Python records; actual canMorph checks every unordered pair including self pairs.',
              'androidPathConstructionInterpolationRendering': 'NOT RUN',
              'hardwareOrAndroidExecution': False, 'finalWholeGoalDoubleCheck': 'NOT RUN'}
    write_json(evidence/'androidx-path-parser-checks.json', report); print(json.dumps(report))


if __name__ == '__main__': main()
