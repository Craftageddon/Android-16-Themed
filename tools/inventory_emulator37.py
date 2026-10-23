"""Inventory official emulator images and existing accepted license hashes only."""
from pathlib import Path
import hashlib,json,urllib.request,xml.etree.ElementTree as ET
SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk');ROOT=Path(__file__).resolve().parents[1];results=[]
for tag in ['android','google_apis']:
 url=f'https://dl.google.com/android/repository/sys-img/{tag}/sys-img2-3.xml'
 try:
  with urllib.request.urlopen(url,timeout=25) as response:data=response.read(10000001);assert len(data)<=10000000
  doc=ET.fromstring(data);licenses={n.get('id'):''.join(n.itertext()).strip() for n in doc.iter() if n.tag.split('}')[-1]=='license'}
  for package in doc.iter():
   if package.tag.split('}')[-1]!='remotePackage':continue
   name=package.get('path','')
   if not name.startswith('system-images;android-37;') or not name.endswith(';x86_64'):continue
   license_node=next((n for n in package if n.tag.split('}')[-1]=='uses-license'),None);license_id=license_node.get('ref') if license_node is not None else None;text=licenses.get(license_id,'');digest=hashlib.sha1(text.encode()).hexdigest();accepted=SDK/'licenses'/str(license_id);license_accepted=accepted.is_file() and digest in accepted.read_text().splitlines()
   for archive in package.iter():
    if archive.tag.split('}')[-1]!='archive':continue
    host=next((n.text for n in archive if n.tag.split('}')[-1]=='host-os'),None)
    if host not in [None,'windows']:continue
    complete=next((n for n in archive if n.tag.split('}')[-1]=='complete'),None)
    if complete is None:continue
    parts={n.tag.split('}')[-1]:n.text for n in complete};results.append({'package':name,'repository':url,'archiveUrl':url.rsplit('/',1)[0]+'/'+parts['url'],'bytes':int(parts['size']),'checksum':parts['checksum'],'licenseId':license_id,'licenseSha1':digest,'alreadyAcceptedLicense':license_accepted,'host':host})
 except Exception as e:results.append({'repository':url,'error':str(e)})
out=ROOT/'build-work/emulator37-inventory.json';out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
