"""Compile the actual new Java/rendering resources. No install and no stubbed Compose claim."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
from audit_os_resource_coverage import ROOT,write_json

OUT=ROOT/'iterations/21-native-workflows';PACKAGE=OUT/'native-patch/hardware/ayn/packages/AynParts';SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk');JDK=Path('C:/Program Files/Android/Android Studio/jbr');ANDROID=SDK/'platforms/android-37.0/android.jar'

def main():
    work=ROOT/'build-work'/('ayn21-compile-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True)
    for name in ['res','gen','classes','tests']:(work/name).mkdir()
    for p in (PACKAGE/'res').glob('drawable-*/cg_*.png'):
        target=work/'res'/p.parent.name/p.name;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target)
    (work/'res/values').mkdir()
    for p in (PACKAGE/'res/values').glob('cg_*.xml'):shutil.copy2(p,work/'res/values'/p.name)
    shutil.copy2(PACKAGE/'res/values/strings.xml',work/'res/values/source_strings.xml')
    shutil.copy2(PACKAGE/'res/values/arrays.xml',work/'res/values/source_arrays.xml')
    manifest=work/'AndroidManifest.xml';manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.lineageos.settings.ayn"><uses-sdk android:minSdkVersion="33" android:targetSdkVersion="37"/><application/></manifest>\n')
    def run(args):
        result=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace');assert result.returncode==0,result.stdout+'\n'+result.stderr;return result.stdout+result.stderr
    aapt=SDK/'build-tools/37.0.0/aapt2.exe';log=run([aapt,'compile','--dir',PACKAGE/'res','-o',work/'all-resource-compile.zip'])
    log+=run([aapt,'compile','--dir',work/'res','-o',work/'render-resources.zip']);log+=run([aapt,'link','-I',ANDROID,'--manifest',manifest,'--java',work/'gen','-o',work/'resource-bank.ap_',work/'render-resources.zip'])
    # Compile-only ID symbols come from the actual patched layout declaration.
    # No replacement layout or widget behavior is created, and these are not runtime IDs.
    layout=E.parse(PACKAGE/'res/layout/dialog_rgb_sliders.xml').getroot();ids=sorted({value.split('/',1)[1] for node in layout.iter() for value in node.attrib.values() if value.startswith('@+id/')});rjava=work/'gen/org/lineageos/settings/ayn/R.java';text=rjava.read_text();extra=' public static final class layout { public static final int dialog_rgb_sliders=0x7fff1000; }\n public static final class id { '+''.join('public static final int '+name+'='+hex(0x7fff1100+i)+';' for i,name in enumerate(ids))+' }\n';end=text.rfind('}');rjava.write_text(text[:end]+extra+text[end:])
    java_sources=list((PACKAGE/'src/org/lineageos/settings/ayn/forge').glob('*.java'))+list((work/'gen').rglob('*.java'));log+=run([JDK/'bin/javac.exe','--release','8','-encoding','UTF-8','-classpath',ANDROID,'-d',work/'classes',*java_sources]);log+=run([JDK/'bin/jar.exe','cf',work/'ayn-forge-rendering.jar','-C',work/'classes','.'])
    policy=PACKAGE/'src/org/lineageos/settings/ayn/forge/ForgeStatePolicy.java';test=OUT/'tests/ForgeStatePolicyTest.java';run([JDK/'bin/javac.exe','--release','8','-d',work/'tests',policy,test]);unit=run([JDK/'bin/java.exe','-cp',work/'tests','org.lineageos.settings.ayn.forge.ForgeStatePolicyTest']);assert 'PASS: 128' in unit
    evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
    for name in ['all-resource-compile.zip','render-resources.zip','ayn-forge-rendering.jar']:shutil.copy2(work/name,evidence/name)
    (evidence/'javac-resource-compile.txt').write_text(log);(evidence/'state-policy-tests.txt').write_text(unit)
    with zipfile.ZipFile(work/'all-resource-compile.zip') as z:assert z.testzip() is None;compiled=len(z.namelist())
    report={'result':'PASS','date':'2026-10-26','actualNewJavaClassesCompiled':4,'compiledNativeResourceEntries':compiled,'renderBankLinkedAgainstApi':37,'nativeRenderingJarSha256':hashlib.sha256((work/'ayn-forge-rendering.jar').read_bytes()).hexdigest(),'nativeStateCombinations':128,'sourceJavaSha256':{p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in java_sources if PACKAGE in p.parents},'api37AndroidJarSha256':hashlib.sha256(ANDROID.read_bytes()).hexdigest(),'kotlinAndFullAynPartsSoongBuild':'NOT RUN; this is the actual Java/resource subset, not a full app or Compose build','androidExecution':'NOT RUN','hardwareActions':'None; original hardware callbacks are not invoked by these tests'};write_json(evidence/'native-subset-build.json',report);print(json.dumps(report))

if __name__=='__main__':main()
