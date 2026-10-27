'''Gallery art: reviewed reuse, source-geometry treatments and transparent media rims.'''
from pathlib import Path
import base64,copy,hashlib,math,shutil,xml.etree.ElementTree as E
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json
from forge_library import setup,steel,lights,joint,layer,raster,xml
from build_pilot import SVG,add,path,chamfer
from build_scalable_frames import ninepatch
from build_updater_workflow_art import readable_cold
OUT=ROOT/'iterations/26-gallery-workflows'
UP=OUT/'upstream/packages/apps/Glimpse';RES=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res'
A='{http://schemas.android.com/apk/res/android}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
DENSITIES=[('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source_treatment(file):
    node=E.fromstring(file.read_bytes());vw=float(node.get(A+'viewportWidth'));vh=float(node.get(A+'viewportHeight'))
    root,groups=setup(96,96,'Gallery / '+file.stem)
    dest={name:add(g,'g',transform=f'scale({96/vw:g} {96/vh:g})') for name,g in groups.items()}
    source_paths=[];path_roles=[]
    for f in root.iter('{'+SVG+'}filter'):
        if f.get('id') in ['light-spill','light-reflection']:
            for primitive in f:
                if primitive.tag=='{'+SVG+'}feGaussianBlur':
                    primitive.set('stdDeviation',str(float(primitive.get('stdDeviation'))*vw/24))
    for pattern in root.iter('{'+SVG+'}pattern'):
        if pattern.get('id')=='forged':
            for node2 in [pattern,*list(pattern)]:
                for a in ['width','height']:
                    if node2.get(a):node2.set(a,str(float(node2.get(a))*vw/24))
    def visit(n,parents):
        if n.tag=='group':
            px=float(n.get(A+'pivotX',0));py=float(n.get(A+'pivotY',0));tx=float(n.get(A+'translateX',0));ty=float(n.get(A+'translateY',0))
            sx=float(n.get(A+'scaleX',1));sy=float(n.get(A+'scaleY',1));rotation=float(n.get(A+'rotation',0))
            tr=f'translate({tx+px:g} {ty+py:g}) rotate({rotation:g}) scale({sx:g} {sy:g}) translate({-px:g} {-py:g})'
            parents={name:add(g,'g',transform=tr) for name,g in parents.items()}
            for c in n:visit(c,parents)
        elif n.tag=='path':
            d=n.get(A+'pathData');assert d
            source_paths.append(d)
            def alpha(color):
                if color in [None,'@android:color/transparent']:return 0.
                if color.startswith('#') and len(color)==9:return int(color[1:3],16)/255
                if color.startswith('#') and len(color)==5:return int(color[1],16)/15
                assert color in ['@android:color/white','@android:color/black'] or (color.startswith('#') and len(color) in [4,7]), (file,color)
                return 1.
            fill=alpha(n.get(A+'fillColor'))*float(n.get(A+'fillAlpha',1))
            stroke_opacity=alpha(n.get(A+'strokeColor'))*float(n.get(A+'strokeAlpha',1))
            stroke=stroke_opacity if float(n.get(A+'strokeWidth',0))>0 else 0.
            visible=fill>0 or stroke>0
            path_roles.append({'pathData':d,'fillOpacity':fill,'strokeOpacity':stroke,'strokeWidth':float(n.get(A+'strokeWidth',0)),'visibleSourcePath':visible})
            if not visible:return
            assert float(n.get(A+'trimPathStart',0))==0 and float(n.get(A+'trimPathEnd',1))==1 and float(n.get(A+'trimPathOffset',0))==0
            width=vw/24*.65 if fill>0 else max(vw/24*.65,float(n.get(A+'strokeWidth',0)))
            local={name:add(g,'g',opacity=max(fill,stroke)) for name,g in parents.items()}
            steel(local['cold'],d,width,fill>0);lights(local,d,vw/24*.20)
            if n.get(A+'fillType')=='evenOdd':
                for g in local.values():
                    for p in list(g):
                        if p.tag=='{'+SVG+'}path' and p.get('d')==d:p.set('fill-rule','evenodd')
        else:raise AssertionError((file,n.tag))
    for n in node:visit(n,dest)
    return readable_cold(root),{'xml':file.relative_to(OUT).as_posix(),'sha256':sha(file),'nativeViewport':[vw,vh],'pathData':source_paths,'sourcePathRoles':path_roles,'autoMirrored':node.get(A+'autoMirrored')=='true'}
def media_frame():
    root,g=setup(96,96,'Gallery transparent media rim')
    outer=chamfer(2,2,92,92,6);inner=chamfer(6,6,84,84,3)
    path(g['cold'],outer+' '+inner,'url(#steel)',fill_rule='evenodd')
    path(g['cold'],outer,stroke='url(#edge)',width=1.2)
    path(g['cold'],inner,stroke='#2b353f',width=.6)
    # Corner detail is outside the protected transparent center.
    for x,y in [(5,5),(91,5),(5,91),(91,91)]:joint(g['cold'],x,y,2)
    rail=chamfer(4,4,88,88,4);lights(g,rail,.65)
    path(g['focus'],chamfer(1,1,94,94,7),stroke='white',width=1)
    return readable_cold(root)
def main():
    assert not (OUT/'complete-assets.zip').exists()
    (OUT/'masters').mkdir(exist_ok=True);(OUT/'source').mkdir(exist_ok=True)
    texture=ROOT/'iterations/11-forge-symbol-library/source/steel-material.png';shutil.copy2(texture,OUT/'source/steel-material.png');texture_data=base64.b64encode(texture.read_bytes()).decode()
    rows=[];bindings=[]
    def export(key,root,logical,origin,kind='source-geometry',stretch=False):
        p=OUT/'masters'/(key+'.svg');p.write_text(xml(root),encoding='utf8');files=[]
        for density,scale in DENSITIES:
            for name in LAYERS:
                im=raster(layer(root,name),round(logical*scale),texture_data)
                if stretch:
                    assert im.width==im.height
                    cap=round(12*scale);w=im.width
                    im=ninepatch(im,[cap,w-cap,cap,w-cap],[0,0,0,0])
                dest=RES/f'drawable-{density}'/(key+'_'+name+('.9.png' if stretch else '.png'));dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
                files.append({'path':dest.relative_to(OUT).as_posix(),'layer':name,'density':density,'size':list(im.size),'sha256':sha(dest)})
        row={'id':key,'logicalSize':logical,'master':p.relative_to(OUT).as_posix(),'masterSha256':sha(p),'kind':kind,'source':origin,'files':files,'labelsBaked':False,'glowBakedInCold':False};rows.append(row);return row
    ledger=read_json(ROOT/'iterations/25-updater-workflows/semantic-family-ledger.json')
    families={r['baselineFamily']['name']:r for r in ledger if r['baselineFamily']['project']=='packages/apps/Glimpse'}
    def reuse_root(original):
        assert original.exists()
        dest=OUT/'masters/original-donors/masters'/original.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,dest)
        root=E.fromstring(original.read_bytes())
        for n in root.iter('{'+SVG+'}image'):
            href=n.get('href');assert href=='../source/steel-material.png',(original,href)
            td=dest.parent/href;td.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original.parent/href,td)
        return readable_cold(E.fromstring(original.read_bytes())),{'original':original.relative_to(ROOT).as_posix(),'sha256':sha(original),'geometryAndMasksChanged':False,'coldOpticalMaterial':'brighter edge / 14 percent texture coat'}
    for file in sorted((UP/'app/src/main/res/drawable').glob('ic_*.xml')):
        if file.stem.startswith('ic_launcher') or file.stem=='ic_star_toggle':continue
        node=E.fromstring(file.read_bytes());assert node.tag=='vector',file
        record=families[file.stem];key='cg_gl_'+file.stem[3:]
        if record.get('reuseDecision'):
            chosen=next(r for r in record['reuseDecision']['chosenAssets'] if r['assetId'].endswith('__detailed'))
            original=ROOT/chosen['path'];assert sha(original)==chosen['sha256']
            root,origin=reuse_root(original);kind='reviewed-donor-optical'
        elif file.stem in ['ic_star','ic_star_border']:
            original=ROOT/'iterations/20-semantic-review/masters'/('favorite__detailed.svg' if file.stem=='ic_star' else 'favorite_outline__detailed.svg')
            root,origin=reuse_root(original);kind='reviewed-favorite-gap-optical'
        else:root,origin=source_treatment(file);kind='source-geometry'
        export(key,root,24,origin,kind)
        mode=1 if file.stem in ['ic_star','ic_check_circle'] else 2 if file.stem in ['ic_star_border','ic_check_circle_outline'] else 0
        bindings.append({'resource':file.stem,'qualifier':'drawable','family':key,'mode':mode,'autoMirrored':node.get(A+'autoMirrored')=='true','source':file.relative_to(OUT).as_posix(),'familyId':record['familyId']})
    media=OUT/'source/media3-ui/original-resources/res'
    values=E.parse(media/'values/values.xml').getroot()
    alias={e.get('name'):e.text.removeprefix('@drawable/') for e in values if e.tag=='drawable' and e.get('name','').startswith('exo_styled_controls_')}
    targets=sorted(set(alias.values())-{'exo_icon_vr'})
    for name in targets:
        file=media/'drawable-anydpi-v21'/(name+'.xml');assert file.exists(),name
        root,origin=source_treatment(file);key='cg_gl_'+name.removeprefix('exo_')
        export(key,root,24,origin,'media3-source-geometry')
        mode=2 if name in ['exo_icon_repeat_off','exo_icon_shuffle_off','exo_ic_subtitle_off','exo_ic_fullscreen_enter'] else 1 if name in ['exo_icon_repeat_one','exo_icon_repeat_all','exo_icon_shuffle_on','exo_ic_subtitle_on','exo_ic_fullscreen_exit','exo_ic_check'] else 0
        node=E.parse(file).getroot()
        bindings.append({'resource':name,'qualifier':'drawable-anydpi-v21','family':key,'mode':mode,'autoMirrored':node.get(A+'autoMirrored')=='true','source':file.relative_to(OUT).as_posix(),'library':'media3-ui1.10.0','sourceAliases':[k for k,v in alias.items() if v==name]})
    export('cg_gl_media_frame',media_frame(),96,{'role':'New transparent-center decoration; original photo load/clip/blur/scale owners remain native'},'new-transparent-frame',True)
    # Reuse exact native frame/control resources; keep source identities separate from new art.
    reuse=[('cg_gl_panel','cg_rf_panel'),('cg_gl_button','cg_rf_button'),('cg_gl_field','cg_rf_field'),('cg_gl_rail','cg_upd_rail'),('cg_gl_switch_track','cg_upd_switch_track'),('cg_gl_switch_thumb','cg_upd_switch_thumb'),('cg_gl_seek_thumb','cg_upd_switch_thumb')]
    reused=[]
    for target,source in reuse:
        for density,scale in DENSITIES:
            for name in LAYERS:
                directory=ROOT/'iterations/25-updater-workflows/native-patch/packages/apps/Updater/app/src/main/res'/('drawable-'+density)
                candidates=list(directory.glob(source+'_'+name+'.*'));assert len(candidates)==1
                src=candidates[0];p=RES/('drawable-'+density)/src.name.replace(source,target);p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p)
                reused.append({'source':src.relative_to(ROOT).as_posix(),'target':p.relative_to(OUT).as_posix(),'sha256':sha(src)})
    # Actual adaptive application identity: existing reviewed Gallery master, cold only.
    prior=next(r for r in read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters'] if r['semanticId']=='app-gallery')
    original=ROOT/prior['source'];assert sha(original)==prior['sha256'];reuse_root(original)
    photo=UP/'app/src/main/res/drawable/ic_image.xml'
    glyph,source=source_treatment(photo);root,g=setup(128,128,'Gallery native application identity')
    circle='M 8 64 A 56 56 0 1 0 120 64 A 56 56 0 1 0 8 64'
    steel(g['cold'],circle,3);lights(g,circle,.7)
    for x,y in [(64,7),(121,64),(64,121),(7,64)]:joint(g['cold'],x,y,4)
    for name,target in g.items():
        group=add(target,'g',transform='translate(28 28) scale(.75)')
        for n in list(glyph.find('{'+SVG+'}g[@id="'+name+'"]')):group.append(copy.deepcopy(n))
    root=readable_cold(root)
    export('cg_gl_app_gallery',root,128,{'actualSourceGeometry':source,'priorSemanticDonor':prior,'newRoundNativeHousing':True},'new-application-identity')
    write_json(OUT/'source/discovered-gallery-component.json',{'module':'Glimpse','sourcePlatformPackage':'org.lineageos.glimpse','manifest':'upstream/packages/apps/Glimpse/app/src/main/AndroidManifest.xml','revision':'89b473594ec8ad01417624e670912450ce5df7e9','applicationIcon':'@mipmap/ic_launcher','sourceLabel':'@string/app_name','prior20BindingAbsent':True,'earlierSemanticDonor':prior,'newNativeIdentityMaster':'masters/cg_gl_app_gallery.svg','manifestEntryInvented':False,'installedPackageFacts':'NOT RUN'})
    bindings.append({'resource':'cg_gl_media_frame','qualifier':'drawable','family':'cg_gl_media_frame','mode':0,'autoMirrored':False,'role':'actual thumbnail/album foreground'})
    for target,_ in reuse:bindings.append({'resource':target,'qualifier':'drawable','family':target,'mode':0,'autoMirrored':False,'role':'scoped native material/control'})
    for r in bindings:
        p=RES/r['qualifier']/(r['resource']+'.xml');p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<!-- Craftageddon: source-owned layered material; actual value and interaction remain distinct. -->\n<drawable xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" class="org.lineageos.glimpse.forge.ForgeDrawable" app:cg_forge_family="'+r['family']+'" app:cg_forge_source_value_mode="'+['dynamic','true_value','false_value'][r['mode']]+'" android:autoMirrored="'+str(r['autoMirrored']).lower()+'"/>\n',encoding='utf8')
    (RES/'values').mkdir(exist_ok=True)
    (RES/'values/cg_gallery_attrs.xml').write_text('''<resources><declare-styleable name="ForgeDrawable">
 <attr name="cg_forge_family" format="string"/>
 <attr name="cg_forge_source_value_mode"><enum name="dynamic" value="0"/><enum name="true_value" value="1"/><enum name="false_value" value="2"/></attr>
 <attr name="cg_forge_momentary" format="boolean"/>
</declare-styleable></resources>
''',encoding='utf8')
    write_json(OUT/'gallery-art-components.json',rows);write_json(OUT/'gallery-resource-bindings.json',bindings);write_json(OUT/'exact-native-control-reuse.json',reused)
    print({'artTreatments':len(rows),'sourceLeafBindings':len(bindings),'newPngConfigs':sum(len(r['files']) for r in rows),'exactReusedPngConfigs':len(reused),'productionGlowsBaked':False,'nativeExecution':False})
if __name__=='__main__':main()
