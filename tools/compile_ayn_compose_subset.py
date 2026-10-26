"""Compile actual seven-phase presentation functions with installed cached Compose libraries.

Read-only cache reuse, no generated stand-ins for source state/model classes, no
claim that this compatibility compilation replaces the pinned LineageOS Soong build.
"""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,zipfile
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/21-native-workflows';PACKAGE=OUT/'native-patch/hardware/ayn/packages/AynParts';CACHE=Path('C:/Users/spencerm/Documents/Codex/2026-08-31/us/android-motion/.gradle-user/caches/modules-2/files-2.1');JDK=Path('C:/Program Files/Android/Android Studio/jbr');SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk')

def main():
    work=ROOT/'build-work'/('ayn21-compose-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);receipts=[]
    def jars(group,artifact,version=None):
        root=CACHE/group/artifact
        if version:root=root/version
        return sorted(root.rglob('*.jar')) if root.exists() else []
    runtime=[]
    for group,artifact,version in [('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.3.21'),('org.jetbrains.kotlin','kotlin-stdlib','2.3.21'),('org.jetbrains.kotlin','kotlin-script-runtime',None),('org.jetbrains.kotlin','kotlin-reflect',None),('org.jetbrains.intellij.deps','trove4j',None),('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm',None),('org.jetbrains','annotations',None)]:runtime+=jars(group,artifact,version)
    assert any(x.name=='kotlin-compiler-embeddable-2.3.21.jar' for x in runtime),runtime
    plugin=jars('org.jetbrains.kotlin','kotlin-compose-compiler-plugin-embeddable','2.3.21');assert len(plugin)==1,plugin
    dependencies=[]
    for group in CACHE.iterdir():
        if not (group.name.startswith('androidx.') or group.name in ['org.jetbrains','org.jetbrains.kotlinx']):continue
        for artifact in group.iterdir():
            versions=[p for p in artifact.iterdir() if p.is_dir()]
            if not versions:continue
            # The cache's exact selected version and hash are recorded below. This is
            # a named compatibility classpath, never represented as official Soong resolution.
            def rank(p):return tuple(int(x) if x.isdigit() else x for x in re.findall(r'\d+|[A-Za-z]+',p.name))
            try:version=max(versions,key=rank)
            except TypeError:version=sorted(versions,key=lambda p:p.name)[-1]
            for p in sorted(version.rglob('*')):
                if p.suffix=='.jar':dependencies.append(p)
                elif p.suffix=='.aar':
                    with zipfile.ZipFile(p) as z:
                        if 'classes.jar' not in z.namelist():continue
                        target=work/(group.name+'__'+artifact.name+'__'+version.name+'.jar');target.write_bytes(z.read('classes.jar'));dependencies.append(target)
                else:continue
                receipts.append({'group':group.name,'artifact':artifact.name,'version':version.name,'cacheFile':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    dependencies+=jars('org.jetbrains.kotlin','kotlin-stdlib','2.3.21');dependencies+=[SDK/'platforms/android-37.0/android.jar',OUT/'verification/evidence/ayn-forge-rendering.jar']
    pins=read_json(OUT/'source/build-dependencies/pinned-aar-receipts.json');official=[]
    for library in pins['libraries']:
        p=Path(library['classesJar']);assert hashlib.sha256(p.read_bytes()).hexdigest()==library['classesSha256'];official.append(p)
    dependencies=official+dependencies
    # Normal compile-only resource symbols, generated from the real pinned layout key.
    # This does not stand in for any owner/model behavior, and never supplies runtime IDs.
    resources=read_json(ROOT/'iterations/20-semantic-review/baseline/resource-files.json');layout=next(x for x in resources if x['project']=='frameworks/base' and x['path']=='packages/SettingsLib/AppPreference/res/layout-v33/preference_app.xml');data=(ROOT/'iterations/20-semantic-review/source/objects'/layout['gitBlobSha1'][:2]/layout['gitBlobSha1'][2:]).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==layout['gitBlobSha1']
    symbols=work/'symbols/com/android/settingslib/widget/preference/app/R.java';symbols.parent.mkdir(parents=True);symbols.write_text('package com.android.settingslib.widget.preference.app; public final class R { public static final class layout { public static final int preference_app=0x7fff0001; } }\n');result=subprocess.run([str(JDK/'bin/javac.exe'),'--release','8','-d',str(work/'symbol-classes'),str(symbols)],capture_output=True,text=True);assert result.returncode==0,result.stderr;dependencies.append(work/'symbol-classes')
    source=PACKAGE/'src/org/lineageos/settings/ayn';names=['forge/ForgeCompose.kt','joystick/PhaseIntroScreen.kt','joystick/CalibrationPhaseScreen.kt','joystick/TestScreen.kt','joystick/components/ButtonGrid.kt','joystick/components/StickVisualizer.kt','joystick/CalibrationUiState.kt','joystick/CalibrationData.kt','joystick/JoystickConstants.kt','joystick/JoystickMapping.kt','joystick/JoystickSample.kt','preferences/RGBPreference.kt','utils/LightUtils.kt','utils/NodeUtils.kt'];sources=[source/x for x in names];assert all(x.is_file() for x in sources)
    args=['-cp',';'.join(str(x) for x in runtime),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-no-stdlib','-no-reflect','-jvm-target','11','-Xplugin='+str(plugin[0]),'-classpath',';'.join(str(x) for x in dependencies),'-d',str(work/'ayn-compose.jar'),*map(str,sources)]
    argfile=work/'java-args.txt';argfile.write_text('\n'.join('"'+x.replace('\\','/').replace('"','\\"')+'"' for x in args),encoding='utf8');result=subprocess.run([str(JDK/'bin/java.exe'),'@'+str(argfile)],capture_output=True,text=True,encoding='utf8',errors='replace');log=result.stdout+'\n'+result.stderr;(work/'compiler.txt').write_text(log);(OUT/'verification/evidence/compose-compiler.txt').write_text(log)
    write_json(OUT/'verification/evidence/compose-compatibility-classpath.json',receipts)
    if result.returncode:print(log[-10000:]);raise SystemExit(result.returncode)
    import shutil
    shutil.copy2(work/'ayn-compose.jar',OUT/'verification/evidence/ayn-compose.jar')
    report={'result':'PASS','actualKotlinSourceFilesCompiled':len(sources),'generatedOwnerOrModelStubs':0,'kotlinCompiler':'2.3.21','composeCompiler':'2.3.21','material3CompatibilityVersion':next(x['version'] for x in receipts if x['group']=='androidx.compose.material3' and x['artifact']=='material3-android'),'sourceSha256':{p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'jarSha256':hashlib.sha256((work/'ayn-compose.jar').read_bytes()).hexdigest(),'scope':'Actual Forge Compose functions, seven-phase presentation, patched RGBPreference and unchanged state/mapping/data/LightUtils/NodeUtils source; official pinned Material/AppCompat/Preference AARs and recorded installed Compose compatibility libraries.','compileOnlySettingsLibResourceSymbol':{'resource':layout,'runtimeIdentifierClaimed':False,'notForRuntimeUse':True},'officialDependencyPin':pins['revision'],'officialDependencies':[{'path':x['path'],'gitBlobSha1':x['gitBlobSha1'],'sha256':x['sha256']} for x in pins['libraries']],'fullPinnedAynPartsSoongBuild':'NOT RUN','rgbPreferenceKotlinCompile':'PASS','hardwareUtilitySourceExecuted':False,'verificationJarsForRuntimeInstallation':False,'androidExecution':'NOT RUN'};write_json(OUT/'verification/evidence/compose-subset-build.json',report);print(json.dumps(report))

if __name__=='__main__':main()
