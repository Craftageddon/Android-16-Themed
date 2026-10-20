"""Hash-bind a complete collection archive without exceeding Windows argument limits."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--helper',type=Path,required=True);a=p.parse_args();root=a.root.resolve();helper=a.helper.resolve()
report=json.loads((root/'verification/evidence/technical.json').read_text());n=report['components']
for stage,method,obs in [(1,'Roadmap and component-family source inspection',f'{n} distinct designed variants have editable cold/seam/core/symbol sources and live-content separation. Roadmap IDs and unresolved scope are explicit. This passes the exploratory checkpoint scope, not final visual acceptance.'),(2,'SVG parsing, alpha and neutral-mask pixel audit',json.dumps(report))]:
 (root/f'verification/evidence/V{stage}.txt').write_text(f'CHECK: V{stage}\nRESULT: PASS\nSCOPE: Work-in-progress desktop design collection.\nMETHOD: {method}\nOBSERVATIONS: {obs}\nTarget Android integration, physical device rendering, final accessibility and performance are NOT RUN.\n')
(root/'verification/evidence/V3-status.md').write_text('CHECK: V3\nRESULT: NOT RUN on target device.\nDesktop visual review is recorded in REVIEW.md. All production integration and physical-device acceptance remain pending. This is a saved source/design checkpoint, not a finalized Android release.\n')
files=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name not in ['SHA256SUMS.txt','complete-assets.zip','complete-assets.zip.sha256'] and p.name!='state.json']
(root/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in files))
subprocess.run([sys.executable,str(Path(__file__).with_name('package_iteration.py')),str(root)],check=True)
subprocess.run([sys.executable,str(helper),'init','--root',str(root),'--project',root.name,'--artifact','complete-assets.zip'],check=True)
for stage,method in [(1,'Roadmap and component-family source inspection'),(2,'SVG parsing, alpha and neutral-mask pixel audit')]:subprocess.run([sys.executable,str(helper),'record','--root',str(root),'--check',str(stage),'--method',method,'--reviewer','Codex desktop verification','--evidence',f'verification/evidence/V{stage}.txt'],check=True)
subprocess.run([sys.executable,str(helper),'status','--root',str(root)],check=True)
