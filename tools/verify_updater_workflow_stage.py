'''Fresh checks for this bounded updater workflow source/artwork checkpoint.'''
from pathlib import Path
import datetime,hashlib,json,math,subprocess,xml.etree.ElementTree as E,zipfile
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json
from check_updater_phase_binding import JDK
from build_pilot import font
OUT=ROOT/'iterations/25-updater-workflows';PATCH=OUT/'native-patch/packages/apps/Updater';UP=OUT/'upstream/packages/apps/Updater'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    sources=read_json(OUT/'source-manifest.json')+read_json(OUT/'source/ui-dependency-manifest.json')
    for r in sources:
        p=OUT/r['saved'];data=p.read_bytes();assert sha(p)==r['sha256'],p
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1'],p
    aliases=read_json(OUT/'unchanged-material-reuse.json')['resources']+read_json(OUT/'additional-control-reuse.json')
    for r in aliases:assert sha(OUT/r['target'])==r['sha256']==sha(ROOT/r['source'])
    pngs=list((PATCH/'app/src/main/res').rglob('*.png'));neutral=0;nine=0;sizechecks=0;empty_masks=[]
    for p in pngs:
        im=Image.open(p).convert('RGBA');nine+=p.name.endswith('.9.png')
        if '_cold.' not in p.name:
            assert all(a==b==c for a,b,c,d in im.get_flattened_data()),p;neutral+=1
        if '_cold.' in p.name:assert im.getchannel('A').getextrema()[1]>0,p
        elif im.getchannel('A').getextrema()[1]==0:empty_masks.append(p.relative_to(PATCH).as_posix())
    art=read_json(OUT/'workflow-art-components.json')
    for row in art:
        for r in row['files']:
            p=OUT/r['path'];assert sha(p)==r['sha256'];im=Image.open(p);assert list(im.size)==r['size'];sizechecks+=1
        if isinstance(row['source'],str):master=OUT/row['source']
        else:
            original=row['source']['original']
            if row['id']=='cg_upd_badge':
                master=OUT/'masters/optical_app_updater.svg'
                original_master=ROOT/'iterations/20-semantic-review'/original['master']
            else:
                master=OUT/('masters/optical_'+('pause' if row['id']=='cg_upd_pause' else 'play')+'_32.svg')
                original_master=ROOT/original['source']
            a=E.fromstring(original_master.read_bytes());b=E.fromstring(master.read_bytes())
            for layer in ['reflection','spill','seam','core','focus','symbol']:
                key="{http://www.w3.org/2000/svg}g[@id='"+layer+"']"
                assert E.tostring(a.find(key))==E.tostring(b.find(key)),(master,layer)
        root=E.fromstring(master.read_bytes());assert not list(root.iter('{http://www.w3.org/2000/svg}text'))
    # Undo all recorded actual-owner changes in the exact reverse stage order.
    groups=[{r['path']:r for r in read_json(OUT/f)} for f in ['glyph-owner-edits.json','workflow-owner-edits.json','owner-material-edits.json','owner-phase-edits.json']]
    paths=set().union(*(g.keys() for g in groups))
    for path in paths:
        raw=(PATCH/path).read_bytes();text=raw.decode('utf8')
        for group in groups:
            row=group.get(path)
            if row is None:continue
            assert hashlib.sha256(text.encode('utf8')).hexdigest()==row['patchedSha256'],(path,'stage output')
            for op in reversed(row['operations']):
                assert text.count(op['after'])==op['count'],(path,op['after'][:70])
                text=text.replace(op['after'],op['before'],op['count'])
            assert hashlib.sha256(text.encode('utf8')).hexdigest()==row.get('inputSha256',row.get('upstreamSha256')),(path,'stage input')
        assert text.encode('utf8')==(UP/path).read_bytes(),path
    # Explicitly retain shared notification alpha silhouettes and actual QR payload generator.
    preserved=['app/src/main/res/drawable/ic_notification.xml','app/src/main/res/drawable/ic_pause.xml',
      'app/src/main/res/drawable/ic_system_update.xml','app/src/main/res/drawable/lineage_mark_tight.xml',
      'app/src/main/res/drawable/ic_launcher_background.xml','app/src/main/res/drawable/ic_launcher_foreground.xml',
      'app/src/main/res/values/config.xml',
      'app/src/main/java/org/lineageos/updater/deviceinfo/actions/QrCodeReportIssues.kt',
      'app/src/main/java/org/lineageos/updater/updates/action/UpdateActionHandler.kt',
      'app/src/main/java/org/lineageos/updater/deviceinfo/DeviceInfoUtils.kt']
    for path in preserved:
        assert (UP/path).exists(),path
        assert not (PATCH/path).exists() or (PATCH/path).read_bytes()==(UP/path).read_bytes(),path
    for name in ['sysupdater_error.json','sysupdater_progress.json']:
        path='app/src/main/res/raw/'+name;assert (PATCH/path).read_bytes()==(UP/path).read_bytes()
    compiled=read_json(OUT/'verification/evidence/material-subset-build.json');assert compiled['result']=='PASS'
    for name,digest in compiled['nativeSources'].items():assert sha(PATCH/name)==digest,name
    for name,digest in compiled['jars'].items():assert sha(OUT/'verification/evidence'/name)==digest,name
    # Execute the real compiled pure presentation classes; never invoke Android or updater operations.
    work=ROOT/'build-work'/('updater25-policy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True)
    java=work/'WorkflowProbe.java';java.write_text('''import org.lineageos.updater.forge.*;
public final class WorkflowProbe {
 static int count=0;
 static void check(boolean b){count++;if(!b)throw new AssertionError("case "+count);}
 public static void main(String[] args){
  for(int bits=0;bits<128;bits++){
   boolean[] b=new boolean[7];for(int i=0;i<7;i++)b[i]=(bits&(1<<i))!=0;
   ForgeStatePolicy p=ForgeStatePolicy.resolve(b[0],b[1],b[2],b[3],b[4],b[5],b[6]);
   boolean on=b[0]&&(b[1]||b[2]||b[5]||(b[6]&&b[4]));
   check(p.active==on);check(p.gains[4]==(b[0]&&b[3]?1f:0f));
   if(!on)for(int i:new int[]{0,1,2,3,5})check(p.gains[i]==0);
  }
  for(Boolean value:new Boolean[]{false,true,null})for(boolean rtl:new boolean[]{false,true})
  for(int density=1;density<=4;density++)for(boolean changeable:new boolean[]{false,true}){
   float travel=20*density;
   float expected=value==null?travel/2:(value!=rtl?travel:0);
   check(ForgeToggleGeometry.thumbLeft(value,52*density,32*density,rtl)==expected);
   check(ForgeToggleGeometry.featureOn(value)==Boolean.TRUE.equals(value));
   // changeability intentionally does not alter actual checked state or its location.
  }
  for(int i=-1000;i<=2000;i++){
   float t=i/1000f;float u=Math.max(0,Math.min(1,t));
   float checking=ForgeIllustrationMotion.emission(0,t);
   float error=ForgeIllustrationMotion.emission(1,t);
   check(checking>=.64999f&&checking<=1.00001f);
   check(error>=0&&error<=.80001f);
   check(Math.abs(ForgeIllustrationMotion.rotation(0,t)-360*u)<.0001f);
   check(ForgeIllustrationMotion.emission(2,t)==0);
   check(ForgeIllustrationMotion.rotation(1,t)==0&&ForgeIllustrationMotion.rotation(2,t)==0);
   if(t<=0||t>=1)check(error==0);
  }
  for(float t:new float[]{Float.NaN,Float.POSITIVE_INFINITY,Float.NEGATIVE_INFINITY}){
   check(ForgeIllustrationMotion.emission(0,t)==.65f);
   check(ForgeIllustrationMotion.emission(1,t)==0);
   check(ForgeIllustrationMotion.rotation(0,t)==0);
  }
  check(ForgeIllustrationMotion.emission(1,1f)==0); // reduced-motion/end frame stays cold
  check(ForgeIllustrationMotion.emission(2,1f)==0);
  System.out.println("PASS actualPresentationAssertions="+count+" phaseOrUpdaterOperations=0");
 }
}''',encoding='utf8')
    jar=OUT/'verification/evidence/updater-rendering.jar'
    def run(a):
        r=subprocess.run([str(x) for x in a],capture_output=True,text=True,encoding='utf8',errors='replace');assert r.returncode==0,r.stdout+r.stderr
        return r.stdout
    run([JDK/'bin/javac.exe','-cp',jar,'-d',work,java])
    output=run([JDK/'bin/java.exe','-cp',str(work)+';'+str(jar),'WorkflowProbe']).strip()
    assert output.startswith('PASS ');(OUT/'verification/evidence/pure-presentation-host.txt').write_text(output+'\n',encoding='utf8')
    # Source-owned capability gates/callbacks remain in place, rather than executing device/repository code.
    prefix='app/src/main/java/org/lineageos/updater/'
    pref=(PATCH/(prefix+'preferences/PreferencesScreen.kt')).read_text(encoding='utf8')
    for needle in ['override val changeable = { !batteryState.isAcCharging }',
      'override val checked = { batteryState.isAcCharging || abPerfMode }','override val enabled = { periodicCheckEnabled }',
      'if (isABDevice)','if (showRecoveryUpdate)','repository.setCheckInterval(interval)']:assert needle in pref
    clock=(PATCH/(prefix+'forge/ForgeIllustrationClock.kt')).read_text(encoding='utf8')
    for needle in ['state.isAtLeast(Lifecycle.State.STARTED)','restartOnPlay = false','ignoreSystemAnimatorScale = false','LottieCancellationBehavior.Immediately']:assert needle in clock
    checked=(PATCH/(prefix+'updatescheck/UpdatesCheck.kt')).read_text(encoding='utf8')
    assert 'MIN_CHECKING_DURATION_MILLIS = 2_000L' in checked and 'iterations = 1' in checked
    import_owner=(PATCH/(prefix+'UpdatesActivity.java')).read_text(encoding='utf8');assert '.setCancelable(false)' in import_owner
    models=(PATCH/(prefix+'forge/ForgeSpaAdapters.kt')).read_text(encoding='utf8')
    for needle in ['wrapOnClickWithLog(model.onClick)','wrapOnSwitchWithLog(model.onCheckedChange)',
      'dialogOpened = false; model.onIdSelected(option.id)','model.options.isNotEmpty()',
      'override fun dismiss() { onDismiss() }']:assert needle in models
    fixtures=read_json(OUT/'workflow-screen-fixtures.json')['fixtures']+read_json(OUT/'card-workflow-fixtures.json')['fixtures'];texts=0
    for f in fixtures:
        xml=E.fromstring((OUT/f['svg']).read_bytes());width=float(xml.get('width'));height=float(xml.get('height'))
        assert not f['deviceScreenshot']
        for t in f['texts']:
            length=font(t['size']).getlength(t['text'])
            left=t['x']-length if t['anchor']=='end' else t['x']-length/2 if t['anchor']=='middle' else t['x']
            assert left>=-.1 and left+length<=width+.1 and 0<=t['y']<=height,(f['id'],t)
        for c in f['controls']:
            x,y,w,h=c['bounds'];assert 0<=x and 0<=y and x+w<=width+.1 and y+h<=height+.1,(f['id'],c)
        for t in f['texts']:
            assert all(not c.isalpha() or 'A'<=c<='Z' or 'a'<=c<='z' for c in t['text']),t['text'];texts+=1
    masters=read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    for r in masters:assert sha(ROOT/r['source'])==r['sha256']
    for p in (OUT/'masters').rglob('*.svg'):
        root=E.fromstring(p.read_bytes());assert not list(root.iter('{http://www.w3.org/2000/svg}text'))
        for n in root.iter('{http://www.w3.org/2000/svg}image'):
            href=n.get('href');assert href and (p.parent/href).is_file(),(p,href)
    im=Image.open(PATCH/'app/src/main/res/drawable-mdpi/cg_upd_badge_cold.png').convert('RGBA')
    max_radius=max(math.hypot((x+.5)/im.width-.5,(y+.5)/im.height-.5)*108*.64 for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]>=16)
    assert max_radius<=33,(max_radius,'foreground outside adaptive safe circle')
    prior=ROOT/'iterations/24-updater/complete-assets.zip'
    assert sha(prior)=='39aa46306a04701bf413b5d2bf5dcf6b3f2b2cc45c6ee80b0eb5d98a796b301e'
    report={'result':'PASS','date':'2026-10-27','pinnedOriginalSourceFiles':len(sources),
      'actualOwnerReverseByteParityFiles':len(paths),'nativePngConfigurations':len(pngs),'neutralMaskConfigurations':neutral,'intentionallyEmptyNeutralMaskConfigurations':empty_masks,
      'exactReusedConfigurations':len(aliases),'newDensityExportIdentities':sizechecks,'ninePatchConfigurations':nine,
      'newArtworkMasters':sum(r['newArtwork'] for r in art),'prior472MastersPreserved':len(masters),
      'previous24ArchivePreserved':True,'strictXmlWorkflowFixtures':len(fixtures),'englishTextEntriesChecked':texts,
      'pureCompiledPresentation':output,'phaseStateCases':compiled['hostPhaseStateCases'],
      'allPatchResourceEntriesCompiled':compiled['allPatchResourceEntriesCompiled'],
      'adaptiveColdBadgeMaximumRadiusOf108':max_radius,'safeCircleRadius':33,
      'actualSharedVectorsQrAndActionHandlerPreserved':preserved,'originalLottieTimingJsonPreserved':True,
      'newClockOrUpdaterOperation':False,'sourceModelLoggingAndCallbackOrderReviewed':True,
      'spaPublicModelAdaptersCompiled':False,'fullPinnedUpdaterSoongBuild':'NOT RUN',
      'androidRenderingInputAccessibilityLifecycle':'NOT RUN','offlineBoundsScope':'Desktop font approximations only; viewport scroll/input NOT RUN',
      'fullUpdaterNativeAcceptance':False,'wholeGoalComplete':False}
    write_json(OUT/'verification/evidence/workflow-source-art-checks.json',report)
    print(json.dumps(report))
if __name__=='__main__':main()
