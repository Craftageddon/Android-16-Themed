"""Acquire the exact pinned SystemUI magnification owners and existing tests."""
from pathlib import Path
import concurrent.futures, gzip, hashlib, json, shutil, urllib.parse
from audit_os_resource_coverage import ROOT, read_json, write_json, get

OUT = ROOT/'iterations/23-magnification'
INPUT = ROOT/'iterations/19-os-resource-audit'
BASE = ROOT/'iterations/20-semantic-review'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    item = next(x for x in read_json(INPUT/'source-projects.json') if x['project']['path']=='frameworks/base')
    project = item['project']; tree = json.loads(gzip.decompress((INPUT/'source-trees/frameworks__base.json.gz').read_bytes()))['entries']
    extra = {'packages/SystemUI/Android.bp',
             'packages/SystemUI/src/com/android/systemui/common/ui/view/SeekBarWithIconButtonsView.java',
             'packages/SystemUI/multivalentTests/src/com/android/systemui/common/ui/view/SeekBarWithIconButtonsViewTest.java',
             'packages/SystemUI/src/com/android/systemui/accessibility/MirrorWindowControl.java',
             'packages/SystemUI/src/com/android/systemui/accessibility/SimpleMirrorWindowControl.java'}
    jobs = [n for n in tree if n['type']=='blob' and (n['path'] in extra or (('/src/com/android/systemui/accessibility/' in n['path'])
            and 'magnif' in Path(n['path']).name.lower() and Path(n['path']).suffix in {'.java','.kt'}))]
    assert extra <= {n['path'] for n in jobs}, extra-{n['path'] for n in jobs}
    def fetch(node):
        path = node['path']; blob = node['sha']; dest = OUT/'upstream/frameworks/base'/path
        url = f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{urllib.parse.quote(path,safe='/')}"
        data = dest.read_bytes() if dest.exists() else get(url)
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blob
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        return {'project': project['path'], 'revision': project['revision'], 'repository': project['name'],
                'path': path, 'url': url, 'gitBlobSha1': blob, 'sha256': hashlib.sha256(data).hexdigest(),
                'bytes': len(data), 'saved': dest.relative_to(OUT).as_posix(),
                'role': 'Upstream unexecuted test' if '/tests/' in path or '/multivalentTests/' in path else 'Actual native magnification owner'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: records = list(pool.map(fetch, jobs))
    files = read_json(BASE/'baseline/resource-files.json')
    extras = {'ic_arrow_top_right_and_bottom_left', 'ic_arrow_top_left_and_bottom_right', 'ic_open_in_full', 'ic_open_in_new_window', 'ic_add', 'ic_remove', 'seekbar_with_icon_buttons'}
    selected = [f for f in files if f['project']=='frameworks/base' and f['path'].startswith('packages/SystemUI/res/') and ('magnif' in f['path'].lower() or f['resourceName'] in extras)]
    for f in selected:
        blob = f['gitBlobSha1']; src = BASE/'source/objects'/blob[:2]/blob[2:]; data = src.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blob
        dest = OUT/'upstream/frameworks/base'/f['path']; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        records.append({**f, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                        'saved': dest.relative_to(OUT).as_posix(), 'role': 'Actual native resource'})
    records.sort(key=lambda x:x['path']); write_json(OUT/'source-manifest.json', records)
    print(json.dumps({'pinnedSourceRecords': len(records), 'ownerAndTestFiles': len(jobs),
                      'resourceVariants': len(selected), 'revision': project['revision'], 'codeExecuted': False}))


if __name__ == '__main__': main()
