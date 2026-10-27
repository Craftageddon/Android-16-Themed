"""Preserve the exact selected Updater owners and their presentation inputs.

Reads pinned public sources only. Does not execute updater/install operations.
"""
from pathlib import Path
import concurrent.futures, gzip, hashlib, json, urllib.parse
from audit_os_resource_coverage import ROOT, read_json, write_json, get

OUT=ROOT/'iterations/24-updater'
AUDIT=ROOT/'iterations/19-os-resource-audit'
BASE=ROOT/'iterations/20-semantic-review'


def main():
    assert not (OUT/'complete-assets.zip').exists(), 'Packaged checkpoint is immutable'
    project=next(x['project'] for x in read_json(AUDIT/'source-projects.json')
                 if x['project']['path']=='packages/apps/Updater')
    tree=read_json(AUDIT/'source-trees/packages__apps__Updater.json')['tree']
    # Exact source tree entries, not guessed filenames. Keep default-language
    # resources and theme variants; translations stay in the preserved corpus.
    jobs=[n for n in tree if n['type']=='blob' and (
        n['path'].endswith(('.java','.kt','.bp','.toml')) or
        n['path'] in {'app/src/main/AndroidManifest.xml','LICENSE','NOTICE'} or
        (n['path'].startswith('app/src/main/res/') and
         ('/values/' in n['path'] or '/values-night/' in n['path'] or
          '/values-v' in n['path'] or '/raw/' in n['path'] or
          '/drawable' in n['path'] or '/mipmap' in n['path'])))]
    # Reuse only byte-verified original payloads; records remain tied to this pin.
    baseline={x['path']:x for x in read_json(BASE/'baseline/resource-files.json')
              if x['project']==project['path']}

    def fetch(node):
        path=node['path'];dest=OUT/'upstream'/project['path']/path
        url=f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{urllib.parse.quote(path,safe='/')}"
        cached=BASE/'source/objects'/node['sha'][:2]/node['sha'][2:]
        prior=AUDIT/'source-evidence'/project['path']/path
        data=(dest.read_bytes() if dest.exists() else cached.read_bytes() if cached.exists()
              else prior.read_bytes() if prior.exists() else get(url))
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual==node['sha'],path
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        return {'project':project['path'],'repository':project['name'],
                'revision':project['revision'],'path':path,'url':url,
                'gitBlobSha1':actual,'sha256':hashlib.sha256(data).hexdigest(),
                'bytes':len(data),'saved':dest.relative_to(OUT).as_posix(),
                'baselineResourceVariant':path in baseline,
                'role':'Original source only; not executed or adapted'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records=sorted(pool.map(fetch,jobs),key=lambda x:x['path'])
    write_json(OUT/'source-manifest.json',records)
    print(json.dumps({'pinnedSourceFiles':len(records),'sourceBytes':sum(r['bytes'] for r in records),
                      'revision':project['revision'],'codeExecuted':False,
                      'ownerAdaptationComplete':False,'fullGoalComplete':False}))


if __name__=='__main__':main()
