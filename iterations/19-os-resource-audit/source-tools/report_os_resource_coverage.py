"""Conservative source-to-art audit: reviewed gaps are distinct from name candidates."""
from pathlib import Path
import collections,csv,gzip,hashlib,json,re,xml.etree.ElementTree as ET
from audit_os_resource_coverage import ROOT,OUT,write_json,read_json

# Explicitly reviewed semantic families, not an automatic unmatched-filename count.
GLYPHS=[
 ('extra_dim','Extra dim','frameworks/base','packages/SystemUI/res/drawable/vd_dim.xml','brightness_low'),
 ('night_light','Night light','frameworks/base','packages/SystemUI/res/drawable/vd_night_light.xml','brightness_low'),
 ('dark_theme','Dark theme','frameworks/base','packages/SystemUI/res/drawable/vd_theme.xml','display'),
 ('color_inversion','Color inversion','frameworks/base','packages/SystemUI/res/drawable/ic_invert_colors.xml','accessibility'),
 ('color_correction','Color correction','frameworks/base','packages/SystemUI/res/drawable/ic_qs_color_correction.xml','accessibility'),
 ('live_captions','Live captions - enabled and disabled','frameworks/base','packages/SystemUI/res/drawable/ic_volume_odi_captions.xml','audio'),
 ('hearing_devices','Hearing devices','frameworks/base','packages/SystemUI/res/drawable/qs_hearing_devices_icon.xml','headphones'),
 ('qr_scanner','QR code scanner','frameworks/base','packages/SystemUI/res/drawable/ic_qr_code_scanner.xml','camera_on'),
 ('ethernet','Ethernet','frameworks/base','packages/SystemUI/res/drawable/ic_statusbar_ethernet.xml','network'),
 ('work_profile','Work profile - enabled and paused','frameworks/base','packages/SystemUI/res/drawable/ic_statusbar_work.xml','person'),
 ('sensors_disabled','Sensors disabled','frameworks/base','packages/SystemUI/res/drawable/stat_sys_sensors_off.xml','privacy'),
 ('wallet','Wallet','frameworks/base','packages/SystemUI/res/drawable/ic_qs_wallet.xml','security'),
 ('keyboard_backlight','Keyboard backlight','frameworks/base','packages/SystemUI/res/drawable/ic_keyboard_backlight.xml','keyboard'),
 ('printing','Printing','frameworks/base','core/res/res/drawable/ic_print.xml','document'),
 ('stylus','Stylus','packages/apps/Settings','res/drawable/ic_stylus.xml','edit'),
 ('favorite','Favorite star - filled and outline','packages/apps/Glimpse','app/src/main/res/drawable/ic_star.xml','check'),
]

APP_TARGETS=[('AynParts','hardware/ayn','packages/AynParts/AndroidManifest.xml','controller'),('Launcher3QuickStep','packages/apps/Launcher3','quickstep/AndroidManifest.xml','app_drawer'),('LineageParts','packages/apps/LineageParts','AndroidManifest.xml','settings'),('LineageSetupWizard','packages/apps/SetupWizard','app/src/main/AndroidManifest.xml','forge_crest'),('Updater','packages/apps/Updater','app/src/main/AndroidManifest.xml','download'),('LatinIME','packages/inputmethods/LatinIME','java/AndroidManifest.xml','keyboard'),('Jelly','packages/apps/Jelly','app/src/main/AndroidManifest.xml','network'),('ExactCalculator','packages/apps/ExactCalculator','AndroidManifest.xml','control-keyboard_letter'),('Etar','packages/apps/Etar','app/src/main/AndroidManifest.xml','clock'),('Recorder','packages/apps/Recorder','app/src/main/AndroidManifest.xml','microphone_on'),('Twelve','packages/apps/Twelve','app/src/main/AndroidManifest.xml','music_note'),('Seedvault','packages/apps/Seedvault','app/src/main/AndroidManifest.xml','security'),('AudioFX','packages/apps/AudioFX','AndroidManifest.xml','eq_band'),('Camelot','packages/apps/Camelot','app/src/main/AndroidManifest.xml','folder'),('Profiles','packages/apps/Profiles','AndroidManifest.xml','person'),('Backgrounds','packages/apps/Backgrounds','AndroidManifest.xml','photo'),('Canvas','packages/apps/Canvas','app/src/main/AndroidManifest.xml','photo'),('ThemePicker','packages/apps/ThemePicker','AndroidManifest.xml','settings'),('AvatarPicker','packages/apps/AvatarPicker','AndroidManifest.xml','person'),('QuickAccessWallet','packages/apps/QuickAccessWallet','AndroidManifest.xml','security')]

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Never rewrite a packaged checkpoint'
    files=read_json(OUT/'resource-files.json');evidence=read_json(OUT/'source-evidence.json');byfile={(x['project'],x['path']):x for x in evidence};catalog=json.loads((ROOT/'iterations/17-forge-coverage/canonical-masters.json').read_text());art=collections.defaultdict(list)
    for row in catalog['masters']:art[row['semanticId']].append({'assetId':row['assetId'],'source':row['source'],'sha256':row['sha256']})
    # A prefix/name resemblance is never accepted as a completed resource binding.
    families=collections.defaultdict(list)
    for f in files:
        p=f['path'];parts=p.split('/');idx=next((i for i,x in enumerate(parts) if x==f['qualifier']),None);resource_root='/'.join(parts[:idx]) if idx is not None else str(Path(p).parent)
        key=(f['project'],resource_root,f['kind'],f['resourceName'],f['sourceSet']);families[key].append(f)
    glyphs=[]
    for i,(semantic,label,project,path,donor) in enumerate(GLYPHS,1):
        if (project,path) not in byfile:
            candidates=[x for x in evidence if x['project']==project and Path(x['path']).name==Path(path).name];assert len(candidates)==1,(semantic,candidates);path=candidates[0]['path']
        source=byfile[(project,path)];doc=ET.parse(OUT/source['saved']).getroot();assert doc.tag=='vector',semantic
        assert semantic not in art,(semantic,'Existing semantic asset needs reuse review rather than missing claim');assert donor in art
        glyphs.append({'id':f'G-{i:02}','family':semantic,'label':label,'priority':'P1','disposition':'Confirmed dedicated semantic coverage gap in current catalog','evidence':source,'catalogCheck':'No dedicated semantic entry in current472-master catalog; generic nearest donor is not equivalent','donors':art[donor],'required':'Design a dedicated compact/detailed treatment or explicitly approve suitable existing geometry and masks; preserve semantic/state labels and bind to the exact owner','deviceAvailability':'Source present; feature visibility/support on Thor NOT proven'})
    write_json(OUT/'confirmed-glyph-gaps.json',glyphs)
    package_rows=[]
    authored={x['packageId']:x for x in json.loads((ROOT/'iterations/17-forge-coverage/app-targets.json').read_text())['identities'] if x['packageId']}
    for module,project,path,donor in APP_TARGETS:
        source=byfile.get((project,path));assert source,(module,path)
        manifest=ET.parse(OUT/source['saved']).getroot();package=manifest.get('package');assert package,(module,'Package absent')
        categories=sorted({n.get('{http://schemas.android.com/apk/res/android}name') for n in manifest.findall('.//category') if n.get('{http://schemas.android.com/apk/res/android}name') in ['android.intent.category.LAUNCHER','android.intent.category.HOME','android.intent.category.LEANBACK_LAUNCHER']})
        package_rows.append({'module':module,'sourceManifestPackage':package,'project':project,'evidence':source,'disposition':'Authored target exists' if package in authored else 'Exact app/component icon binding absent; existing housing/geometry may be reused','declaredLauncherCategories':categories,'iconScope':'Source declares launcher entry; enablement/merged manifest NOT verified' if 'android.intent.category.LAUNCHER' in categories else 'Component/home role; not automatically a new launcher icon','existingTarget':authored.get(package,{}).get('assetId'),'donors':art[donor],'presence':'Product/module source candidate; not verified installed; conditions and non-launcher components may apply','packageLimit':'Source platform manifest package only; Gradle/dev variants may differ. Effective compiled package not verified.'})
    write_json(OUT/'additional-app-targets.json',package_rows)
    # Retain source declarations, make conditionals, and includes as evidence, not a guessed installed set.
    declarations=[];inherits=[]
    for source in evidence:
        if not source['path'].endswith('.mk'):continue
        lines=(OUT/source['saved']).read_text(encoding='utf8').splitlines();conditions=[];current=None
        for line_no,raw in enumerate(lines,1):
            text=raw.split('#',1)[0].strip()
            if text.startswith(('ifeq','ifneq','ifdef','ifndef')):conditions.append(text)
            elif text=='else' and conditions:conditions[-1]='else of '+conditions[-1]
            elif text.startswith('endif') and conditions:conditions.pop()
            if 'inherit-product' in text or re.match(r'-?include\s',text):inherits.append({'source':source['project']+'/'+source['path'],'line':line_no,'text':text,'conditions':list(conditions)})
            m=re.match(r'PRODUCT_PACKAGES(?:_DEBUG|_ENG)?\s*(?:\+=|:=|=)\s*(.*)',text)
            if m:current=source['project']+'/'+source['path'];payload=m.group(1)
            elif current:payload=text
            else:continue
            for token in payload.rstrip('\\').split():
                if re.fullmatch(r'[A-Za-z0-9_.+-]+',token):declarations.append({'module':token,'source':current,'line':line_no,'conditions':list(conditions),'status':'Literal source declaration; includes/conditions are not a resolved installed-module list'})
            if not text.endswith('\\'):current=None
    write_json(OUT/'product-package-declarations.json',{'declarations':declarations,'inheritanceStatements':inherits,'limits':'Make was not evaluated. Proprietary vendor includes, partner/GMS and user apps remain outside this source audit. Do not infer final image membership from all downloaded config files.'})
    names={x['family']:x for x in glyphs};exact_gap={(x['evidence']['project'],x['evidence']['path']):x['id'] for x in glyphs}
    dispositions=[]
    for (project,resource_root,kind,name,source_set),variants in sorted(families.items()):
        pathset={(project,x['path']) for x in variants};gap=next((exact_gap[x] for x in pathset if x in exact_gap),None)
        tokens=name
        for prefix in ['ic_settings_','ic_statusbar_','ic_qs_','ic_sysbar_','ic_','stat_sys_','sym_','qs_','vd_']:
            if tokens.startswith(prefix):tokens=tokens[len(prefix):];break
        tokens=re.sub(r'_(?:\d+dp|\d+|black|white|dark|light|24|48)$','',tokens)
        candidates=art.get(tokens,[])
        if source_set!='production-candidate':status='Test/sample source; excluded from production gap count'
        elif gap:status='Reviewed semantic artwork gap'
        elif kind in ['layout','values-visual','color']:status='Native layout/token adaptation; new illustration requirement unreviewed'
        elif kind in ['anim','animator','transition']:status='Native state/motion adaptation; no automatic new drawing claim'
        elif candidates:status='Name-based reuse candidate; exact geometry/state/owner binding NOT verified'
        else:status='Unassigned visual source family; requires semantic review; NOT counted as confirmed missing artwork'
        dispositions.append({'project':project,'resourceRoot':resource_root,'kind':kind,'name':name,'sourceSet':source_set,'variants':len(variants),'status':status,'reviewedGapId':gap or '', 'candidateAssetIds':';'.join(x['assetId'] for x in candidates),'examplePath':variants[0]['path'],'sourceUrl':variants[0]['url']})
    write_json(OUT/'resource-family-dispositions.json',dispositions)
    for name,rows in [('resource-files.csv',files),('resource-family-dispositions.csv',dispositions)]:
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
        (OUT/(name+'.gz')).write_bytes(gzip.compress((OUT/name).read_bytes(),mtime=0))
    write_json(OUT/'catalog-audit-input.json',{'source':'iterations/17-forge-coverage/canonical-masters.json','sha256':hashlib.sha256((ROOT/'iterations/17-forge-coverage/canonical-masters.json').read_bytes()).hexdigest(),'masterFiles':472,'semanticIds':sorted(art)})
    summary={'date':'2026-10-26','baseline':'Official2026-10-19 LineageOS24 odin2thor source manifest; intentionally pinned, not latest-build assertion','sourceProjects':len(json.loads((OUT/'source-projects.json').read_text())),'frameworkSections':5,'visualSourceFiles':len(files),'resourceFamilies':len(families),'productionCandidateFiles':sum(x['sourceSet']=='production-candidate' for x in files),'testOrSampleFiles':sum(x['sourceSet']!='production-candidate' for x in files),'hashVerifiedEvidenceFiles':len(evidence),'confirmedSemanticCoverageGaps':len(glyphs),'additionalAppSourceTargets':len(package_rows),'familyDispositionCounts':dict(collections.Counter(x['status'] for x in dispositions)),'allOsAssetsClaim':'NOT ESTABLISHED. Complete inventory for listed sections/projects; filename candidates and unassigned families are not visual approval. Not a complete built-ROM resource/overlay reachability audit.','installedAppInventory':'NOT RUN - device deferred by user','modifiedOsOrDevice':False}
    write_json(OUT/'audit-summary.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
