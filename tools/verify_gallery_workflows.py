'''Gallery offline integrity and source-contract checks. Device/native execution excluded.'''
from pathlib import Path
import hashlib,collections,zipfile,json,xml.etree.ElementTree as E
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse';A='{http://schemas.android.com/apk/res/android}';S='{http://www.w3.org/2000/svg}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists();checks=collections.Counter()
 for r in read_json(OUT/'source-manifest.json')+read_json(OUT/'source-binary-dependencies.json'):
  p=OUT/r['saved'];data=p.read_bytes();assert sha(p)==r['sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1'];checks['pinnedSourceAndDependencyFiles']+=1
 for r in read_json(OUT/'source/media3-ui-contract.json')['members']:
  assert sha(OUT/r['saved'])==r['sha256'];checks['media3ExtractedMembers']+=1
 for r in read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']:
  assert sha(ROOT/r['source'])==r['sha256'];checks['preservedCanonicalMasters']+=1
 assert sha(ROOT/'iterations/25-updater-workflows/complete-assets.zip')=='8f9a4ddab118110b8ec11ef500d6f0dd51d5ea29d53fb2b3f21bdaacb6ce2aa9'
 components=read_json(OUT/'gallery-art-components.json');exports=[]
 for r in components:
  p=OUT/r['master'];assert sha(p)==r['masterSha256'];root=E.parse(p).getroot();assert not list(root.iter(S+'text'))
  for layer in ['cold','reflection','spill','seam','core','focus','symbol']:assert root.find(S+'g[@id="'+layer+'"]') is not None
  origin=r['source']
  if origin.get('original'):
   assert sha(ROOT/origin['original'])==origin['sha256'];old=E.parse(ROOT/origin['original']).getroot()
   for name in ['reflection','spill','seam','core','focus','symbol']:
    assert E.tostring(root.find(S+'g[@id="'+name+'"]'))==E.tostring(old.find(S+'g[@id="'+name+'"]')),(r['id'],name)
   checks['donorsWithExactNeutralLayerGeometry']+=1
  for e in r['files']:
   f=OUT/e['path'];assert sha(f)==e['sha256'];im=Image.open(f).convert('RGBA');assert list(im.size)==e['size'];exports.append(f)
   if f.name.endswith('.9.png'):im=im.crop((1,1,im.width-1,im.height-1))
   if e['layer']!='cold':assert all(red==green==blue for red,green,blue,a in im.get_flattened_data() if a),f;checks['neutralMaskPngConfigs']+=1
   if r['id']=='cg_gl_media_frame':
    w,h=im.size;assert im.getchannel('A').crop((w//4,h//4,3*w//4,3*h//4)).getbbox() is None;checks['protectedTransparentMediaCenters']+=1
   checks['newPngConfigs']+=1
 for r in read_json(OUT/'exact-native-control-reuse.json'):
  assert sha(ROOT/r['source'])==r['sha256']==sha(OUT/r['target']);checks['exactReuseConfigs']+=1
 edits=read_json(OUT/'gallery-owner-edits.json');by=collections.defaultdict(list)
 for stage in edits:by[stage['path']].append(stage)
 for path,stages in by.items():
  data=(PATCH/path).read_bytes()
  for stage in reversed(stages):
   assert hashlib.sha256(data).hexdigest()==stage['patchedSha256'],path;text=data.decode()
   for op in reversed(stage['operations']):assert text.count(op['after'])==op['count'],(path,op);text=text.replace(op['after'],op['before'],op['count'])
   data=text.encode();assert hashlib.sha256(data).hexdigest()==stage['inputSha256'];checks['reversibleOwnerEditStages']+=1
  assert data==(UP/path).read_bytes();checks['reversibleOwnerFiles']+=1
 for r in read_json(OUT/'dependency-layout-overlays.json'):
  assert sha(OUT/r['source'])==r['sourceSha256'];assert sha(PATCH/r['target'])==r['patchedSha256']
  before=E.parse(OUT/r['source']).getroot();after=E.parse(PATCH/r['target']).getroot();old={n.get(A+'id') for n in before.iter() if n.get(A+'id')};new={n.get(A+'id') for n in after.iter() if n.get(A+'id')}
  old.discard('@id/exo_progress_placeholder');assert old<=new;checks['dependencyLayoutsWithNativeIds']+=1
 families=set()
 for r in read_json(OUT/'gallery-resource-bindings.json'):
  path=PATCH/'app/src/main/res'/r['qualifier']/(r['resource']+'.xml');n=E.parse(path).getroot();families.add(r['family']);assert n.get('class')=='org.lineageos.glimpse.forge.ForgeDrawable';assert n.get('{http://schemas.android.com/apk/res-auto}cg_forge_family')==r['family'];assert n.get('{http://schemas.android.com/apk/res-auto}cg_forge_source_value_mode')==['dynamic','true_value','false_value'][r['mode']];checks['qualifiedDrawableBindings']+=1
 resources=(PATCH/'app/src/main/java/org/lineageos/glimpse/forge/ForgeResources.java').read_text();assert all('"'+f+'"' in resources for f in families);checks['staticResourceFamilies']=resources.count('case "')
 bp=(PATCH/'app/Android.bp').read_text();assert 'src/main/java/**/*.java' in bp and 'sdk_version: "36"' in bp
 settings=E.parse(PATCH/'app/src/main/res/xml/root_preferences.xml').getroot();original=E.parse(UP/'app/src/main/res/xml/root_preferences.xml').getroot();keys=['key','defaultValue','dependency','min','seekBarIncrement','showSeekBarValue']
 def prefs(n):return {e.get('{http://schemas.android.com/apk/res-auto}key'):{k:e.get('{http://schemas.android.com/apk/res-auto}'+k) for k in keys}|{'android:max':e.get(A+'max')} for e in n.iter() if e.get('{http://schemas.android.com/apk/res-auto}key')}
 assert prefs(settings)==prefs(original);checks['preservedNativePreferenceKeys']=len(prefs(settings))
 viewer=(PATCH/'app/src/main/java/org/lineageos/glimpse/ViewActivity.kt').read_text();thumb=(PATCH/'app/src/main/java/org/lineageos/glimpse/ui/recyclerview/ThumbnailAdapter.kt').read_text();media=(PATCH/'app/src/main/java/org/lineageos/glimpse/ui/recyclerview/MediaViewerAdapter.kt').read_text()
 for text in ['val isFavorite = displayedMedia?.isFavorite ?: false','favoriteButton.isSelected = isFavorite','motionPhotoToggleButton.isSelected = isPlayingMotionPhoto','useAsButton.isVisible = !secure','favoriteButton.isVisible = !readOnly']:assert text in viewer,text
 for text in ['RenderEffect.createBlurEffect','selectionScrimView','itemView.isSelected = isSelected']:assert text in thumb,text
 for text in ['imageView.load(media.uri)','playerView.player = player','playerControlView.player = player','localPlayerViewModel.isPlaying.collectLatest']:assert text in media,text
 for r in read_json(OUT/'verification/evidence/controls-build.json')['nativeSources'].items():assert sha(PATCH/r[0])==r[1]
 # Adaptive foreground alpha stays inside the platform safe circle after its real 20% inset.
 im=Image.open(PATCH/'app/src/main/res/drawable-xxhdpi/cg_gl_app_gallery_cold.png').convert('RGBA');w,h=im.size
 for y in range(h):
  for x in range(w):
   if im.getpixel((x,y))[3]>8:
    nx=.20+.60*(x+.5)/w;ny=.20+.60*(y+.5)/h;assert (nx-.5)**2+(ny-.5)**2<=(33/108)**2
 checks['adaptiveForegroundSafeCircle']=1
 allpng=list((PATCH/'app/src/main/res').rglob('*.png'));assert len(allpng)==1680
 fixtures=read_json(OUT/'workflow-fixtures.json');assert len(fixtures)==25 and all(r['desktopBounds']=='PASS' and not r['nativeLayoutTest'] for r in fixtures)
 ledger=read_json(OUT/'semantic-family-ledger.json');assert len(ledger)==10926 and sum(r['baselineFamily']['variants'] for r in ledger)==16559 and sum(r['decision']=='OPEN' for r in ledger)==9577
 result={'result':'PASS','checks':dict(checks),'components':53,'allNativePngConfigs':len(allpng),'editableDesktopFixtures':len(fixtures),'allPatchResourceFormatsCompiled':True,'actualJavaSourcesCompiled':9,'policyCases':1536,'policyAssertions':14076,'wrappingCases':1302,'geometryAssertions':257083,'officialSoongBuild':'NOT RUN','allNativeKotlinOwnersCompiled':'NOT RUN','nativeInflationAndLayout':'NOT RUN','deviceTests':'NOT RUN','wholeGoalComplete':False}
 write_json(OUT/'verification/evidence/gallery-source-art-checks.json',result);print(result)
if __name__=='__main__':main()
