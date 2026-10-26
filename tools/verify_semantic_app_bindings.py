"""Verify reviewed manifest bindings and real output states, not generated counts alone."""
import hashlib,json,xml.etree.ElementTree as E,zipfile
from PIL import Image,ImageChops
from audit_os_resource_coverage import ROOT,read_json,write_json
from forge_library import compose_layers,lighting_descriptor

OUT=ROOT/'iterations/20-semantic-review';AN='{http://schemas.android.com/apk/res/android}'

def main():
    bindings=read_json(OUT/'app-component-bindings.json');components=read_json(OUT/'app-components.json');style=read_json(OUT/'runtime-style.json');assert len(bindings)==20 and len(components)==16
    assert len({x['module'] for x in bindings})==20
    assert {x['module'] for x in bindings if x['assetId'] is None}=={'Profiles','Backgrounds','AvatarPicker','QuickAccessWallet'}
    for x in bindings:
        manifest=E.parse(ROOT/'iterations/19-os-resource-audit'/x['manifest']['saved']).getroot();assert manifest.get('package')==x['sourcePlatformPackage'];app=manifest.find('application');assert app.get(AN+'icon')==x['applicationIcon']
        if x['assetId'] is None:assert not app.get(AN+'icon') and not app.get(AN+'roundIcon');continue
        assert hashlib.sha256((OUT/x['master']).read_bytes()).hexdigest()==x['masterSha256']
        assert all(ord(c)<128 for c in x['authoredEnglishLabel'])
        assert not E.parse(OUT/x['master']).findall('.//{http://www.w3.org/2000/svg}text')
    cases=exports=0
    for row in components:
        images={}
        for name in row['layers']:
            for scale in [1,2]:
                im=Image.open(OUT/'app-exports'/f"{row['id']}.{name}@{scale}x.png").convert('RGBA');assert im.size==(128*scale,128*scale);exports+=1
                if name!='cold':
                    r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox()
                if scale==2:images[name]=im
            key=row['module'].lower();native=Image.open(OUT/'android-apps/res/drawable-mdpi'/f'cg_app_{key}_{name}.png').convert('RGBA');assert native.size==(108,108)
            box=native.getchannel('A').getbbox()
            if box and name=='cold':assert min(box)>=20 and max(box)<=88,(row['id'],box)
        for state,descriptor in style['sampleStates'].items():
            actual=Image.open(OUT/'app-exports'/f"{row['id']}.{state}.preview.png").convert('RGBA');expected=compose_layers(images,lighting_descriptor(descriptor,False));assert actual.tobytes()==expected.tobytes();cases+=1
            if state=='off':assert actual.tobytes()==images['cold'].tobytes()
    with zipfile.ZipFile(OUT/'verification/evidence/native-app-resources.zip') as z:assert z.testzip() is None;compiled=len(z.namelist());assert compiled==146,compiled
    report={'result':'PASS','sourceManifestBindings':20,'authoredAppIdentities':16,'noInventedApplicationIcons':4,'layerExports':exports,'exactStateRecompositions':cases,'nativeAdaptiveSafeZoneChecks':16,'compiledAndroidResourceEntries':compiled,'nativeRuntimeAcceptance':'NOT RUN','scope':'Manifest/role bindings, authored artwork, export masks and native resource compilation. Not an effective merged manifest, installed application list or live launcher test.'};write_json(OUT/'verification/evidence/app-binding-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
