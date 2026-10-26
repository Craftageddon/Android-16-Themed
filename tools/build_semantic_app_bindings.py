"""Bind reviewed platform components to deliberately chosen Forge identities.

Manifest roles, not project names, decide whether an icon exists. Camelot is
a PDF viewer; Canvas edits images. Resource-only and iconless manifests do not
become invented launcher applications.
"""
from pathlib import Path
import base64,copy,hashlib,io,json,re,xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageChops
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import add,font,resvg_py
from forge_library import ForgedPilot,steel,lights,xml,embed,layer,compose_layers,lighting_descriptor
from build_symbols import geometry as symbols
from forge_completion_geometry import geometry as utilities,circle
from build_forge_coverage_art import native_vector

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit';AN='{http://schemas.android.com/apk/res/android}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
SPECS={
 'AynParts':('AYN settings','Hardware settings and calibration component',symbols('controller'),'Controller metaphor is appropriate for the actual AYN settings owner.'),
 'Launcher3QuickStep':('Trebuchet','Home, recents and taskbar component',symbols('app_drawer'),'App grid denotes the home launcher; quickstep manifest is merged with the base manifest.'),
 'LineageParts':('LineageOS settings','System settings component',symbols('settings'),'Gear denotes native settings; no new launcher category is introduced.'),
 'LineageSetupWizard':('Setup','First-run device setup', [('M4 3 H20 V21 H4 Z M8 12 L11 15 L17 8',False)],'Checklist denotes the actual setup flow, including restore and navigation.'),
 'Updater':('Updater','System update settings',[(circle(12,12,10),False),('M12 4 V15 M7 10 L12 15 L17 10 M6 19 H18',False)],'Download-to-system ring denotes the actual update owner; activation is download state, not installation permission.'),
 'LatinIME':('Keyboard','Input method and keyboard settings', [('M2 5 H22 V20 H2 Z M6 9 H7 M11 9 H12 M16 9 H17 M6 13 H7 M11 13 H12 M16 13 H17 M6 17 H17',False)],'Keyboard is the input-method role confirmed by android.view.InputMethod.'),
 'Jelly':('Jelly','Web browser',[(circle(12,12,10),False),('M2 12 H22 M12 2 Q3 12 12 22 Q21 12 12 2 Z M5 6 Q12 10 19 6 M5 18 Q12 14 19 18',False)],'Globe denotes HTTP/HTML browser intent ownership.'),
 'ExactCalculator':('Calculator','Calculator', [('M4 2 H20 V22 H4 Z M7 5 H17 V9 H7 Z M7 13 H10 M8.5 11.5 V14.5 M14 13 H17 M7 18 H10 M14 17 H17 M14 19 H17',False)],'Arithmetic display is deliberately distinct from generic settings.'),
 'Etar':('Calendar','Calendar event viewer and editor', [('M3 4 H21 V22 H3 Z M3 9 H21 M7 1 V6 M17 1 V6 M7 13 H10 M14 13 H17 M7 18 H10 M14 18 H17',False)],'Calendar follows native event MIME types; platform package retained rather than Gradle development ID.'),
 'Recorder':('Recorder','Sound recorder', [('M8 4 Q8 1 12 1 Q16 1 16 4 V12 Q16 16 12 16 Q8 16 8 12 Z M4 10 V12 Q4 20 12 20 Q20 20 20 12 V10 M12 20 V23 M7 23 H17',False)],'Microphone denotes RECORD_SOUND and SoundRecorderService, not screen recording.'),
 'Twelve':('Twelve','Music player and media library',utilities('music_note'),'Music note matches audio media intents and the media library service.'),
 'Seedvault':('Seedvault','Backup transport and restore component', [('M12 1 L22 5 V12 Q21 20 12 23 Q3 20 2 12 V5 Z M7 9 H17 V17 H7 Z M7 9 L12 6 L17 9 M12 10 V16',False)],'Protected archive denotes backup transport; no launcher entry is invented.'),
 'AudioFX':('AudioFX','Audio effects control panel', [('M4 3 V21 M12 3 V21 M20 3 V21 M1 8 H7 M9 16 H15 M17 6 H23',False)],'Equalizer channels follow DISPLAY_AUDIO_EFFECT_CONTROL_PANEL.'),
 'Camelot':('Camelot','PDF viewer component', [('M5 2 H15 L21 8 V22 H5 Z M15 2 V8 H21 M8 12 H17 M8 16 H17 M8 19 H14',False)],'Document page follows PdfViewerActivity and application/pdf. Earlier folder candidate is rejected.'),
 'Profiles':('System profiles','Profile picker and trust-agent component',[(circle(8,7,3),False),(circle(17,9,2.5),False),('M1 21 V18 Q1 12 8 12 Q15 12 15 18 V21 Z M16 14 Q23 13 23 20 H18',False)],'Multiple people denote profile selection; not a launcher-installed-app assertion.'),
 'Canvas':('Canvas','Image editor component', [('M6 2 V18 H22 M2 6 H18 V22 M9 13 L17 5 L21 9 L13 17 L8 18 Z',False)],'Crop and pen follow EDIT image/jpeg,image/png,image/webp; PDF donor is rejected.'),
 'ThemePicker':('Wallpaper and style','Wallpaper and customization settings', [('M3 3 H21 V21 H3 Z M3 17 L8 11 L12 15 L17 9 L21 13',False),(circle(8,7,1.5),False)],'Image frame follows SET_WALLPAPER and customization activities.'),
}

def main():
    assert not (OUT/'complete-assets.zip').exists();targets=read_json(INPUT/'additional-app-targets.json');declarations=read_json(OUT/'resource-declarations.json');texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode();style=read_json(OUT/'runtime-style.json');bindings=[];components=[]
    for d in ['app-masters','app-exports','android-apps/res/drawable-mdpi','android-apps/res/drawable','android-apps/res/mipmap-anydpi-v33','android-apps/res/values']:(OUT/d).mkdir(parents=True,exist_ok=True)
    strings=E.Element('resources')
    for target in targets:
        module=target['module'];manifest=E.parse(INPUT/target['evidence']['saved']).getroot();application=manifest.find('application');icon=application.get(AN+'icon');round_icon=application.get(AN+'roundIcon');root=target['evidence']['path'].split('AndroidManifest.xml')[0]+'res';key=re.sub('[^a-z0-9_]','_',module.lower());component_roles=[]
        for child in application:
            if child.tag not in ['activity','activity-alias','service','provider']:continue
            component_roles.append({'kind':child.tag,'name':child.get(AN+'name'),'icon':child.get(AN+'icon'),'label':child.get(AN+'label'),'actions':[x.get(AN+'name') for x in child.findall('.//action')],'categories':[x.get(AN+'name') for x in child.findall('.//category')],'mimeTypes':[x.get(AN+'mimeType') for x in child.findall('.//data') if x.get(AN+'mimeType')]})
        label=application.get(AN+'label');label_name=label.split('/')[-1] if label and label.startswith('@string/') else None
        label_evidence=[x for x in declarations if x['project']==target['project'] and x['type']=='string' and x['name']==label_name and x['qualifier'] in ['values','values-en','values-en-rUS']]
        binding={'module':module,'sourcePlatformPackage':manifest.get('package'),'manifest':target['evidence'],'applicationIcon':icon,'roundIcon':round_icon,'sourceLabel':label,'sourceEnglishLabelDeclarations':label_evidence,'components':component_roles,'effectivePackageOrInstalledPresence':'Not established by source manifests; no installed launcher inventory claim','nativeOwnerIntegrated':False}
        if not icon and not round_icon:
            assert not icon and not round_icon,(module,icon,round_icon)
            binding.update({'decision':'No application icon declared; no invented launcher identity','rationale':{'Profiles':'Profile picker and trust-agent components declare no application icon. Bind their actual selection/trust controls in the owner review.','Backgrounds':'Resource-only package supplies wallpaper resources; bind its actual content in the wallpaper review.','AvatarPicker':'Activities supply avatar selection; no application icon declaration. Avatar choices are content, with Forge selection chrome handled separately.','QuickAccessWallet':'Empty plugin application manifest; wallet UI belongs to the SystemUI/plugin owner, using the reviewed wallet control glyph.'}[module],'assetId':None})
            bindings.append(binding);continue
        assert icon,module
        english,role,geometry,rationale=SPECS[module];asset='app-'+key;o=ForgedPilot((asset,english,128,128,''));o.circle(64,64,54);groups={name:add(o.layers[name],'g',transform='translate(37.6 37.6) scale(2.2)') for name in LAYERS}
        for path_data,fill in geometry:steel(groups['cold'],path_data,1.7,fill);lights(groups,path_data,.23)
        doc=o.finish();(OUT/'app-masters'/f'{asset}.svg').write_text(xml(doc),encoding='utf8');images={}
        for name in LAYERS:
            for scale in [1,2]:
                im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(layer(doc,name),texture)),width=128*scale,skip_system_fonts=True))).convert('RGBA');im.save(OUT/'app-exports'/f'{asset}.{name}@{scale}x.png')
                if scale==2:images[name]=im
            fg=layer(copy.deepcopy(doc),name);fg.set('viewBox','-51.2 -51.2 230.4 230.4');fg.set('width','108');fg.set('height','108')
            Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(fg,texture)),width=108,skip_system_fonts=True))).save(OUT/'android-apps/res/drawable-mdpi'/f'cg_app_{key}_{name}.png')
        for state,descriptor in style['sampleStates'].items():compose_layers(images,lighting_descriptor(descriptor,False)).save(OUT/'app-exports'/f'{asset}.{state}.preview.png')
        (OUT/'android-apps/res/drawable'/f'cg_app_{key}_monochrome.xml').write_text(native_vector(geometry,True),encoding='utf8')
        (OUT/'android-apps/res/mipmap-anydpi-v33'/f'cg_app_{key}.xml').write_text('<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/cg_forge_background"/><foreground android:drawable="@drawable/cg_app_'+key+'_cold"/><monochrome android:drawable="@drawable/cg_app_'+key+'_monochrome"/></adaptive-icon>\n',encoding='utf8')
        E.SubElement(strings,'string',name='cg_app_'+key+'_label').text=english
        binding.update({'decision':'Authored Forge application/component identity; reviewed role binding','authoredEnglishLabel':english,'role':role,'rationale':rationale,'assetId':asset,'master':f'app-masters/{asset}.svg','masterSha256':hashlib.sha256((OUT/'app-masters'/f'{asset}.svg').read_bytes()).hexdigest(),'adaptiveResource':'@mipmap/cg_app_'+key,'nativeLayers':{name:'@drawable/cg_app_'+key+'_'+name for name in LAYERS},'stateContract':'Application icon is cold by default. Optional selected/pressed host rendering uses the separate neutral masks. Application existence is not an active/on state. Focus alone stays neutral.','priorCandidateDisposition':'Reviewed metaphor accepted in a newly authored housing; this is not a claim that the old donor file was an exact drop-in.'})
        components.append({'id':asset,'module':module,'label':english,'size':[128,128],'layers':LAYERS,'labelsBaked':False,'nativeIntegrated':False,'deviceVerified':False});bindings.append(binding);print(module,flush=True)
    assert len(bindings)==20 and len(components)==16
    (OUT/'android-apps/res/values/strings.xml').write_bytes(E.tostring(strings,encoding='utf-8',xml_declaration=True));(OUT/'android-apps/res/values/colors.xml').write_text('<resources><color name="cg_forge_background">#0B1015</color></resources>\n',encoding='utf8')
    write_json(OUT/'app-component-bindings.json',bindings);write_json(OUT/'app-components.json',components)
    for start in range(0,len(components),10):
        board=Image.new('RGB',(1800,1070),'#080c11');draw=ImageDraw.Draw(board);draw.text((28,18),'FORGE / REVIEWED PLATFORM APP AND COMPONENT IDENTITIES',font=font(28,True),fill='#eee7d9');draw.text((28,62),'Cold default and selected preview. Component icons do not imply launcher entries or verified installation.',font=font(18),fill='#b5bdc6')
        for i,row in enumerate(components[start:start+10]):
            x=i%5*360;y=115+i//5*460;draw.text((x+18,y),row['label'],font=font(23,True),fill='#eee7d9')
            for col,state in enumerate(['off','on']):
                im=Image.open(OUT/'app-exports'/f"{row['id']}.{state}.preview.png");im.thumbnail((165,165));board.paste(im,(x+12+col*175,y+55),im)
            draw.text((x+18,y+255),row['module'],font=font(16),fill='#b5bdc6');draw.text((x+18,y+285),'Cold              Selected',font=font(17),fill='#b5bdc6')
        board.save(OUT/'previews'/f'app-components-{start//10+1:02}.png')
    print(json.dumps({'reviewedTargets':len(bindings),'authoredIdentities':len(components),'iconlessManifestTargets':4,'productionLayerExports':len(components)*14,'nativeAdaptiveIcons':len(components)}))

if __name__=='__main__':main()
