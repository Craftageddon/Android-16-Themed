"""Preserve raw originals and add path-portable SVG copies for direct editing."""
from pathlib import Path
import argparse,hashlib,json,xml.etree.ElementTree as ET
def build(root):
 repo=Path(__file__).resolve().parents[1];rows=json.loads((root/'source/asset-provenance.json').read_text(encoding='utf8'))['masters'];out=root/'source/portable-masters';out.mkdir(exist_ok=True);manifest=[]
 for row in rows:
  original=repo/row['source'];doc=ET.parse(original).getroot()
  for image in doc.findall('.//{http://www.w3.org/2000/svg}image'):
   href=image.get('href','')
   if href.startswith(('data:','#')):continue
   path=(original.parent/href).resolve();assert path.is_relative_to(repo);data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();target=root/'source/rasters'/f'{digest}.png';assert target.read_bytes()==data;image.set('href',f'../rasters/{digest}.png')
  target=out/Path(row['originalCopy']).name;ET.register_namespace('','http://www.w3.org/2000/svg');target.write_bytes(ET.tostring(doc,encoding='utf-8',xml_declaration=True));manifest.append({'original':row['source'],'originalSha256':row['sha256'],'portableCopy':target.relative_to(root).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'change':'External image paths only; unchanged original raster bytes'})
 (root/'source/portable-source-manifest.json').write_text(json.dumps({'masters':manifest,'scope':'Open these copies in a vector editor; raw original-masters retain exact original bytes and original relative paths'},indent=2)+'\n')
 print(json.dumps({'portableMasters':len(manifest),'unchangedRasterBytes':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
