'''Rework both original Gallery icon leaves in their actual adaptive composition.'''
from pathlib import Path
import hashlib,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists();res=PATCH/'app/src/main/res';original_bg=E.parse(UP/'app/src/main/res/drawable/ic_launcher_background.xml').getroot();original_fg=E.parse(UP/'app/src/main/res/drawable/ic_launcher_foreground.xml').getroot()
 assert original_bg.tag==original_fg.tag=='vector'
 for attr in ['width','height','viewportWidth','viewportHeight']:assert original_bg.get(A+attr)==original_fg.get(A+attr)
 assert original_bg.get(A+'width')=='108dp' and original_bg.get(A+'viewportWidth')=='108'
 # The foreground carries the approved steel photo badge; background remains the opaque field.
 bg='''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
 <path android:pathData="M0,0h108v108h-108z" android:fillColor="@color/cg_gl_icon_background"/>
</vector>
'''
 fg='''<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
 <item android:width="108dp" android:height="108dp" android:gravity="center">
  <inset android:inset="20%"><bitmap android:src="@drawable/cg_gl_app_gallery_cold" android:gravity="fill" android:filter="true"/></inset>
 </item>
</layer-list>
'''
 (res/'drawable/ic_launcher_background.xml').write_bytes(bg.encode());(res/'drawable/ic_launcher_foreground.xml').write_bytes(fg.encode())
 # Existing foreground helper remains a compatible alias, not an unused alternate rendering.
 (res/'drawable/cg_gl_launcher_foreground.xml').write_bytes(b'<inset xmlns:android="http://schemas.android.com/apk/res/android" android:drawable="@drawable/ic_launcher_foreground" android:inset="0dp"/>\n')
 manifest=E.parse(UP/'app/src/main/AndroidManifest.xml').getroot();assert manifest.find('application').get(A+'icon')=='@mipmap/ic_launcher'
 mip=UP/'app/src/main/res/mipmap-anydpi/ic_launcher.xml';node=E.parse(mip).getroot();assert node.find('background').get(A+'drawable')=='@drawable/ic_launcher_background' and node.find('foreground').get(A+'drawable')=='@drawable/ic_launcher_foreground'
 (res/'mipmap-anydpi/ic_launcher.xml').write_bytes(mip.read_bytes())
 path='app/src/main/res/mipmap-anydpi/ic_launcher.xml';previous=ROOT/'iterations/26-gallery-workflows/native-patch/packages/apps/Glimpse'/path;stages=read_json(OUT/'gallery-owner-edits.json');before=previous.read_text(encoding='utf8');after=mip.read_text(encoding='utf8')
 if not any(r['path']==path and r['patchedSha256']==sha(PATCH/path) for r in stages):
  stages.append({'path':path,'inputSha256':sha(previous),'patchedSha256':sha(PATCH/path),'operations':[{'before':before,'after':after,'count':1}],'reverseByteParity':True});write_json(OUT/'gallery-owner-edits.json',stages)
 record={'result':'AUTHORED','originalSourceRoles':{'background':'Landscape behind the white aperture/photo frame','foreground':'White even-odd photo aperture with radial highlight'},'newCompositeRoles':{'background':'Opaque fixed dark field, original vector and108dp viewport contract retained','foreground':'Approved cold steel photo badge in an explicit108dp item,20percent safe-circle inset'},'sourceComposition':{'manifestIcon':'@mipmap/ic_launcher','background':'@drawable/ic_launcher_background','foreground':'@drawable/ic_launcher_foreground','monochrome':'@drawable/ic_launcher_monochrome'},'reusedMaster':{'path':'masters/cg_gl_app_gallery.svg','sha256':sha(OUT/'masters/cg_gl_app_gallery.svg')},'sourceLeaves':[{'path':'app/src/main/res/drawable/'+name+'.xml','originalSha256':sha(UP/('app/src/main/res/drawable/'+name+'.xml')),'patchedSha256':sha(res/'drawable'/(name+'.xml'))} for name in ['ic_launcher_background','ic_launcher_foreground']],'newRasterOrBakedEmission':False,'originalSourcesPreserved':True,'reviewBasis':'Joint original composition, approved photo identity geometry, fixed intrinsic size and actual retained native adaptive child references; not absence of consumers','nativeInflationAndDeviceAcceptance':'NOT RUN','wholeGoalComplete':False}
 write_json(OUT/'source/legacy-gallery-identity-rework.json',record);print({'originalLeavesReworked':2,'actualAdaptiveOwnersRetained':True,'nativeIntrinsicDp':108,'reusedColdArt':True})
if __name__=='__main__':main()
