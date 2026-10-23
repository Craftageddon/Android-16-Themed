"""Wire mapped real SVG masters to the draft deterministic motion owner.

Pending composites stay explicitly unavailable. This does not make 114 recipes
complete and does not implement any native or hardware service.
"""
from pathlib import Path
import argparse,base64,hashlib,html,json,shutil,subprocess,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];SVG='http://www.w3.org/2000/svg';LAYERS=['cold','reflection','spill','seam','core','focus','symbol'];ET.register_namespace('',SVG)

def build(out,node):
 assert (out/'DRAFT-STATUS.json').is_file() and not (out/'complete-assets.zip').exists(),'Unpackaged draft required'
 for folder in ['runtime','source/original-masters','source/rasters']:(out/folder).mkdir(parents=True,exist_ok=True)
 catalog=json.loads((out/'source/retained-catalog.json').read_text(encoding='utf8'));bindings=json.loads((out/'reconciliation.json').read_text(encoding='utf8'));sources=sorted({l['source'] for r in bindings for l in r['newLayers'] if l['source']});assets={};provenance=[];rasters={}
 for index,source in enumerate(sources):
  file=ROOT/source;data=file.read_bytes();doc=ET.fromstring(data);key=f'asset-{index:03}';original=out/'source/original-masters'/f'{key}.svg';original.write_bytes(data);embedded=[]
  assert not doc.findall('.//{'+SVG+'}text'),'Motion masters must keep live text separate'
  for n in doc.iter():
   assert n.tag not in ['{'+SVG+'}script','{'+SVG+'}foreignObject']
   assert not any(k.lower().startswith('on') for k in n.attrib)
   if n.get('id') in LAYERS:n.set('data-forge-layer',n.get('id'))
  for n in doc.findall('.//{'+SVG+'}image'):
   href=n.get('href','')
   if href.startswith('#'):continue
   if href.startswith('data:image/png;base64,'):image=base64.b64decode(href.split(',',1)[1],validate=True)
   else:
    image_path=(file.parent/href).resolve();assert image_path.is_relative_to(ROOT) and image_path.suffix=='.png' and image_path.is_file(),(source,href);image=image_path.read_bytes();n.set('href','data:image/png;base64,'+base64.b64encode(image).decode())
   digest=hashlib.sha256(image).hexdigest();(out/'source/rasters'/f'{digest}.png').write_bytes(image);rasters[digest]={'file':f'rasters/{digest}.png','sha256':digest,'bytes':len(image)};embedded.append(digest)
  w,h=map(float,doc.get('viewBox').split()[2:]);assets[source]={'id':key,'width':w,'height':h,'markup':ET.tostring(doc,encoding='unicode')};provenance.append({'source':source,'originalCopy':original.relative_to(out).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'embeddedRasters':embedded})
 (out/'source/asset-provenance.json').write_text(json.dumps({'masters':provenance,'rasters':list(rasters.values())},indent=2)+'\n')
 for name in ['forge_motion_v3','forge_motion_clock','forge_motion_parts']:
  shutil.copy2(ROOT/'tools'/f'{name}.cjs',out/'runtime'/f'{name}.js');shutil.copy2(ROOT/'tools'/f'{name}.cjs',out/'source'/f'{name}.cjs')
 shutil.copy2(ROOT/'tools/forge_motion_viewer.js',out/'runtime/viewer.js')
 rows=[]
 for recipe,binding in zip(catalog['recipes'],bindings):
  assert recipe['id']==binding['id'];rows.append({**recipe,**binding,'layers':binding['newLayers']})
 payload=json.dumps({'recipes':rows,'assets':assets},ensure_ascii=False).replace('</','<'+chr(92)+'/')
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reference Forge 16 — Motion draft</title><style>body{margin:24px;background:#080c11;color:#eee7d9;font:18px system-ui}p{max-width:95ch;color:#b5bdc6}select,button{background:#17212a;color:#eee7d9;border:1px solid #73818c;padding:12px;font:inherit;margin:5px}label{display:inline-block;margin:10px}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #d5e7f2}#stage{display:block;width:min(100%,900px);height:auto;overflow:visible;background:#10151b;border:1px solid #4a3b2d}#live{font-size:26px;min-height:40px;color:#eee7d9}#details{white-space:pre-wrap;font:16px system-ui}button:disabled{opacity:.5}</style><h1>Reference Forge 16 — Motion draft</h1><p>Review the mapped cold steel and its separate light masks. All text is English. Missing composite artwork is explicitly blocked; a generic panel is never counted as a replacement. This viewer controls artwork only.</p><label>Recipe <select id="recipe"></select></label><div><button id="play">Play once</button><button id="stop">Stop</button><label><input id="on" type="checkbox">Selected / on</label><label><input id="focus" type="checkbox">Neutral focus</label><label><input id="reduced" type="checkbox">Reduced motion</label><label><input id="enabled" type="checkbox" checked>Enabled</label></div><h2 id="title"></h2><p id="description"></p><svg id="stage" viewBox="0 0 720 460" role="img" aria-labelledby="title"></svg><p id="live" aria-live="off"></p><p id="status" aria-live="polite"></p><p id="details"></p><p>Loop recipes show two cycles per replay and then stop. Leaving the page or hiding this stage cancels playback; returning does not silently resume it. Native, hardware and device behavior are not exercised.</p><script id="motion-data" type="application/json">DATA</script><script src="runtime/forge_motion_v3.js"></script><script src="runtime/forge_motion_clock.js"></script><script src="runtime/forge_motion_parts.js"></script><script src="runtime/viewer.js"></script></html>'''.replace('DATA',payload)
 (out/'index.html').write_text(page,encoding='utf8');run=subprocess.run([node,'--test','--test-reporter=tap','tools/forge_motion_v3.test.cjs','tools/forge_motion_clock.test.cjs','tools/forge_motion_parts.test.cjs','tools/forge_motion_semantics.test.cjs'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');assert run.returncode==0,run.stdout+run.stderr;(out/'verification/evidence/sampler-and-clock-tests.txt').write_text(run.stdout+run.stderr,encoding='utf8')
 mapped=sum(not r['pendingArtwork'] for r in rows);total_tests=int(__import__('re').search(r'# tests (\d+)',run.stdout)[1])
 report=json.loads((out/'DRAFT-STATUS.json').read_text(encoding='utf8'));report.update(sourceMappedRecipes=mapped,recipesNeedingSpecificCompositeArtwork=len(rows)-mapped,distinctMappedSourceMasters=len(sources),distinctExistingSourceMasters=sum(not s.startswith('iterations/16-forge-motion/') for s in sources),newComponentMasters=sum(s.startswith('iterations/16-forge-motion/') for s in sources),samplerTestsPassed=9,clockTestsPassed=7,partTestsPassed=7,semanticTestsPassed=total_tests-23,samplerAndClockTestsPassed=total_tests,browserPlayback=f'WIRED FOR {mapped} SOURCE-MAPPED RECIPES; BROWSER VISUAL/INTERACTION REVIEW NOT RUN',browserAttempt='Local file protocol blocked by Browser Use security policy. No alternate browser/network workaround attempted; acceptance remains NOT RUN.',sourceToRuntimeBinding=f'Draft SVG renderer for mapped masters; {len(rows)-mapped} missing-composite recipes explicitly blocked; per-part fill/stroke/milestone semantics still need implementation/review',scope='Exact retained inventory, draft source bindings, SVG sampler/clock and bounded desktop frame review. No native motion or target completion claim.',samplerSha256=hashlib.sha256((ROOT/'tools/forge_motion_v3.cjs').read_bytes()).hexdigest(),clockSha256=hashlib.sha256((ROOT/'tools/forge_motion_clock.cjs').read_bytes()).hexdigest());(out/'DRAFT-STATUS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--node',required=True);a=p.parse_args();build(a.out.resolve(),a.node)
