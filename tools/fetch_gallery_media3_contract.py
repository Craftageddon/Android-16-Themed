'''Preserve exact Gallery Media3 UI resource and source contracts.'''
from pathlib import Path,PurePosixPath
import hashlib,zipfile,json
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/26-gallery-workflows'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    aar=next((OUT/'upstream/packages/apps/Glimpse/app/libs').rglob('media3-ui-*.aar'))
    dest=OUT/'source/media3-ui';dest.mkdir(parents=True,exist_ok=True)
    base='https://dl.google.com/dl/android/maven2/androidx/media3/media3-ui/1.10.0/media3-ui-1.10.0'
    canonical=dest/'official-media3-ui-1.10.0.aar'
    if not canonical.exists():canonical.write_bytes(get(base+'.aar'))
    assert hashlib.sha256(aar.read_bytes()).hexdigest()==hashlib.sha256(canonical.read_bytes()).hexdigest(),'Official artifact differs from committed pin'
    src=dest/'media3-ui-1.10.0-sources.jar'
    if not src.exists():src.write_bytes(get(base+'-sources.jar'))
    rows=[]
    for archive,folder,accept in [(aar,'original-resources',lambda n:n.startswith('res/') or n in ['R.txt','AndroidManifest.xml','classes.jar']),
                                  (src,'original-java',lambda n:n.endswith('.java') or n.endswith('LICENSE'))]:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            for name in z.namelist():
                if name.endswith('/') or not accept(name):continue
                rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in name
                data=z.read(name);p=dest/folder/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                rows.append({'archive':archive.relative_to(OUT).as_posix(),'member':name,'saved':p.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    write_json(OUT/'source/media3-ui-contract.json',{'version':'1.10.0','sourceUrl':base+'-sources.jar','sourceJarSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'officialAarUrl':base+'.aar','officialAarMatchesPinnedCommittedArtifact':True,'aarSha256':hashlib.sha256(aar.read_bytes()).hexdigest(),'members':rows,'executed':False})
    print({'media3ResourcesAndSources':len(rows),'committedMatchesOfficialAar':True,'sourceJarBytes':src.stat().st_size,'executed':False})
if __name__=='__main__':main()
