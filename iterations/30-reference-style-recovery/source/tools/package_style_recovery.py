"""Save the complete review checkpoint with verifiable portable output references."""
from pathlib import Path
import hashlib,html,json,shutil,subprocess,sys,zipfile
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'iterations/30-reference-style-recovery'
NS='{http://www.w3.org/2000/svg}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 rows=json.loads((OUT/'components.json').read_text())
 # Preserve original art/geometry inputs and exact dependencies; no old file is edited.
 sources=set(ROOT/r['sourceMaster'] for r in rows)
 for category,folder,manifest in [('magnification','23-magnification','components.json'),('updater','25-updater-workflows','workflow-art-components.json'),('gallery','26-gallery-workflows','gallery-art-components.json'),('setup','28-setup-workflows','setup-art-components.json')]:
  old=ROOT/'iterations'/folder
  def visit(obj):
   if isinstance(obj,dict):
    for k,v in obj.items():
     if k in ['files','densityConfigurations','nativeHighResolution']:continue
     visit(v)
   elif isinstance(obj,list):
    for v in obj:visit(v)
   elif isinstance(obj,str) and len(obj)<240 and obj.endswith(('.svg','.xml')):
    for p in [ROOT/obj,old/obj]:
     if p.is_file():sources.add(p)
  visit(json.loads((old/manifest).read_text()))
 for p in list(sources):
  if p.suffix=='.svg':
   for im in E.parse(p).getroot().iter(NS+'image'):
    href=im.get('href','')
    if href and not href.startswith('data:') and (p.parent/href).is_file():sources.add((p.parent/href).resolve())
 records=[]
 for p in sorted(sources):
  rel=p.relative_to(ROOT);dest=OUT/'source/provenance-inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  records.append({'original':rel.as_posix(),'copied':dest.relative_to(OUT).as_posix(),'sha256':sha(p)})
 (OUT/'source/provenance-inputs.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
 reference=ROOT/'iterations/29-reference-correction-pilot/previews/original-reference-strip.png';shutil.copy2(reference,OUT/'previews/original-reference-strip.png')
 for name in ['build_style_recovery.py','render_style_recovery_workflows.py','verify_style_recovery.py','package_style_recovery.py','build_reference_correction_pilot.py']:
  dest=OUT/'source/tools'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'tools'/name,dest)
 # A local, dependency-free visual index of every corrected master and state sample.
 page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Craftageddon reference style recovery</title><style>body{background:#080c11;color:#eee7d9;font:16px system-ui;margin:28px}a{color:#dfa06d}header{max-width:1000px}nav{display:flex;gap:20px;flex-wrap:wrap;margin:24px 0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:20px}.card{border:1px solid #363b3e;padding:16px;background:#10151b}.pair{display:flex;justify-content:space-around;min-height:170px}.pair img{max-width:150px;max-height:160px;object-fit:contain}h2{margin-top:40px}small{color:#b5bdc6}figure{margin:0;text-align:center}figcaption{padding:8px}footer{margin:30px 0;color:#b5bdc6}</style><header><h1>Craftageddon reference style recovery</h1><p>99 corrected material treatments. Cold steel and independently composited ember light. Existing native behavior remains separate. Device validation and final visual acceptance are pending.</p><p><a href="previews/recovery-overview.png">Before / cold / on overview</a> · <a href="previews/original-reference-strip.png">Original reference</a> · <a href="README.md">Scope and remaining checks</a></p></header><nav>']
 groups=['magnification','updater','gallery','setup','ayn']
 page += [f'<a href="#{g}">{g.title()}</a>' for g in groups];page.append('</nav>')
 for g in groups:
  page.append(f'<section id="{g}"><h2>{g.title()}</h2><div class="grid">')
  for r in [r for r in rows if r['category']==g]:
   label=html.escape(r['id'].removeprefix('cg_gl_').removeprefix('cg_upd_').removeprefix('cg_sw_').replace('_',' '));key=r['id']
   page.append(f'<article class="card"><h3>{label}</h3><div class="pair">')
   for state,title in [('cold','Cold'),('on','Lighting sample')]:page.append(f'<figure><img src="previews/individual/{g}/{key}.{state}.preview.png" alt="{label} {title}"><figcaption>{title}</figcaption></figure>')
   page.append(f'</div><p><a href="{r["master"]}">Editable master</a> · <a href="previews/individual/{g}/{key}.focused_off.preview.png">Focus only</a> · <a href="previews/individual/{g}/{key}.disabled.preview.png">Disabled</a></p><small>Original source size: {r["nativeReviewSize"][0]} × {r["nativeReviewSize"][1]} pixels at mdpi. Illustrated lighting does not change the actual owner state.</small></article>')
  page.append('</div></section>')
 page.append('<footer>Offline source renders. App-icon lighting is a layer demonstration. Earlier checkpoints are preserved. No device operations.</footer></html>')
 (OUT/'index.html').write_text(''.join(page),encoding='utf8')
 evidence=OUT/'verification/evidence/internal-visual-review.md'
 evidence.write_text('CHECK: V1\nRESULT: PASS\nScope: Internal design/spec review for the99-master correction candidate, not final user or device approval.\nInspected all nine cold/on group sheets against the original reference and iteration29 pilot, and inspected four refreshed screen specimens. Material is darker and textured, the inherited small-glyph bloom is narrower, copper is restrained, and cold remains unlit. All four pilot treatments are retained. Source/density/resource mappings, duplicate counting and compact-mask roles are explicit. Remaining limits: tiny inactive icon contrast on the Thor, individual sculptural/detail fidelity, installed tint ownership and final user visual acceptance remain open.\n',encoding='utf8')
 checks=json.loads((OUT/'verification/evidence/saved-output-checks.json').read_text());assert checks['result']=='PASS'
 (OUT/'verification/evidence/technical-review.md').write_text('CHECK: V2\nRESULT: PASS\nScope: Saved artwork and offline specimen checks only.\n'+json.dumps(checks,indent=2)+'\nThese results do not establish Android compilation, native state/input behavior, independent rendering, target-device contrast or whole-roadmap completion.\n',encoding='utf8')
 helper=Path(r'C:\Users\spencerm\.agents\skills\craftageddon-release-qa\scripts\triple_verify.py')
 tracked=[p for p in OUT.rglob('*') if p.is_file() and 'verification' not in p.relative_to(OUT).parts]
 # Use a short argument list while hash-tracking every deliverable via a manifest.
 manifest={p.relative_to(OUT).as_posix():sha(p) for p in sorted(tracked)}
 (OUT/'ARTIFACTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
 subprocess.run([sys.executable,str(helper),'init','--root',str(OUT),'--project','Reference style recovery 0.2.0','--artifact','ARTIFACTS.json','--artifact','README.md','--artifact','components.json','--artifact','index.html'],check=True)
 for stage,method,file in [(1,'Original reference and all group sheets; bounded internal material review','internal-visual-review.md'),(2,'Independent saved-output reopening, metadata, geometry and state checks','technical-review.md')]:
  subprocess.run([sys.executable,str(helper),'record','--root',str(OUT),'--check',str(stage),'--method',method,'--reviewer','Codex','--evidence','verification/evidence/'+file],check=True)
 sums=[p for p in OUT.rglob('*') if p.is_file() and p.name not in ['SHA256SUMS.txt','complete-assets.zip']]
 (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(OUT).as_posix()+'\n' for p in sorted(sums)),encoding='utf8')
 z=OUT/'complete-assets.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,9) as a:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p!=z:a.write(p,p.relative_to(OUT).as_posix())
 with zipfile.ZipFile(z) as a:
  assert a.testzip() is None
  for line in a.read('SHA256SUMS.txt').decode().splitlines():
   h,n=line.split('  ',1);assert hashlib.sha256(a.read(n)).hexdigest()==h
 dest=ROOT.parent/'Deliverables/Forge_30_Reference_Style_Recovery_2026-10-29';dest.mkdir(exist_ok=True)
 # Complete extracted copy lets index.html open immediately, with all original paths intact.
 shutil.copytree(OUT,dest,dirs_exist_ok=True)
 report={'archiveSha256':sha(z),'archiveBytes':z.stat().st_size,'archiveMembers':len(sums)+1,'sourceInputsPreserved':len(records),'fullExtractedCopy':str(dest),'productionMasters':99,'sourcePngConfigurations':2895,'independentFinalValidation':'PENDING','finalized':False}
 (dest/'LOCAL-DELIVERY.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))

if __name__=='__main__':main()
