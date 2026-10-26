"""Make this review checkpoint portable while preserving original source notices."""
from pathlib import Path
import gzip,hashlib,json,shutil
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit'

def main():
    assert not (OUT/'complete-assets.zip').exists();records=[]
    for row in read_json(INPUT/'source-evidence.json'):
        source=INPUT/row['saved'];target=OUT/'source/context'/row['project']/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'];records.append({**row,'checkpointCopy':target.relative_to(OUT).as_posix()})
    write_json(OUT/'source/context-manifest.json',records)
    for name in ['resource-files.json','resource-family-dispositions.json','source-projects.json','workflow-adaptations.json']:
        data=read_json(INPUT/name);write_json(OUT/'baseline'/name,data)
    shutil.copy2(INPUT/'signing-public-key.pem',OUT/'signing-public-key.pem')
    for name in ['app-component-bindings.json','source-gap-bindings.json']:
        rows=read_json(OUT/name)
        for row in rows:
            ev=row['manifest'] if 'manifest' in row else row['sourceEvidence'];ev['checkpointCopy']='source/context/'+ev['project']+'/'+ev['path'];assert (OUT/ev['checkpointCopy']).is_file()
        write_json(OUT/name,rows)
    # CSV is also available inside the signed archive; compressed Git transport is exact.
    for csv in OUT.glob('*.csv'):csv.with_suffix(csv.suffix+'.gz').write_bytes(gzip.compress(csv.read_bytes(),mtime=0))
    large=[]
    for p in list(OUT.glob('*.json'))+list((OUT/'baseline').glob('*.json'))+[OUT/'source/context-manifest.json']:
        data=p.read_bytes()
        if len(data)>80000:p.with_suffix(p.suffix+'.gz').write_bytes(gzip.compress(data,mtime=0));large.append(p.relative_to(ROOT).as_posix())
    ignore=ROOT/'.gitignore';existing=ignore.read_text();entries=['iterations/20-semantic-review/complete-assets.zip','iterations/20-semantic-review/source/objects/','iterations/20-semantic-review/source/context/','iterations/20-semantic-review/app-exports/','iterations/20-semantic-review/review-corrections/exports/','iterations/20-semantic-review/semantic-family-ledger.csv']+large
    new=[x for x in entries if x not in existing.splitlines()]
    if new:ignore.write_text(existing+'\n'+'\n'.join(new)+'\n')
    write_json(OUT/'remaining-work.json',{'date':'2026-10-26','goalStatus':'ACTIVE - whole review is not finished','openFamilyDecisions':read_json(OUT/'semantic-review-progress.json')['openSemanticDecisions'],'sevenWorkflowAdaptations':read_json(INPUT/'workflow-adaptations.json'),'nativeOwnerBridges':'New symbol/app artwork is not substituted underneath old path-morph targets. Native owner, state/accessibility and output contracts still require implementation/validation.','finalIndependentDoubleCheck':'NOT RUN - must follow completion of all required semantic/artwork/adaptation work. Current tests are checkpoint checks only.','deviceAcceptance':'NOT RUN; user explicitly chose to continue without the device.','noFlashing':True})
    print(json.dumps({'preservedContextSourceFiles':len(records),'completeRawObjectCorpus':'source/objects','historicalBaselineUnchanged':True}))

if __name__=='__main__':main()
