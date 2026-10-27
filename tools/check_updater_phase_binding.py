'''Compile and exercise the phase presentation subset using its real native types.

The native enum declaration is extracted verbatim, not replaced by an invented
owner model. Full controller/mapper/Compose/Soong execution is not claimed.
'''
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/24-updater'
UP=OUT/'upstream/packages/apps/Updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
PREFIX='app/src/main/java/org/lineageos/updater/'
CACHE=Path('C:/Users/spencerm/Documents/Codex/2026-08-31/us/android-motion/.gradle-user/caches/modules-2/files-2.1')
JDK=Path('C:/Program Files/Android/Android Studio/jbr')
SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk')

HOST='''package craftageddon.hostcheck

import org.lineageos.updater.forge.ForgeUpdatePresentation
import org.lineageos.updater.forge.ForgeUpdateTone
import org.lineageos.updater.updates.action.UpdateAction
import org.lineageos.updater.updates.action.UpdateActions
import org.lineageos.updater.updates.action.UpdateActionType
import org.lineageos.updater.updates.state.ProgressState
import org.lineageos.updater.updates.state.UpdateItemState
import org.lineageos.updater.updates.state.UpdateOperationPhase

fun main() {
    val active = setOf("DOWNLOADING", "VERIFYING", "INSTALLING_RECOVERY", "INSTALLING", "FINALIZING")
    val errors = setOf("DOWNLOAD_ERROR", "VERIFICATION_FAILED", "INSTALLATION_FAILED")
    val progressValues = listOf(null, ProgressState.Indeterminate, ProgressState.Determinate(62f, "620 MB of 1 GB", ""))
    var cases = 0
    for (phase in UpdateOperationPhase.entries) {
        val expected = if (phase.name in active) ForgeUpdateTone.ACTIVE else if (phase.name in errors) ForgeUpdateTone.ERROR else ForgeUpdateTone.COLD
        for (progress in progressValues) for (status in listOf("", "Downloading", "Update ready")) for (enabled in listOf(false, true)) {
            val state = UpdateItemState(
                downloadId = "host-fixture", operationPhase = phase, isLocal = false,
                buildDate = "Fixture", buildVersion = "Fixture", status = status,
                fileSize = "1 GB", androidUpdateInfo = "", securityUpdate = "", installNote = 0,
                progress = progress, actions = UpdateActions(UpdateAction(UpdateActionType.START_DOWNLOAD, enabled))
            )
            check(ForgeUpdatePresentation.tone(state.operationPhase) == expected) { "Wrong tone: $phase / $progress / $status / $enabled" }
            if (phase.name == "DOWNLOAD_PAUSED" || phase.name == "INSTALLATION_SUSPENDED") {
                check(ForgeUpdatePresentation.tone(state.operationPhase) == ForgeUpdateTone.COLD)
            }
            cases++
        }
    }
    check(cases == 234)
    println("PASS phases=" + UpdateOperationPhase.entries.size + " stateCombinations=" + cases)
}
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,cwd=None):
    p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,text=True,encoding='utf8',errors='replace')
    assert p.returncode==0,p.stdout+'\n'+p.stderr
    return p.stdout+'\n'+p.stderr

def main():
    assert not (OUT/'complete-assets.zip').exists()
    work=ROOT/'build-work'/('updater24-phase-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    work.mkdir(parents=True)
    evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
    records=read_json(OUT/'source-manifest.json')
    for r in records:
        data=(OUT/r['saved']).read_bytes()
        assert sha(OUT/r['saved'])==r['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1']
    # Clean apply and reverse exact-source checks use a new isolated directory.
    apply_root=work/'clean-apply';apply_root.mkdir()
    edits=read_json(OUT/'owner-phase-edits.json')
    for row in edits:
        dest=apply_root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(UP/row['path'],dest)
        # The phase-only stage is retained separately after subsequent material edits.
        snapshot=OUT/'source/phase-stage'/row['path']
        text=(snapshot if snapshot.exists() else PATCH/row['path']).read_bytes().decode('utf8')
        for edit in reversed(row['operations']):
            assert text.count(edit['after'])==edit['count']
            text=text.replace(edit['after'],edit['before'],edit['count'])
        assert text.encode('utf8')==(UP/row['path']).read_bytes()
    # Match the repository's byte-preserving attributes; host autocrlf otherwise rewrites new files.
    (apply_root/'.gitattributes').write_text('* -text\n',encoding='ascii')
    run(['git','init','-q'],apply_root)
    run(['git','apply','--check',OUT/'Updater-phase-binding.patch'],apply_root)
    run(['git','apply',OUT/'Updater-phase-binding.patch'],apply_root)
    status=read_json(OUT/'phase-binding-status.json')
    for row in status['files']:
        snapshot=OUT/'source/phase-stage'/row['path']
        expected=snapshot if snapshot.exists() else PATCH/row['path']
        assert (apply_root/row['path']).read_bytes()==expected.read_bytes()
        assert sha(expected)==row['sha256']
    # The declaration below is verbatim from the pinned native source. Only its
    # compilation unit imports/package are supplied. No controller/model stand-ins.
    native=UP/(PREFIX+'updates/state/UpdateOperationState.kt')
    raw=native.read_bytes();start=raw.index(b'enum class UpdateOperationPhase')
    end=raw.index(b'data class UpdateOperationState',start)
    fragment=raw[start:end]
    enum_file=work/'UpdateOperationPhase.kt'
    enum_file.write_bytes(b'package org.lineageos.updater.updates.state\nimport androidx.annotation.StringRes\nimport org.lineageos.updater.R\n\n'+fragment)
    sources=[PATCH/(PREFIX+'updates/state/UpdateItemState.kt'),
             UP/(PREFIX+'updates/action/UpdateAction.kt'),
             PATCH/(PREFIX+'forge/ForgeUpdatePresentation.kt'),enum_file]
    keys=set()
    for p in sources:keys.update(re.findall(r'(?<!android\.)\bR\.string\.([a-z_]+)',p.read_text(encoding='utf8')))
    strings={}
    for p in (UP/'app/src/main/res/values').glob('*.xml'):
        for e in ET.fromstring(p.read_bytes()):
            if e.tag=='string':strings[e.attrib['name']]=''.join(e.itertext())
    assert keys<=strings.keys(),keys-strings.keys()
    r=work/'symbols/org/lineageos/updater/R.java';r.parent.mkdir(parents=True)
    r.write_text('package org.lineageos.updater; public final class R { public static final class string {\n'+
                 ''.join('public static final int '+name+'='+str(0x7f010001+i)+';\n' for i,name in enumerate(sorted(keys)))+
                 '} }\n',encoding='utf8')
    symbols=work/'symbol-classes';symbols.mkdir()
    run([JDK/'bin/javac.exe','--release','11','-d',symbols,r])
    def jars(group,artifact,version=None):
        p=CACHE/group/artifact
        if version:p=p/version
        return sorted(p.rglob('*.jar')) if p.exists() else []
    runtime=[]
    for group,artifact,version in [
        ('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.3.21'),
        ('org.jetbrains.kotlin','kotlin-stdlib','2.3.21'),
        ('org.jetbrains.kotlin','kotlin-script-runtime',None),
        ('org.jetbrains.kotlin','kotlin-reflect',None),
        ('org.jetbrains.intellij.deps','trove4j',None),
        ('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm',None),
        ('org.jetbrains','annotations',None)]:runtime+=jars(group,artifact,version)
    assert any(p.name=='kotlin-compiler-embeddable-2.3.21.jar' for p in runtime)
    stdlib=jars('org.jetbrains.kotlin','kotlin-stdlib','2.3.21')
    annotation=jars('androidx.annotation','annotation-jvm','1.9.1')
    assert stdlib and len(annotation)==1
    host=work/'HostPhaseCheck.kt';host.write_text(HOST,encoding='utf8');sources.append(host)
    deps=[SDK/'platforms/android-37.0/android.jar',symbols,*stdlib,*annotation]
    output=work/'updater-phase-host.jar'
    args=['-cp',';'.join(map(str,runtime)),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
          '-no-stdlib','-no-reflect','-jvm-target','11','-classpath',';'.join(map(str,deps)),
          '-d',str(output),*map(str,sources)]
    argfile=work/'compiler-args.txt'
    argfile.write_text('\n'.join('"'+x.replace('\\','/').replace('"','\\"')+'"' for x in args),encoding='utf8')
    compile_log=run([JDK/'bin/java.exe','@'+str(argfile)])
    host_log=run([JDK/'bin/java.exe','-cp',';'.join(map(str,[output,*stdlib])),
                  'craftageddon.hostcheck.HostPhaseCheckKt'])
    assert 'PASS phases=13 stateCombinations=234' in host_log,host_log
    shutil.copy2(output,evidence/output.name)
    (evidence/'phase-compiler.txt').write_text(compile_log,encoding='utf8')
    (evidence/'phase-host-check.txt').write_text(host_log,encoding='utf8')
    (evidence/'HostPhaseCheck.kt').write_text(HOST,encoding='utf8')
    report={'result':'PASS','pinnedSourceFilesVerified':len(records),'cleanPatchApplyByteParity':True,
        'sourceEditReverseByteParity':True,'patchParityScope':'Retained phase-only stage; combined material patch is checked separately','phaseCount':13,'stateCombinations':234,
        'wholeNativeKotlinFilesCompiled':3,'verbatimNativeEnumDeclarationCompiled':True,
        'enumExtraction':{'source':native.relative_to(OUT).as_posix(),'sourceSha256':sha(native),
                          'startByte':start,'endByteExclusive':end,
                          'verbatimFragmentSha256':hashlib.sha256(fragment).hexdigest()},
        'generatedOwnerOrModelStubs':0,'compileOnlyResourceKeys':sorted(keys),
        'compileOnlyResourceIdsForRuntime':False,
        'kotlinCompilerCompatibilityVersion':'2.3.21','pinnedUpstreamKotlinVersion':'2.2.0',
        'classpath':[{'path':str(p),'sha256':sha(p)} for p in [*runtime,*annotation,SDK/'platforms/android-37.0/android.jar']],
        'nativeInputs':[{ 'path':str(p.relative_to(OUT)),'sha256':sha(p)} for p in sources[:3]],
        'jarSha256':sha(output),'actualMapperCompiled':False,'actualComposeOwnerCompiled':False,
        'fullPinnedSoongBuild':'NOT RUN','androidExecution':'NOT RUN',
        'updaterControllerActionOrInstallerOperationsExecuted':False,'presentationTypesExecutedInHostFixture':True,'newArtworkAuthored':False,
        'androidRendererExecuted':False,'wholeGoalComplete':False}
    write_json(evidence/'phase-binding-checks.json',report)
    print(json.dumps({k:report[k] for k in ['result','pinnedSourceFilesVerified','phaseCount','stateCombinations',
        'wholeNativeKotlinFilesCompiled','verbatimNativeEnumDeclarationCompiled','generatedOwnerOrModelStubs',
        'actualMapperCompiled','actualComposeOwnerCompiled','androidRendererExecuted','newArtworkAuthored']}))

if __name__=='__main__':main()
