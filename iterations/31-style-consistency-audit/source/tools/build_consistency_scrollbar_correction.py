"""Fix the one additional material omission found by the catalog audit."""
from pathlib import Path
import base64,copy,hashlib,json,shutil,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageChops
from forge_library import layer,raster,xml,compose_layers
from build_pilot import font
from audit_style_consistency import ROOT,OUT,THUMB_SOURCE,write,sha
N='{http://www.w3.org/2000/svg}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']

def main():
 assert not (OUT/'complete-assets.zip').exists()
 source=ROOT/THUMB_SOURCE;original_bytes=source.read_bytes();before=E.fromstring(original_bytes);after=copy.deepcopy(before)
 cold=after.find(N+"g[@id='cold']");matches=[n for n in cold.iter(N+'path') if n.get('fill')=='url(#edge)' and n.get('stroke') is None]
 assert len(matches)==1;thumb=matches[0];original_d=thumb.get('d')
 defs=after.find(N+'defs');material=copy.deepcopy(defs.find(N+"pattern[@id='forged']"));material.set('id','scrollbar-thumb-forged')
 for n in material.iter():
  for a in ['width','height']:
   if n.get(a):n.set(a,'32')
 defs.append(material)
 # The original silhouette supplies the clipping boundary; no control bounds move.
 clip=E.SubElement(defs,N+'clipPath',id='scrollbar-thumb-silhouette');E.SubElement(clip,N+'path',d=original_d)
 thumb.set('fill','url(#scrollbar-thumb-forged)');thumb.set('stroke','url(#edge)');thumb.set('stroke-width','.8');thumb.set('stroke-linejoin','round');thumb.set('clip-path','url(#scrollbar-thumb-silhouette)')
 assert [n.get('d') for n in cold.iter(N+'path')]==[n.get('d') for n in before.find(N+"g[@id='cold']").iter(N+'path')]
 (OUT/'masters').mkdir(parents=True,exist_ok=True);(OUT/'source').mkdir(exist_ok=True)
 tex=ROOT/'iterations/12-forge-controls-and-screens/source/steel-material.png';shutil.copy2(tex,OUT/'source/steel-material.png');texture=base64.b64encode(tex.read_bytes()).decode()
 (OUT/'source/control-scrollbar.before.svg').write_bytes(original_bytes)
 # A before-source copy has the same ../source image path within this folder.
 p=OUT/'masters/control-scrollbar.svg';p.write_text(xml(after),encoding='utf8')
 style=json.loads((ROOT/'iterations/12-forge-controls-and-screens/runtime-style.json').read_text());write(OUT/'runtime-style.json',style)
 exports=[];native={}
 for name in LAYERS:
  doc=layer(after,name)
  if name!='cold':
   for definition in list(doc.find(N+'defs')):
    if definition.tag==N+'pattern':doc.find(N+'defs').remove(definition)
  target=OUT/'layers'/('control-scrollbar.'+name+'.svg');target.parent.mkdir(exist_ok=True);target.write_text(xml(doc),encoding='utf8')
  for width in [32,64]:
   im=raster(doc,width,texture);old=raster(layer(before,name),width,texture);scale=width//32
   assert im.size==old.size==(width,192*scale)
   if name=='cold':
    difference=ImageChops.difference(im,old);mask=Image.new('L',im.size,255);ImageDraw.Draw(mask).rectangle((7*scale,47*scale,25*scale,113*scale),fill=0)
    assert not ImageChops.multiply(difference,Image.merge('RGBA',(mask,mask,mask,mask))).getbbox()
    assert im.getchannel('A').getbbox()==old.getchannel('A').getbbox()
   else:
    assert im.tobytes()==old.tobytes()
    assert all(r==g==b for r,g,b,a in im.get_flattened_data() if a)
   target=OUT/'exports'/f'control-scrollbar.{name}.{width}.png';target.parent.mkdir(exist_ok=True);im.save(target);exports.append({'path':target.relative_to(OUT).as_posix(),'sha256':sha(target),'layer':name,'size':list(im.size)})
   if width==32:native[name]=im
 for state,desc in style['sampleStates'].items():
  target=OUT/'previews'/('control-scrollbar.'+state+'.png');target.parent.mkdir(exist_ok=True);compose_layers(native,desc).save(target)
 # Larger comparison renders come directly from the editable SVGs, not retouching.
 banks=[{n:raster(layer(doc,n),80,texture) for n in LAYERS} for doc in [before,after]]
 images=[compose_layers(banks[0],style['sampleStates']['off']),compose_layers(banks[1],style['sampleStates']['off']),compose_layers(banks[1],style['sampleStates']['on'])]
 board=Image.new('RGB',(1120,780),'#080c11');d=ImageDraw.Draw(board)
 d.text((28,20),'STYLE CHECK / SCROLLBAR MATERIAL CORRECTION',font=font(28,True),fill='#eee7d9')
 for x,label,im in zip([110,450,790],['Before / smooth','Corrected / cold','Corrected / on'],images):
  d.text((x-38,85),label,font=font(19),fill='#eee7d9');board.paste(im,(x,135),im)
  tiny=native['cold'] if x!=790 else compose_layers(native,style['sampleStates']['on']);board.paste(tiny,(x+110,260),tiny)
 d.text((28,680),'Original texture restored. Same paths, bounds and six neutral masks.',font=font(20),fill='#b5bdc6')
 d.text((28,720),'Large examples at 2.5x; narrow examples at actual 32 x 192 pixels. Device validation pending.',font=font(16),fill='#b5bdc6');board.save(OUT/'previews/scrollbar-before-cold-on.png')
 write(OUT/'correction.json',{'source':THUMB_SOURCE,'sourceSha256':hashlib.sha256(original_bytes).hexdigest(),'corrected':'masters/control-scrollbar.svg','correctedSha256':sha(p),'scope':'One additional untextured scrollbar-thumb surface; material and clipped bevel only','pathDataUnchanged':True,'canvasAndAspectUnchanged':True,'neutralMasksPixelIdentical':True,'coldChangesConfinedToThumbRegion':True,'productionLayerPngs':14,'nativeIntegrated':False,'deviceVerified':False,'files':exports})
 assert source.read_bytes()==original_bytes
 print(json.dumps({'additionalCorrectedMasters':1,'productionLayers':len(exports),'originalPathsAndMasksPreserved':True,'sourceBeforeUnchanged':True}))

if __name__=='__main__':main()
