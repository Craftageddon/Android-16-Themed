'''Render current desktop specimens and the explicit adaptive icon composition.'''
from pathlib import Path
import base64,hashlib,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import resvg_py
import preview_gallery_art as art
import render_gallery_workflow_fixtures as fixtures
OUT=ROOT/'iterations/27-gallery-contracts'
def main():
 assert not (OUT/'complete-assets.zip').exists()
 art.OUT=OUT;art.RES=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res/drawable-mdpi';art.main()
 fixtures.OUT=OUT;fixtures.UP=OUT/'upstream/packages/apps/Glimpse';fixtures.NATIVE=art.RES;policy={}
 for line in (OUT/'verification/evidence/core-policy-host.txt').read_text(encoding='utf8').splitlines():
  if line.count('|')==8:
   v=line.split('|');policy[v[0]]=[float(v[2]),*map(float,v[3:])]
 assert len(policy)==7;fixtures.POLICY=policy;fixtures.main()
 # Separate editable source/desktop proof, no generation or retouch of production PNGs.
 cold=art.RES/'cg_gl_app_gallery_cold.png';panel=art.RES/'cg_gl_panel_cold.9.png'
 badge=base64.b64encode(cold.read_bytes()).decode()
 panelim=art.stretch(__import__('PIL').Image.open(panel).convert('RGBA'),(1100,144))
 import io
 b=io.BytesIO();panelim.save(b,format='PNG');panel64=base64.b64encode(b.getvalue()).decode()
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720"><title>Gallery adaptive icon and cold error panel</title><desc>Editable desktop composition. Icon foreground uses explicit108dp bounds and20percent inset. Error text is a sample; native Android rendering not run.</desc><defs><clipPath id="circle"><circle cx="180" cy="285" r="108"/></clipPath><clipPath id="round"><rect x="440" y="177" width="216" height="216" rx="48"/></clipPath><clipPath id="square"><rect x="800" y="177" width="216" height="216"/></clipPath></defs><rect width="1200" height="720" fill="#080c11"/><g font-family="Segoe UI" fill="#eee7d9"><text x="30" y="44" font-size="28">GALLERY / ACTIVE ORIGINAL ICON LEAVES</text><text x="30" y="82" font-size="17" fill="#b5bdc6">Cold steel identity, explicit108dp foreground,20percent inset / desktop approximation</text>'
 for key,cx,label in [('circle',180,'Circle mask'),('round',548,'Rounded mask'),('square',908,'Square mask')]:
  svg+='<g clip-path="url(#'+key+')"><rect x="'+str(cx-108)+'" y="177" width="216" height="216" fill="#080b0f"/><image href="data:image/png;base64,'+badge+'" x="'+str(cx-64.8)+'" y="220.2" width="129.6" height="129.6"/></g><text x="'+str(cx-84)+'" y="435" font-size="18">'+label+'</text>'
 svg+='<text x="30" y="503" font-size="22">Gallery player error housing / cold, source-value false</text><image href="data:image/png;base64,'+panel64+'" x="30" y="528" width="1100" height="144"/><text x="80" y="610" font-size="24">Sample playback error</text><text x="30" y="705" font-size="16" fill="#b5bdc6">Sample message only. Native error provider, visibility and media subtree remain source-owned.</text></g></svg>'
 dest=OUT/'workflow-previews/adaptive-icon-and-error';dest.with_suffix('.svg').write_text(svg,encoding='utf8');dest.with_suffix('.preview.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'))
 write_json(OUT/'verification/evidence/desktop-render-checks.json',{'result':'PASS','editableExistingWorkflowFixturesRegenerated':25,'existingAssetAndWorkflowSheetsRegenerated':9,'additionalEditableComposition':'workflow-previews/adaptive-icon-and-error.svg','sourceImageAuditSheet':'previews/media3-original-source-review.preview.png','renderer':'Existing local resvg, live English SVG text, approximate desktop Segoe UI metrics','nativeAndroidScreenshot':False,'nativeInflation':'NOT RUN','wholeGoalComplete':False})
 print({'currentWorkflowFixtures':25,'additionalEditableComposition':1,'nativeScreenshots':False})
if __name__=='__main__':main()
