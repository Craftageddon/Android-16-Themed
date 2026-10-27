'''Snapshot the editable current workflow sources without rerunning earlier owner edits.'''
import difflib,hashlib
from audit_os_resource_coverage import ROOT,write_json
OUT=ROOT/'iterations/25-updater-workflows'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    patch=OUT/'native-patch/packages/apps/Updater';up=OUT/'upstream/packages/apps/Updater'
    rows=[];lines=[]
    for p in sorted(patch.rglob('*')):
        if p.suffix not in {'.java','.kt','.xml'}:continue
        rel=p.relative_to(patch).as_posix();a=up/rel
        before=a.read_bytes() if a.exists() else b'';after=p.read_bytes()
        if before==after:continue
        rows.append({'path':rel,'bytes':len(after),'sha256':hashlib.sha256(after).hexdigest()})
        for line in difflib.unified_diff(before.decode('utf8').splitlines(keepends=True),after.decode('utf8').splitlines(keepends=True),fromfile='a/'+rel if a.exists() else '/dev/null',tofile='b/'+rel):
            lines.append(line if line.endswith(chr(10)) else line+chr(10)+'\\ No newline at end of file'+chr(10))
    (OUT/'Updater-forge-workflows.patch').write_bytes(''.join(lines).encode('utf8'))
    write_json(OUT/'current-native-files.json',rows)
    print({'nativeTextFiles':len(rows),'patch':'Updater-forge-workflows.patch'})
if __name__=='__main__':main()
