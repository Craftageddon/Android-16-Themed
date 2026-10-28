'''Scope player error decoration to Gallery while preserving the native media subtree.'''
import hashlib,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';PATCH=OUT/'native-patch/packages/apps/Glimpse';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 original=OUT/'source/media3-ui/original-resources/res/layout/exo_player_view.xml';target=PATCH/'app/src/main/res/layout/cg_gl_player_view.xml';data=original.read_bytes();before='android:background="@drawable/exo_rounded_rectangle"';after='android:background="@drawable/cg_gl_player_error_panel"';text=data.decode('utf8');assert text.count(before)==1;target.write_bytes(text.replace(before,after).encode('utf8'))
 bridge=PATCH/'app/src/main/res/drawable/cg_gl_player_error_panel.xml';bridge.write_bytes(b'<drawable xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" class="org.lineageos.glimpse.forge.ForgeDrawable" app:cg_forge_family="cg_gl_panel" app:cg_forge_source_value_mode="false_value"/>\n')
 path='app/src/main/res/layout/media_view.xml';owner=PATCH/path;data=owner.read_bytes();text=data.decode('utf8');old='        app:controller_layout_id="@layout/cg_gl_player_controls"';new='        app:player_layout_id="@layout/cg_gl_player_view"\n'+old
 stages=read_json(OUT/'gallery-owner-edits.json')
 if new not in text:
  assert text.count(old)==1;owner.write_bytes(text.replace(old,new).encode('utf8'));stages.append({'path':path,'inputSha256':hashlib.sha256(data).hexdigest(),'patchedSha256':sha(owner),'operations':[{'before':old,'after':new,'count':1}],'reverseByteParity':True});write_json(OUT/'gallery-owner-edits.json',stages)
 assert target.read_bytes().replace(after.encode(),before.encode())==original.read_bytes()
 oldroot=E.parse(original).getroot();newroot=E.parse(target).getroot();ids=lambda n:[(x.tag,x.get(A+'id')) for x in n.iter() if x.get(A+'id')];assert ids(oldroot)==ids(newroot)
 write_json(OUT/'source/scoped-player-error-layout.json',{'result':'PASS','source':str(original.relative_to(OUT)),'sourceSha256':sha(original),'target':'app/src/main/res/layout/cg_gl_player_view.xml','patchedSha256':sha(target),'actualOwner':path,'actualOwnerSha256':sha(owner),'nativeIdAndWidgetParity':ids(newroot),'onlySubtreeChange':{'before':before,'after':after},'errorBackground':{'family':'cg_gl_panel','sourceValueMode':'false_value','featureOn':False,'runtimeMessageSource':'PlayerView.updateErrorMessage keeps nullable custom/error provider messages and original visibility conditions'},'globalLibraryErrorShapeUnchanged':True,'protectedNativeContracts':['surface insertion','image and artwork view scale and IDs','subtitles','buffering visibility','shutter','ads and overlay containers','controller placeholder','error text dimensions and padding'],'nativeInflation':'NOT RUN','wholeGoalComplete':False})
 print({'scopedPlayerLayout':True,'nativeMediaWidgetIdsRetained':len(ids(newroot)),'errorPanelCold':True,'globalDependencyChanged':False})
if __name__=='__main__':main()
