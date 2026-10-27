"""Record the source-backed Updater presentation contract before authoring art.

This is an inventory/review, not a native test or an artwork completion gate.
"""
from pathlib import Path
import hashlib, json, re, xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json

OUT=ROOT/'iterations/24-updater'
PROJECT=OUT/'upstream/packages/apps/Updater'
SRC=PROJECT/'app/src/main/java/org/lineageos/updater'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    records=read_json(OUT/'source-manifest.json')
    for row in records:
        data=(OUT/row['saved']).read_bytes()
        assert len(data)==row['bytes']
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1']
    operation=(SRC/'updates/state/UpdateOperationState.kt').read_text(encoding='utf8')
    mapper=(SRC/'updates/state/UpdateItemStateMapper.kt').read_text(encoding='utf8')
    item=(SRC/'updates/state/UpdateItemState.kt').read_text(encoding='utf8')
    check=(SRC/'updatescheck/UpdatesCheck.kt').read_text(encoding='utf8')
    phases=re.findall(r'^    ([A-Z][A-Z_]+)(?:\(R\.string\.([a-z_]+)\))?,?$',
                      operation.split('data class UpdateOperationState',1)[0],re.M)
    roles={
        'IDLE':'COLD', 'DOWNLOADING':'ACTIVE', 'DOWNLOAD_PAUSED':'COLD',
        'DOWNLOAD_ERROR':'ERROR', 'VERIFYING':'ACTIVE', 'VERIFICATION_FAILED':'ERROR',
        'VERIFIED':'COLD', 'INSTALLING_RECOVERY':'ACTIVE', 'INSTALLING':'ACTIVE',
        'FINALIZING':'ACTIVE', 'INSTALLATION_SUSPENDED':'COLD',
        'INSTALLATION_FAILED':'ERROR', 'WAITING_FOR_REBOOT':'COLD',
    }
    assert {p for p,_ in phases}==set(roles),phases
    # The current source explicitly includes suspended installation in isInstalling.
    # A new renderer must receive phase, not infer activation from progress/text.
    assert 'UpdateOperationPhase.INSTALLATION_SUSPENDED -> true' in operation
    assert 'state.isDownloadPaused -> ProgressState.Determinate(' in mapper
    assert 'state.isInstalling -> ProgressState.Determinate(' in mapper
    assert 'val phase:' not in item
    assert 'private const val MIN_CHECKING_DURATION_MILLIS = 2_000L' in check
    strings={}
    for p in (PROJECT/'app/src/main/res/values').glob('*.xml'):
        for e in ET.fromstring(p.read_bytes()):
            if e.tag=='string':strings[e.attrib['name']]=''.join(e.itertext())
    phase_rows=[]
    for phase,label in phases:
        assert not label or label in strings,(phase,label)
        phase_rows.append({'phase':phase,'nativeTitleResource':label or None,
                           'nativeDefaultEnglish':strings.get(label),
                           'proposedMaterialRole':roles[phase],
                           'bindingImplemented':False})
    action=(SRC/'updates/action/UpdateAction.kt').read_text(encoding='utf8')
    actions=re.findall(r'^    ([A-Z][A-Z_]+)\((android\.)?R\.string\.([a-z_]+)\)',action,re.M)
    assert len(actions)==14
    action_rows=[]
    for name,android,label in actions:
        assert android or label in strings,label
        action_rows.append({'action':name,'nativeTitleResource':('android:' if android else '')+label,
                            'nativeDefaultEnglish':strings.get(label) if not android else None,
                            'androidFrameworkStringNotInvented':bool(android),
                            'handlerAndEnablementToPreserve':True})
    illustrations=[]
    for p in sorted((PROJECT/'app/src/main/res/raw').glob('*.json')):
        o=json.loads(p.read_bytes())
        illustrations.append({'resource':p.stem,'viewport':[o['w'],o['h']],
                              'fps':o['fr'],'firstFrame':o['ip'],'lastFrameExclusive':o['op'],
                              'durationSeconds':(o['op']-o['ip'])/o['fr'],
                              'layers':len(o['layers']),'embeddedAssets':len(o.get('assets',[])),
                              'newMaterialAndLightTreatmentAuthored':False})
    report={'revision':records[0]['revision'],'pinnedSourceFilesVerified':len(records),
        'scope':'Source contract review only; no artwork, adaptation or runtime acceptance claimed.',
        'phaseBindingsProposed':phase_rows,'actions':action_rows,
        'checkStates':[
            {'state':'Idle','presentation':'No status illustration; original button/timestamp rules'},
            {'state':'Checking','presentation':'Active progress illustration; source minimum display is 2000ms'},
            {'state':'NoInternet','presentation':'Error illustration, one iteration; distinct actual English message'},
            {'state':'Error','presentation':'Error illustration, one iteration; distinct actual English message'}],
        'illustrationSourceContracts':illustrations,
        'requiredFirstImplementation':
            'Pass the actual UpdateOperationPhase through UpdateItemState/mapper before rendering. '
            'Paused/suspended operations can retain determinate progress and must remain cold. '
            'Do not infer active state from localized status text, isInstalling, or non-null progress.',
        'ownerTargets':[
            'UpdatesScaffoldActivity.kt','deviceinfo/UpdaterCard.kt','deviceinfo/DeviceInfoBanner.kt',
            'updates/UpdateItem.kt','updates/button/ActionBar.kt',
            'updatescheck/UpdatesCheck.kt','updates/UpdateZeroStatePreference.kt',
            'updates/action/UpdateActionDialog.kt','preferences/PreferencesScreen.kt',
            'preferences/PreferencesActivity.kt'],
        'preserve':['Controller/repository/installer/notification operations and safety dialogs',
                    'Exact action enablement, click callbacks, real progress/ETA/file/build data',
                    'Narrow/wide 600dp layout branch, window density and native text measurement',
                    'Default English strings, existing localization resources and live text',
                    'Check-state minimum duration and one-shot error versus looping progress roles',
                    'Lineage mark geometry/brand identity and actual build information'],
        'requiredAuthoring':['Cold scalable card/button/dialog/rail treatments with separate neutral masks',
                             'Actual Compose owner and state bindings; no whole global-library swap',
                             'Dedicated progress/error illustration treatments and motion rules',
                             'Source-backed compact/wide/large-text/error/paused/blocked/dialog fixtures'],
        'requiredGates':['Source and patch parity','Actual classes/resources compatibility compilation',
                         'State/mask/layout/English checks and visual passes',
                         'Pinned Soong/SPA/Material dependency build','Android inflation/render/input checks',
                         'Physical Thor comparison and final whole-goal independent check'],
        'artifact24Complete':False,'ledgerDecisionsClosedHere':0,
        'nativeCodeExecuted':False,'deviceModified':False,'wholeGoalComplete':False}
    write_json(OUT/'source-contract-review.json',report)
    (OUT/'WORK-IN-PROGRESS.md').write_text('''# Updater pass in progress

Iteration 23 is saved and published as draft PR #9. This folder starts W04 using
75 byte-verified files from the selected Updater source revision. It is not an
authored artwork checkpoint, has no native build/runtime pass and closes no
family decisions yet. The authoritative ledger remains iteration 23: 9,630 OPEN.

The source review maps all 13 operation phases, 14 action types, four check states
and both actual Lottie input contracts. Paused downloads and suspended installs
can retain progress. The first implementation must carry the domain phase into
the presentation state so those controls stay cold; labels and progress presence
are not reliable activation signals. Ready-to-reboot and verified states are
ready states, not running operations. Errors retain distinct text and symbols.

Next: add this explicit phase binding, author/reuse actual steel treatments with
separate neutral light masks, bind the actual Compose owners and inspect multiple
width/text/state fixtures. Preserve callbacks, enablement, build/progress data,
minimum checking duration, dialogs and installer logic. Source/runtime/native
acceptance and the final whole-goal review remain separate. No hardware operation
or update/install action has executed.
''',encoding='utf8')
    print(json.dumps({'sourceFilesVerified':len(records),'operationPhases':len(phases),
                      'actions':len(actions),'checkStates':4,'illustrations':len(illustrations),
                      'newArtwork':0,'newLedgerDecisions':0,'nativeCodeExecuted':False}))


if __name__=='__main__':main()
