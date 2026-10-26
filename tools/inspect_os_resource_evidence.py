"""Fetch hash-checked source examples and product declarations for the resource audit."""
from pathlib import Path
import base64,concurrent.futures,gzip,hashlib,json,re,xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT,OUT,get,write_json

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Never rewrite a packaged checkpoint'
    projects=json.loads((OUT/'source-projects.json').read_text());files=json.loads((OUT/'resource-files.json').read_text());jobs={};selection={}
    def add(project,path,sha,reason):
        key=project['path']+'/'+path;jobs[key]=(project,path,sha);selection.setdefault(key,[]).append(reason)
    for result in projects:
        project=result['project'];prefix=project['path']
        if prefix=='frameworks/base':continue
        tree=json.loads(gzip.decompress((OUT/result['treeCache']).read_bytes()))['tree']
        for f in tree:
            if f['type']!='blob':continue
            p=f['path']
            product=(prefix.startswith('device/ayn/') and p.endswith(('.mk','.bp'))) or (prefix=='hardware/ayn' and (p.endswith(('.mk','.bp')) or p.endswith('/AndroidManifest.xml') or p.endswith('/res/xml/ayn_parts.xml'))) or (prefix=='vendor/lineage' and (p.startswith('config/') and p.endswith('.mk') or p in ['bootanimation/Android.bp','charger/Android.bp']))
            product=product or (prefix=='build/make' and p.startswith('target/product/') and p.endswith('.mk'))
            identity=(prefix.startswith('packages/') and (p.endswith(('Android.bp','AndroidManifest.xml','build.gradle.kts','build.gradle')) and not any(v in p.split('/') for v in ['tests','test','samples'])))
            ayn_code=prefix=='hardware/ayn' and p.startswith('packages/AynParts/src/') and p.endswith('.kt')
            ayn_prefs=prefix=='hardware/ayn' and '/res/xml/' in p and p.endswith('.xml')
            app_ui=prefix in ['packages/apps/Updater','packages/apps/SetupWizard'] and p.startswith('app/src/main/') and (p.endswith(('Activity.kt','Activity.java')) or '/ui/' in p and p.endswith('.kt'))
            if product or identity or ayn_code or ayn_prefs or app_ui:add(project,p,f['sha'],'Application UI owner' if app_ui else 'AYN source-drawn UI' if ayn_code else 'AYN preference resource' if ayn_prefs else 'Product/module/package declaration')
    targets={
      'Extra dim':['qs_extra_dim_icon_on','qs_extra_dim_icon_off','vd_dim'],
      'Night light':['vd_night_light','qs_nightlight_icon_on','qs_nightlight_icon_off'],
      'Dark theme':['qs_light_dark_theme_icon_on','qs_light_dark_theme_icon_off','vd_theme'],
      'Color inversion':['ic_invert_colors','qs_invert_colors_icon_on','vd_inversion'],
      'Color correction':['ic_qs_color_correction'],
      'Live captions':['ic_volume_odi_captions','ic_volume_odi_captions_disabled'],
      'Hearing devices':['hearing','qs_hearing_devices_icon'],
      'QR scanner':['ic_qr_code_scanner'],
      'Ethernet':['ic_statusbar_ethernet','stat_sys_ethernet'],
      'Work profile':['ic_statusbar_work','vd_work','qs_work_mode_icon_off'],
      'Sensors disabled':['stat_sys_sensors_off'],
      'Wallet':['ic_qs_wallet','ic_wallet_lockscreen'],
      'Keyboard backlight':['ic_keyboard_backlight'],
      'Screen magnification':['ic_control_magnification_grey','fullscreen_magnification_border'],
      'Printing':['ic_print','ic_settings_print'],
      'Stylus':['ic_stylus','ic_settings_stylus'],
      'AYN RGB dialog':['dialog_rgb_sliders','ic_gamepad'],
    }
    for f in files:
        if f['sourceSet']!='production-candidate':continue
        reasons=[label for label,names in targets.items() if f['resourceName'] in names]
        app_detail=(f['project'] in ['packages/apps/SetupWizard','packages/apps/Updater','packages/apps/Glimpse'] and f['kind'] in ['drawable','mipmap','layout'] and f['path'].endswith('.xml'))
        vector_paths=f['project']=='frameworks/base' and f['path']=='packages/SystemUI/res/values/paths.xml'
        if reasons or app_detail or vector_paths:
            project=next(p['project'] for p in projects if p['project']['path']==f['project'])
            add(project,f['path'],f['gitBlobSha1'],', '.join(reasons) or 'Application visual/detail review')
    evidence=[];errors=[]
    def fetch(item):
        key,(project,path,sha)=item;dest=OUT/'source-evidence'/key;url=f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{path}"
        if project.get('remote')=='aosp':url=f"https://android.googlesource.com/{project['name']}/+/{project['revision']}/{path}?format=TEXT"
        data=dest.read_bytes() if dest.exists() else (base64.b64decode(get(url)) if project.get('remote')=='aosp' else get(url))
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha,key+' Git blob mismatch'
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        meta={'project':project['path'],'path':path,'revision':project['revision'],'url':url,'saved':dest.relative_to(OUT).as_posix(),'bytes':len(data),'gitBlobSha1':sha,'sha256':hashlib.sha256(data).hexdigest(),'reasons':selection[key]}
        if path.endswith('.xml'):
            doc=ET.fromstring(data);meta['xmlRoot']=doc.tag;meta['xmlNodes']=len(list(doc.iter()));meta['references']=sorted(set(re.findall(r'@(?:[\w.]+:)?(?:drawable|mipmap|layout|anim|color)/[\w.]+',data.decode('utf8'))))
            meta['xmlAttributes']={k:v for k,v in doc.attrib.items() if not k.endswith('pathData')}
        return meta
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        pending={pool.submit(fetch,item):item[0] for item in jobs.items()}
        for future in concurrent.futures.as_completed(pending):
            try:evidence.append(future.result())
            except Exception as e:errors.append({'source':pending[future],'error':str(e)})
    evidence.sort(key=lambda x:(x['project'],x['path']));write_json(OUT/'source-evidence.json',evidence);write_json(OUT/'evidence-fetch-errors.json',errors)
    print(json.dumps({'hashCheckedFiles':len(evidence),'errors':errors,'resourceExampleLabels':sorted(targets)}))

if __name__=='__main__':main()
