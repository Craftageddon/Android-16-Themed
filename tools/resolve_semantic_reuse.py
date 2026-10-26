"""Record the explicit source/donor review decisions, including rejected matches.

An artwork reuse approval is distinct from a native drop-in approval. Native
selectors, density formats, accessibility labels and AVD target paths retain
their exact owner contracts until the relevant adapter is built and accepted.
"""
import collections,hashlib,json,shutil
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review'
CORRECT={
 'F-ddf0410129c20487':'accessibility_figure','F-be0c5bd6aa6eadf9':'accessibility_figure','F-8939d3b61b3e5333':'accessibility_figure',
 'F-3557bd6a0a5f561f':'screenshot_frame','F-e33e790081dbe5a7':'screenshot_frame',
 'F-5686c07d00bc056b':'notifications_muted','F-8e7edb4ff3401224':'pin_entry',
 'F-b1b807fcde2051ce':'error_alert','F-cc9a1160629b5553':'error_alert',
 'F-1837e15c8c112a47':'headphones','F-bee7b2ce0a2d6d06':'headphones','F-75f5c6a365735f69':'headphones','F-1246c61af643fecd':'headphones','F-8ca025987b657b77':'headphones',
 'F-7243f236fe47e6e1':'data_disabled','F-be7c1928984c4d13':'recents_square',
}
RETARGET={'F-9ba0f665f6319903':'close'}

def main():
    evidence=read_json(OUT/'reuse-review-evidence.json');rows=[]
    for item in evidence:
        fid=item['familyId'];source=item['source'];original=source['status'].startswith('Name-based reuse candidate');decision='APPROVE_SEMANTIC_ART_REUSE';assets=item['donors'];rationale='Actual upstream geometry and Forge compact/detailed donor depict the same reviewed function. Outline/filled styling and ornamental detail may differ; the native semantic ID and live English label remain distinct.'
        if not item['sourceGeometryRendered']:
            decision='REJECT_WHOLE_RESOURCE_ICON_SWAP';assets=[];rationale='Parsed source is a native '+', '.join(sorted({v['xmlRoot'] for v in item['variants'] if v['xmlRoot']}))+' contract. Replacing the whole resource with a symbol would discard structure, state, animation or component behavior. Its actual referenced leaf treatment belongs to the owner adaptation.'
        if fid in CORRECT:
            decision='REJECT_DONOR_USE_NEW_REVIEWED_GEOMETRY';name=CORRECT[fid];assets=[]
            for optical in ['compact','detailed']:
                p=OUT/'review-corrections/masters'/f'{name}__{optical}.svg';assets.append({'assetId':'20/review-corrections/'+name+'__'+optical,'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
            rationale=next(x['rationale'] for x in read_json(OUT/'review-corrections/components.json') if x['semanticId']==name)
            if not item['sourceGeometryRendered']:rationale+=' Preserve the outer native wrapper; bind this treatment to its actual leaf/owner rather than swapping the entire wrapper.'
        if fid in RETARGET:
            decision='REJECT_DONOR_RETARGET_REVIEWED_ART';name=RETARGET[fid];assets=[]
            for optical in ['compact','detailed']:
                p=ROOT/'iterations/11-forge-symbol-library/masters'/f'{name}__{optical}.svg';assets.append({'assetId':'11/'+name+'__'+optical,'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
            rationale='Actual source bitmap is an X/remove-cancel mark. The proposed trash-can donor is rejected; use the unchanged reviewed close/X artwork while retaining the native owner label and action.'
        rows.append({'familyId':fid,'wasOneOf210TentativeCandidates':original,'source':source,'evidence':item['variants'],'sourceReviewCard':f"previews/reuse-review-{evidence.index(item)//24+1:02}.png",'decision':decision,'chosenAssets':assets,'rejectedOriginalDonors':item['donors'] if decision!='APPROVE_SEMANTIC_ART_REUSE' else [],'rationale':rationale,'reviewMethod':'Parsed actual native source contents and inspected source-to-donor geometry cards, native resource roles, exact Forge master bytes and the explicit source-domain corrections. No approval is derived solely from a matching name.','reviewedBy':'Codex under the user instruction to finish semantic reuse review','reviewedAt':'2026-10-26','nativeDropInApproved':False,'ownerConditions':['Keep native semantic resource IDs and live English labels/content descriptions.','Preserve density/size/RTL, selector order, levels, insets, hotspots and callbacks.','Do not substitute new path geometry under an old AVD path-morph target; owner bridge is required.','Cold is the default; feature/selection activation is explicit native domain input. Focus alone is neutral.','Recovery bitmap protocols and native runtime acceptance remain separately verified output/owner work.']})
    copied={}
    for row in rows:
        for asset in row['chosenAssets']:
            if not asset['assetId'].startswith(('11/','17/')):continue
            iteration=asset['assetId'].split('/')[0];source=ROOT/asset['path'];target=OUT/'approved-reuse'/iteration/'masters'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==asset['sha256']
            for relative in ['../source/steel-material.png']:
                texture=source.parent/relative
                if texture.exists():
                    texture_target=target.parent/relative;texture_target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(texture,texture_target)
            asset['checkpointCopy']=target.relative_to(OUT).as_posix();copied[asset['checkpointCopy']]=asset['sha256']
    write_json(OUT/'approved-reuse/manifest.json',copied)
    assert sum(x['wasOneOf210TentativeCandidates'] for x in rows)==210;assert len(rows)==214;assert set(CORRECT)|set(RETARGET)<=set(x['familyId'] for x in rows)
    write_json(OUT/'reuse-decisions.json',rows);summary={'result':'REVIEW DECISIONS RECORDED','tentativeCandidatesResolved':210,'additionalStructuralNameMatchesRejected':4,'totalReviewedRows':214,'decisions':dict(collections.Counter(x['decision'] for x in rows)),'nativeDropInApprovals':0,'newCorrectionSemanticGlyphs':8,'unchangedPortableDonorMasters':len(copied),'sourceFamilyReviewElsewhereStillOpen':True};write_json(OUT/'reuse-decision-summary.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
