"""Source-backed visual fixtures, never represented as screenshots from Android/Thor."""
from pathlib import Path
import base64,copy,io,json,math,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font,resvg_py
from build_scalable_frames import stretch
from forge_library import COLORS

OUT=ROOT/'iterations/21-native-workflows';PACKAGE=OUT/'native-patch/hardware/ayn/packages/AynParts';LAYERS=['cold','reflection','spill','seam','core','focus','symbol'];NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)

def el(parent,tag,**attrs):return E.SubElement(parent,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})

class Scene:
    def __init__(self,key,title):
        self.key=key;self.root=E.Element('{'+NS+'}svg',{'width':'960','height':'580','viewBox':'0 0 960 580'});el(self.root,'title').text=title;el(self.root,'desc').text='Source-backed desktop visual fixture. Native callbacks and values are mapped in the adjacent JSON. This is not an Android screenshot, device measurement or runtime acceptance.';el(self.root,'rect',width=960,height=580,fill='#080c11');self.defs=el(self.root,'defs');self.seq=0;self.texts=[];self.controls=[]
        self.text(24,564,'Source-backed visual fixture / sample values / not a device screenshot',14,'#8f9ba7')
    def text(self,x,y,text,size=18,color='#eee7d9',anchor='start'):
        node=el(self.root,'text',x=x,y=y,font_size=size,font_family='Segoe UI',fill=color,text_anchor=anchor);node.text=text;self.texts.append({'text':text,'position':[x,y],'size':size,'anchor':anchor})
    def paragraph(self,text,y,width=820,size=17):
        for paragraph in text.replace('\\n','\n').split('\n'):
            line=''
            for word in paragraph.split():
                candidate=(line+' '+word).strip()
                if font(size).getlength(candidate)>width and line:self.text(480,y,line,size,anchor='middle');y+=size+7;line=word
                else:line=candidate
            if line:self.text(480,y,line,size,anchor='middle');y+=size+7
            else:y+=size//2
        return y
    def place(self,family,x,y,w,h,state='off',strength=1):
        style=read_json(OUT/'runtime-style.json')['sampleStates'][state];self.seq+=1
        for name in LAYERS:
            if family.startswith('cg_rf_'):
                source=Image.open(PACKAGE/'res/drawable-mdpi'/f'{family}_{name}.9.png').convert('RGBA');image=stretch(source,(round(w),round(h)))
            else:image=Image.open(PACKAGE/'res/drawable-mdpi'/f'{family}_{name}.png').convert('RGBA')
            buffer=io.BytesIO();image.save(buffer,format='PNG');gain=style['baseOpacity'] if name=='cold' else style['gains'][name]*(1 if name=='focus' else strength)
            if gain==0:continue
            g=el(self.root,'g',opacity=gain,data_forge_layer=name)
            if name!='cold':
                fid=f'tint-{self.seq}-{name}';f=el(self.defs,'filter',id=fid,color_interpolation_filters='sRGB');el(f,'feFlood',flood_color=COLORS[name]);el(f,'feComposite',in2='SourceGraphic',operator='in');g.set('filter','url(#'+fid+')')
            el(g,'image',x=x,y=y,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode())
        self.controls.append({'family':family,'bounds':[x,y,w,h],'state':state,'emissionStrength':strength})
    def button(self,label,x,y,enabled=True,outlined=False,pressed=False):
        w=max(112 if outlined else 96,math.ceil(font(16).getlength(label))+48);self.place('cg_rf_field' if outlined else 'cg_rf_button',x,y,w,56,'disabled' if not enabled else 'active_pressed' if pressed else 'off');self.text(x+w/2,y+34,label,16,'#eee7d9' if enabled else '#8f9ba7',anchor='middle');return w
    def stick(self,x,y,vx,vy,label):
        magnitude=math.hypot(vx,vy);strength=min(1,magnitude);state='on' if magnitude else 'off';self.place('cg_ayn_gate',x,y,120,120,state,strength);el(self.root,'path',d=f'M{x+4} {y+60} H{x+116} M{x+60} {y+4} V{y+116}',fill='none',stroke='#627482',stroke_width=1);scale=1/magnitude if magnitude>1 else 1;dx=x+60+vx*scale*48;dy=y+60+vy*scale*48;self.place('cg_ayn_dot',dx-10,dy-10,20,20,state,strength);self.controls[-1].update(actualInput=[vx,vy],sourceDotCenter=[dx,dy],nativeDotRadius=8,accessibleLabel=label)
        assert math.hypot(dx-x-60,dy-y-60)<=48.000001
    def save(self,metadata):
        folder=OUT/'workflow-previews';folder.mkdir(exist_ok=True);source=E.tostring(self.root,encoding='unicode');(folder/(self.key+'.svg')).write_text(source,encoding='utf8');(folder/(self.key+'.png')).write_bytes(resvg_py.svg_to_bytes(svg_string=source,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'));return {'id':self.key,'fixtureOnly':True,'logicalViewport':[960,540],'deviceScreenshot':False,'sourceMapping':metadata,'text':self.texts,'controls':self.controls}

def main():
    assert not (OUT/'complete-assets.zip').exists();strings={x.get('name'):''.join(x.itertext()) for x in E.parse(PACKAGE/'res/values/strings.xml').getroot()};cases=[('intro','Intro',False,[]),('center-no-sample','Center',False,None),('center-collecting','Center',False,[(.035,-.02),(-.025,.01)]),('center-ready','Center',True,[(0,0),(0,0)]),('range-left','RangeLeft',False,[(1,1)]),('range-right','RangeRight',True,[(.6,-.8)]),('deadzone-left','DeadzoneLeft',False,[(.05,-.03)]),('deadzone-right','DeadzoneRight',True,[(0,0)]),('test-calibration','Test',True,[(.04,-.02),(-.035,.025),(0,0),(0,0)])];rows=[]
    phase_keys={'Center':'center','RangeLeft':'range_left','RangeRight':'range_right','DeadzoneLeft':'deadzone_left','DeadzoneRight':'deadzone_right'}
    for key,phase,ready,points in cases:
        scene=Scene('calibration-'+key,'Joystick calibration / '+phase)
        if phase=='Intro':
            scene.text(480,66,strings['calibration_title'],28,anchor='middle');end=scene.paragraph(strings['calibration_intro_description'],114);scene.button(strings['calibration_start'],432,end+24);scene.button(strings['calibration_cancel'],424,end+92,outlined=True)
        elif phase=='Test':
            scene.text(480,54,strings['calibration_test_title'],28,anchor='middle');scene.paragraph(strings['calibration_test_desc'],86);scene.text(480,130,strings['calibration_test_before'],17,anchor='middle');scene.stick(348,145,*points[0],'Left stick');scene.stick(492,145,*points[1],'Right stick');scene.text(480,300,strings['calibration_test_after'],17,anchor='middle');scene.stick(348,315,*points[2],'Left stick');scene.stick(492,315,*points[3],'Right stick');scene.button(strings['calibration_retry'],692,460,outlined=True);scene.button(strings['calibration_accept'],816,460)
        else:
            pk=phase_keys[phase];scene.text(480,66,strings['calibration_phase_'+pk+'_title'],28,anchor='middle');scene.paragraph(strings['calibration_phase_'+pk+'_desc'],110)
            if points is not None:
                for i,(vx,vy) in enumerate(points):scene.stick(348+i*144 if len(points)==2 else 420,205,vx,vy,'Left stick' if phase in ['RangeLeft','DeadzoneLeft'] or phase=='Center' and i==0 else 'Right stick')
            scene.button(strings['calibration_next'],432,380,enabled=ready)
        rows.append(scene.save({'group':'W-01','phase':phase,'readyToAdvance':ready,'samplePresent':points is not None,'pointInputs':points,'owner':'CalibrationScreen -> PhaseIntroScreen / CalibrationPhaseScreen / TestScreen -> StickVisualizer','actualPhaseAndHardwareOwnersUnmodified':True}))
    for key,dragged,values in [('idle',None,[255,255,255,255]),('green-dragged',1,[255,95,20,170])]:
        scene=Scene('rgb-'+key,'RGB lighting');scene.place('cg_rf_panel',200,24,560,500);scene.text(236,66,strings['gamepad_lights_rgb_lighting_title'],25)
        for i,(label,color,value) in enumerate(zip(['Red','Green','Blue','Brightness'],['#ff3b30','#34c759','#007aff','#ffffff'],values)):
            y=102+i*86;scene.text(236,y,label,18);left=254;right=706;cy=y+30;position=left+(right-left)*value/255;el(scene.root,'rect',x=left,y=cy-12,width=right-left,height=24,rx=12,fill='#29343f');el(scene.root,'rect',x=left,y=cy-12,width=max(.1,position-left),height=24,rx=12,fill=color)
            if dragged==i:el(scene.root,'circle',cx=position,cy=cy,r=24,fill='#d5e7f2',opacity=.20)
            scene.place('cg_ayn_rgb_thumb',position-18,cy-18,36,36,'active_pressed' if dragged==i else 'off');el(scene.root,'circle',cx=position,cy=cy,r=4,fill=color)
            if dragged==i:scene.text(position,cy-32,str(value),16,anchor='middle')
        scene.button('Cancel',520,456);scene.button('OK',632,456);rows.append(scene.save({'group':'W-02','owner':'RGBPreference -> actual dialog_rgb_sliders IDs','channels':values,'sourceSteps':[5,5,5,17],'draggedChannelIndex':dragged,'liveApplyConfirmCancelBodiesUnmodified':True,'trackAndFlatSwatchColorsRemainData':True}))
    write_json(OUT/'workflow-visual-fixtures.json',rows)
    for start in range(0,len(rows),6):
        board=Image.new('RGB',(1920,1280),'#080c11');draw=ImageDraw.Draw(board);draw.text((24,14),'FORGE / SOURCE-BOUND AYN WORKFLOW FIXTURES',font=font(30,True),fill='#eee7d9');draw.text((24,59),'Actual phase/value roles. Desktop fixtures, not Android screenshots or connected-controller evidence.',font=font(19),fill='#b5bdc6')
        for i,row in enumerate(rows[start:start+6]):
            x=i%2*960;y=100+i//2*390;draw.text((x+18,y),row['id'].replace('-',' ').title(),font=font(20),fill='#eee7d9');image=Image.open(OUT/'workflow-previews'/(row['id']+'.png'));image.thumbnail((900,345));board.paste(image,(x+25,y+36))
        board.save(OUT/'previews'/f'ayn-workflows-{start//6+1:02}.png')
    print(json.dumps({'sourceBackedWorkflowFixtures':len(rows),'nativeCalibrationPhasesRepresented':7,'rgbCases':2,'androidRuntimeScreenshots':0}))

if __name__=='__main__':main()
