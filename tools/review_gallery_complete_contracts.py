'''Review all Media3 drawable/layout variants and verify the real compiled alias and icon contracts.'''
from pathlib import Path
import collections,hashlib,json,math,re,subprocess,xml.etree.ElementTree as E,zipfile
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font
OUT=ROOT/'iterations/27-gallery-contracts';BASE=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse';RES=PATCH/'app/src/main/res';MEDIA=OUT/'source/media3-ui/original-resources/res';JAVA=OUT/'source/media3-ui/original-java/androidx/media3/ui';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def refs(path,terms):
 p=JAVA/path;lines=p.read_text(encoding='utf8').splitlines();hits=[{'line':i+1,'text':s.strip()} for i,s in enumerate(lines) if any(t in s for t in terms)];assert hits,path
 return {'source':p.relative_to(OUT).as_posix(),'sha256':sha(p),'lines':hits}
def main():
 assert not (OUT/'complete-assets.zip').exists()
 link=read_json(OUT/'verification/evidence/full-resource-link.json');comp=read_json(OUT/'verification/evidence/complete-owner-compilation.json');ns=read_json(OUT/'verification/evidence/real-resource-namespace-checks.json')
 assert link['result']==comp['result']==ns['result']=='PASS'
 assert link['linkedResourcePackageSha256']==comp['resourceLinkSha256']==ns['resourceLinkSha256']
 work=Path(link['work']);pkg=work/'linked-resources.ap_';assert sha(pkg)==link['linkedResourcePackageSha256']
 with zipfile.ZipFile(pkg) as z:assert z.testzip() is None
 expected={}
 for root in [UP/'app/src/main/res',RES]:
  for p in root.rglob('*'):
   if p.is_file():expected[p.relative_to(root).as_posix()]=sha(p)
 effective={p.relative_to(work/'app-res').as_posix():sha(p) for p in (work/'app-res').rglob('*') if p.is_file()};assert expected==effective
 for row in link['libraries']:assert sha(Path(row['aar']))==row['aarSha256']
 for key,row in comp['sourceFiles'].items():assert sha(ROOT/row['source'])==row['sha256']
 table=(work/'resource-table.txt').read_text(encoding='utf8');entries={}
 for match in re.finditer(r'^    resource (0x[0-9a-f]+) ([^\s]+)\n(.*?)(?=^    resource |^  type |\Z)',table,re.M|re.S):entries[match[2]]={'id':match[1],'body':match[3]}
 aliases=read_json(OUT/'source/shared-media3-consumer-review.json');aliaschecks=[]
 for name,target in aliases['currentPlayerAliasesRetargeted'].items():
  body=entries['drawable/'+name]['body'];assert '() @drawable/'+target+'\n' in body,(name,body);aliaschecks.append({'alias':name,'target':target,'compiledResourceId':entries['drawable/'+name]['id'],'role':'styled_player'})
 for row in aliases['nativeConsumers']:
  name=row['alias'];target=row['sourceAlias'];body=entries['drawable/'+name]['body'];assert '() @drawable/'+target+'\n' in body,(name,body);aliaschecks.append({'alias':name,'target':target,'compiledResourceId':entries['drawable/'+name]['id'],'role':'native_shared_consumer'})
 aapt=Path('C:/Users/spencerm/AppData/Local/Android/Sdk/build-tools/37.0.0/aapt2.exe')
 xmls={}
 for rel in ['res/drawable/ic_launcher_background.xml','res/drawable/ic_launcher_foreground.xml','res/mipmap-anydpi-v21/ic_launcher.xml','res/layout/cg_gl_player_view.xml']:
  p=subprocess.run([str(aapt),'dump','xmltree',str(pkg),'--file',rel],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr
  dest=OUT/'verification/evidence'/('compiled-'+Path(rel).stem+'.txt');dest.write_text(p.stdout,encoding='utf8');xmls[rel]={'dump':dest.relative_to(OUT).as_posix(),'dumpSha256':sha(dest)}
 fg=E.parse(RES/'drawable/ic_launcher_foreground.xml').getroot();item=fg.find('item');assert item.get(A+'width')==item.get(A+'height')=='108dp';assert item.find('inset').get(A+'inset')=='20%';assert item.find('inset/bitmap').get(A+'gravity')=='fill'
 for r in read_json(OUT/'source/legacy-gallery-identity-rework.json')['sourceLeaves']:assert sha(UP/r['path'])==r['originalSha256'] and sha(PATCH/r['path'])==r['patchedSha256']
 adaptive=E.parse(RES/'mipmap-anydpi/ic_launcher.xml').getroot();assert adaptive.find('foreground').get(A+'drawable')=='@drawable/ic_launcher_foreground'
 im=Image.open(RES/'drawable-xxhdpi/cg_gl_app_gallery_cold.png').convert('RGBA');w,h=im.size;alphaPixels=0
 for y in range(h):
  for x in range(w):
   if im.getpixel((x,y))[3]>8:
    alphaPixels+=1;nx=.2+.6*(x+.5)/w;ny=.2+.6*(y+.5)/h;assert (nx-.5)**2+(ny-.5)**2<=(33/108)**2
 # Every physical drawable/layout variant, including PNG-only families, remains visible in this catalog.
 binding={r['priorSharedLeaf']:r for r in read_json(OUT/'gallery-resource-bindings.json') if r.get('library')}
 overlays={Path(r['source']).stem:r for r in read_json(OUT/'dependency-layout-overlays.json')}
 values=E.parse(MEDIA/'values/values.xml').getroot();aliasmap={n.get('name'):n.text for n in values if n.tag=='drawable'}
 grouped=collections.defaultdict(list)
 for p in sorted(MEDIA.rglob('*')):
  if p.is_file() and p.parent.name.startswith(('drawable','layout')):grouped[('layout' if p.parent.name.startswith('layout') else 'drawable',p.stem)].append(p)
 catalog=[];preview=[];counts=collections.Counter()
 for (kind,name),files in sorted(grouped.items()):
  variants=[]
  for p in files:
   v={'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'qualifier':p.parent.name,'format':p.suffix}
   if p.suffix=='.png':
    img=Image.open(p);img.load();v.update(dimensions=list(img.size),mode=img.mode,decodedRgbaSha256=hashlib.sha256(img.convert('RGBA').tobytes()).hexdigest());counts['decodedPngVariants']+=1
   elif p.suffix=='.xml':
    node=E.parse(p).getroot();v.update(xmlRoot=node.tag,nativeViewport=[node.get(A+'viewportWidth'),node.get(A+'viewportHeight')],pathCount=len(list(node.iter('path'))));counts['parsedXmlVariants']+=1
   else:raise AssertionError(p)
   variants.append(v)
  consumers=[{'alias':n,'target':v} for n,v in aliasmap.items() if v=='@drawable/'+name]
  proof=[];reason='';disposition=''
  if kind=='drawable' and name in binding:
   disposition='STYLED_ALIAS_PRESENTATION_AUTHORED_SHARED_SOURCE_RETAINED';reason='Source glyph geometry has its scoped steel/mask bridge for the styled player aliases only. Every original vector and density bitmap remains intact for other alias owners. This is not visual completion of legacy or notification consumers.';proof=[{'scopedBinding':binding[name]}]
  elif kind=='drawable' and name in ['exo_icon_fullscreen_enter','exo_icon_fullscreen_exit','exo_icon_next','exo_icon_pause','exo_icon_play','exo_icon_previous','exo_icon_stop','exo_icon_circular_play','exo_icon_vr']:
   disposition='SHARED_OWNER_PRESENTATION_PENDING';reason='Actual legacy styles/controller or notification builder bind this source glyph. Preserve current native role, dimensions, tint behavior and source images while the shared-owner presentation needs its own scoped adaptation. No global untouched consumer is declared visually complete.';proof=[refs('PlayerNotificationManager.java',['smallIconResourceId = R.drawable.exo_notification_small_icon','playActionIconResourceId = R.drawable.exo_notification_play','stopActionIconResourceId = R.drawable.exo_notification_stop']),refs('LegacyPlayerControlView.java',['int controllerLayoutId = R.layout.exo_legacy_player_control_view','showVrButton = false'])]
  elif name=='exo_edit_mode_logo':
   disposition='PRESERVE_IDE_PREVIEW_CONTRACT';reason='The positive isInEditMode constructor branch creates an IDE preview ImageView and returns before normal player inflation; configureEditModeLogo assigns this media-library identity and preview background. Preserve the recognizable third-party development logo, not an app control or textual UI.';proof=[refs('PlayerView.java',['if (isInEditMode())','configureEditModeLogo(context','R.drawable.exo_edit_mode_logo'])]
  elif name=='exo_ic_default_album_image':
   disposition='ARTWORK_OWNER_REVIEW_PENDING';reason='Actual512dp source vector is an opaque gray album field with a musical-note silhouette. It is distinct from video imagery and Gallery photo identity. No positive application display/default-art owner is established yet; retain source and leave artwork disposition open, without inferring approval from absence of references.';proof=[refs('PlayerView.java',['int defaultArtworkId = 0','R.styleable.PlayerView_default_artwork','defaultArtwork = defaultArtworkId'])]
  elif name=='exo_rounded_rectangle':
   disposition='SCOPED_ERROR_PANEL_AUTHORED_SHARED_SOURCE_RETAINED';reason='Native16dp rounded error shape remains globally intact. Gallery selects a source-identical player subtree whose only visual substitution is a cold steel error panel. Actual error provider/custom message and native visibility still own content; error is not a toggled-on feature.';proof=[refs('PlayerView.java',['private void updateErrorMessage()','errorMessageView.setText(customErrorMessage)','errorMessageProvider.getErrorMessage','errorMessageView.setVisibility(View.GONE)']),read_json(OUT/'source/scoped-player-error-layout.json')]
  elif kind=='layout' and name in overlays:
   disposition='NATIVE_LAYOUT_PRESENTATION_AUTHORED';reason='Pinned native layout is adapted through the recorded scoped layout/row treatment, preserving action and data IDs. Code compilation and actual resource linking pass; native XML inflation is not run.';proof=[overlays[name]]
  elif name=='exo_player_view':
   disposition='SCOPED_MEDIA_LAYOUT_AUTHORED';reason='The10 original media widgets/IDs, native surface insertion, shutter, artwork, image, subtitle, buffering and overlay hierarchy remain unchanged. Gallery selects cg_gl_player_view through the real player_layout_id; only the error background reference differs.';proof=[read_json(OUT/'source/scoped-player-error-layout.json')]
  elif name=='exo_legacy_player_control_view':
   disposition='SHARED_OWNER_PRESENTATION_PENDING';reason='Positive LegacyPlayerControlView default layout contains native action controls plus position/duration and a timebar placeholder. Retain IDs, styles, action visibility and time binding; its legacy presentation needs a separate adaptation.';proof=[refs('LegacyPlayerControlView.java',['int controllerLayoutId = R.layout.exo_legacy_player_control_view'])]
  elif name=='exo_list_divider':
   disposition='TRACK_DIALOG_PRESENTATION_PENDING';reason='Actual one-pixel native listDivider themed View is inserted at two TrackSelectionView call sites. It is a separator, not a missing illustration; native track dialog styling and effective theme still need acceptance.';proof=[refs('TrackSelectionView.java',['inflate(R.layout.exo_list_divider'])]
  elif name=='exo_track_selection_dialog':
   disposition='TRACK_DIALOG_PRESENTATION_PENDING';reason='Actual ScrollView wraps TrackSelectionView; two builder branches inflate it and retain track options, scrolling and selection callbacks. Preserve the container/schema while its dialog presentation remains a separate pending owner.';proof=[refs('TrackSelectionDialogBuilder.java',['inflate(R.layout.exo_track_selection_dialog'])]
  elif name in ['exo_player_control_ffwd_button','exo_player_control_rewind_button']:
   disposition='PRESERVE_NATIVE_AMOUNT_LAYOUT_CONTRACT';reason='Native API23+ merge/Button layout intentionally sets singleLine=false to avoid its documented Material layout bug. The styled amount-button housing is retargeted by scoped aliases; actual time amount text, matching ID, style and native formatting remain unchanged.';proof=[refs('PlayerControlView.java',['exo_ffwd_with_amount','exo_rew_with_amount','setText('])]
  else:raise AssertionError((kind,name))
  catalog.append({'kind':kind,'resource':name,'variants':variants,'consumerAliases':consumers,'disposition':disposition,'rationale':reason,'sourceContentAndConsumers':proof,'nativeAcceptance':'NOT RUN','globalVisualCompletion':False})
  png=next((p for p in files if p.parent.name=='drawable-mdpi-v4'),next((p for p in files if p.suffix=='.png'),None))
  if png:preview.append((name,png,disposition))
 assert len(catalog)==45 and sum(len(r['variants']) for r in catalog)==232
 out=OUT/'previews';out.mkdir(exist_ok=True);sheet=Image.new('RGB',(1440,math.ceil(len(preview)/5)*180+100),'#12181f');d=ImageDraw.Draw(sheet);d.text((24,18),'MEDIA3 / ORIGINAL SOURCE CONTENT REVIEW',font=font(24),fill='#eee7d9');d.text((24,56),'All34 drawable families with density PNGs / unthemed source samples, not finished artwork',font=font(16),fill='#bac3ce')
 for i,(name,p,state) in enumerate(preview):
  x=24+(i%5)*286;y=110+(i//5)*180;img=Image.open(p).convert('RGBA');img.thumbnail((110,110));img=img.resize((max(1,img.width*2),max(1,img.height*2)),Image.Resampling.NEAREST) if max(img.size)<50 else img;sheet.paste(img,(x,y),img);d.text((x,y+114),name,font=font(12),fill='#eee7d9');d.text((x,y+136),'Scoped art' if name in binding else 'Native / see review',font=font(12),fill='#bac3ce')
 sheet.save(out/'media3-original-source-review.preview.png')
 report={'result':'PASS','physicalDrawableAndLayoutVariants':232,'families':45,'counts':dict(counts),'dispositions':dict(collections.Counter(r['disposition'] for r in catalog)),'resources':catalog,'baselineCorpusExtended':False,'sharedOwnerPresentationStillPending':True,'defaultAlbumArtworkOwnerStillPending':True,'remainingAdditionalScope':['Material/AppCompat/platform-widget visual families and actual effective themes','Native XML inflation, text layout, accessibility and Thor input/display acceptance'],'wholeGoalComplete':False}
 write_json(OUT/'discovered-media3-visual-scope.json',report)
 write_json(OUT/'verification/evidence/compiled-gallery-contracts.json',{'result':'PASS','actualAarsLinked':link['libraryAarsLinked'],'actualEffectiveAppResourceInputsVerified':len(expected),'compiledAliasesVerified':len(aliaschecks),'aliasChecks':aliaschecks,'compiledXmlDumps':xmls,'sourceOwnerJavaCompiled':comp['actualJavaSources'],'sourceOwnerKotlinCompiled':comp['actualKotlinSources'],'allCurrentOwnerSourceHashesVerified':True,'explicitAdaptiveIntrinsicDp':108,'adaptiveSafeCircleAlphaPixels':alphaPixels,'originalSourceVariantsReviewed':232,'pngVariantsDecoded':counts['decodedPngVariants'],'officialSoongBuild':'NOT RUN','nativeXmlInflation':'NOT RUN','wholeGoalComplete':False})
 print({'compiledAliasesVerified':len(aliaschecks),'allSourceVariants':232,'nativePngVariants':counts['decodedPngVariants'],'catalogFamilies':45,'wholeGoalComplete':False})
if __name__=='__main__':main()
