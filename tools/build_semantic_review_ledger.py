"""Per-family content review ledger. Never promote parsing to a reuse approval."""
from pathlib import Path
import collections,csv,hashlib,json
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit'

def old_key(row):
    parts=row['path'].split('/');i=next((i for i,x in enumerate(parts) if x==row['qualifier']),None);resource_root='/'.join(parts[:i]) if i is not None else str(Path(row['path']).parent)
    return (row['project'],resource_root,row['kind'],row['resourceName'],row['sourceSet'])

def main():
    assert not (OUT/'complete-assets.zip').exists()
    files=read_json(INPUT/'resource-files.json');families=read_json(INPUT/'resource-family-dispositions.json');features={x['gitBlobSha1']:x for x in read_json(OUT/'content-evidence.json')};grouped=collections.defaultdict(list)
    for file in files:grouped[old_key(file)].append(file)
    bindings=read_json(OUT/'source-gap-bindings.json');gap_sources={(x['sourceEvidence']['project'],x['sourceEvidence']['path']):x for x in bindings};rows=[];reuse={x['familyId']:x for x in read_json(OUT/'reuse-decisions.json')} if (OUT/'reuse-decisions.json').exists() else {}
    for baseline in families:
        key=tuple(baseline[k] for k in ['project','resourceRoot','kind','name','sourceSet']);variants=grouped[key];assert len(variants)==baseline['variants'];objects={x['gitBlobSha1']:features[x['gitBlobSha1']] for x in variants};classes=sorted({x['contentClass'] for x in objects.values()});roots=sorted({x.get('xmlRoot','') for x in objects.values() if x.get('xmlRoot')});source_gap=next((gap_sources[(x['project'],x['path'])] for x in variants if (x['project'],x['path']) in gap_sources),None)
        evidence=[{'path':x['path'],'qualifier':x['qualifier'],'gitBlobSha1':x['gitBlobSha1'],'sha256':features[x['gitBlobSha1']]['sha256'],'contentClass':features[x['gitBlobSha1']]['contentClass'],'xmlRoot':features[x['gitBlobSha1']].get('xmlRoot'),'size':features[x['gitBlobSha1']].get('size'),'stateItems':features[x['gitBlobSha1']].get('stateItems',[])} for x in variants]
        family_id='F-'+hashlib.sha256(json.dumps(key,ensure_ascii=True).encode()).hexdigest()[:16]
        decision='OPEN';action='Review actual source geometry/state/context and choose a precise Forge treatment, approved reuse, native data preservation or supported owner adaptation.';reason='Actual source content acquired and parsed; no reuse is approved solely from its identifier.';role=' / '.join(classes+roots)
        if baseline['sourceSet']=='test-or-sample':
            decision='PRESERVE_TEST_DATA';action='Retain original fixture bytes and source-test role; exclude from production-art obligations.';reason='Source path belongs to test/sample/benchmark scope. Content is verified, including intentional malformed ZIP and oversized GIF fixtures; do not turn test data into theme artwork.'
        elif classes==['Empty upstream resource']:
            decision='PRESERVE_EMPTY_SLOT';action='Keep the zero-byte upstream slot; owner/overlay handling remains a native integration condition.';reason='Verified zero bytes contain no visible source artwork. This is not evidence that a new standalone drawing is required.'
        elif classes==['Text/build contract']:
            decision='PRESERVE_BUILD_CONTRACT';action='Retain the build/description contract; satisfy its visual payload through W-07 output adaptation.';reason='Actual UTF8 build/description text is a packaging contract, not an image. Its referenced outputs remain a separate required task.'
        elif classes==['JSON'] and all(not x.get('lottie') and 'version' in x.get('jsonTopKeys',[]) and any(k.startswith('downgrade_to_') for k in x.get('jsonTopKeys',[])) for x in objects.values()):
            decision='PRESERVE_DATABASE_SCHEMA';action='Preserve database migration data unchanged; remove it from the graphic backlog.';reason='Parsed JSON defines database version/downgrade schema, not Lottie layers or artwork. Android JSON comments were handled without corrupting quoted strings.'
        elif source_gap:
            decision='GAP_ART_AUTHORED';action='Use the linked reviewed source-gap treatment and native English state contract; native owner conversion remains separate.';reason='Dedicated Forge geometry or exact-byte approved alias exists, with off/on masks, independent native vector pixels and actual state/export checks.'
        elif family_id in reuse:
            approved=reuse[family_id];decision=approved['decision'];reason=approved['rationale'];action='Use chosen exact master bytes where approved. Preserve the recorded native owner conditions; this is not approval to replace a selector, animation or layout with a standalone icon.'
        elif classes==['XML'] and roots==['resources']:
            role='Native typed value/style/path-data bundle';action='Review each native value category and source consumers; retain functional dimensions/configuration and resolve exact Forge palette/style/path-data use.'
        elif classes==['XML'] and all(x in ['selector','animated-selector','layer-list','inset','ripple','animation-list','animated-vector','level-list','rotate','animated-rotate','transition','bitmap','nine-patch','pointer-icon','com.android.internal.graphics.drawable.AnimationScaleListDrawable'] for x in roots):
            role='Native state/composition/geometry-reference wrapper';action='Trace actual referenced leaf assets, state order, levels, inset/stretch/hotspot and motion targets. A changed glyph is not automatically compatible with an old path-morph animator.'
        elif classes==['XML'] and roots==['vector']:
            role='Native vector geometry';action='Compare actual paths, configuration parameters, masks and semantic/color content; approve exact geometry reuse or author a dedicated treatment and verify its rendered states.'
        elif classes==['Bitmap']:
            role='Bitmap payload / stretch surface / glyph / content';action='Inspect source pixels and consumers, including alpha/color, stretch/content bands, cursor hotspots or localized text/data protocols; do not flatten data or assume every bitmap is an icon.'
        rows.append({'familyId':family_id,'baselineFamily':baseline,'contentRole':role,'decision':decision,'requiredAction':action,'rationale':reason,'evidence':evidence,'sourceGapId':source_gap['gapId'] if source_gap else None,'gapBindings':source_gap or None,'reuseDecision':reuse.get(family_id),'previousFilenameCandidates':baseline['candidateAssetIds'],'notApprovalEvidence':'A name resemblance, successful parse or existing donor hash alone does not establish semantic or visual fitness.'})
    assert len(rows)==len(families)==10926;assert sum(len(x['evidence']) for x in rows)==len(files)==16559
    write_json(OUT/'semantic-family-ledger.json',rows)
    small=[{'familyId':x['familyId'],'project':x['baselineFamily']['project'],'resourceRoot':x['baselineFamily']['resourceRoot'],'name':x['baselineFamily']['name'],'kind':x['baselineFamily']['kind'],'variants':len(x['evidence']),'contentRole':x['contentRole'],'decision':x['decision'],'action':x['requiredAction']} for x in rows]
    with (OUT/'semantic-family-ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:writer=csv.DictWriter(f,list(small[0]));writer.writeheader();writer.writerows(small)
    summary={'date':'2026-10-26','familyRecords':len(rows),'fileVariants':len(files),'decisions':dict(collections.Counter(x['decision'] for x in rows)),'openSemanticDecisions':sum(x['decision']=='OPEN' for x in rows),'semanticReviewFinished':all(x['decision']!='OPEN' for x in rows),'tentativeReuseCandidatesResolved':210 if reuse else 0,'appComponentArtworkBindingsRecorded':20 if (OUT/'app-component-bindings.json').exists() else 0,'fullGoalComplete':False,'otherRequiredWork':'Wider source-family artwork/semantic review, seven workflow/output adaptations, native owner bridges for replacement art, newly discovered artwork and the final independent double-check remain open.'};write_json(OUT/'semantic-review-progress.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
