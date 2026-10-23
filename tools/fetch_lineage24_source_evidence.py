"""Fetch read-only primary Lineage target/package evidence; execute no downloads."""
from pathlib import Path
import hashlib,json,re,urllib.request,urllib.error,datetime
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'integration/research/2026-10-23';OUT.mkdir(exist_ok=True)
def get(url):
 request=urllib.request.Request(url,headers={'User-Agent':'Craftageddon source compatibility research','Accept':'application/json, text/plain, */*'})
 with urllib.request.urlopen(request,timeout=30) as r:
  body=r.read(10000001);assert len(body)<=10000000
  return body,r.status,r.headers.get('Content-Type','')
specs=[
 ('device','android_device_ayn_odin2thor','lineage_odin2thor.mk',None),
 ('files','android_packages_apps_DocumentsUI','AndroidManifest.xml','com.android.documentsui'),
 ('gallery','android_packages_apps_Glimpse','app/build.gradle.kts','org.lineageos.glimpse'),
 ('settings','android_packages_apps_Settings','AndroidManifest.xml','com.android.settings'),
]
pins=[]
for key,repo,file,package in specs:
 try:
  branch_url=f'https://api.github.com/repos/LineageOS/{repo}/branches/lineage-24.0';data,status,ct=get(branch_url);sha=json.loads(data)['commit']['sha'];url=f'https://raw.githubusercontent.com/LineageOS/{repo}/{sha}/{file}';body,status,ct=get(url);text=body.decode('utf8');assert package is None or package in text
  if key=='device':assert 'PRODUCT_NAME := lineage_odin2thor' in text and 'common_full_tablet_wifionly.mk' in text
  pins.append({'key':key,'repository':'LineageOS/'+repo,'branch':'lineage-24.0','commit':sha,'path':file,'sourceUrl':url,'sha256':hashlib.sha256(body).hexdigest(),'packageId':package,'result':'PASS'})
 except Exception as e:pins.append({'key':key,'result':'UNVERIFIED','error':str(e)})
report={'date':datetime.date.today().isoformat(),'sourcePins':pins,'deviceInventory':'User chose to continue without a connected device; installed packages and physical acceptance NOT RUN'}
(OUT/'lineage24-source-pins.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
url='https://download.lineageos.org/api/v2/devices/odin2thor/builds'
try:
 body,status,ct=get(url);data=json.loads(body);p=OUT/'official-thor-builds-response.json';p.write_bytes(body);result={'url':url,'date':datetime.date.today().isoformat(),'httpStatus':status,'contentType':ct,'sha256':hashlib.sha256(body).hexdigest(),'responseFile':p.name,'jsonType':type(data).__name__,'scope':'Retrieved official build API metadata only; no ROM download, signature or device compatibility verified'}
except Exception as e:result={'url':url,'date':datetime.date.today().isoformat(),'result':'UNVERIFIED','error':str(e),'scope':'No build availability or authenticity inference from a failed metadata fetch'}
(OUT/'official-thor-builds-fetch.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
