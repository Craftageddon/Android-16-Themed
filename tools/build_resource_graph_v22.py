"""Correct per-file Android resource scopes and reference/declaration grammar.

The historical20 graph used the first 'res' path component. core/res/res then
acquired a false 'res' qualifier/type. This new, separately versioned graph fixes
that scope, array declaration types, private/+id/short theme reference grammar,
and text-node references without mutating the published20 evidence.
"""
from pathlib import Path
import collections, hashlib, json, re
import xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT, read_json, write_json

BASE = ROOT/'iterations/20-semantic-review'
OUT = ROOT/'iterations/22-native-contract-review'
FOLDER = re.compile(r'(?:drawable|mipmap|layout|anim|animator|transition|color|values|xml|raw|interpolator|font|menu)(?:-[A-Za-z0-9_+]+)*$')
REF = re.compile(r'(?P<sig>[@?])(?P<private>\*)?(?:(?P<pkg>[\w.]+):)?(?:(?P<type>\+?[A-Za-z_][\w.]*)/)?(?P<name>[\w.]+)')
VALUE_TYPES = {'bool', 'color', 'dimen', 'drawable', 'integer', 'string', 'style',
               'array', 'string-array', 'integer-array', 'fraction', 'id', 'attr',
               'declare-styleable', 'item', 'plurals', 'macro'}


def scope(row):
    parts = row['path'].split('/')
    # Select the actual resource directory, never an arbitrary earlier 'res'.
    candidates = [i for i, part in enumerate(parts[:-1]) if FOLDER.fullmatch(part)]
    if row.get('qualifier') and row['qualifier'] in parts[:-1]:
        exact = [i for i in candidates if parts[i] == row['qualifier']]
        if exact: candidates = exact
    if candidates:
        i = candidates[-1]; container = parts[:i]
        # AAPT flag(...) directories select resources inside the same resource
        # root; they do not create an independent package with no base fallback.
        while container and re.fullmatch(r'flag\(.+\)', container[-1]):
            container = container[:-1]
        return '/'.join(container), parts[i]
    return str(Path(row['path']).parent).replace('\\', '/'), ''


def references(text):
    # Native scalar references occupy the whole value. Scanning arbitrary text
    # would turn URL queries and literal explanatory strings into fake attrs.
    m = REF.fullmatch((text or '').strip())
    for m in [m] if m else []:
        r = m.groupdict(); r['private'] = bool(r['private'])
        if r['sig'] == '?' and not r['type']: r['type'] = 'attr'
        if r['sig'] == '@' and not r['type'] and r['name'] not in {'null', 'empty'}:
            # Do not pretend arbitrary @text is a valid Android resource use.
            continue
        yield r


def main():
    assert not (OUT/'complete-assets.zip').exists()
    supporting = read_json(OUT/'source/supporting-interpolators.json') if (OUT/'source/supporting-interpolators.json').exists() else []
    files = read_json(BASE/'baseline/resource-files.json') + read_json(BASE/'auxiliary-source-files.json') + supporting
    features = {x['gitBlobSha1']: x for x in read_json(BASE/'content-evidence.json')}
    features.update({x['gitBlobSha1']: x for x in supporting})
    declarations = []; uses = []; trees = {}; corrections = []
    old_scopes = {(d['project'], d['path']): (d['resourceRoot'], d['qualifier']) for d in read_json(BASE/'resource-declarations.json')}
    for f in files:
        root_path, qualifier = scope(f); feature = features[f['gitBlobSha1']]
        base = {'project': f['project'], 'resourceRoot': root_path, 'qualifier': qualifier,
                'path': f['path'], 'gitBlobSha1': f['gitBlobSha1'], 'sha256': feature['sha256']}
        base['sourceResourceContainer'] = str(Path(f['path']).parent.parent).replace('\\', '/') if qualifier else root_path
        base['pathFeatureFlags'] = [part[5:-1] for part in f['path'].split('/') if re.fullmatch(r'flag\(.+\)', part)]
        old = old_scopes.get((f['project'], f['path']))
        if old and old != (root_path, qualifier):
            corrections.append({'project': f['project'], 'path': f['path'],
                                'previousResourceRoot': old[0], 'previousQualifier': old[1],
                                'resourceRoot': root_path, 'qualifier': qualifier})
        if feature['contentClass'] != 'XML':
            if 'resourceName' in f and qualifier:
                declarations.append({**base, 'type': qualifier.split('-')[0], 'name': f['resourceName'], 'value': None})
            continue
        sha = f['gitBlobSha1']
        if sha not in trees:
            obj = BASE/'source/objects'/sha[:2]/sha[2:]
            if not obj.exists(): obj = OUT/'source/objects'/sha[:2]/sha[2:]
            data = obj.read_bytes()
            assert hashlib.sha256(data).hexdigest() == feature['sha256']
            trees[sha] = ET.fromstring(data)
        root = trees[sha]
        if root.tag == 'resources':
            for node in root:
                if not node.get('name') or node.tag not in VALUE_TYPES: continue
                typ = node.get('type') if node.tag == 'item' else node.tag
                if typ in {'string-array', 'integer-array'}: typ = 'array'
                if typ == 'declare-styleable': typ = 'styleable'
                declarations.append({**base, 'type': typ, 'name': node.get('name'),
                                     'value': ''.join(node.itertext()).strip(), 'attributes': dict(node.attrib),
                                     'children': [{'tag': c.tag, 'attributes': dict(c.attrib), 'text': ''.join(c.itertext()).strip()} for c in node],
                                     'runtimeResource': typ != 'styleable'})
                if node.tag == 'declare-styleable':
                    for child in node.findall('attr'):
                        if child.get('name') and ':' not in child.get('name'):
                            declarations.append({**base, 'type': 'attr', 'name': child.get('name'),
                                                 'value': ''.join(child.itertext()).strip(),
                                                 'attributes': dict(child.attrib),
                                                 'children': [{'tag': c.tag, 'attributes': dict(c.attrib), 'text': ''.join(c.itertext()).strip()} for c in child],
                                                 'declaredWithinStyleable': node.get('name')})
        elif 'resourceName' in f and qualifier:
            declarations.append({**base, 'type': qualifier.split('-')[0], 'name': f['resourceName'], 'value': None})
        for index, node in enumerate(root.iter()):
            for key, value in list(node.attrib.items()) + [('#text', node.text or '')]:
                for ref in references(value):
                    uses.append({**base, 'nodeIndex': index, 'element': node.tag,
                                 'attribute': key, 'rawValue': value, 'reference': ref})
    index = collections.defaultdict(list)
    for i, d in enumerate(declarations): index[(d['project'], d['resourceRoot'], d['type'], d['name'])].append(i)
    for use in uses:
        ref = use['reference']; typ = ref['type']; name = ref['name']; package = ref['pkg']
        if ref['sig'] == '?': use.update(resolution='Runtime theme attribute', candidates=[]); continue
        if typ in {'id', '+id'} or name in {'null', 'empty'}:
            use.update(resolution='Identity or null/empty contract', candidates=[]); continue
        if package == 'android': key = ('frameworks/base', 'core/res/res', typ, name)
        elif package is None: key = (use['project'], use['resourceRoot'], typ, name)
        else:
            use.update(resolution='Explicit external package; effective package mapping required', candidates=[]); continue
        candidates = index.get(key, [])
        use.update(resolution='Exact local declaration set; runtime qualifier/overlay selection preserved' if candidates else 'External library, generated declaration or unindexed source scope', candidates=candidates)
    write_json(OUT/'resource-declarations.json', declarations); write_json(OUT/'resource-reference-graph.json', uses)
    write_json(OUT/'resource-scope-corrections.json', corrections)
    paths = [u for u in uses if u['attribute'].split('}')[-1] == 'pathData']
    unresolved_paths = [u for u in paths if not u['candidates']]
    write_json(OUT/'unresolved-path-parameters.json', unresolved_paths)
    summary = {'date': '2026-10-26', 'sourceFileRecords': len(files), 'supportingTimingSourceFiles': len(supporting), 'parsedUniqueXmlObjects': len(trees),
               'declarations': len(declarations), 'nativeReferenceUses': len(uses),
               'correctedFileScopes': len(corrections),
               'referenceResolution': dict(collections.Counter(u['resolution'] for u in uses)),
               'parameterizedPathUses': len(paths), 'unresolvedParameterizedPathUses': len(unresolved_paths),
               'coreResourceRoot': 'core/res/res', 'effectiveRuntimeResourceSelection': 'NOT EVALUATED',
               'supersedes': 'iterations/20-semantic-review/resource-reference-graph.json.gz',
               'historicalSourceBytesOrArchiveChanged': False,
               'scope': 'Source declarations and reference candidates only. Resource root from actual resource directory; array aliases and short/private/identity reference grammar retained. Metadata symbols are not treated as value declarations. Qualifiers, overlays and external libraries are not implicitly evaluated.'}
    write_json(OUT/'resource-graph-summary.json', summary); print(json.dumps(summary))


if __name__ == '__main__': main()
