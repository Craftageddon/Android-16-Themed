"""Check actual patch application, source callback preservation and emitted resources."""
from pathlib import Path
import copy,datetime,hashlib,io,json,math,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
from PIL import Image,ImageChops
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import resvg_py
from forge_library import embed,xml,compose_layers,lighting_descriptor
from build_scalable_frames import bounds as nine_patch_bounds

OUT=ROOT/'iterations/21-native-workflows';PREFIX='hardware/ayn/packages/AynParts';SOURCE=PREFIX+'/src/org/lineageos/settings/ayn';AN='{http://schemas.android.com/apk/res/android}';AP='{http://schemas.android.com/apk/res-auto}'

def block(text,needle):
    start=text.index(needle);opening=text.index('{',start);level=0;quoted=False;escaped=False
    for i in range(opening,len(text)):
        ch=text[i]
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
            continue
        if ch=='"':quoted=True;continue
        if ch=='{':level+=1
        elif ch=='}':
            level-=1
            if level==0:return text[opening:i+1]
    raise AssertionError('Unbalanced source block '+needle)

def main():
    upstream=OUT/'upstream';patch=OUT/'native-patch';receipts=read_json(OUT/'upstream-receipts.json');changes=read_json(OUT/'changed-files.json');changed={x['path'] for x in changes};preserved=[]
    for row in receipts:
        p=upstream/row['baseline'];data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1']
        if row['baseline'] not in changed:assert (patch/row['baseline']).read_bytes()==data;preserved.append(row['baseline'])
    critical=['CalibrationViewModel.kt','CalibrationEngine.kt','CalibrationPersistence.kt','CalibrationScreen.kt','CalibrationUiState.kt','JoystickMapping.kt','JoystickSampler.kt','JoystickSample.kt','CalibrationData.kt','JoystickConstants.kt']
    for name in critical:assert SOURCE+'/joystick/'+name in preserved,name
    old=(upstream/SOURCE/'preferences/RGBPreference.kt').read_text();new=(patch/SOURCE/'preferences/RGBPreference.kt').read_text()
    for marker in ['fun loadPersistedState()', 'val getKernelColor =', 'val liveApply =', 'val updateColor =', 'fun Slider.bind(', 'val resetToInitial =']:
        assert block(old,marker)==block(new,marker),marker
    for marker in ['.setPositiveButton(','.setNegativeButton(','.setOnCancelListener']:
        # Resource labels may become native English keys; all original callback bodies stay exact.
        assert block(old,marker)==block(new,marker),marker
    old_layout=E.parse(upstream/PREFIX/'res/layout/dialog_rgb_sliders.xml').getroot();new_layout=E.parse(patch/PREFIX/'res/layout/dialog_rgb_sliders.xml').getroot();assert new_layout.tag=='ScrollView';old_sliders=list(old_layout);new_sliders=new_layout.findall('.//com.google.android.material.slider.Slider');assert len(old_sliders)==len(new_sliders)==4
    for a,b in zip(old_sliders,new_sliders):
        for attr in [AN+'id',AN+'valueFrom',AN+'valueTo',AN+'stepSize',AP+'trackColorActive',AP+'thumbColor',AP+'trackHeight',AP+'thumbHeight',AP+'labelBehavior']:assert a.get(attr)==b.get(attr),(attr,a.attrib,b.attrib)
        assert b.get(AN+'minHeight')=='48dp' and b.get(AP+'thumbWidth')=='36dp';assert b.get(AN+'contentDescription').startswith('@string/cg_ayn_channel_')
    old_stick=(upstream/SOURCE/'joystick/components/StickVisualizer.kt').read_text();new_stick=(patch/SOURCE/'joystick/components/StickVisualizer.kt').read_text()
    geometry_lines=['val cx = size.width / 2f','val cy = size.height / 2f','val radius = size.minDimension / 2f - 4.dp.toPx()','val dotRadius = 8.dp.toPx()','val maxTravel = radius - dotRadius','val rawDist = kotlin.math.sqrt(x * x + y * y).coerceAtLeast(Float.MIN_VALUE)','val scale = if (rawDist > 1f) 1f / rawDist else 1f','val dotX = cx + x * scale * maxTravel','val dotY = cy + y * scale * maxTravel']
    for line in geometry_lines:assert line in old_stick and line in new_stick
    assert 'contentDescription = labelText' in new_stick and 'stateDescription = position' in new_stick;assert 'setInputStrength(inputStrength)' in new_stick
    test=(patch/SOURCE/'joystick/TestScreen.kt').read_text();assert 'Modifier.weight(1f).verticalScroll' in test and 'Alignment.BottomEnd' not in test
    assert 'state.rawLeftX' in test and 'state.mappedLeftX' in test and 'state.rawRightX' in test and 'state.mappedRightX' in test
    phase=(patch/SOURCE/'joystick/CalibrationPhaseScreen.kt').read_text();assert 'enabled = state.readyToAdvance' in phase and 'if (sample != null)' in phase
    for name in ['Center','RangeLeft','RangeRight','DeadzoneLeft','DeadzoneRight']:assert 'CalibrationPhase.'+name in phase
    work=ROOT/'build-work'/('ayn21-apply-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));shutil.copytree(upstream,work)
    def run(args):
        r=subprocess.run([str(x) for x in args],cwd=work,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;return r.stdout+r.stderr
    run(['git','init','-q']);run(['git','-c','core.autocrlf=false','apply','--check',OUT/'AynParts-forge-source.patch']);run(['git','-c','core.autocrlf=false','apply',OUT/'AynParts-forge-source.patch'])
    for row in changes:
        data=(patch/row['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
        if Path(row['path']).suffix!='.png':assert (work/row['path']).read_bytes()==data,row['path']
    for row in read_json(OUT/'unchanged-resource-reuse.json'):assert hashlib.sha256((OUT/row['target']).read_bytes()).hexdigest()==row['sha256'];assert (OUT/row['target']).read_bytes()==(ROOT/row['source']).read_bytes()
    adapted=read_json(OUT/'adapted-native-frames.json');assert len(adapted)==84
    for row in adapted:
        assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sourceSha256'];assert hashlib.sha256((OUT/row['target']).read_bytes()).hexdigest()==row['targetSha256'];image=Image.open(OUT/row['target']).convert('RGBA');assert image.size==(row['contentSize'][0]+2,row['contentSize'][1]+2);(x0,x1),(y0,y1)=nine_patch_bounds(image);assert [x0,x1,y0,y1]==row['stretch']
        if '_cold.' not in row['target']:
            r,g,b,_=image.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox()
        if '/drawable-mdpi/' in row['target']:
            minimum=(image.width-2-(x1-x0),image.height-2-(y1-y0));family='button' if 'cg_rf_button_' in row['target'] else 'field' if 'cg_rf_field_' in row['target'] else 'panel';target={'button':(96,56),'field':(112,56),'panel':(112,88)}[family];assert minimum[0]<=target[0] and minimum[1]<=target[1],(family,minimum,target)
    style=read_json(OUT/'runtime-style.json');exports=states=0;texture=__import__('base64').b64encode((OUT/'source/steel-material.png').read_bytes()).decode()
    for row in read_json(OUT/'components.json'):
        doc=E.parse(OUT/'masters'/(row['id']+'.svg')).getroot();assert not doc.findall('.//{http://www.w3.org/2000/svg}text');w,h=row['size'];doc.set('viewBox',f'-2 -2 {w+4} {h+4}');doc.set('width',str(w+4));doc.set('height',str(h+4))
        im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(doc,texture)),width=(w+4)*3,skip_system_fonts=True))).convert('RGBA');bounds=im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox();assert bounds is None or (bounds[0]>=6 and bounds[1]>=6 and bounds[2]<=(w+2)*3 and bounds[3]<=(h+2)*3),(row['id'],bounds)
        cached={}
        for layer in row['layers']:
            for scale in [1,2,3]:
                image=Image.open(OUT/'exports'/f"{row['id']}.{layer}@{scale}x.png").convert('RGBA');assert image.size==(w*scale,h*scale);assert image.getchannel('A').getextrema()[0]==0;exports+=1
                if layer!='cold':
                    r,g,b,_=image.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox()
                if scale==2:cached[layer]=image
        for state,descriptor in style['sampleStates'].items():
            actual=Image.open(OUT/'exports'/f"{row['id']}.{state}.preview.png").convert('RGBA');assert actual.tobytes()==compose_layers(cached,lighting_descriptor(descriptor,False)).tobytes();states+=1
    compile=read_json(OUT/'verification/evidence/native-subset-build.json');compose=read_json(OUT/'verification/evidence/compose-subset-build.json');assert compile['result']==compose['result']=='PASS';assert compile['nativeStateCombinations']==128 and compose['generatedOwnerOrModelStubs']==0
    for report in [compile,compose]:
        for name,sha in report.get('sourceSha256',report.get('sourceJavaSha256',{})).items():assert hashlib.sha256((patch/PREFIX/name).read_bytes()).hexdigest()==sha
    with zipfile.ZipFile(OUT/'verification/evidence/ayn-compose.jar') as z:
        names=z.namelist()
        for klass in ['CalibrationPhaseScreenKt.class','TestScreenKt.class','PhaseIntroScreenKt.class','ForgeComposeKt.class','StickVisualizerKt.class','CalibrationUiState.class']:assert any(x.endswith('/'+klass) for x in names),klass
        for phase in ['Intro','Center','RangeLeft','RangeRight','DeadzoneLeft','DeadzoneRight','Test']:assert any(x.endswith('/CalibrationPhase$'+phase+'.class') for x in names),phase
        assert any(x.endswith('/preferences/RGBPreference.class') for x in names)
    pins=read_json(OUT/'source/build-dependencies/pinned-aar-receipts.json');material=next(x for x in pins['libraries'] if '/com/google/android/material/material/' in x['path']);java=Path('C:/Program Files/Android/Android Studio/jbr/bin/javap.exe');dump=subprocess.check_output([str(java),'-classpath',material['classesJar'],'-p','-c','com.google.android.material.slider.BaseSlider'],text=True,encoding='utf8');start=dump.index('initializeCustomThumbDrawable(android.graphics.drawable.Drawable)');end=dump.index('\n  ',dump.index('areturn',start)+7);clone_code=dump[start:end];assert 'getConstantState' in clone_code and 'newDrawable' in clone_code;assert 'setPressed:(Z)V' in dump;(OUT/'verification/evidence/pinned-slider-cloning-bytecode.txt').write_text(clone_code+'\n')
    thumb=(patch/SOURCE/'forge/ForgeRgbThumbDrawable.java').read_text();assert 'getConstantState() { return constantState; }' in thumb and 'housing.setState(slider.getDrawableState())' in thumb and 'WeakReference<View>' in thumb;assert 'setGestureActive' not in thumb
    def luminance(color):
        c=[int(color[i:i+2],16)/255 for i in [1,3,5]];c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c];return sum(x*y for x,y in zip(c,[.2126,.7152,.0722]))
    ratio=(luminance('#627482')+.05)/(luminance('#10151b')+.05);assert ratio>=3;assert 'Color(0xFF627482)' in new_stick
    fixtures=read_json(OUT/'workflow-visual-fixtures.json');assert {x['sourceMapping']['phase'] for x in fixtures if x['sourceMapping']['group']=='W-01'}=={'Intro','Center','RangeLeft','RangeRight','DeadzoneLeft','DeadzoneRight','Test'}
    for fixture in fixtures:
        assert not fixture['deviceScreenshot']
        assert all(all(not char.isalpha() or char.isascii() for char in text['text']) for text in fixture['text'])
        if fixture['sourceMapping']['group']=='W-02':assert all(v%step==0 for v,step in zip(fixture['sourceMapping']['channels'],fixture['sourceMapping']['sourceSteps']))
    assert hashlib.sha256((ROOT/'iterations/20-semantic-review/complete-assets.zip').read_bytes()).hexdigest()=='734f7b39c1a546fe770e64622a9652bcff431cb85867a200532155d8f4e0ce92'
    report={'result':'PASS','date':'2026-10-26','pinnedUpstreamRecords':len(receipts),'unchangedSourceFiles':len(preserved),'unchangedCriticalCalibrationOwnerFiles':len(critical),'sourceRgbCallbackBlocksPreserved':9,'preservedRgbSliderNumericContracts':4,'nativeStickGeometryExpressionsPreserved':len(geometry_lines),'cleanGitApplyAndByteParity':True,'newProductionLayerExports':exports,'stateRecompositions':states,'newControlMasters':3,'compactFrameTreatments':3,'adaptedNativeNinePatchResources':84,'newJavaClassesCompiled':4,'actualKotlinFilesCompiled':compose['actualKotlinSourceFilesCompiled'],'standInSourceModels':0,'compileOnlyResourceSymbolsAreRuntimeIds':False,'pinnedMaterialCloneContractChecked':True,'nativeStateCases':128,'crosshairContrastOnWell':round(ratio,3),'sourceWorkflowFixtures':len(fixtures),'calibrationPhases':7,'previousSignedCheckpointUnchanged':True,'fullPinnedSoongAndAndroidExecution':'NOT RUN','wholeSemanticReviewComplete':False};write_json(OUT/'verification/evidence/patch-art-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
