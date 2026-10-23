"""Independently re-open the complete portable handoff and verify provenance."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];root=ROOT/'iterations/17-forge-coverage';NS='{http://www.w3.org/2000/svg}'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
catalog=json.loads((root/'canonical-masters.json').read_text());masters=json.loads((root/'current-library/manifest.json').read_text())['masters'];scenes=json.loads((root/'current-library/compositions.json').read_text())['compositions']
assert len(masters)==472 and len(scenes)==189
assert {r['assetId'] for r in masters}=={r['assetId'] for r in catalog['masters']}
labels=images=0;rasters=set()
for row in masters+scenes:
 source=ROOT/row.get('source',row.get('original'));portable=root/row.get('portableMaster',row.get('portable'))
 assert h(source)==row.get('sha256',row.get('originalSha256'))
 assert h(portable)==row['portableSha256']
 a=E.parse(source).getroot();b=E.parse(portable).getroot();aa=list(a.iter());bb=list(b.iter());assert len(aa)==len(bb)
 for x,y in zip(aa,bb):
  assert x.tag==y.tag and x.text==y.text
  assert x.tag.split('}')[-1] not in ['script','foreignObject']
  assert not any(k.lower().startswith('on') for k in y.attrib)
  ax=dict(x.attrib);ay=dict(y.attrib)
  if x.tag==NS+'image':
   ax.pop('href',None);href=ay.pop('href',None)
   if href and not href.startswith('#'):
    p=(portable.parent/href).resolve();assert p.is_relative_to((root/'current-library/rasters').resolve()) and p.is_file()
    assert h(p)==p.stem;rasters.add(p.stem);images+=1
  assert ax==ay,(portable,'geometry changed')
  if y.tag==NS+'text':
   labels+=1;assert not any(c.isalpha() and not c.isascii() for c in ''.join(y.itertext())),portable
 if 'portableMaster' in row:
  assert not b.findall('.//'+NS+'text')
  for name in ['reflection','spill','seam','core','focus','symbol']:assert b.find(NS+'g[@id="'+name+'"]').get('style')=='display:none'
for p in (root/'current-library/previews').glob('*.png'):
 with Image.open(p) as im:im.verify()
assert len(list((root/'current-library/previews').glob('current-masters-*.png')))==20
assert len(list((root/'current-library/previews').glob('current-compositions-*.png')))==16
report={'result':'PASS','date':'2026-10-23','portableMasters':len(masters),'portableCompositions':len(scenes),'liveEnglishTextNodes':labels,'resolvedImageReferences':images,'sharedRasters':len(rasters),'masterSheets':20,'compositionSheets':16,'method':'Re-open source and portable XML independently; SHA256 source and copied files; exact geometry/attribute/live-text parity excluding normalized image paths; reference containment and raster hashes; parse all live labels and verify all sheet PNGs.','limits':'Representative sheets manually inspected. No automated browser, Inkscape editing round trip, native renderer or physical device acceptance claimed.'}
(root/'verification/evidence/current-library-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
