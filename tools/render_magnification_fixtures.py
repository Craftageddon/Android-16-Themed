"""Source-backed English fixtures, not Android screenshots or device metrics."""
from pathlib import Path
import base64, copy, hashlib, io, json, math, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from audit_os_resource_coverage import ROOT, read_json, write_json
from build_pilot import add, font, resvg_py
from forge_library import setup, xml, embed, layer
from build_scalable_frames import stretch

OUT=ROOT/'iterations/23-magnification'
NATIVE=OUT/'native-patch/frameworks/base/packages/SystemUI'
SVG='{http://www.w3.org/2000/svg}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']


class Fixtures:
    def __init__(self):
        declarations=read_json(ROOT/'iterations/22-native-contract-review/resource-declarations.json')
        self.values={d['name']:d for d in declarations if d['project']=='frameworks/base' and d['resourceRoot']=='packages/SystemUI/res' and d['qualifier']=='values'}
        self.style=read_json(OUT/'runtime-style.json');self.texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode()
        self.serial=0;self.cases=[];self.border_records=[]

    def value(self,name):return self.values[name]['value']
    def dim(self,name):return float(self.value(name).replace('dp','').replace('sp',''))
    def text(self,parent,x,y,label,size=18,color='#eee7d9',weight='normal'):
        add(parent,'text',x=x,y=y,font_family='Segoe UI',font_size=size,fill=color,font_weight=weight).text=label

    def asset(self,parent,key,x,y,w,h,state='off'):
        descriptor=self.style['sampleStates'][state]
        group=add(parent,'g',transform=f'translate({x} {y})')
        for name in LAYERS:
            gain=descriptor['baseOpacity'] if name=='cold' else descriptor['gains'][name]
            if not gain:continue
            base=NATIVE/'res/drawable-mdpi'/('cg_mag_'+key+'_'+name)
            p=base.with_name(base.name+'.9.png');nine=p.exists()
            if not nine:p=base.with_name(base.name+'.png')
            image=Image.open(p).convert('RGBA');image=stretch(image,(round(w),round(h))) if nine else image.resize((round(w),round(h)),Image.Resampling.LANCZOS)
            stream=io.BytesIO();image.save(stream,format='PNG');attrs={}
            if name!='cold':
                self.serial+=1;fid='tint-'+str(self.serial);defs=add(group,'defs');f=add(defs,'filter',id=fid,x=0,y=0,width='100%',height='100%',color_interpolation_filters='sRGB')
                add(f,'feFlood',flood_color=self.style['colors'][name],flood_opacity=gain)
                add(f,'feComposite',in2='SourceAlpha',operator='in');attrs['filter']='url(#'+fid+')'
            else:attrs['opacity']=gain
            add(group,'image',x=0,y=0,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode(),**attrs)

    def wrapped(self,label,size,width):
        metric=font(round(size));lines=[];line=''
        for word in label.split():
            if line and metric.getlength(line+' '+word)>width:lines.append(line);line=''
            # Android's text view can break a long word as well; preserve every
            # character instead of silently accepting a desktop overflow.
            for char in word:
                if metric.getlength((line+' ' if line and line[-1]!=' ' else line)+char)>width and line:
                    lines.append(line);line=''
                if not line:line=char
                elif line[-1]==' ':line+=char
                else:line+=char
            line+=' '
        if line.strip():lines.append(line.strip())
        return [x.strip() for x in lines]

    def border(self,kind,w,h,physical_radius=32):
        label='Runtime '+kind+' magnification border parameter example'
        root,groups=setup(w,h,label)
        defs=root.find(SVG+'defs');bevel=add(defs,'linearGradient',id='native-bevel',x1=0,y1=0,x2=0,y2=h,gradientUnits='userSpaceOnUse')
        for off,col in [(0,'#9da9b2'),(.22,'#394957'),(.52,'#101924'),(.78,'#576b7b'),(1,'#b0bec8')]:add(bevel,'stop',offset=off,stop_color=col)
        if kind=='fullscreen':
            stroke=self.dim('magnifier_border_width_fullscreen_with_offset');visible=self.dim('magnifier_border_width_fullscreen')
            radius=physical_radius;outer=0;outer_radius=0;inward=(stroke-visible)/2;band=visible;dash=None
        else:
            stroke=self.dim('magnifier_border_width');visible=stroke;outer=self.dim('magnifier_stroke_width')
            radius=self.dim('magnifier_edit_corner_radius' if kind=='window-edit' else 'magnifier_corner_radius')
            outer_radius=self.dim('magnifier_edit_outer_corner_radius' if kind=='window-edit' else 'magnifier_outer_corner_radius')
            inward=0;band=stroke;dash=self.dim('magnifier_edit_dash_gap') if kind=='window-edit' else None
        inset=stroke/2;rad=max(0,min(radius,(min(w,h)-stroke)/2))
        common={'x':inset,'y':inset,'width':w-stroke,'height':h-stroke,'rx':rad,'ry':rad,'fill':'none'}
        if dash:common['stroke-dasharray']=f'{dash} {dash}'
        add(groups['cold'],'rect',**common,stroke='url(#forged)',stroke_width=stroke)
        add(groups['cold'],'rect',**common,stroke='url(#native-bevel)',stroke_width=stroke,style='mix-blend-mode:multiply')
        add(groups['cold'],'rect',**common,stroke='#b2bdc6',stroke_width=min(.75,stroke*.12),opacity=.7)
        glow={**common,'x':inset+inward,'y':inset+inward,'width':w-stroke-2*inward,'height':h-stroke-2*inward,'rx':max(0,rad-inward),'ry':max(0,rad-inward)}
        add(groups['reflection'],'rect',**glow,stroke='white',stroke_width=band*.64)
        for width,gain in [(.9,.035),(.72,.065),(.54,.12),(.36,.22)]:
            add(groups['spill'],'rect',**glow,stroke='white',stroke_width=band*width,opacity=gain/.72)
        add(groups['seam'],'rect',**glow,stroke='white',stroke_width=min(2,band*.18))
        add(groups['core'],'rect',**glow,stroke='white',stroke_width=min(.65,band*.055))
        if outer:
            edge=add(root,'g',id='outer-cold-lip')
            add(edge,'rect',x=outer/2,y=outer/2,width=w-outer,height=h-outer,rx=min(outer_radius,(min(w,h)-outer)/2),fill='none',stroke='#10171f',stroke_width=outer)
            # This final lip must remain cold above all light layers, as in the
            # native renderer. Treat it as a persistent cold composition leaf.
        record={'id':kind,'parameterExampleSize':[w,h],'sourceStroke':stroke,'sourceRadius':radius,
                'sourceOuterStroke':outer,'sourceOuterRadius':outer_radius,'dash':dash,'visibleFullscreenStroke':visible,
                'glowInwardOffset':inward,'dynamicRadiusSource':'ScreenDecorationsUtils.getWindowCornerRadius(context)' if kind=='fullscreen' else 'Native resource dimensions',
                'fullscreenRadiusShownIsIllustrative':kind=='fullscreen','nativeRenderer':'ForgeMagnificationBorderDrawable.java',
                'geometrySource':'Pinned GradientDrawable half-stroke inset and uniform-radius clamp',
                'nativeAndroidPixelsVerified':False}
        return root,record

    def show_border(self,parent,kind,x,y,w,h):
        doc,record=self.border(kind,w,h);group=add(parent,'g',transform=f'translate({x} {y})')
        # Embed actual vector layers with separate runtime color filters. There
        # is no flattened glowing border in the native resource tree.
        defs=doc.find(SVG+'defs');group.append(copy.deepcopy(defs))
        for n in doc.findall(SVG+'g'):
            key=n.get('id');q=copy.deepcopy(n);q.attrib.pop('style',None)
            if key in LAYERS[1:]:
                gain=self.style['sampleStates']['on']['gains'][key]
                if not gain:continue
                # Geometry masks are neutral. Color belongs to this fixture's
                # state owner, mirroring the native color resources.
                for node in q.iter():
                    if node.get('stroke')=='white':node.set('stroke',self.style['colors'][key])
                q.set('opacity',str(gain))
            group.append(q)
        return record

    def panel(self,parent,width,height,capability,mode,selected='size_medium',diagonal=True,typing=True,keyboard=False,font_scale=1,scroll=0):
        self.asset(parent,'panel',0,0,width,height)
        pad=self.dim('magnification_setting_background_padding');content=width-2*pad
        size=18*font_scale;line_height=max(20*font_scale,20);done_height=max(48,line_height+18)
        body_height=height-2*pad-24-done_height
        self.serial+=1;clipid='scroll-'+str(self.serial);clip=add(add(parent,'defs'),'clipPath',id=clipid)
        add(clip,'rect',x=pad,y=pad,width=content,height=body_height)
        view=add(parent,'g',clip_path='url(#'+clipid+')');body=add(view,'g',transform=f'translate({pad} {pad-scroll})');y=0
        size_controls=capability!='fullscreen'
        if size_controls:
            edit_width=max(64,font(round(size)).getlength(self.value('accessibility_magnifier_edit'))+18)
            stacked=font(round(size)).getlength(self.value('accessibility_magnifier_size'))+edit_width+12>content
            title_lines=self.wrapped(self.value('accessibility_magnifier_size'),size,content if stacked else content-edit_width-12)
            title_height=len(title_lines)*line_height+4
            rowheight=title_height+max(48,line_height+18) if stacked else max(48,title_height)
            for i,label in enumerate(title_lines):self.text(body,0,18+i*line_height,label,size)
            if mode!='fullscreen':
                edit_y=title_height if stacked else 0;edit_height=rowheight-title_height if stacked else rowheight
                self.asset(body,'control',content-edit_width,edit_y,edit_width,edit_height)
                self.text(body,content-edit_width+9,edit_y+edit_height/2+size*.34,self.value('accessibility_magnifier_edit'),size)
            y+=rowheight
            buttons=['size_small','size_medium','size_large']+(['fullscreen'] if capability=='all' else [])
            self.asset(body,'control',0,y,content,58)
            for i,key in enumerate(buttons):
                bw=content/len(buttons);state='on' if key==selected else 'off'
                self.asset(body,'control',i*bw,y,bw,58,state)
                icon_size=24 if key=='fullscreen' else 32
                self.asset(body,key,i*bw+(bw-icon_size)/2,y+(58-icon_size)/2,icon_size,icon_size,state)
            y+=58
        rows=[]
        if mode!='fullscreen':rows.append(('accessibility_allow_diagonal_scrolling',diagonal))
        if mode=='fullscreen':rows.append(('accessibility_magnify_keyboard',keyboard))
        rows.append(('accessibility_magnify_typing',typing))
        for label,on in rows:
            y+=24;lines=self.wrapped(self.value(label),size,content-52-12);rowheight=max(48,len(lines)*line_height+4)
            for i,value in enumerate(lines):self.text(body,0,y+rowheight/2-(len(lines)-1)*line_height/2+size*.34+i*line_height,value,size)
            state='on' if on else 'off';sx=content-52;sy=y+(rowheight-32)/2
            self.asset(body,'switch_track',sx,sy,52,32,state)
            self.asset(body,'switch_thumb',sx+(20 if on else 0),sy,32,32,state)
            y+=rowheight
        y+=24
        self.asset(body,'control',0,y,48,48);self.asset(body,'zoom_out',12,y+12,24,24)
        self.asset(body,'control',content-48,y,48,48);self.asset(body,'zoom_in',content-36,y+12,24,24)
        rail_width=content-96;self.asset(body,'zoom_rail',48,y+18,rail_width,12)
        # Source minimum1 and default maximum8. The unchanged native owner
        # reads ro.config.max_magnification_scale at runtime instead of fixing8.
        zoom_fraction=2/7;self.asset(body,'seek_thumb',48+zoom_fraction*(rail_width-28),y+10,28,28)
        y+=48
        self.asset(parent,'control',pad,height-pad-done_height,content,done_height)
        label=self.value('accessibility_magnification_done');tw=font(round(size)).getlength(label)
        self.text(parent,pad+(content-tw)/2,height-pad-done_height/2+size*.34,label,size)
        actual_scroll=min(max(0,scroll),max(0,y-body_height))
        body.set('transform',f'translate({pad} {pad-actual_scroll})')
        if y>body_height:
            thumb=max(24,body_height*body_height/y)
            sy=pad+actual_scroll/(y-body_height)*(body_height-thumb)
            add(parent,'rect',x=width-pad-3,y=sy,width=3,height=thumb,rx=1.5,fill='#91a1ae',opacity=.65)
        return {'capability':capability,'mode':mode,'selected':selected if size_controls else None,'fontScale':font_scale,'scrollOffset':scroll,
                'actualClampedScrollOffset':actual_scroll,
                'panelSize':[width,height],'bodyViewportHeight':body_height,'bodyContentHeight':y,
                'doneHeight':done_height,'doneOutsideScroll':True,'zoomShown':3,'zoomMaximumContext':'Source default8, runtime property can override',
                'labelsAreDefaultEnglishSourceStrings':True,'fontMetricScope':'Desktop Segoe UI fixture; actual Android font and widget measurement NOT RUN'}

    def save(self,key,root,record):
        target=OUT/'workflow-previews';target.mkdir(exist_ok=True)
        svg=xml(root);(target/(key+'.svg')).write_text(svg,encoding='utf8')
        (target/(key+'.png')).write_bytes(resvg_py.svg_to_bytes(svg_string=svg,skip_system_fonts=False))
        self.cases.append({'id':key,'svg':str((target/(key+'.svg')).relative_to(OUT)),'png':str((target/(key+'.png')).relative_to(OUT)),**record})

    def run(self):
        for key,width,height,cap,mode,selected,scale,scroll in [
                ('window-panel-selected',360,450,'all','window','size_medium',1,0),
                ('fullscreen-panel-selected',360,450,'all','fullscreen','fullscreen',1,0),
                ('window-only-panel',320,450,'window','window','size_small',1,0),
                ('fullscreen-only-panel',320,360,'fullscreen','fullscreen','fullscreen',1,0),
                ('compact-large-text-top',240,420,'all','window','size_large',1.5,0),
                ('compact-large-text-bottom',240,420,'all','window','size_large',1.5,170)]:
            root=ET.Element(SVG+'svg',{'width':str(width+32),'height':str(height+96),'viewBox':f'0 0 {width+32} {height+96}'})
            add(root,'rect',width=width+32,height=height+96,fill='#080c11');group=add(root,'g',transform='translate(16 16)')
            rec=self.panel(group,width,height,cap,mode,selected,font_scale=scale,scroll=scroll)
            self.text(root,16,height+56,'Source-backed fixture',14,'#b5bdc6');self.text(root,16,height+78,'Native rendering pending',14,'#b5bdc6')
            self.save(key,root,rec)
        for kind,w,h in [('window',294,294),('window-edit',330,230),('fullscreen',972,552)]:
            root,record=self.border(kind,w,h)
            (OUT/'masters'/('border-'+kind+'-parameter-example.svg')).write_text(xml(root),encoding='utf8')
            self.border_records.append(record)
        root=ET.Element(SVG+'svg',{'width':'960','height':'610','viewBox':'0 0 960 610'})
        add(root,'rect',width=960,height=610,fill='#080c11')
        for x in range(0,960,40):add(root,'path',d=f'M{x} 0V540',stroke='#273647',stroke_width=.7)
        for y in range(0,540,40):add(root,'path',d=f'M0 {y}H960',stroke='#273647',stroke_width=.7)
        self.text(root,40,56,'FIELD NOTES',28,'#d5e0e8');self.text(root,40,94,'Live content sample',18,'#94a9bb')
        # A medium window is324 square at this logical540px display height:
        # floor(540/3 *1.8) rounded down to an even value, exactly as source.
        outer=324;x,y=70,150;surface_margin=self.dim('magnification_mirror_surface_margin');margin=self.dim('magnification_outer_border_margin')
        add(root,'rect',x=x+surface_margin,y=y+surface_margin,width=outer-2*surface_margin,height=outer-2*surface_margin,rx=28,fill='#13283a')
        self.text(root,x+42,y+100,'FIELD',42,'#d4e2ed');self.text(root,x+42,y+155,'NOTES',42,'#d4e2ed')
        self.text(root,x+42,y+205,'Live sample',25,'#96b0c5')
        self.show_border(root,'window',x+margin,y+margin,outer-2*margin,outer-2*margin)
        # Actual70dp drag target has17dp insets around its36dp visible shell.
        self.asset(root,'drag_handle',x+outer-70+17,y+outer-70+17,36,36,'on')
        self.asset(root,'move',x+outer-70+23,y+outer-70+23,24,24,'on')
        panel=add(root,'g',transform='translate(570 42)');self.panel(panel,360,450,'all','window','size_medium')
        self.text(root,20,568,'Logical960x540 source fixture / medium324px window / actual mirrored pixels remain native data.',17,'#b5bdc6')
        self.text(root,20,596,'Source dimensions and states; desktop font/measurement approximation. This is not an Android screenshot.',16,'#b5bdc6')
        self.save('window-and-settings',root,{'logicalViewport':[960,540],'windowPresetSourceScale':1.8,'windowRootSize':[324,324],
                                        'surfaceMargin':surface_margin,'borderViewMargin':margin,'actualNativeScreenshot':False})
        root=ET.Element(SVG+'svg',{'width':'960','height':'610','viewBox':'0 0 960 610'})
        add(root,'rect',width=960,height=610,fill='#080c11')
        self.text(root,26,44,'WINDOW SIZE EDITING',26,'#eee7d9')
        x,y=280,140;w,h=360,260
        add(root,'rect',x=x+20,y=y+20,width=w-40,height=h-40,rx=16,fill='#13283a')
        self.text(root,x+58,y+100,'FIELD NOTES',30,'#d4e2ed');self.text(root,x+58,y+152,'Live content sample',21,'#96b0c5')
        self.show_border(root,'window-edit',x+margin,y+margin,w-2*margin,h-2*margin)
        for index,(cx,cy,key) in enumerate([(0,0,'resize_a'),(w-48,0,'resize_b'),(0,h-48,'resize_b'),(w-48,h-48,'resize_a')]):
            state='active_pressed' if index==1 else 'off'
            self.asset(root,'corner_handle',x+cx+11,y+cy+11,26,26,state)
            self.asset(root,key,x+cx+16,y+cy+16,16,16,state)
        self.asset(root,'control',x+w-30-48,y+h-30-48,48,48,'focused_off')
        self.asset(root,'close',x+w-30-40,y+h-30-40,32,32,'focused_off')
        self.text(root,26,568,'Source dashed edit border /48dp declared resize targets /26dp visible housings /48dp Done target.',17,'#b5bdc6')
        self.text(root,26,596,'Hidden control rectangles do not capture input. Actual Android rendering and touch acceptance remain pending.',16,'#b5bdc6')
        self.save('window-size-editing',root,{'logicalViewport':[960,540],'editWindowRootSize':[w,h],
                 'declaredResizeTouchTargetDp':48,'visibleResizeHousingDp':26,'nativeDragIconHidden':True,'actualNativeScreenshot':False})
        root=ET.Element(SVG+'svg',{'width':'960','height':'610','viewBox':'0 0 960 610'})
        add(root,'rect',width=960,height=610,fill='#132333');self.text(root,50,85,'FIELD NOTES',42,'#d5e0e8')
        self.text(root,50,142,'Live fullscreen content sample',25,'#96b0c5')
        self.show_border(root,'fullscreen',-6,-6,972,552)
        self.asset(root,'control',880,450,56,56,'off');self.asset(root,'settings_gear',890,460,36,36,'off')
        self.text(root,20,568,'Fullscreen source fixture / native12dp stroke and6dp surface offset / illustrative32dp device radius.',17,'#b5bdc6')
        self.text(root,20,596,'The real owner supplies physical corner radius and per-display bounds. Inactive magnification removes the overlay.',16,'#b5bdc6')
        self.save('fullscreen-border-and-settings-button',root,{'logicalViewport':[960,540],'fullscreenSurfaceSize':[972,552],
                'surfaceOffset':[-6,-6],'illustrativeCornerRadius':32,'nativePhysicalRadius':'Runtime owner supplies actual value','actualNativeScreenshot':False})
        write_json(OUT/'workflow-fixtures.json',self.cases);write_json(OUT/'border-parameter-examples.json',self.border_records)
        cards=[]
        for record in self.cases[:6]:
            im=Image.open(OUT/record['png']).convert('RGB');im.thumbnail((355,560));cards.append((record['id'],im))
        board=Image.new('RGB',(1155,1270),'#080c11');draw=ImageDraw.Draw(board)
        draw.text((18,14),'FORGE / MAGNIFICATION OWNER STATES',font=font(27,True),fill='#eee7d9')
        for i,(key,im) in enumerate(cards):
            x=18+(i%3)*380;y=70+(i//3)*595
            draw.text((x,y),key.replace('-',' '),font=font(15),fill='#b5bdc6');board.paste(im,(x,y+26))
        board.save(OUT/'previews/magnification-owner-states.png')
        print(json.dumps({'sourceBackedFixtures':len(self.cases),'proceduralBorderParameterExamples':len(self.border_records),
                          'nativeScreenshotClaim':False,'allAuthoredLabelsEnglish':True}))


if __name__=='__main__':Fixtures().run()
