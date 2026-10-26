"""Reopen checkpoint bytes independently; never equate parsing with completion."""
from pathlib import Path,PurePosixPath
import collections,gzip,hashlib,json,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review'

def main():
    files=read_json(OUT/'baseline/resource-files.json');families=read_json(OUT/'baseline/resource-family-dispositions.json');ledger=read_json(OUT/'semantic-family-ledger.json');objects=read_json(OUT/'source-objects.json');aux=read_json(OUT/'auxiliary-source-files.json');all_objects={x['gitBlobSha1']:x for x in objects+aux};verified={};xmls=0
    for sha,row in all_objects.items():
        data=(OUT/row['object']).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha;assert hashlib.sha256(data).hexdigest()==row['sha256'];assert len(data)==row['bytes'];verified[sha]=row
    assert len(files)==16559 and len(families)==len(ledger)==10926 and len(objects)==15915
    for f in files:assert f['gitBlobSha1'] in verified
    assert collections.Counter((x['project'],x['path'],x['gitBlobSha1']) for x in files)==collections.Counter((r['baselineFamily']['project'],v['path'],v['gitBlobSha1']) for r in ledger for v in r['evidence'])
    descriptors=read_json(OUT/'content-evidence.json');assert {x['gitBlobSha1'] for x in descriptors}==set(verified)
    for d in descriptors:
        if d['contentClass']!='XML':continue
        doc=E.fromstring((OUT/d['object']).read_bytes());assert doc.tag==d['xmlRoot'];assert len(list(doc.iter()))==d['nodeCount'];xmls+=1
        if doc.tag=='resources':assert len([x for x in doc if x.get('name')])==len(d['namedValues'])
    assert read_json(OUT/'unresolved-path-parameters.json')==[]
    reuse=read_json(OUT/'reuse-decisions.json');assert len(reuse)==214;assert sum(x['wasOneOf210TentativeCandidates'] for x in reuse)==210
    for r in reuse:
        assert not r['nativeDropInApproved']
        for asset in r['chosenAssets']:
            p=OUT/asset['checkpointCopy'] if 'checkpointCopy' in asset else ROOT/asset['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256']
    corrections={x['familyId']:x for x in reuse};assert corrections['F-8e7edb4ff3401224']['chosenAssets'][0]['assetId'].startswith('20/review-corrections/pin_entry');assert corrections['F-d65ee2b037005745']['chosenAssets'][0]['assetId']=='17/pin__compact';assert corrections['F-9ba0f665f6319903']['chosenAssets'][0]['assetId']=='11/close__compact'
    context=read_json(OUT/'source/context-manifest.json')
    for r in context:
        data=(OUT/r['checkpointCopy']).read_bytes();assert hashlib.sha256(data).hexdigest()==r['sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1']
    previous=read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    for r in previous:assert hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest()==r['sha256']
    assert len(previous)==472
    cold=json.loads((OUT/'state-domain-decisions.json').read_text());assert not cold['sensorsOffMode']['emissionLockedOff'];assert cold['sensorsOffMode']['featureActive']=='All-sensor privacy mode enabled'
    for r in read_json(OUT/'components.json'):
        if r['semanticId']=='sensors_disabled':assert not r['emissionLockedOff']
    for p in OUT.rglob('*.gz'):
        plain=p.with_suffix('')
        if plain.exists():assert gzip.decompress(p.read_bytes())==plain.read_bytes()
    layers=sum(read_json(p)['productionExports'] for p in [OUT/'verification/evidence/gap-art-checks.json',OUT/'review-corrections/verification/evidence/gap-art-checks.json'])+read_json(OUT/'verification/evidence/app-binding-checks.json')['layerExports'];assert layers==980
    art_count=sum(len(read_json(p)) for p in [OUT/'components.json',OUT/'app-components.json',OUT/'review-corrections/components.json']);assert art_count==70
    progress=read_json(OUT/'semantic-review-progress.json');assert not progress['semanticReviewFinished'] and not progress['fullGoalComplete'];assert progress['openSemanticDecisions']==10554
    report={'result':'PASS','date':'2026-10-26','checkpointScope':'Bounded full-source acquisition and content index, resolved210 tentative artwork reuse decisions,16 named gap treatments plus8 discovered corrections,20 app/component artwork bindings. Whole-family semantic completion and seven workflow adaptations are still open.','components':70,'sourceFileVariants':len(files),'sourceFamilies':len(families),'verifiedPrimaryObjects':len(objects),'verifiedObjectsIncludingAuxiliary':len(verified),'verifiedBytesIncludingAuxiliary':sum(x['bytes'] for x in verified.values()),'independentlyReparsedXmlObjects':xmls,'preservedContextFiles':len(context),'reuseDecisionRows':len(reuse),'originalTentativeCandidatesResolved':210,'unchangedHistoricalMasters':472,'unchangedPortableDonorMasters':112,'productionLayerExports':layers,'openFamilyDecisions':10554,'finalWholeGoalDoubleCheck':'NOT RUN - unfinished scope remains','v1Scope':'Actual pinned bytes and contents, reviewed comparison cards, explicit source-domain corrections, live English labels and cold/separate-mask artwork; full requirement register remains open.','v2Method':'Independent reread of Git blob/SHA256 object proofs, XML/value declaration counts, file/family conservation, exact chosen donor hashes, context/master hashes, PIN-versus-pushpin correction, privacy-active state, gzip parity, mask/native-resource and state-recomposition evidence.','targetV3':'NOT RUN - native/device acceptance and independent final goal review remain pending'}
    write_json(OUT/'verification/evidence/technical.json',report);print(json.dumps(report))

if __name__=='__main__':main()
