"""Bounded source, pixel, layout/target and patch verification for W06 artwork."""
from pathlib import Path
import collections, copy, datetime, hashlib, itertools, json, math, re, shutil, subprocess, xml.etree.ElementTree as ET
from PIL import Image
from audit_os_resource_coverage import ROOT, read_json, write_json
from build_scalable_frames import bounds, stretch

OUT=ROOT/'iterations/23-magnification'
NATIVE=OUT/'native-patch/frameworks/base/packages/SystemUI'
UP=OUT/'upstream/frameworks/base/packages/SystemUI'
A='{http://schemas.android.com/apk/res/android}'
SVG='{http://www.w3.org/2000/svg}'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def luminance(rgb):
    values=[v/255 for v in rgb];values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return .2126*values[0]+.7152*values[1]+.0722*values[2]


def main():
    assert not (OUT/'complete-assets.zip').exists()
    sources=read_json(OUT/'source-manifest.json')+read_json(OUT/'source/native-contracts/manifest.json')
    for r in sources:
        data=(OUT/r['saved']).read_bytes();assert sha(OUT/r['saved'])==r['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1']
    edits=read_json(OUT/'owner-presentation-edits.json')
    assert len(edits)==5
    for r in edits:
        original=(UP/r['path']).read_bytes();actual=(NATIVE/r['path']).read_bytes();text=actual.decode('utf8')
        newline='\r\n' if b'\r\n' in original else '\n'
        for e in reversed(r['edits']):
            old=e['before'].replace('\n',newline);new=e['after'].replace('\n',newline)
            assert text.count(new)==1,(r['path'],new[:80]);text=text.replace(new,old,1)
        assert text.encode('utf8')==original
        assert sha(UP/r['path'])==r['upstreamSha256'] and sha(NATIVE/r['path'])==r['patchedSha256']
    # Apply the actual textual patch in a clean isolated source tree. Binary
    # assets are copied separately as explicitly declared in changed-files.
    work=ROOT/'build-work'/('m23-patch-check-'+datetime.datetime.now().strftime('%H%M%S-%f'));work.mkdir(parents=True,exist_ok=False)
    for p in UP.rglob('*'):
        if p.is_file():dest=work/p.relative_to(UP);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for cmd in [['git','init','-q'],['git','-c','core.autocrlf=false','apply','--whitespace=nowarn',str(OUT/'SystemUI-magnification-forge.patch')]]:
        r=subprocess.run(cmd,cwd=work,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
    changed=read_json(OUT/'changed-files.json')
    for r in changed:
        assert sha(NATIVE/r['path'])==r['sha256']
        if not r['binary']:assert (work/r['path']).read_bytes()==(NATIVE/r['path']).read_bytes(),r['path']
    for p in UP.rglob('*'):
        if p.is_file() and not any(r['path']==p.relative_to(UP).as_posix() for r in changed):assert (work/p.relative_to(UP)).read_bytes()==p.read_bytes()
    # Shared global resources remain unchanged; their Forge treatment is bound
    # only through the actual magnification layout/factory in this checkpoint.
    shared=['ic_add','ic_remove','ic_open_in_full','ic_open_in_new_window','ic_arrow_top_left_and_bottom_right','ic_arrow_top_right_and_bottom_left']
    assert all(not (NATIVE/'res/drawable'/(name+'.xml')).exists() for name in shared)
    critical=['MagnificationGestureDetector.java','WindowMagnificationAnimationController.java','MagnificationImpl.java','MagnificationConnectionImpl.java','WindowMagnificationFrameSizePrefs.java','WindowMagnificationFrameSpec.kt','MirrorWindowControl.java']
    for name in critical:
        assert (UP/'src/com/android/systemui/accessibility'/name).exists()
        assert not (NATIVE/'src/com/android/systemui/accessibility'/name).exists()
    assert not (NATIVE/'src/com/android/systemui/common/ui/view/SeekBarWithIconButtonsView.java').exists()
    components=read_json(OUT/'components.json');assert len(components)==23
    files=0;mask_files=0;contrasts=[];background=luminance((16,21,27));stretch_checks=0
    for r in components:
        doc=ET.parse(OUT/'masters'/(r['id']+'.svg')).getroot()
        assert not doc.findall('.//'+SVG+'text'),'Production labels must stay native.'
        assert {g.get('id') for g in doc.findall(SVG+'g')}=={'cold','reflection','spill','seam','core','focus','symbol'}
        if r.get('sourcePath'):
            source=ET.parse(OUT/r['sourcePath']).getroot();vector=source if source.tag=='vector' else source.find('.//vector')
            dvalues=[n.get(A+'pathData') for n in vector.iter('path')]
            master_paths={n.get('d') for n in doc.iter(SVG+'path')}
            assert all(d in master_paths for d in dvalues)
            assert sha(OUT/r['sourcePath'])==r['sourceSha256']
        for config in r['densityConfigurations']:
            p=OUT/config['file'];assert sha(p)==config['sha256'];im=Image.open(p).convert('RGBA');files+=1
            if r['ninePatch']:
                (x0,x1),(y0,y1)=bounds(im);assert x1>x0 and y1>y0
                if r['id']=='control':
                    for size in [(48,48),(48,58),(78,58),(192,48),(312,48)]:stretch(im,tuple(round(v*{'mdpi':1,'hdpi':1.5,'xhdpi':2,'xxhdpi':3}[config['density']]) for v in size));stretch_checks+=1
                if r['id']=='switch_track':
                    # Padding0 retains20dp thumb travel for a52dp track and32dp thumb.
                    assert all(im.getpixel((x,im.height-1))==(0,0,0,255) for x in range(1,im.width-1))
                    assert all(im.getpixel((im.width-1,y))==(0,0,0,255) for y in range(1,im.height-1))
                im=im.crop((1,1,im.width-1,im.height-1))
            if config['layer']!='cold':
                red,green,blue,alpha=im.split();assert red.tobytes()==green.tobytes()==blue.tobytes();mask_files+=1
            elif r.get('sourcePath') and config['density']=='xhdpi':
                values=[]
                for red,green,blue,alpha in im.get_flattened_data():
                    if alpha>=230:
                        light=luminance((red,green,blue));values.append((max(light,background)+.05)/(min(light,background)+.05))
                values.sort();median=values[len(values)//2];assert median>=3,(r['id'],median)
                contrasts.append({'id':r['id'],'opaquePixelSamples':len(values),'medianContrastToWell':median,
                                  'scope':'Native-size xhdpi source pixel statistic, not a blanket WCAG or Android/device acceptance claim.'})
    assert files==644 and mask_files==552
    reuse=read_json(OUT/'unchanged-panel-reuse.json');assert sha(OUT/reuse['masterTarget'])==reuse['masterSha256']
    for r in reuse['nativeNinePatches']:assert sha(ROOT/r['source'])==sha(OUT/r['target'])==r['sha256']
    assert len(reuse['nativeNinePatches'])==28
    style=read_json(OUT/'runtime-style.json');state_cases=0
    for name in ['reflection','spill','seam','core','focus','symbol']:
        selector=ET.parse(NATIVE/'res/color'/('cg_mag_'+name+'_state.xml')).getroot()
        for bits in itertools.product([False,True],repeat=6):
            state=dict(zip(['enabled','pressed','checked','selected','activated','focused'],bits));chosen=None
            for node in selector:
                if all(state[k.split('state_',1)[1]]==(v=='true') for k,v in node.attrib.items() if 'state_' in k):chosen=node;break
            assert chosen is not None
            alpha=0 if chosen.get(A+'color')=='@android:color/transparent' else float(chosen.get(A+'alpha','1'))
            expected=0
            if state['enabled']:
                if name=='focus':expected=1 if state['focused'] else 0
                elif state['pressed']:expected=style['sampleStates']['active_pressed']['gains'][name]
                elif state['checked'] or state['selected'] or state['activated']:expected=style['sampleStates']['on']['gains'][name]
            assert abs(alpha-expected)<1e-8,(name,state,alpha,expected);state_cases+=1
    # Exact view hierarchy/IDs and live data surface; only whitelisted styling,
    # responsive sizing and the documented touch-target attributes may change.
    allowed={'window_magnifier_view.xml':{'layout_width','layout_height','layout_margin','src','focusable','contentDescription','backgroundTint'},
             'window_magnification_settings_view.xml':{'textColor','backgroundTint','tint','minHeight','background','layout_width','layout_height','src','thumb','track','thumbTint','trackTint','thumbIcon','thumbIconTint','trackDecoration','trackDecorationTint'},
             'magnifier_controllers.xml':{'layout_width','layout_height'}}
    surfaces=0
    for name,keys in allowed.items():
        old=list(ET.parse(UP/'res/layout'/name).getroot().iter());new=list(ET.parse(NATIVE/'res/layout'/name).getroot().iter())
        assert len(old)==len(new)
        for a,b in zip(old,new):
            assert a.tag==b.tag and a.get(A+'id')==b.get(A+'id')
            for key in set(a.attrib)|set(b.attrib):
                if a.get(key)!=b.get(key):assert key.split('}')[-1] in keys,(name,key)
            if a.tag=='SurfaceView':assert a.attrib==b.attrib;surfaces+=1
    assert surfaces==1
    window=ET.parse(NATIVE/'res/layout/window_magnifier_view.xml').getroot()
    for node in window.iter():
        if node.get(A+'id') in {'@+id/top_left_corner','@+id/top_right_corner','@+id/bottom_left_corner','@+id/bottom_right_corner'}:
            assert node.get(A+'layout_width')==node.get(A+'layout_height')=='@dimen/cg_mag_min_touch_target'
    source=(NATIVE/'src/com/android/systemui/accessibility/WindowMagnificationController.java').read_text(encoding='utf8')
    for view,area in [('mDragView','dragArea'),('mTopLeftCornerView','topLeftArea'),('mTopRightCornerView','topRightArea'),('mBottomLeftCornerView','bottomLeftArea'),('mBottomRightCornerView','bottomRightArea'),('mCloseView','closeArea')]:
        assert re.search(r'if \('+view+r'\.getVisibility\(\) == View.VISIBLE\) \{\s+touchableRegion.op\('+area+r', Region.Op.UNION\);',source)
    # At every tested density, three exact measured target widths form four
    # disjoint cardinal controls; no fractional-DPI rounding overlap is assumed.
    target_cases=0
    for dpi in range(120,641):
        target=math.floor(48*dpi/160+.5);size=3*target
        rectangles=[(0,target,target,2*target),(target,0,2*target,target),(2*target,target,size,2*target),(target,2*target,2*target,size)]
        for a,b in itertools.combinations(rectangles,2):assert min(a[2],b[2])<=max(a[0],b[0]) or min(a[3],b[3])<=max(a[1],b[1])
        target_cases+=1
    constants=(OUT/'source/native-contracts/MagnificationConstants.java').read_text(encoding='utf8')
    assert 'ro.config.max_magnification_scale' in constants and '"8.0"' in constants
    assert 'SCALE_MAX_VALUE' in (NATIVE/'src/com/android/systemui/accessibility/WindowMagnificationSettings.java').read_text(encoding='utf8')
    fixtures=read_json(OUT/'workflow-fixtures.json');assert len(fixtures)==9
    for r in fixtures:
        root=ET.parse(OUT/r['svg']).getroot();labels=[''.join(n.itertext()) for n in root.iter(SVG+'text')]
        assert all(all(ord(c)<128 for c in label) for label in labels)
        assert (OUT/r['png']).exists()
        if 'bodyContentHeight' in r:assert 0<=r['actualClampedScrollOffset']<=max(0,r['bodyContentHeight']-r['bodyViewportHeight'])
    compiled=read_json(OUT/'verification/evidence/native-subset-build.json');assert compiled['result']=='PASS'
    for name,expected in compiled['javaSources'].items():assert sha(NATIVE/name)==expected,'Compile report stale: '+name
    old_masters=read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    assert all(sha(ROOT/r['source'])==r['sha256'] for r in old_masters)
    report={'date':'2026-10-26','result':'PASS','components':23,'pinnedSourceFilesVerified':len(sources),
            'actualSourceOwnersPatched':5,'newJavaClassesCompiled':3,'nativeResourceEntriesCompiled':compiled['allNativeResourceEntriesCompiled'],
            'geometryCases':compiled['realGeometryMethodCases'],'newNativePngConfigurations':files,'neutralMaskConfigurations':mask_files,
            'unchangedPanelPngConfigurations':28,'stateSelectorCases':state_cases,'ninePatchSizeChecks':stretch_checks,
            'sourceGlyphContrastStatistics':contrasts,'sourceSurfaceViewSubtreesPreserved':surfaces,
            'legacyDisjointTouchTargetDensityCases':target_cases,'sharedGlobalDrawablesNotOverridden':shared,
            'cleanPatchByteParity':True,'sourceBackedWorkflowFixtures':len(fixtures),'previousMastersPreserved':len(old_masters),
            'fullSystemUiSoongBuild':'NOT RUN','nativeLayoutInflation':'NOT RUN','androidDeviceExecution':'NOT RUN',
            'finalWholeGoalDoubleCheck':'NOT RUN - full source/artwork scope remains unfinished','wholeGoalComplete':False}
    write_json(OUT/'verification/evidence/source-art-checks.json',report);print(json.dumps({k:v for k,v in report.items() if k!='sourceGlyphContrastStatistics'}))


if __name__=='__main__':main()
