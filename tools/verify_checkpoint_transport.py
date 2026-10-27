"""Verify a frozen signed source checkpoint and make a hash-checked local delivery."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,shutil,zipfile
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,utils
from cryptography.exceptions import InvalidSignature

ROOT=Path(__file__).resolve().parents[1];PIN='efed639940a40e073b8c30f4f515eb7859d65fd03b660e179006798fc9c6ac9c'

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restored',type=Path,required=True);p.add_argument('--delivery',required=True);a=p.parse_args();root=a.root.resolve();archive=root/'complete-assets.zip';digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert digest==(root/'complete-assets.zip.sha256').read_text().split()[0];public=serialization.load_pem_public_key((root/'signing-public-key.pem').read_bytes());assert hashlib.sha256(public.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest()==PIN;signature=(root/'complete-assets.zip.sig').read_bytes();pss=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32);public.verify(signature,bytes.fromhex(digest),pss,utils.Prehashed(hashes.SHA256()));tampered=bytearray(bytes.fromhex(digest));tampered[0]^=1
    try:public.verify(signature,bytes(tampered),pss,utils.Prehashed(hashes.SHA256()));raise AssertionError('Tamper accepted')
    except InvalidSignature:pass
    markers=[('-----BEGIN '+x+'-----').encode() for x in ['PRIVATE KEY','ENCRYPTED PRIVATE KEY','RSA PRIVATE KEY','EC PRIVATE KEY']]
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            path=PurePosixPath(name);assert not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name;assert not {'local-secrets','build-work','__pycache__'}&set(path.parts);data=z.read(name);assert data==(root/name).read_bytes();assert not any(x in data for x in markers)
        lines=z.read('SHA256SUMS.txt').decode('utf8').splitlines()
        for line in lines:sha,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==sha
    transport=json.loads((root/'distribution/ARCHIVE-PARTS.json').read_bytes());joined=hashlib.sha256()
    for part in transport['parts']:
        data=(root/'distribution'/part['file']).read_bytes();assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256'];joined.update(data)
    assert joined.hexdigest()==digest;assert hashlib.sha256(a.restored.read_bytes()).hexdigest()==digest
    delivery=ROOT.parent/'Deliverables'/a.delivery;assert delivery.parent.resolve()==(ROOT.parent/'Deliverables').resolve();delivery.mkdir(parents=True,exist_ok=False);wanted=['complete-assets.zip','complete-assets.zip.sha256','complete-assets.zip.sig','complete-assets.zip.sig.json','signing-public-key.pem','README.md','REVIEW.md','semantic-review-progress.json','semantic-review-delta.json','changed-files.json','AynParts-forge-source.patch'];wanted += [p.relative_to(root).as_posix() for p in (root/'previews').glob('*.png')];wanted += ['workflow-previews/rgb-green-dragged.png','workflow-previews/calibration-test-calibration.png'];saved={}
    wanted += ['SystemUI-magnification-forge.patch','asset-inventory.json','workflow-fixtures.json','owner-binding-review.json','border-parameter-examples.json','verification/evidence/source-art-checks.json','verification/evidence/native-subset-build.json']
    wanted += [p.relative_to(root).as_posix() for p in (root/'workflow-previews').glob('*') if p.suffix in ['.svg','.png']]
    wanted += ['Updater-forge-source.patch','Updater-phase-binding.patch','card-workflow-fixtures.json','owner-workflow-progress.json','asset-inventory.json','verification/evidence/card-stage-checks.json','verification/evidence/material-subset-build.json']
    wanted += ['Updater-forge-workflows.patch','workflow-screen-fixtures.json','workflow-art-components.json','current-native-files.json','verification/evidence/workflow-source-art-checks.json']
    wanted += ['Glimpse-forge-workflows.patch','REMAINING.md','gallery-family-review.json','discovered-media3-visual-scope.json','verification/evidence/gallery-source-art-checks.json','verification/evidence/controls-build.json','verification/evidence/clean-patch-application.json']
    for name in dict.fromkeys(wanted):
        source=root/name
        if not source.exists():continue
        target=delivery/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);sha=hashlib.sha256(target.read_bytes()).hexdigest();assert sha==hashlib.sha256(source.read_bytes()).hexdigest();saved[name]=sha
    report={'result':'PASS','archiveBytes':archive.stat().st_size,'archiveSha256':digest,'archiveMembers':len(names),'checksumEntriesVerified':len(lines),'signatureVerified':True,'tamperRejected':True,'transportPartsVerified':len(transport['parts']),'powershellRestorationVerified':True,'allArchiveMembersMatchSavedFiles':True,'privatePathAndKeyMarkerGuard':'PASS','delivery':str(delivery),'deliveryHashes':saved,'wholeGoalComplete':False};(delivery/'DELIVERY-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');(ROOT/'build-work'/('transport-'+root.name+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='deliveryHashes'}))

if __name__=='__main__':main()
