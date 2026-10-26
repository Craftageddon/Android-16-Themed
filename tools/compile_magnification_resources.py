"""Compile actual new rendering classes/resources; keep full SystemUI unclaimed."""
from pathlib import Path
import datetime, hashlib, itertools, json, re, shutil, subprocess, xml.etree.ElementTree as ET, zipfile
from audit_os_resource_coverage import ROOT, read_json, write_json

OUT=ROOT/'iterations/23-magnification'
NATIVE=OUT/'native-patch/frameworks/base/packages/SystemUI'
UP=OUT/'upstream/frameworks/base/packages/SystemUI'
SDK=Path(r'C:\Users\spencerm\AppData\Local\Android\Sdk')
ANDROID=SDK/'platforms/android-37.0/android.jar'
AAPT=SDK/'build-tools/37.0.0/aapt2.exe'
JDK=Path(r'C:\Program Files\Android\Android Studio\jbr\bin')
A='{http://schemas.android.com/apk/res/android}'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    work=ROOT/'build-work'/('m23-'+datetime.datetime.now().strftime('%H%M%S-%f'));work.mkdir(parents=True)
    for folder in ['res','gen','classes','tests']:(work/folder).mkdir()
    for p in (NATIVE/'res').rglob('*'):
        if not p.is_file() or p.relative_to(NATIVE/'res').parts[0].startswith('layout'):continue
        dest=work/'res'/p.relative_to(NATIVE/'res');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    java_sources=list((NATIVE/'src/com/android/systemui/accessibility').glob('Forge*.java'))
    native_text='\n'.join(p.read_text(encoding='utf8') for p in java_sources)
    resource_xml='\n'.join(p.read_text(encoding='utf8') for p in (work/'res').rglob('*.xml'))
    dims=set(re.findall(r'R\.dimen\.([A-Za-z0-9_]+)',native_text))|set(re.findall(r'@dimen/([A-Za-z0-9_]+)',resource_xml))
    already_defined={n.get('name') for p in (work/'res/values').glob('*.xml') for n in ET.parse(p).getroot() if n.tag=='dimen'}
    dims-=already_defined
    declarations=read_json(ROOT/'iterations/22-native-contract-review/resource-declarations.json')
    source_values=ET.Element('resources');dimension_receipts=[]
    for name in sorted(dims):
        candidates=[d for d in declarations if d['project']=='frameworks/base' and d['resourceRoot']=='packages/SystemUI/res' and d['type']=='dimen' and d['name']==name and d['qualifier']=='values']
        assert len(candidates)==1,(name,candidates)
        d=candidates[0];ET.SubElement(source_values,'dimen',{'name':name}).text=d['value'];dimension_receipts.append(d)
    ids=set()
    for path in ['res/layout/window_magnification_settings_view.xml','res/layout/window_magnifier_view.xml','res/layout/seekbar_with_icon_buttons.xml','res/layout/magnifier_controllers.xml']:
        root=ET.parse(UP/path).getroot()
        ids.update(v.split('/',1)[1] for n in root.iter() for v in n.attrib.values() if v.startswith('@+id/'))
    for name in sorted(ids):ET.SubElement(source_values,'item',{'type':'id','name':name})
    (work/'res/values/cg_actual_source_symbols.xml').write_bytes(ET.tostring(source_values,encoding='utf-8',xml_declaration=True))
    manifest=work/'AndroidManifest.xml'
    manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.android.systemui.res"><uses-sdk android:minSdkVersion="33" android:targetSdkVersion="37"/><application/></manifest>\n',encoding='utf8')
    def run(args):
        r=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace')
        assert r.returncode==0,'Exit '+str(r.returncode)+'\n'+r.stdout+'\n'+r.stderr
        return r.stdout+r.stderr
    log=run([AAPT,'compile','--dir',NATIVE/'res','-o',work/'all-native-resources.zip'])
    log+=run([AAPT,'compile','--dir',work/'res','-o',work/'render-resources.zip'])
    log+=run([AAPT,'link','-I',ANDROID,'--manifest',manifest,'--java',work/'gen','-o',work/'resource-bank.ap_',work/'render-resources.zip'])
    log+=run([JDK/'javac.exe','--release','8','-encoding','UTF-8','-cp',ANDROID,'-d',work/'classes',*java_sources,*list((work/'gen').rglob('*.java'))])
    log+=run([JDK/'jar.exe','cf',work/'verification-rendering.jar','-C',work/'classes','.'])
    runner=work/'GeometryProbe.java'
    runner.write_text('''import java.nio.file.*;
import java.util.*;
import com.android.systemui.accessibility.ForgeBorderGeometry;
public final class GeometryProbe {
 public static void main(String[] args) throws Exception {
  for(String row:Files.readAllLines(Path.of(args[0]))) {
   String[] values=row.split(","); float[] input=new float[5];
   for(int i=0;i<5;i++) input[i]=Float.parseFloat(values[i]);
   float[] base=ForgeBorderGeometry.centerline(input[0],input[1],input[2],input[3]);
   float[] glow=ForgeBorderGeometry.glowline(base,input[4]);
   System.out.println(Arrays.toString(base)+"|"+Arrays.toString(glow));
  }
 }
}
''',encoding='utf8')
    log+=run([JDK/'javac.exe','-encoding','UTF-8','-cp',work/'classes','-d',work/'tests',runner])
    cases=[]
    for w,h,stroke,density,radius in itertools.product([0,4,8,12,24,64,96,240,360,540,1080],[0,4,8,12,24,64,96,240,360,540,1080],[2,8,12],[1,1.5,2,3],[0,16,18,28,30,40,999]):
        delta=stroke*density/4 if stroke==12 else 0
        cases.append([w*density,h*density,stroke*density,radius*density,delta])
    fixture=work/'geometry-input.csv';fixture.write_text(''.join(','.join(map(str,c))+'\n' for c in cases),encoding='utf8')
    output=run([JDK/'java.exe','-cp',str(work/'tests')+';'+str(work/'classes'),'GeometryProbe',fixture]).splitlines()
    assert len(output)==len(cases)
    close=lambda a,b:abs(a-b)<.001
    for case,line in zip(cases,output):
        width,height,stroke,radius,inward=case;actual_base,actual_glow=[json.loads(x) for x in line.split('|')]
        if width<=stroke or height<=stroke:expected_base=None;expected_glow=None
        else:
            inset=stroke/2;rad=min(radius,(min(width,height)-stroke)/2)
            expected_base=[inset,inset,width-inset,height-inset,max(0,rad)]
            if width-stroke<=2*inward or height-stroke<=2*inward:expected_glow=None
            else:expected_glow=[inset+inward,inset+inward,width-inset-inward,height-inset-inward,max(0,rad-inward)]
        for actual,expected in [(actual_base,expected_base),(actual_glow,expected_glow)]:
            assert (actual is None)==(expected is None),(case,actual,expected)
            if expected is not None:assert all(close(a,b) for a,b in zip(actual,expected)),(case,actual,expected)
    evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
    for name in ['all-native-resources.zip','render-resources.zip','verification-rendering.jar']:shutil.copy2(work/name,evidence/name)
    (evidence/'javac-resource-compile.txt').write_text(log,encoding='utf8')
    write_json(evidence/'source-dimension-harness.json',dimension_receipts)
    with zipfile.ZipFile(work/'all-native-resources.zip') as z:assert z.testzip() is None;count=len(z.namelist())
    report={'date':'2026-10-26','result':'PASS','actualNewJavaClassesCompiled':len(java_sources),
            'allNativeResourceEntriesCompiled':count,'renderBankApi':37,
            'nativeLayouts':'COMPILED ONLY - full SystemUI/Material resource linking and inflation NOT RUN',
            'defaultSourceDimensionDeclarations':len(dimension_receipts),'compileOnlyNativeViewIds':len(ids),
            'realGeometryMethodCases':len(cases),'geometryMethod':'Compiled actual ForgeBorderGeometry evaluated against separately derived pinned GradientDrawable stroke/corner equations, including small bounds and four density scales.',
            'api37JarSha256':hashlib.sha256(ANDROID.read_bytes()).hexdigest(),
            'renderingJarSha256':hashlib.sha256((work/'verification-rendering.jar').read_bytes()).hexdigest(),
            'javaSources':{p.relative_to(NATIVE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in java_sources},
            'sourceOwnersWithHiddenPlatformApis':'NOT COMPILED - full pinned Soong build remains required',
            'verificationJarsInstallable':False,'androidExecution':'NOT RUN','hardwareActions':'NONE'}
    write_json(evidence/'native-subset-build.json',report);print(json.dumps(report))


if __name__=='__main__':main()
