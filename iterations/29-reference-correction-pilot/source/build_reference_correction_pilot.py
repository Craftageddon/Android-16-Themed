"""Bounded material correction. Never rebuild or overwrite an earlier checkpoint."""
from pathlib import Path
import base64, copy, hashlib, io, json, shutil, sys, xml.etree.ElementTree as E
from PIL import Image, ImageDraw, ImageFont
from forge_library import setup, steel, lights, joint, layer, raster, xml
from build_pilot import add, path, chamfer
import build_gallery_art as gallery
import build_magnification_art as magnification

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'iterations/29-reference-correction-pilot'
SVG = '{http://www.w3.org/2000/svg}'
LAYERS = ['cold','reflection','spill','seam','core','focus','symbol']
COLORS = dict(zip(LAYERS[1:], ['#dc5920','#ff4908','#ff5b0b','#ffd083','#d5e7f2','#ffe5bc']))
STATES = {
 'cold':[1,0,0,0,0,0,0], 'on':[1,.32,.72,1,.62,0,0],
 'focused_off':[1,0,0,0,0,1,0], 'selected_focused':[1,.32,.72,1,.62,1,1],
 'pressed_off':[1,0,0,0,0,0,0], 'disabled':[.42,0,0,0,0,0,0],
 'reduced_motion_on':[1,.32,.72,1,.62,0,0],
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
def circle(x,y,r): return f'M{x-r} {y} A{r} {r} 0 1 0 {x+r} {y} A{r} {r} 0 1 0 {x-r} {y}'
def font(n,bold=False): return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',n)

def focus(root,pad=1):
 w,h=float(root.get('width')),float(root.get('height'))
 g=root.find(SVG+"g[@id='focus']")
 if not len(g):
  path(g,f'M{pad} {pad+3}V{pad}H{pad+3} M{w-pad-3} {pad}H{w-pad}V{pad+3} M{pad} {h-pad-3}V{h-pad}H{pad+3} M{w-pad-3} {h-pad}H{w-pad}V{h-pad-3}',stroke='white',width=.6)

def location():
 # Rebuild exact existing source paths with the unmodified original material.
 gallery.OUT=ROOT/'iterations/28-setup-workflows'
 gallery.readable_cold=lambda root:root
 root,_=gallery.source_treatment(gallery.OUT/'source/geometry-inputs/ic_location.xml')
 for n in root.find(SVG+'defs').find(SVG+"pattern[@id='forged']").iter():
  for a in ['width','height']:
   if n.get(a):n.set(a,'19')
 # Tiny restrained copper fasteners stay within the existing pin body.
 cold=root.find(SVG+"g[@id='cold']")
 local=add(cold,'g',transform='scale(4)')
 for x,y,s in [(12,3.1,.62),(12,19.9,.50)]:joint(local,x,y,s)
 # The filled face needs inset channels, not an illuminated silhouette outline.
 channel='M6.4 8.8C6.5 5.6 8.2 3.7 10.5 3.4 M13.5 3.4C15.8 3.7 17.5 5.6 17.6 8.8 M6.6 11.2Q8 15.5 11 18.9 M17.4 11.2Q16 15.5 13 18.9'
 path(local,channel,stroke='#030609',width=.60)
 for name in ['reflection','spill','seam','core']:
  g=root.find(SVG+"g[@id='"+name+"']")
  for child in list(g):g.remove(child)
 groups={name:add(root.find(SVG+"g[@id='"+name+"']"),'g',transform='scale(4)') for name in ['reflection','spill','seam','core']}
 lights(groups,channel,.17)
 for x,y in [(7.5,5.6),(16.5,5.6),(10.7,18.4),(13.3,18.4)]:add(groups['core'],'circle',cx=x,cy=y,r=.12,fill='white')
 for fid,sigma in [('light-spill','.30'),('light-reflection','.12')]:
  root.find(SVG+'defs').find(SVG+"filter[@id='"+fid+"']").find(SVG+'feGaussianBlur').set('stdDeviation',sigma)
 focus(root)
 return root

def thin_control():
 root,_,_,_=magnification.glyph('ic_magnification_menu_close','Finish editing window size')
 cold=root.find(SVG+"g[@id='cold']")
 paths=list(cold)
 paths[0].set('stroke','#020509')
 paths[0].set('stroke-width','1.7')
 paths[1].set('stroke','url(#edge)')
 paths[1].set('stroke-width','1.5')
 textured=copy.deepcopy(paths[1]);textured.set('stroke','url(#forged)');textured.set('stroke-width','1.02');cold.append(textured)
 # Recess is drawn underneath the independent ember seam, and is cold off.
 dark=copy.deepcopy(paths[1]);dark.set('stroke','#080b0e');dark.set('stroke-width','.24');cold.append(dark)
 for name,width in [('seam','.36'),('core','.11'),('spill','1.0'),('reflection','1.2')]:
  for p in root.find(SVG+"g[@id='"+name+"']").iter(SVG+'path'):p.set('stroke-width',width)
 # Remove an unused silver gradient as well, so it cannot be reused accidentally.
 defs=root.find(SVG+'defs');defs.remove(defs.find(SVG+"linearGradient[@id='glyph-steel']"))
 # Optical adjustment for this 32px stroke only; no blue/silver face gradient.
 for n,c in zip(defs.find(SVG+"linearGradient[@id='edge']"),['#84817a','#4b4c49','#282b2c','#66645f','#252829']):n.set('stop-color',c)
 for n in defs.find(SVG+"pattern[@id='forged']").iter():
  for a in ['width','height']:
   if n.get(a):n.set(a,'24')
 focus(root)
 return root

def photo_frame():
 root,g=setup(96,96,'Correction pilot / transparent photo rim')
 outer=chamfer(2,2,92,92,6);inner=chamfer(6,6,84,84,3)
 path(g['cold'],outer+' '+inner,'url(#edge)',stroke='#020509',width=.65,fill_rule='evenodd')
 path(g['cold'],chamfer(2.6,2.6,90.8,90.8,5.7)+' '+inner,'url(#forged)',fill_rule='evenodd')
 path(g['cold'],inner,stroke='#674733',width=.50)
 # Channels stop at the corner fasteners rather than outlining the whole shape.
 rails='M11 4H85 M92 11V85 M85 92H11 M4 85V11'
 path(g['cold'],rails,stroke='#050709',width=1.45);lights(g,rails,.44)
 for x,y in [(5,5),(91,5),(5,91),(91,91)]:
  joint(g['cold'],x,y,2.7)
  add(g['core'],'circle',cx=x,cy=y,r=.22,fill='white')
 focus(root)
 return root

def app_badge():
 root,g=setup(128,128,'Correction pilot / Gallery badge')
 steel(g['cold'],circle(64,64,55),8)
 steel(g['cold'],circle(64,64,46),2)
 # Four separate recessed arcs terminate before the copper braces.
 arcs='M72 12A52.6 52.6 0 0 1 116 56 M116 72A52.6 52.6 0 0 1 72 116 M56 116A52.6 52.6 0 0 1 12 72 M12 56A52.6 52.6 0 0 1 56 12'
 path(g['cold'],arcs,stroke='#040609',width=2.0);lights(g,arcs,.78)
 for x,y in [(64,9),(119,64),(64,119),(9,64)]:
  joint(g['cold'],x,y,6)
  add(g['core'],'circle',cx=x,cy=y,r=.42,fill='white')
 gallery.OUT=ROOT/'iterations/26-gallery-workflows'
 photo=gallery.OUT/'upstream/packages/apps/Glimpse/app/src/main/res/drawable/ic_image.xml'
 glyph,_=gallery.source_treatment(photo)
 fine=copy.deepcopy(root.find(SVG+'defs').find(SVG+"pattern[@id='forged']"));fine.set('id','forged-glyph')
 for n in fine.iter():
  for a in ['width','height']:
   if n.get(a):n.set(a,'19')
 root.find(SVG+'defs').append(fine)
 for name in LAYERS:
  target=add(g[name],'g',transform='translate(28 28) scale(.75)')
  for n in glyph.find(SVG+"g[@id='"+name+"']"):
   q=copy.deepcopy(n)
   for node in q.iter():
    for a,v in list(node.attrib.items()):node.set(a,v.replace('url(#forged)','url(#forged-glyph)'))
   target.append(q)
 focus(root)
 return root

def compose(layers,state):
 gains=STATES[state];out=layers['cold'].copy()
 out.putalpha(out.getchannel('A').point(lambda a:round(a*gains[0])))
 for name,gain in zip(LAYERS[1:],gains[1:]):
  if gain:
   im=Image.new('RGBA',out.size,COLORS[name]);im.putalpha(layers[name].getchannel('A').point(lambda a:round(a*gain)));out.alpha_composite(im)
 return out

def main():
 assert not (OUT/'complete-assets.zip').exists(),'Checkpoint is frozen; use a new version.'
 OUT.mkdir(parents=True,exist_ok=True)
 source=ROOT/'iterations/11-forge-symbol-library/source/steel-material.png'
 dest=OUT/'source/steel-material.png';dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
 texture=base64.b64encode(source.read_bytes()).decode()
 samples=[('location','Filled symbol',24,ROOT/'iterations/28-setup-workflows/masters/cg_sw_location.svg',location),
          ('close','Thin control',32,ROOT/'iterations/23-magnification/masters/close.svg',thin_control),
          ('photo_frame','Photo frame',96,ROOT/'iterations/26-gallery-workflows/masters/cg_gl_media_frame.svg',photo_frame),
          ('gallery_badge','App badge',128,ROOT/'iterations/26-gallery-workflows/masters/cg_gl_app_gallery.svg',app_badge)]
 inventory=[];views={};checks=[]
 for key,label,native,old,builder in samples:
  root=builder();master=OUT/'masters'/(key+'.svg');master.parent.mkdir(exist_ok=True);master.write_text(xml(root),encoding='utf8')
  prior=OUT/'source/before'/old.name;prior.parent.mkdir(exist_ok=True)
  prior_doc=E.parse(old).getroot()
  for im in prior_doc.iter(SVG+'image'):
   if 'steel-material.png' in im.get('href',''):im.set('href','data:image/png;base64,'+texture)
  prior.write_text(xml(prior_doc),encoding='utf8')
  # Before masters use a different relative folder; portable SVGs embed the exact texture.
  for im in root.iter(SVG+'image'):im.set('href','data:image/png;base64,'+texture)
  master.write_text(xml(root),encoding='utf8')
  before=E.parse(old).getroot()
  exports=[]
  for scale in [1,2,3]:
   bank={}
   for name in LAYERS:
    single=layer(root,name);p=OUT/'layers'/(key+'.'+name+'.svg');p.parent.mkdir(exist_ok=True)
    if scale==1:p.write_text(xml(single),encoding='utf8')
    im=raster(single,native*scale,texture);p=OUT/'exports'/f'{key}.{name}@{scale}x.png';p.parent.mkdir(exist_ok=True);im.save(p);bank[name]=im
    if name!='cold':assert all(r==g==b for r,g,b,a in im.get_flattened_data() if a),p
    assert im.getchannel('A').getextrema()[0]==0,p
    exports.append({'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'layer':name,'size':list(im.size)})
   for state in STATES:
    p=OUT/'previews/states'/f'{key}.{state}@{scale}x.preview.png';p.parent.mkdir(parents=True,exist_ok=True);compose(bank,state).save(p)
   assert compose(bank,'cold').tobytes()==compose(bank,'pressed_off').tobytes()
   assert compose(bank,'on').tobytes()==compose(bank,'reduced_motion_on').tobytes()
  detail={name:raster(layer(root,name),240,texture) for name in LAYERS}
  before_detail={name:raster(layer(before,name),240,texture) for name in LAYERS}
  views[key]=(compose(before_detail,'cold'),compose(detail,'cold'),compose(detail,'on'))
  def visible_luma(im):
   vals=sorted((.2126*r+.7152*g+.0722*b) for r,g,b,a in im.get_flattened_data() if a>230)
   return round(vals[len(vals)//2],2) if vals else None
  checks.append({'id':key,'beforeColdMedianVisibleLuma':visible_luma(before_detail['cold']),'correctedColdMedianVisibleLuma':visible_luma(detail['cold']),'neutralMasks':True,'coldPressedOffIdentical':True,'reducedMotionStaticOnIdentical':True})
  inventory.append({'id':key,'label':label,'nativeReviewSizePxAtMdpi':native,'sourceBefore':old.relative_to(ROOT).as_posix(),'sourceBeforeSha256':sha(old),'master':master.relative_to(OUT).as_posix(),'masterSha256':sha(master),'exports':exports,'nativeBindingsModified':False})
 # Reference strip uses actual original master layer renders, never a newly generated imitation.
 refs=ROOT/'iterations/11-forge-symbol-library/masters'
 selected=[]
 for name in ['wifi','bluetooth','shield']:
  candidates=[p for p in refs.glob('*.svg') if p.stem=='hero-'+name]
  if candidates:selected.append(candidates[0])
 board=Image.new('RGB',(1320,1570),'#080c11');d=ImageDraw.Draw(board)
 d.text((28,16),'CRAFTAGEDDON / REFERENCE CORRECTION PILOT',font=font(27,True),fill='#eee7d9')
 d.text((28,55),'Four editable samples / dark rough steel, copper braces, separate ember light',font=font(18),fill='#b5bdc6')
 for x,title in [(220,'BEFORE / COLD'),(590,'CORRECTED / COLD'),(960,'CORRECTED / ON')]:d.text((x,102),title,font=font(18,True),fill='#eee7d9')
 for i,(key,label,native,old,builder) in enumerate(samples):
  y=145+i*335
  d.text((25,y+65),label,font=font(19,True),fill='#eee7d9')
  d.text((25,y+95),str(native)+'px at 1x',font=font(16),fill='#b5bdc6')
  for j,im in enumerate(views[key]):board.paste(im,(220+j*370,y),im)
  for j,state in enumerate(['cold','on','focused_off','disabled']):
   p=OUT/'previews/states'/f'{key}.{state}@1x.preview.png';im=Image.open(p);x=220+j*270
   small=im.copy();small.thumbnail((128,80));board.paste(small,(x,y+245),small)
   d.text((x+max(40,small.width+8),y+262),['Cold','On','Focus only','Disabled'][j],font=font(14),fill='#b5bdc6')
 d.text((28,1518),'Offline layer renders. On-state is a lighting demonstration, not a change to native app-icon behavior.',font=font(17),fill='#b5bdc6')
 board.save(OUT/'previews/correction-comparison.png')
 refsheet=Image.new('RGB',(1320,400),'#080c11');rd=ImageDraw.Draw(refsheet)
 rd.text((28,15),'ORIGINAL MASTERS / SCULPTED MATERIAL REFERENCE',font=font(25,True),fill='#eee7d9')
 rd.text((28,52),'Same established cold metal and independent ember layers used as the visual anchor',font=font(17),fill='#b5bdc6')
 for i,p in enumerate(selected):
  doc=E.parse(p).getroot()
  for node in doc.iter(SVG+'image'):
   href=node.get('href','')
   if href and not href.startswith('data:'):node.set('href','data:image/png;base64,'+base64.b64encode((p.parent/href).read_bytes()).decode())
  bank={n:raster(layer(doc,n),200,texture) for n in LAYERS}
  for j,state in enumerate(['cold','on']):
   im=compose(bank,state);refsheet.paste(im,(i*440+j*210,105),im)
   rd.text((i*440+j*210+35,320),p.stem.removeprefix('hero-')+' / '+state,font=font(16),fill='#b5bdc6')
 refsheet.save(OUT/'previews/original-reference-strip.png')
 reference=ROOT/'iterations/11-forge-symbol-library/previews/nine-motifs-off-on.png'
 shutil.copy2(reference,OUT/'source/original-nine-motifs-reference.png')
 write(OUT/'components.json',inventory)
 write(OUT/'runtime-style.json',{'colors':COLORS,'layers':LAYERS,'states':STATES,'activation':'enabled && (on || checked || selected); off press/focus/hover do not activate ember','motion':'Static pilot; no animation. Reduced motion uses same steady on state.','nativeIntegration':'NOT RUN; no owner state or resource binding changed'})
 write(OUT/'verification/evidence/technical-checks.json',{'result':'PASS','samples':4,'coldAndNeutralPngs':84,'neutralPngs':72,'transparentExports':84,'states':7,'scales':[1,2,3],'checks':checks,'originalTextureSha256':sha(source),'originalReferenceSha256':sha(reference),'visualApproval':'PENDING USER REVIEW','deviceRendering':'NOT RUN','independentValidation':'PENDING'})
 print(json.dumps({'out':str(OUT),'masters':4,'layerPngs':84,'comparison':str(OUT/'previews/correction-comparison.png'),'checks':checks}))

if __name__=='__main__':main()
