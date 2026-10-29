"""Refresh existing offline workflow specimens from corrected layer banks."""
from pathlib import Path
import base64, io, json, shutil, xml.etree.ElementTree as E
from PIL import Image
from build_pilot import resvg_py
from build_style_recovery import ROOT,OUT,NS,correct_material,save_json,sha

WORK=ROOT/'build-work/forge30-preview-inputs'
ORIGINALS={
 'magnification':ROOT/'iterations/23-magnification/native-patch/frameworks/base/packages/SystemUI/res',
 'updater':ROOT/'iterations/25-updater-workflows/native-patch/packages/apps/Updater/app/src/main/res',
 'gallery':ROOT/'iterations/27-gallery-contracts/native-patch/packages/apps/Glimpse/app/src/main/res',
 'ayn':ROOT/'iterations/21-native-workflows/native-patch/hardware/ayn/packages/AynParts/res',
}

def prepare(category):
 bank=WORK/category/'res/drawable-mdpi';bank.mkdir(parents=True,exist_ok=True)
 for p in (ORIGINALS[category]/'drawable-mdpi').glob('*.png'):shutil.copy2(p,bank/p.name)
 for p in (OUT/'resources'/category/'drawable-mdpi').glob('*.png'):shutil.copy2(p,bank/p.name)
 folder=OUT/'workflow-review'/category
 for sub in ['previews','masters','source','workflow-previews']:(folder/sub).mkdir(parents=True,exist_ok=True)
 return bank,folder

def adaptive_identity(bank,folder):
 badge=base64.b64encode((bank/'cg_gl_app_gallery_cold.png').read_bytes()).decode()
 root=E.Element(NS+'svg',width='1200',height='480',viewBox='0 0 1200 480')
 def add(parent,name,**attrs):return E.SubElement(parent,NS+name,{k.replace('_','-'):str(v) for k,v in attrs.items()})
 add(root,'rect',width=1200,height=480,fill='#080c11');add(root,'title').text='Corrected Gallery identity / cold adaptive mask review'
 add(root,'text',x=28,y=42,font_family='Segoe UI',font_size=27,fill='#eee7d9').text='GALLERY / CORRECTED COLD ADAPTIVE IDENTITY'
 defs=add(root,'defs')
 for key,cx,label in [('circle',180,'Circle mask'),('round',580,'Rounded mask'),('square',980,'Square mask')]:
  clip=add(defs,'clipPath',id=key)
  if key=='circle':add(clip,'circle',cx=cx,cy=245,r=108)
  else:add(clip,'rect',x=cx-108,y=137,width=216,height=216,rx=48 if key=='round' else 0)
  g=add(root,'g',clip_path='url(#'+key+')');add(g,'rect',x=cx-108,y=137,width=216,height=216,fill='#080b0f')
  add(g,'image',href='data:image/png;base64,'+badge,x=cx-64.8,y=180.2,width=129.6,height=129.6)
  add(root,'text',x=cx-75,y=390,font_family='Segoe UI',font_size=18,fill='#eee7d9').text=label
 add(root,'text',x=28,y=455,font_family='Segoe UI',font_size=17,fill='#b5bdc6').text='Existing 108dp bounds and 20% inset / desktop approximation / native launcher acceptance NOT RUN'
 p=folder/'workflow-previews/adaptive-icon-and-error.svg';p.write_text(E.tostring(root,encoding='unicode'),encoding='utf8')
 p.with_suffix('.preview.png').write_bytes(resvg_py.svg_to_bytes(svg_string=p.read_text(),skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'))

def main():
 assert not (OUT/'complete-assets.zip').exists()
 reports=[]
 # Imports read prior pinned source strings/policies but never execute their builders.
 import render_magnification_fixtures as mag
 bank,folder=prepare('magnification');mag.OUT=folder;mag.NATIVE=bank.parent.parent
 shutil.copy2(ROOT/'iterations/23-magnification/runtime-style.json',folder/'runtime-style.json')
 shutil.copy2(OUT/'source/steel-material.png',folder/'source/steel-material.png')
 old_border=mag.Fixtures.border
 def fixed_border(self,*args,**kwargs):
  doc,record=old_border(self,*args,**kwargs);return correct_material(doc,'border'),record
 mag.Fixtures.border=fixed_border
 mag.Fixtures().run();reports.append({'group':'magnification','fixtures':9,'materialSource':'Corrected PNG bank and corrected vector border palette'})
 print('Refreshed magnification specimens',flush=True)
 import render_updater_workflow_fixtures as upd
 import preview_updater_workflow_art as upd_art
 bank,folder=prepare('updater');upd.OUT=folder;upd.NATIVE=bank;upd.cards.OUT=folder;upd.cards.NATIVE=bank;upd_art.RES=bank
 upd.main();reports.append({'group':'updater','fixtures':25,'materialSource':'Corrected PNG bank; existing error semantics retained'})
 print('Refreshed updater specimens',flush=True)
 import render_gallery_workflow_fixtures as gal
 bank,folder=prepare('gallery');gal.OUT=folder;gal.NATIVE=bank
 gal.main();adaptive_identity(bank,folder);reports.append({'group':'gallery','fixtures':26,'materialSource':'Corrected PNG bank; 25 existing workflows plus adaptive identity sample'})
 print('Refreshed Gallery specimens',flush=True)
 import render_ayn_workflow_fixtures as ayn
 bank,folder=prepare('ayn');ayn.OUT=folder;ayn.PACKAGE=bank.parent.parent
 values=bank.parent/'values';values.mkdir(exist_ok=True);shutil.copy2(ORIGINALS['ayn']/'values/strings.xml',values/'strings.xml')
 shutil.copy2(ROOT/'iterations/21-native-workflows/runtime-style.json',folder/'runtime-style.json')
 ayn.main();reports.append({'group':'ayn','fixtures':11,'materialSource':'Corrected live-position ornament; original gate/RGB data unchanged'})
 print('Refreshed AYN specimens',flush=True)
 save_json(OUT/'verification/evidence/refreshed-workflows.json',{'result':'PASS','groups':reports,'totalFixtures':sum(r['fixtures'] for r in reports),'fixtureVisuals':'English editable offline specimens; pinned prior source labels and original sample values','nativeScreenshots':False,'actualAndroidStateInputAndDeviceAcceptance':'NOT RUN'})

if __name__=='__main__':main()
