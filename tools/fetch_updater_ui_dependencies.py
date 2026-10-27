'''Read exact pinned SPA presentation interfaces; never execute them.'''
from pathlib import Path
import hashlib
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/24-updater'
AUDIT=ROOT/'iterations/19-os-resource-audit'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    project=next(x['project'] for x in read_json(AUDIT/'source-projects.json') if x['project']['path']=='frameworks/base')
    tree=read_json(AUDIT/'source-trees/frameworks__base.json')['entries']
    names={'Preference.kt','SwitchPreference.kt','SettingsTheme.kt','SettingsAlertDialog.kt',
           'SettingsScaffold.kt','SettingsDimension.kt','SettingsSpace.kt','ProgressBar.kt'}
    nodes=[x for x in tree if Path(x['path']).name in names and '/spa/' in x['path'] and x['type']=='blob']
    assert len(nodes)==len(names)
    rows=[]
    for n in nodes:
        p=OUT/'source/actual-ui-dependencies/frameworks/base'/n['path']
        url='https://raw.githubusercontent.com/'+project['name']+'/'+project['revision']+'/'+n['path']
        data=p.read_bytes() if p.exists() else get(url)
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==n['sha']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append({'project':'frameworks/base','revision':project['revision'],'path':n['path'],
                     'gitBlobSha1':n['sha'],'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
                     'url':url,'saved':p.relative_to(OUT).as_posix(),'sourceOnlyNotExecuted':True})
    write_json(OUT/'source/ui-dependency-manifest.json',rows)
    print({'pinnedUiDependencySources':len(rows),'executed':False})
if __name__=='__main__':main()
