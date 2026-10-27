'''Bind the exact Updater operation phase without changing updater operations.'''
from pathlib import Path
import difflib,hashlib,json
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/24-updater'
UP=OUT/'upstream/packages/apps/Updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
PREFIX='app/src/main/java/org/lineageos/updater/'
NOTICE='// Craftageddon: explicit presentation phase; updater actions and enablement are retained.\n'

HELPER='''/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: Apache-2.0
 */
package org.lineageos.updater.forge

import org.lineageos.updater.updates.state.UpdateOperationPhase

enum class ForgeUpdateTone { COLD, ACTIVE, ERROR }

/** Phase is domain data. Progress, translated status and enabled buttons do not imply activity. */
object ForgeUpdatePresentation {
    fun tone(phase: UpdateOperationPhase): ForgeUpdateTone = when (phase) {
        UpdateOperationPhase.DOWNLOADING,
        UpdateOperationPhase.VERIFYING,
        UpdateOperationPhase.INSTALLING_RECOVERY,
        UpdateOperationPhase.INSTALLING,
        UpdateOperationPhase.FINALIZING -> ForgeUpdateTone.ACTIVE

        UpdateOperationPhase.DOWNLOAD_ERROR,
        UpdateOperationPhase.VERIFICATION_FAILED,
        UpdateOperationPhase.INSTALLATION_FAILED -> ForgeUpdateTone.ERROR

        UpdateOperationPhase.IDLE,
        UpdateOperationPhase.DOWNLOAD_PAUSED,
        UpdateOperationPhase.VERIFIED,
        UpdateOperationPhase.INSTALLATION_SUSPENDED,
        UpdateOperationPhase.WAITING_FOR_REBOOT -> ForgeUpdateTone.COLD
    }
}
'''

def main():
    assert not (OUT/'complete-assets.zip').exists()
    sources={r['path']:r for r in read_json(OUT/'source-manifest.json')}
    files={};edits=[]
    def change(name,operations):
        path=PREFIX+name;original=(UP/path).read_bytes();text=original.decode('utf8')
        assert hashlib.sha256(original).hexdigest()==sources[path]['sha256']
        nl='\r\n' if b'\r\n' in original else '\n'
        performed=[]
        for before,after,count in operations:
            before=before.replace('\n',nl);after=after.replace('\n',nl)
            assert text.count(before)==count,(path,before,text.count(before),count)
            text=text.replace(before,after,count)
            performed.append({'before':before,'after':after,'count':count})
        # Preserve original bytes and record each edit, including the required change notice.
        before='package org.lineageos.updater';after=NOTICE.replace('\n',nl)+before
        assert text.count(before)==1;text=text.replace(before,after,1)
        performed.append({'before':before,'after':after,'count':1})
        payload=text.encode('utf8');dest=PATCH/path;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(payload);files[path]=payload
        # Reverse in reverse order and compare with exact pinned bytes.
        reversed_text=text
        for e in reversed(performed):
            assert reversed_text.count(e['after'])==e['count'],(path,e['after'])
            reversed_text=reversed_text.replace(e['after'],e['before'],e['count'])
        assert reversed_text.encode('utf8')==original
        edits.append({'path':path,'upstreamSha256':hashlib.sha256(original).hexdigest(),
                      'patchedSha256':hashlib.sha256(payload).hexdigest(),
                      'operations':performed,'reverseByteParity':True})
    change('updates/state/UpdateItemState.kt',[
        ('    val downloadId: String,\n','    val downloadId: String,\n    val operationPhase: UpdateOperationPhase,\n',1)])
    change('updates/state/UpdateItemStateMapper.kt',[
        ('            downloadId = update.downloadId,\n',
         '            downloadId = update.downloadId,\n            operationPhase = state.phase,\n',1)])
    change('updates/UpdateItem.kt',[
        ('import org.lineageos.updater.updates.state.UpdateItemState\n',
         'import org.lineageos.updater.updates.state.UpdateItemState\nimport org.lineageos.updater.updates.state.UpdateOperationPhase\n',1),
        ('                status = "",\n','                status = "",\n                operationPhase = UpdateOperationPhase.IDLE,\n',2),
        ('                status = "Downloading",\n','                status = "Downloading",\n                operationPhase = UpdateOperationPhase.DOWNLOADING,\n',1)])
    helper_path=PREFIX+'forge/ForgeUpdatePresentation.kt'
    dest=PATCH/helper_path;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(HELPER.encode('utf8'));files[helper_path]=dest.read_bytes()
    lines=[]
    for path,data in sorted(files.items()):
        old=(UP/path).read_bytes().decode('utf8').splitlines(keepends=True) if (UP/path).exists() else []
        new=data.decode('utf8').splitlines(keepends=True)
        diff=difflib.unified_diff(old,new,fromfile='a/'+path if old else '/dev/null',tofile='b/'+path)
        for line in diff:
            if line.endswith('\n'):lines.append(line)
            else:lines.extend([line+'\n','\\ No newline at end of file\n'])
    (OUT/'Updater-phase-binding.patch').write_bytes(''.join(lines).encode('utf8'))
    write_json(OUT/'owner-phase-edits.json',edits)
    write_json(OUT/'phase-binding-status.json',{
        'actualOwnerFilesChanged':3,'newPurePresentationHelpers':1,
        'sourceConstructorsBound':4,'requiredPhaseHasNoDefault':True,
        'reverseEditByteParity':True,
        'files':[{'path':p,'sha256':hashlib.sha256(b).hexdigest()} for p,b in sorted(files.items())],
        'controllerInstallerRepositoryActionsModified':False,
        'rendererBound':False,'newArtworkAuthored':False,'fullNativeBuild':'NOT RUN',
        'nativeCodeExecuted':False,'wholeGoalComplete':False})
    print(json.dumps({'modifiedNativeFiles':3,'newHelper':1,'actualConstructorsBound':4,
                      'reverseByteParity':True,'rendererBound':False,'nativeExecution':False}))

if __name__=='__main__':main()
