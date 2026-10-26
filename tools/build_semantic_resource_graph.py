"""Index exact declarations and native references with conservative scope resolution.

Resolution returns all compatible candidates. It never pretends that source lookup
has evaluated product overlays or Android's complete runtime configuration matcher.
"""
from pathlib import Path
import collections,hashlib,json,re,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit'
AN='{http://schemas.android.com/apk/res/android}'
REF=re.compile(r'(?P<sig>[@?])(?:(?P<pkg>[\w.]+):)?(?P<type>[A-Za-z_][\w.]*)/(?P<name>[\w.]+)')

def scope(row):
    parts=row['path'].split('/')
    for i,part in enumerate(parts):
        if part=='res':return '/'.join(parts[:i+1]),parts[i+1] if i+1<len(parts) else ''
    return str(Path(row['path']).parent).replace('\\','/'),''

def build():
    files=read_json(INPUT/'resource-files.json');aux=read_json(OUT/'auxiliary-source-files.json');features={x['gitBlobSha1']:x for x in read_json(OUT/'content-evidence.json')};declarations=[];uses=[]
    for f in files+aux:
        root,qualifier=scope(f);d=features[f['gitBlobSha1']];base={'project':f['project'],'resourceRoot':root,'qualifier':qualifier,'path':f['path'],'gitBlobSha1':f['gitBlobSha1'],'sha256':d['sha256']}
        if d.get('xmlRoot')=='resources':
            for v in d['namedValues']:
                declarations.append({**base,'type':v['type'],'name':v['name'],'value':v['text'],'attributes':v['attributes'],'children':v['children']})
        elif 'resourceName' in f:
            kind=f['kind'];typ=qualifier.split('-')[0] if qualifier else kind
            declarations.append({**base,'type':typ,'name':f['resourceName'],'value':None})
        if d['contentClass']=='XML':
            # Actual attribute uses exclude comments and XML documentation examples.
            for use in d['nativeUses']:
                uses.append({**base,**use})
            if d.get('xmlRoot')=='resources':
                for v in d['namedValues']:
                    for m in REF.finditer(v['text']):uses.append({**base,'element':v['type'],'attribute':'text','declaration':v['name'],'reference':m.groupdict()})
    index=collections.defaultdict(list)
    for i,d in enumerate(declarations):index[(d['project'],d['resourceRoot'],d['type'],d['name'])].append(i)
    for use in uses:
        ref=use['reference'];typ=ref['type'];name=ref['name'];package=ref['pkg'];sig=ref['sig']
        if sig=='?':use.update(resolution='Runtime theme attribute',candidates=[]);continue
        if typ in ['id','+id'] or name=='null':use.update(resolution='Identity or null contract',candidates=[]);continue
        if package=='android':key=('frameworks/base','core/res/res',typ,name)
        elif package is None:key=(use['project'],use['resourceRoot'],typ,name)
        else:
            use.update(resolution='Explicit external package; effective package mapping required',candidates=[]);continue
        candidates=index.get(key,[])
        if candidates:use.update(resolution='Exact local declaration set; runtime qualifier/overlay selection preserved',candidates=candidates)
        else:use.update(resolution='External library, generated declaration or unindexed source scope',candidates=[])
    write_json(OUT/'resource-declarations.json',declarations);write_json(OUT/'resource-reference-graph.json',uses)
    path_refs=[x for x in uses if x['attribute'].split('}')[-1]=='pathData'];unresolved=[x for x in path_refs if not x['candidates']]
    write_json(OUT/'unresolved-path-parameters.json',unresolved)
    summary={'date':'2026-10-26','originalFiles':len(files),'supportingFiles':len(aux),'declarations':len(declarations),'nativeReferenceUses':len(uses),'referenceResolution':dict(collections.Counter(x['resolution'] for x in uses)),'parameterizedPathUses':len(path_refs),'unresolvedPathUses':len(unresolved),'scopeGuarantee':'Actual project/resource-root/type/name declarations. Candidates remain a set; no Make evaluation, runtime configuration selection or installed-app claim.','nestedStyleItemsAreIndependentDeclarations':False,'commentsAreReferenceEvidence':False}
    write_json(OUT/'resource-graph-summary.json',summary);print(json.dumps(summary))

if __name__=='__main__':build()
