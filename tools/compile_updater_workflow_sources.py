'''Compile the real material library/types and check the current source patch.

Recorded cache compatibility dependencies are not the official pinned Soong
resolution. No invented controller or SPA implementations are compiled.
'''
from pathlib import Path
import copy,datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET,zipfile
from audit_os_resource_coverage import ROOT,read_json,write_json
from check_updater_phase_binding import CACHE,JDK,SDK,HOST

OUT=ROOT/'iterations/25-updater-workflows'
UP=OUT/'upstream/packages/apps/Updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
PREFIX='app/src/main/java/org/lineageos/updater/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    work=ROOT/'build-work'/('updater25-material-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    work.mkdir(parents=True);evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
    log=[]
    def run(args,cwd=None):
        p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,text=True,encoding='utf8',errors='replace')
        log.append(p.stdout+'\n'+p.stderr)
        assert p.returncode==0,'Exit '+str(p.returncode)+'\n'+log[-1]
        return p.stdout
    current=read_json(OUT/'current-native-files.json')
    apply=work/'clean-apply';apply.mkdir()
    (apply/'.gitattributes').write_text('* -text\n',encoding='ascii')
    for r in current:
        assert sha(PATCH/r['path'])==r['sha256']
        if (UP/r['path']).exists():
            dest=apply/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(UP/r['path'],dest)
    run(['git','init','-q'],apply)
    run(['git','apply','--check',OUT/'Updater-forge-workflows.patch'],apply)
    run(['git','apply',OUT/'Updater-forge-workflows.patch'],apply)
    for r in current:assert (apply/r['path']).read_bytes()==(PATCH/r['path']).read_bytes()
    aliases=read_json(OUT/'unchanged-material-reuse.json')['resources']
    for r in aliases:
        assert sha(ROOT/r['source'])==r['sha256']==sha(OUT/r['target'])
        assert r['unchanged']
    # Compile all actual patch resources, including the real legacy layout, without
    # pretending to link its external appcompat/material style dependencies.
    run([SDK/'build-tools/37.0.0/aapt2.exe','compile','--dir',PATCH/'app/src/main/res','-o',work/'all-native-resources.zip'])
    with zipfile.ZipFile(work/'all-native-resources.zip') as z:
        assert z.testzip() is None;all_resource_count=len(z.namelist())
    # The separate linked rendering bank excludes that dependency-bearing layout.
    (work/'res').mkdir()
    for file in (PATCH/'app/src/main/res').rglob('*'):
        if not file.is_file() or file.relative_to(PATCH/'app/src/main/res').parts[0].startswith('layout'):continue
        dest=work/'res'/file.relative_to(PATCH/'app/src/main/res');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
    java=list((PATCH/(PREFIX+'forge')).glob('*.java'))
    phase_source=UP/(PREFIX+'updates/state/UpdateOperationState.kt')
    raw=phase_source.read_bytes();start=raw.index(b'enum class UpdateOperationPhase')
    end=raw.index(b'data class UpdateOperationState',start)
    enum=work/'UpdateOperationPhase.kt'
    enum.write_bytes(b'package org.lineageos.updater.updates.state\nimport androidx.annotation.StringRes\nimport org.lineageos.updater.R\n\n'+raw[start:end])
    kotlin=[PATCH/(PREFIX+'forge/'+name) for name in ['ForgeUpdaterCompose.kt','ForgeUpdaterControls.kt','ForgeIllustrations.kt','ForgeIllustrationClock.kt','ForgeUpdatePresentation.kt']]
    kotlin += [PATCH/(PREFIX+'updates/state/UpdateItemState.kt'),UP/(PREFIX+'updates/action/UpdateAction.kt'),
               UP/(PREFIX+'ui/Lottie.kt'),UP/(PREFIX+'ui/LottieColorUtils.kt'),enum]
    keys=set()
    for p in kotlin:keys.update(re.findall(r'(?<!android\.)\bR\.string\.([a-z_]+)',p.read_text(encoding='utf8')))
    strings={}
    for p in (UP/'app/src/main/res/values').glob('*.xml'):
        for e in ET.fromstring(p.read_bytes()):
            if e.tag=='string':strings[e.attrib['name']]=e
    assert keys<=strings.keys()
    values=ET.Element('resources')
    for name in sorted(keys):values.append(copy.deepcopy(strings[name]))
    (work/'res/values').mkdir(exist_ok=True)
    (work/'res/values/actual_english_source.xml').write_bytes(ET.tostring(values,encoding='utf-8',xml_declaration=True))
    manifest=work/'AndroidManifest.xml'
    manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.lineageos.updater"><uses-sdk android:minSdkVersion="33" android:targetSdkVersion="37"/><application/></manifest>\n',encoding='utf8')
    (work/'gen').mkdir();(work/'classes').mkdir()
    android=SDK/'platforms/android-37.0/android.jar';aapt=SDK/'build-tools/37.0.0/aapt2.exe'
    run([aapt,'compile','--dir',work/'res','-o',work/'resources.zip'])
    with zipfile.ZipFile(work/'resources.zip') as z:
        assert z.testzip() is None;resource_count=len(z.namelist())
    run([aapt,'link','-I',android,'--manifest',manifest,'--java',work/'gen',
         '-o',work/'resource-bank.ap_',work/'resources.zip'])
    pinned=read_json(ROOT/'iterations/21-native-workflows/source/build-dependencies/pinned-aar-receipts.json')
    official=[Path(r['classesJar']) for r in pinned['libraries']]
    for r in pinned['libraries']:assert sha(Path(r['classesJar']))==r['classesSha256']
    java_cp=';'.join(map(str,[android,*official]))
    run([JDK/'bin/javac.exe','--release','8','-encoding','UTF-8','-cp',java_cp,'-d',work/'classes',
         *java,*list((work/'gen').rglob('*.java'))])
    run([JDK/'bin/jar.exe','cf',work/'updater-rendering.jar','-C',work/'classes','.'])
    def jars(group,artifact,version=None):
        p=CACHE/group/artifact
        if version:p=p/version
        return sorted(p.rglob('*.jar')) if p.exists() else []
    runtime=[]
    for g,a,v in [('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.3.21'),
                  ('org.jetbrains.kotlin','kotlin-stdlib','2.3.21'),
                  ('org.jetbrains.kotlin','kotlin-script-runtime',None),
                  ('org.jetbrains.kotlin','kotlin-reflect',None),
                  ('org.jetbrains.intellij.deps','trove4j',None),
                  ('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm',None),
                  ('org.jetbrains','annotations',None)]:runtime+=jars(g,a,v)
    plugin=jars('org.jetbrains.kotlin','kotlin-compose-compiler-plugin-embeddable','2.3.21')
    assert len(plugin)==1
    dependencies=[];receipts=[]
    for group in CACHE.iterdir():
        if not (group.name.startswith('androidx.') or group.name in ['org.jetbrains','org.jetbrains.kotlinx']):continue
        for artifact in group.iterdir():
            versions=[p for p in artifact.iterdir() if p.is_dir()]
            if not versions:continue
            def rank(p):return tuple(int(x) if x.isdigit() else x for x in re.findall(r'\d+|[A-Za-z]+',p.name))
            try:version=max(versions,key=rank)
            except TypeError:version=sorted(versions,key=lambda p:p.name)[-1]
            for p in sorted(version.rglob('*')):
                if p.suffix=='.jar':dependencies.append(p)
                elif p.suffix=='.aar':
                    with zipfile.ZipFile(p) as z:
                        if 'classes.jar' not in z.namelist():continue
                        target=work/(group.name+'__'+artifact.name+'__'+version.name+'.jar')
                        target.write_bytes(z.read('classes.jar'));dependencies.append(target)
                else:continue
                receipts.append({'group':group.name,'artifact':artifact.name,'version':version.name,
                                 'cacheFile':str(p),'sha256':sha(p)})
    stdlib=jars('org.jetbrains.kotlin','kotlin-stdlib','2.3.21')
    lottie=OUT/'source/build-dependencies'
    dependencies += [*stdlib,android,work/'updater-rendering.jar',*official,lottie/'lottie-classes.jar',lottie/'lottie-compose-classes.jar']
    host=work/'HostPhaseCheck.kt';host.write_text(HOST,encoding='utf8');kotlin.append(host)
    args=['-cp',';'.join(map(str,runtime)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
          '-no-stdlib','-no-reflect','-jvm-target','11','-Xplugin='+str(plugin[0]),
          '-classpath',';'.join(map(str,dependencies)),'-d',str(work/'updater-material.jar'),*map(str,kotlin)]
    argfile=work/'compiler-args.txt';argfile.write_text('\n'.join('"'+x.replace('\\','/').replace('"','\\"')+'"' for x in args),encoding='utf8')
    run([JDK/'bin/java.exe','@'+str(argfile)])
    output=run([JDK/'bin/java.exe','-cp',';'.join(map(str,[work/'updater-material.jar',work/'updater-rendering.jar',*stdlib])),
                'craftageddon.hostcheck.HostPhaseCheckKt'])
    assert 'PASS phases=13 stateCombinations=234' in output
    for name in ['resources.zip','all-native-resources.zip','updater-rendering.jar','updater-material.jar']:shutil.copy2(work/name,evidence/name)
    (evidence/'material-compiler.txt').write_text('\n'.join(log),encoding='utf8')
    write_json(evidence/'material-compatibility-classpath.json',receipts)
    report={'result':'PASS','cleanCurrentPatchByteParity':True,'nativeTextFilesInPatch':len(current),
        'unchangedPngResourceConfigurations':len(aliases),'nativeResourceEntriesCompiled':resource_count,'allPatchResourceEntriesCompiled':all_resource_count,
        'actualJavaRenderingClassesCompiled':len(java),'wholeNativeKotlinFilesCompiled':len(kotlin)-2,
        'verbatimNativePhaseEnumCompiled':True,'hostPhaseStateCases':234,'resourceBankApi':37,
        'actualDefaultEnglishResourceKeys':sorted(keys),'generatedOwnerOrModelStubs':0,
        'kotlinCompatibilityCompiler':'2.3.21','pinnedSourceKotlinVersion':'2.2.0',
        'material3CompatibilityVersion':next(r['version'] for r in receipts if r['group']=='androidx.compose.material3' and r['artifact']=='material3-android'),
        'resourceIdsForActualInstalledApp':False,'privateSpaOrUpdaterOwnersCompiled':False,'actualLottieWrappersCompiled':True,'spaModelAdaptersCompiled':False,
        'nativeSources':{p.relative_to(PATCH).as_posix():sha(p) for p in [*java,*[p for p in kotlin if p.is_relative_to(PATCH)]]},
        'jars':{name:sha(evidence/name) for name in ['updater-rendering.jar','updater-material.jar']},
        'newDrawings':8,'fullPinnedSoongBuild':'NOT RUN','androidRenderingInputAccessibility':'NOT RUN',
        'visualFixtureInspection':'NOT RUN','fullUpdaterWorkflowComplete':False,'wholeGoalComplete':False}
    write_json(evidence/'material-subset-build.json',report)
    print(json.dumps({k:report[k] for k in ['result','nativeTextFilesInPatch','unchangedPngResourceConfigurations',
        'nativeResourceEntriesCompiled','actualJavaRenderingClassesCompiled','wholeNativeKotlinFilesCompiled',
        'verbatimNativePhaseEnumCompiled','hostPhaseStateCases','privateSpaOrUpdaterOwnersCompiled',
        'material3CompatibilityVersion','visualFixtureInspection','fullUpdaterWorkflowComplete']}))

if __name__=='__main__':main()
