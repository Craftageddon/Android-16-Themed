"""Independently check pins, content hashes, file/family conservation and audit limits."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,OUT,read_json

def main():
    manifest=E.parse(ROOT/'integration/research/2026-10-23/official-20261019-build-manifest.xml').getroot();pins={n.get('path'):n.attrib for n in manifest.findall('project')}
    sources=json.loads((OUT/'source-projects.json').read_text());summary=json.loads((OUT/'audit-summary.json').read_text());count=0
    for source in sources:
        p=source['project'];assert p['name']==pins[p['path']]['name'] and p['revision']==pins[p['path']]['revision']
        if 'sections' in source:
            for section in source['sections']:
                raw=gzip.decompress((OUT/section['cache']).read_bytes());data=json.loads(raw);assert not data.get('truncated');assert hashlib.sha256(raw).hexdigest()==section['jsonSha256'];assert len(data['tree'])==section['entries'];count+=1
        else:
            raw=gzip.decompress((OUT/source['treeCache']).read_bytes());data=json.loads(raw);assert not data.get('truncated');assert hashlib.sha256(raw).hexdigest()==source['treeJsonSha256'];count+=1
    evidence=json.loads((OUT/'source-evidence.json').read_text());keys=set()
    for row in evidence:
        key=(row['project'],row['path']);assert key not in keys;keys.add(key);assert row['revision']==pins[row['project']]['revision'];p=OUT/row['saved'];data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1'];assert len(data)==row['bytes']
        if p.suffix=='.xml':E.fromstring(data)
    files=read_json(OUT/'resource-files.json');families=read_json(OUT/'resource-family-dispositions.json');assert len(files)==summary['visualSourceFiles'];assert len(families)==summary['resourceFamilies'];assert sum(x['variants'] for x in families)==len(files)
    p=OUT/'resource-files.csv';data=p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes());csvfiles=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
    assert [(x['project'],x['path'],x['gitBlobSha1']) for x in files]==[(x['project'],x['path'],x['gitBlobSha1']) for x in csvfiles]
    assert len({(x['project'],x['path']) for x in files})==len(files)
    bypath={(x['project'],x['path']):x for x in files}
    glyphs=json.loads((OUT/'confirmed-glyph-gaps.json').read_text());assert len(glyphs)==16
    catalog=json.loads((ROOT/'iterations/17-forge-coverage/canonical-masters.json').read_text());names={x['semanticId'] for x in catalog['masters']}
    for row in glyphs:
        assert row['family'] not in names;assert row['evidence']['gitBlobSha1']==bypath[(row['evidence']['project'],row['evidence']['path'])]['gitBlobSha1'];assert E.parse(OUT/row['evidence']['saved']).getroot().tag=='vector'
        assert all(x['sha256']==hashlib.sha256((ROOT/x['source']).read_bytes()).hexdigest() for x in row['donors'])
    for row in catalog['masters']:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256'],'Existing master altered'
    apps=json.loads((OUT/'additional-app-targets.json').read_text());assert len(apps)==20;assert len({(x['project'],x['sourceManifestPackage']) for x in apps})==20
    assert all(E.parse(OUT/x['evidence']['saved']).getroot().get('package')==x['sourceManifestPackage'] for x in apps)
    workflows=json.loads((OUT/'workflow-adaptations.json').read_text());assert len(workflows)==7
    for row in workflows:
        assert all((x['project'],x['path']) in keys for x in row['sources']);assert set(row['donorSemanticIds'])<=names
    assert not json.loads((OUT/'source-fetch-errors.json').read_text());assert not json.loads((OUT/'evidence-fetch-errors.json').read_text())
    assert summary['familyDispositionCounts']==dict(collections.Counter(x['status'] for x in families))
    assert summary['allOsAssetsClaim'].startswith('NOT ESTABLISHED')
    report={'result':'PASS','date':'2026-10-26','pinnedSourceProjects':len(sources),'completeTreeSectionsOrProjects':count,'contentHashCheckedFiles':len(evidence),'fileRecordsConserved':len(files),'familyRecordsConserved':len(families),'confirmedGlyphFamilies':len(glyphs),'additionalAppComponentTargets':len(apps),'workflowAdaptationGroups':len(workflows),'unchangedExistingMasterHashes':len(catalog['masters']),'method':'Independent stdlib re-open of pinned manifest, all tree proofs, every saved source byte and XML; Git blob/SHA256 checks; CSV-to-JSON exact conservation; family variant totals; donor/catalog hashes; source identity parsing and explicit unresolved-scope assertions.','deviceValidation':'NOT RUN - source audit only','remainingSemanticReview':sum(x['status'].startswith('Unassigned') for x in families),'notClaimed':'Complete built-ROM reachability or all visual resources redesigned'}
    out=OUT/'verification/evidence';out.mkdir(parents=True,exist_ok=True);(out/'audit-integrity.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))

if __name__=='__main__':main()
