"""Acquire pinned native timing-curve dependencies omitted from the art census."""
from pathlib import Path
import base64, concurrent.futures, gzip, hashlib, json, re, urllib.parse
from audit_os_resource_coverage import ROOT, read_json, write_json, get

BASE = ROOT/'iterations/20-semantic-review'
INPUT = ROOT/'iterations/19-os-resource-audit'
OUT = ROOT/'iterations/22-native-contract-review'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    existing = {(r['project'], r['path']) for r in read_json(BASE/'baseline/resource-files.json')+read_json(BASE/'auxiliary-source-files.json')}
    jobs = []
    for item in read_json(INPUT/'source-projects.json'):
        project = item['project']
        if 'sections' in item: tree = json.loads(gzip.decompress((INPUT/'source-trees/frameworks__base.json.gz').read_bytes()))['entries']
        else: tree = json.loads(gzip.decompress((INPUT/item['treeCache']).read_bytes()))['tree']
        for node in tree:
            if node['type'] != 'blob': continue
            path = node['path']; parent = Path(path).parent.name
            if not re.fullmatch(r'interpolator(?:-[A-Za-z0-9_+]+)*', parent) or not path.endswith('.xml'): continue
            if (project['path'], path) not in existing: jobs.append((project, path, node['sha']))
    def fetch(job):
        project, path, blob = job; target = OUT/'source/objects'/blob[:2]/blob[2:]
        encoded = urllib.parse.quote(path, safe='/')
        url = (f"https://android.googlesource.com/{project['name']}/+/{project['revision']}/{encoded}?format=TEXT"
               if project.get('remote') == 'aosp' else f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{encoded}")
        data = target.read_bytes() if target.exists() else get(url)
        if not target.exists() and project.get('remote') == 'aosp': data = base64.b64decode(data)
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == blob, path
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        return {'project': project['path'], 'repository': project['name'], 'revision': project['revision'],
                'path': path, 'kind': 'supporting-native-interpolator', 'qualifier': Path(path).parent.name,
                'resourceName': Path(path).stem, 'sourceSet': 'supporting-timing-contract',
                'gitBlobSha1': blob, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                'object': target.relative_to(OUT).as_posix(), 'url': url,
                'contentClass': 'XML', 'role': 'Native timing curve; separate from the10926-family visual baseline.'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results = list(pool.map(fetch, jobs))
    results.sort(key=lambda x: (x['project'], x['path']))
    write_json(OUT/'source/supporting-interpolators.json', results)
    print(json.dumps({'supportingInterpolatorSourceFiles': len(results), 'originalVisualFamilyCount': 10926,
                      'originalVisualVariantCount': 16559, 'notNewArtwork': True}))


if __name__ == '__main__': main()
