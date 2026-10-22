"""Read a factory candidate's file list/XML/AVB signatures. Never runs flash tools."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,struct,subprocess,xml.etree.ElementTree as ET
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa,padding

def avb(data):
 assert data[:4]==b'AVB0','Not a standalone AVB vbmeta image'
 q=lambda off:struct.unpack_from('>Q',data,off)[0]
 i=lambda off:struct.unpack_from('>I',data,off)[0]
 auth,aux,algorithm=q(12),q(20),i(28);assert len(data)>=256+auth+aux
 header=data[:256];authentication=data[256:256+auth];auxiliary=data[256+auth:256+auth+aux]
 result={'algorithmId':algorithm,'flags':i(120),'rollbackIndex':q(112),'releaseString':data[128:176].split(b'\0')[0].decode(errors='replace'),'signatureValid':False,'manufacturerTrustVerified':False}
 if algorithm==0:result['status']='unsigned';return result
 algorithms={1:(hashes.SHA256,2048),2:(hashes.SHA256,4096),3:(hashes.SHA256,8192),4:(hashes.SHA512,2048),5:(hashes.SHA512,4096),6:(hashes.SHA512,8192)}
 assert algorithm in algorithms,'Unsupported AVB algorithm'
 hash_cls,bits=algorithms[algorithm];public=auxiliary[q(64):q(64)+q(72)];assert len(public)==8+bits//4 and struct.unpack_from('>I',public,0)[0]==bits
 modulus=int.from_bytes(public[8:8+bits//8],'big');key=rsa.RSAPublicNumbers(65537,modulus).public_key();signed=header+auxiliary
 digest=hashes.Hash(hash_cls());digest.update(signed);expected=digest.finalize();assert authentication[q(32):q(32)+q(40)]==expected,'AVB digest mismatch'
 signature=authentication[q(48):q(48)+q(56)];key.verify(signature,signed,padding.PKCS1v15(),hash_cls())
 result.update(signatureValid=True,publicKeySha256=hashlib.sha256(public).hexdigest(),algorithm=hash_cls().name+'-RSA'+str(bits),bootVerificationDisabled=bool(i(120)&2),hashtreeVerificationDisabled=bool(i(120)&1));return result

def inspect(archive,out,report_path):
 tar=Path('C:/Windows/System32/tar.exe');listing=subprocess.run([str(tar),'-tf',str(archive)],capture_output=True,text=True,check=True).stdout.splitlines()
 assert listing and all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and ':' not in n and '\\' not in n for n in listing),'Unsafe archive entry'
 out.mkdir(parents=True,exist_ok=False)
 selected=[n for n in listing if n.endswith('.xml') or PurePosixPath(n).name in ['vbmeta.img','vbmeta_system.img','boot.img','android-info.txt']]
 p=subprocess.run([str(tar),'-xf',str(archive),'-C',str(out),*selected],capture_output=True,text=True,check=True)
 rows=[];avbs=[];labels=set();references=set()
 for name in selected:
  file=out/name;data=file.read_bytes();row={'member':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  if file.suffix=='.xml':
   doc=ET.fromstring(data)
   for node in doc.iter():
    if node.get('label'):labels.add(node.get('label'))
    if node.get('filename'):references.add(node.get('filename'))
  if file.name.startswith('vbmeta'):
   try:row['avb']=avb(data)
   except Exception as e:row['avb']={'signatureValid':False,'error':str(e),'manufacturerTrustVerified':False}
   avbs.append(row['avb'])
  if file.name=='boot.img':row['androidBootMagic']=data[:8].decode(errors='replace');row['bootHeaderVersion']=struct.unpack_from('<I',data,40)[0] if data[:8]==b'ANDROID!' else None
  rows.append(row)
 existing={PurePosixPath(n).name for n in listing};missing=sorted(n for n in references if n and n!='DISK' and n not in existing)
 report={'date':'2026-10-22','archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'memberCount':len(listing),'members':listing,'inspectedFiles':rows,'partitionLabels':sorted(labels),'xmlReferencedFilesMissing':missing,'candidateType':'Full partition/EDL-style firmware bundle; not an Android OTA ZIP','containsBootStack':all('Thor_20260112/'+n in listing for n in ['boot.img','init_boot.img','vendor_boot.img','recovery.img','dtbo.img','vbmeta.img']),'fullArchiveCrcTest':'NOT RUN; selected members read/extracted successfully with Windows bsdtar','manufacturerProvenanceVerified':False,'exactDeviceCompatibility':'NOT VERIFIED','avbSignaturesValid':bool(avbs) and all(x['signatureValid'] for x in avbs),'executedBundledUtilities':False,'deviceModified':False}
 report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['members','inspectedFiles','partitionLabels']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();inspect(a.archive.resolve(),a.out.resolve(),a.report.resolve())
