'''Layered updater illustrations and source-backed glyph/icon exports.'''
from pathlib import Path
import base64,copy,hashlib,json,math,shutil,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import SVG,INK,add,path,poly
from forge_library import setup,steel,lights,joint,layer,raster,xml
OUT=ROOT/'iterations/25-updater-workflows'
RES=OUT/'native-patch/packages/apps/Updater/app/src/main/res'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
DENSITIES=[('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3)]
def circle(cx,cy,r):return f'M {cx-r} {cy} A {r} {r} 0 1 0 {cx+r} {cy} A {r} {r} 0 1 0 {cx-r} {cy}'
def make(kind):
    r,g=setup(160,160,'Updater '+kind)
    outer=[]
    for i in range(48):
        angle=-math.pi/2+i*math.tau/48;radius=73 if i%6 in [0,1] else 68
        outer.append((80+math.cos(angle)*radius,80+math.sin(angle)*radius))
    steel(g['cold'],poly(outer),4,True)
    add(g['cold'],'circle',cx=80,cy=80,r=57,fill='#10151b',stroke='#020509',stroke_width=3)
    steel(g['cold'],circle(80,80,61),3)
    steel(g['cold'],circle(80,80,50),3)
    lights(g,circle(80,80,60),1.4)
    for x,y in [(80,13),(147,80),(80,147),(13,80)]:joint(g['cold'],x,y,6)
    if kind=='scan':
        d='M 80 47 V 105 M 61 66 L 80 47 L 99 66 M 55 111 H 105'
        steel(g['cold'],d,8);lights(g,d,1.1)
        motion=add(r,'g',id='motion');motion.set('{'+INK+'}groupmode','layer');motion.set('{'+INK+'}label','motion neutral mask');motion.set('style','display:none')
        path(motion,'M 80 20 A 60 60 0 0 1 132 50',stroke='white',width=2.2)
        add(motion,'circle',cx=132,cy=50,r=2.5,fill='white')
    elif kind=='error':
        steel(g['cold'],'M 80 45 V 88',11)
        steel(g['cold'],circle(80,106,5),6,True)
        lights(g,'M 80 46 V 87',1.3)
        lights(g,circle(80,106,4),1.2)
    else:
        steel(g['cold'],'M 50 80 L 72 102 L 112 59',9)
        # Ready is a steady cold status; the separate layers exist but are not activated.
        lights(g,'M 50 80 L 72 102 L 112 59',1.2)
    return r


def mini(kind):
    r,g=setup(96,96,'Updater '+kind+' glyph')
    shapes={
        'local':['M 24 39 H 72 V 76 H 24 Z','M 19 27 H 77 V 40 H 19 Z','M 39 48 H 57 V 56 H 39 Z'],
        'remote':['M 24 61 C 8 59 10 39 26 36 C 27 15 59 14 65 34 C 84 30 92 55 76 62 H 67','M 49 42 V 78 M 36 65 L 49 78 L 62 65'],
        'expand':['M 25 37 L 48 62 L 72 37'],
        'collapse':['M 25 61 L 48 36 L 72 61'],
        'more':[circle(48,24,4),circle(48,48,4),circle(48,72,4)],
    }[kind]
    for d in shapes:
        steel(g['cold'],d,7,kind in ['local','more'])
        lights(g,d,1.2)
    return r


def readable_cold(root):
    # Material-only derivative: geometry and all neutral light masks are retained.
    edge=root.find(f".//{{{SVG}}}linearGradient[@id='edge']")
    if edge is not None:
        stops=['#c9d0d6','#71808f','#273340','#84929f','#35414c']
        for node,color in zip(list(edge),stops):node.set('stop-color',color)
    cold=root.find(f"{{{SVG}}}g[@id='cold']")
    if cold is not None:
        for node in cold.iter():
            if node.get('fill')=='url(#forged)':node.set('fill','none')
            if node.get('stroke')=='url(#forged)':node.set('opacity','.14')
    return root

def main():
    assert not (OUT/'complete-assets.zip').exists()
    (OUT/'masters').mkdir(exist_ok=True);(OUT/'source').mkdir(exist_ok=True)
    texture=ROOT/'iterations/11-forge-symbol-library/source/steel-material.png'
    assert texture.exists()
    shutil.copy2(texture,OUT/'source/steel-material.png')
    texture_data=base64.b64encode(texture.read_bytes()).decode()
    rows=[]
    def export(key,root,logical,origin,new_art,tex=texture_data):
        files=[]
        for density,scale in DENSITIES:
            for name in LAYERS+(['motion'] if key=='cg_upd_scan' else []):
                im=raster(layer(root,name),round(logical*scale),tex)
                file=RES/f'drawable-{density}'/(key+'_'+name+'.png')
                file.parent.mkdir(parents=True,exist_ok=True);im.save(file)
                files.append({'path':file.relative_to(OUT).as_posix(),'layer':name,'density':density,
                              'size':list(im.size),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        rows.append({'id':key,'logicalSize':logical,'source':origin,'newArtwork':new_art,'files':files,
                     'labelsBaked':False,'emissionLockedOff':key=='cg_upd_ready'})
    for kind in ['scan','error','ready']:
        root=readable_cold(make(kind));p=OUT/'masters'/('update_'+kind+'.svg');p.write_text(xml(root),encoding='utf8')
        export('cg_upd_'+kind,root,160 if kind!='ready' else 96,p.relative_to(OUT).as_posix(),True)
    for kind in ['local','remote','expand','collapse','more']:
        root=readable_cold(mini(kind));p=OUT/'masters'/('glyph_'+kind+'.svg');p.write_text(xml(root),encoding='utf8')
        export('cg_upd_'+kind,root,32,p.relative_to(OUT).as_posix(),True)
    canonical=read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    for key,name in [('cg_upd_pause','pause'),('cg_upd_resume','play')]:
        src=next(r for r in canonical if r['semanticId']==name and r['optical']=='detailed')
        p=ROOT/src['source'];assert hashlib.sha256(p.read_bytes()).hexdigest()==src['sha256']
        dest=OUT/'masters/reused-symbols/masters'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        td=OUT/'masters/reused-symbols/source/steel-material.png';td.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(texture,td)
        variant=readable_cold(E.fromstring(p.read_bytes()))
        vp=OUT/'masters'/('optical_'+name+'_32.svg');vp.write_text(xml(variant),encoding='utf8')
        export(key,variant,32,{'original':src,'materialDerivative':'brighter cold edge / 14 percent texture coat','geometryAndMasksChanged':False},False)
    binding=next(x for x in read_json(ROOT/'iterations/20-semantic-review/app-component-bindings.json') if x['sourcePlatformPackage']=='org.lineageos.updater')
    p=ROOT/'iterations/20-semantic-review'/binding['master'];assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['masterSha256']
    dest=OUT/'masters/reused-app/masters'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    apptex=ROOT/'iterations/20-semantic-review/source/steel-material.png'
    if not apptex.exists():apptex=texture
    td=OUT/'masters/reused-app/source/steel-material.png';td.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(apptex,td)
    variant=readable_cold(E.fromstring(p.read_bytes()))
    vp=OUT/'masters/optical_app_updater.svg';vp.write_text(xml(variant),encoding='utf8')
    export('cg_upd_badge',variant,128,{'original':binding,'materialDerivative':'brighter cold edge / 14 percent texture coat','geometryAndMasksChanged':False},False,base64.b64encode(apptex.read_bytes()).decode())
    mono=ROOT/'iterations/20-semantic-review/android-apps/res/drawable/cg_app_updater_monochrome.xml'
    dest=RES/'drawable/cg_upd_badge_monochrome.xml';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(mono,dest)
    (RES/'values/cg_updater_icon.xml').write_text('<?xml version="1.0" encoding="utf-8"?><resources><color name="cg_upd_icon_background">#080c11</color></resources>\n',encoding='utf8')
    (RES/'mipmap-anydpi').mkdir(exist_ok=True)
    (RES/'mipmap-anydpi/ic_launcher.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<!-- Craftageddon: actual application icon owner; source notification vectors are preserved. -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
 <background android:drawable="@color/cg_upd_icon_background"/>
 <foreground android:drawable="@drawable/cg_upd_badge_launcher"/>
 <monochrome android:drawable="@drawable/cg_upd_badge_monochrome"/>
</adaptive-icon>
''',encoding='utf8')
    (RES/'drawable/cg_upd_badge_launcher.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<!-- 18% inset keeps the entire cold badge inside the 66/108 adaptive safe circle. -->
<inset xmlns:android="http://schemas.android.com/apk/res/android"
 android:drawable="@drawable/cg_upd_badge_cold" android:inset="18%"/>
''',encoding='utf8')
    write_json(OUT/'workflow-art-components.json',rows)
    write_json(OUT/'source/app-icon-owner-binding.json',{'actualManifest':binding['manifest'],'sourceLabel':binding['sourceLabel'],
        'manifestIconIdentifierRetained':'@mipmap/ic_launcher','coldByDefault':True,'monochromeSource':str(mono.relative_to(ROOT)),
        'originalNotificationVectorsUntouched':True,'effectiveInstalledSelection':'NOT RUN'})
    print({'newIllustrationMasters':3,'newMiniGlyphMasters':5,'existingSourceGlyphOrAppMasters':3,
           'newDensityExports':sum(len(r['files']) for r in rows),'productionGlowsBaked':False,'nativeExecution':False})
if __name__=='__main__':main()
