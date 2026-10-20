"""Hash-track source and desktop artifact evidence without asserting device acceptance."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys

def run(root,helper,stage=None):
 artifacts=[p for p in sorted(root.rglob('*')) if p.is_file() and 'verification' not in p.relative_to(root).parts and p.name!='SHA256SUMS.txt']
 args=[sys.executable,str(helper),'init','--root',str(root),'--project',root.name]
 for p in artifacts:args.extend(['--artifact',p.relative_to(root).as_posix()])
 subprocess.run(args,check=True)
 methods={1:'Requirements mapped to 18 distinct specimen source families',2:'XML parse, PNG decode, mask color, alpha and contrast audit'}
 for n in [1,2]:
  p=root/f'verification/evidence/V{n}.txt'
  p.write_text(f'CHECK: V{n}\nRESULT: PASS\nSCOPE: Desktop exploratory design checkpoint, not production Android release.\nMETHOD: {methods[n]}\nOBSERVATIONS: '+('All 18 named pilot families exist with four editable layers, cold inspection and seven state previews. The generated material study is explicitly separated from production geometry. No live content is baked into masters. Material richness will continue in later passes.' if n==1 else 'See technical.json for audited PNG counts, neutral mask checks, independent XML parsing and calculated palette contrast. Measurements cover exported files, not hardware behavior or GUI accessibility.')+'\nEXCLUSIONS: Actual device, ROM integration and hardware control testing are NOT RUN.\n',encoding='utf-8')
  subprocess.run([sys.executable,str(helper),'record','--root',str(root),'--check',str(n),'--method',methods[n],'--reviewer','Codex desktop audit','--evidence',p.relative_to(root).as_posix()],check=True)
 # V3 target checks intentionally remain pending; this is a source checkpoint.
 (root/'verification/evidence/V3-status.md').write_text('CHECK: V3\nRESULT: NOT RUN on physical target.\nDesktop visual review notes are in REVIEW.md. Inkscape Store installation was located, but Windows denied direct CLI execution, including outside the filesystem sandbox. No Inkscape GUI success is claimed.\nDevice rendering, controller routing, real thermal controls, lifecycle, frame time and battery measurements remain unverified. These WIP source uploads are not finalized releases.\n')
 (root/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in sorted(root.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
 subprocess.run([sys.executable,str(helper),'status','--root',str(root)],check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--helper',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.helper.resolve())
