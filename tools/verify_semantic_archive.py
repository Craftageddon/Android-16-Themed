"""Audit the frozen checkpoint archive, signature, transport and local delivery."""
from pathlib import Path,PurePosixPath
import hashlib,json,shutil,zipfile
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,utils
from cryptography.exceptions import InvalidSignature

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'iterations/20-semantic-review';PIN='efed639940a40e073b8c30f4f515eb7859d65fd03b660e179006798fc9c6ac9c'

def main():
    archive=OUT/'complete-assets.zip';data=archive.read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==(OUT/'complete-assets.zip.sha256').read_text().split()[0]
    public=serialization.load_pem_public_key((OUT/'signing-public-key.pem').read_bytes());assert hashlib.sha256(public.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest()==PIN;signature=(OUT/'complete-assets.zip.sig').read_bytes();pss=padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32);public.verify(signature,bytes.fromhex(digest),pss,utils.Prehashed(hashes.SHA256()))
    changed=bytearray(bytes.fromhex(digest));changed[0]^=1
    try:public.verify(signature,bytes(changed),pss,utils.Prehashed(hashes.SHA256()));raise AssertionError('Tamper accepted')
    except InvalidSignature:pass
    markers=[('-----BEGIN '+s+'-----').encode() for s in ['PRIVATE KEY','RSA PRIVATE KEY','ENCRYPTED PRIVATE KEY','EC PRIVATE KEY']];checked=0
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None;assert len(z.namelist())==len(set(z.namelist()))
        for name in z.namelist():
            p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name;assert not {'local-secrets','build-work','__pycache__'}&set(p.parts);payload=z.read(name);assert not any(marker in payload for marker in markers);assert payload==(OUT/name).read_bytes()
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            sha,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==sha;checked+=1
    transport=json.loads((OUT/'distribution/ARCHIVE-PARTS.json').read_text());joined=hashlib.sha256()
    for part in transport['parts']:
        payload=(OUT/'distribution'/part['file']).read_bytes();assert len(payload)==part['bytes'] and hashlib.sha256(payload).hexdigest()==part['sha256'];joined.update(payload)
    assert joined.hexdigest()==digest;assert hashlib.sha256((ROOT/'build-work/forge20-restored.zip').read_bytes()).hexdigest()==digest
    delivery=ROOT.parent/'Deliverables/Forge_20_Semantic_Review_2026-10-26';delivery.mkdir(parents=True,exist_ok=False)
    names=['complete-assets.zip','complete-assets.zip.sha256','complete-assets.zip.sig','complete-assets.zip.sig.json','signing-public-key.pem','README.md','REVIEW.md','remaining-work.json','semantic-review-progress.json','reuse-decision-summary.json','app-component-bindings.json.gz','semantic-family-ledger.csv.gz','previews/semantic-gap-art-01.png','previews/semantic-gap-art-02.png','previews/app-components-01.png','previews/app-components-02.png','review-corrections/previews/source-review-corrections.png']
    manifest={}
    for name in names:
        target=delivery/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OUT/name,target);sha=hashlib.sha256(target.read_bytes()).hexdigest();assert sha==hashlib.sha256((OUT/name).read_bytes()).hexdigest();manifest[name]=sha
    report={'result':'PASS','archiveBytes':len(data),'archiveSha256':digest,'archiveMembers':len(zipfile.ZipFile(archive).namelist()),'checksumEntriesVerified':checked,'signatureVerified':True,'tamperRejected':True,'transportParts':len(transport['parts']),'powershellRestoredBytesVerified':True,'allArchiveMembersMatchSavedFiles':True,'privatePathAndKeyMarkerGuard':'PASS','delivery':str(delivery),'deliverySha256':manifest,'wholeGoalComplete':False}
    (delivery/'DELIVERY-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'build-work/forge20-archive-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='deliverySha256'}))

if __name__=='__main__':main()
