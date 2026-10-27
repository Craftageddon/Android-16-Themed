'''Editable source-backed updater card previews, not Android screenshots.'''
from pathlib import Path
import base64,io,math,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font,resvg_py
from build_scalable_frames import stretch,bounds

OUT=ROOT/'iterations/24-updater'
NATIVE=OUT/'native-patch/packages/apps/Updater/app/src/main/res/drawable-mdpi'
UP=OUT/'upstream/packages/apps/Updater/app/src/main/res/values/strings.xml'
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
COLORS={'reflection':'#dc5920','spill':'#ff4908','seam':'#ff5b0b','core':'#ffd083','focus':'#d5e7f2','symbol':'#ffe5bc'}
TEXT='#eee7d9';COLD='#b5bdc6';EMBER='#e56620';ERROR='#ff8585'
def el(parent,tag,**attrs):return E.SubElement(parent,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
def inset(family):
    im=Image.open(NATIVE/(family+'_cold.9.png')).convert('RGBA');w,h=im.width-2,im.height-2
    xs=[i for i in range(im.width) if im.getpixel((i,im.height-1))==(0,0,0,255)]
    ys=[i for i in range(im.height) if im.getpixel((im.width-1,i))==(0,0,0,255)]
    return {'intrinsic':[w,h],'padding':[min(xs)-1,min(ys)-1,w-max(xs),h-max(ys)],'stretch':bounds(im)}
def wrap(text,width,size):
    output=[]
    for p in text.replace('\\n','\n').split('\n'):
        line=''
        for word in p.split():
            candidate=(line+' '+word).strip()
            if line and font(size).getlength(candidate)>width:output.append(line);line=word
            else:line=candidate
        output.append(line)
    return output

class Fixture:
    def __init__(self,key,title,width,scale=1,expressive=True):
        self.key=key;self.w=width;self.scale=scale;self.expressive=expressive
        self.root=E.Element('{'+NS+'}svg',{'width':str(width+32),'height':'1000','viewBox':f'0 0 {width+32} 1000'})
        el(self.root,'title').text=title
        el(self.root,'desc').text='Source-backed editable desktop card fixture. Segoe UI metrics and native glyph/progress rendering are approximations. Sample metadata only; not an Android screenshot or device/installed-build evidence.'
        self.bg=el(self.root,'rect',width=width+32,height=1000,fill='#080c11');self.defs=el(self.root,'defs')
        self.card=el(self.root,'g');self.content=el(self.root,'g');self.seq=0;self.texts=[];self.controls=[]
        self.text(16,24,title,14,COLD)
    def text(self,x,y,text,size=14,color=TEXT,anchor='start'):
        el(self.content,'text',x=x,y=y,font_size=size,font_family='Segoe UI',fill=color,text_anchor=anchor).text=text
        self.texts.append({'text':text,'x':x,'y':y,'size':size,'anchor':anchor})
    def paragraph(self,x,y,text,width,size=14,color=TEXT):
        for line in wrap(text,width,size):self.text(x,y+size,line,size,color);y+=math.ceil(size*1.35)
        return y
    def skin(self,family,x,y,w,h,active=False,enabled=True,parent=None):
        parent=parent if parent is not None else self.content;self.seq+=1
        gains={name:0 for name in LAYERS[1:]}
        if enabled and active:gains.update(reflection=.32,spill=.72,seam=1,core=.82,symbol=1)
        for layer in LAYERS:
            src=Image.open(NATIVE/(family+'_'+layer+'.9.png')).convert('RGBA')
            im=stretch(src,(round(w),round(h)));buf=io.BytesIO();im.save(buf,format='PNG')
            gain=(1 if enabled else .42) if layer=='cold' else gains[layer]
            group=el(parent,'g',id=f'component-{self.seq}-{layer}',opacity=gain,data_forge_layer=layer)
            if layer!='cold':
                fid=f'tint-{self.seq}-{layer}';f=el(self.defs,'filter',id=fid,color_interpolation_filters='sRGB')
                el(f,'feFlood',flood_color=COLORS[layer]);el(f,'feComposite',in2='SourceGraphic',operator='in')
                group.set('filter','url(#'+fid+')')
            el(group,'image',x=x,y=y,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode())
        self.controls.append({'family':family,'bounds':[x,y,w,h],'active':active,'enabled':enabled})
    def button(self,label,x,y,max_width,enabled=True,secondary=False,icon=None):
        family='cg_rf_field' if secondary else 'cg_rf_button';m=inset(family)
        size=round(14*self.scale);pad=m['padding'];minimum=m['intrinsic']
        w=minimum[0] if icon else max(minimum[0],min(max_width,math.ceil(font(size).getlength(label))+pad[0]+pad[2]))
        lines=[] if icon else wrap(label,w-pad[0]-pad[2],size)
        h=max(minimum[1],math.ceil(len(lines)*size*1.35)+pad[1]+pad[3])
        self.skin(family,x,y,w,h,enabled=enabled)
        color=TEXT if enabled else '#8f9ba7';cx=x+w/2;cy=y+h/2
        if icon=='pause':
            el(self.content,'path',d=f'M{cx-8} {cy-10} h5 v20 h-5 Z M{cx+3} {cy-10} h5 v20 h-5 Z',fill=color)
        elif icon=='resume':
            el(self.content,'path',d=f'M{cx-7} {cy-11} L{cx+10} {cy} L{cx-7} {cy+11} Z',fill=color)
        else:
            ty=cy-len(lines)*size*1.35/2+size
            for line in lines:self.text(cx,ty,line,size,color,'middle');ty+=size*1.35
        self.controls[-1].update(accessibleLabel=label,sourceNativeIconApproximation=bool(icon))
        return w,h
    def save(self,card_height,meta):
        self.skin('cg_rf_panel',16,44,self.w,card_height,active=meta['tone']=='ACTIVE',parent=self.card)
        height=card_height+94
        self.bg.set('height',str(height));self.root.set('height',str(height));self.root.set('viewBox',f'0 0 {self.w+32} {height}')
        self.text(16,height-22,'Desktop fixture / sample data',12,'#8f9ba7')
        self.text(16,height-6,'Native rendering and fonts remain unverified',11,'#8f9ba7')
        path=OUT/'workflow-previews'/self.key;path.parent.mkdir(parents=True,exist_ok=True)
        svg=E.tostring(self.root,encoding='unicode');E.fromstring(svg)
        path.with_suffix('.svg').write_text(svg,encoding='utf8')
        png=resvg_py.svg_to_bytes(svg_string=svg,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI')
        path.with_suffix('.preview.png').write_bytes(png)
        return {'id':self.key,'fixtureOnly':True,'deviceScreenshot':False,'logicalCardWidth':self.w,
                'fontScaleSample':self.scale,'spaExpressiveSample':self.expressive,
                'sourceMapping':meta,'texts':self.texts,'controls':self.controls,
                'svg':path.with_suffix('.svg').relative_to(OUT).as_posix(),
                'preview':path.with_suffix('.preview.png').relative_to(OUT).as_posix()}

def main():
    assert not (OUT/'complete-assets.zip').exists()
    strings={e.get('name'):''.join(e.itertext()).replace("\\'","'") for e in E.parse(UP).getroot() if e.tag=='string'}
    review=read_json(OUT/'source-contract-review.json');phases={r['phase']:r for r in review['phaseBindingsProposed']}
    actions={r['action']:r['nativeDefaultEnglish'] for r in review['actions']}
    # Source framework label, not a substitute action or handler.
    native_cancel=[d for d in read_json(ROOT/'iterations/22-native-contract-review/resource-declarations.json')
                   if d['project']=='frameworks/base' and d['resourceRoot']=='core/res/res' and d['type']=='string' and d['name']=='cancel' and d['qualifier']=='values']
    assert len(native_cancel)==1 and native_cancel[0]['value']=='Cancel'
    actions['CANCEL_DOWNLOAD']=actions['CANCEL_INSTALL']=native_cancel[0]['value']
    cases=[
        ('idle-expanded','IDLE',None,'START_DOWNLOAD',None,True),
        ('download-starting','DOWNLOADING','indeterminate','PAUSE_DOWNLOAD','CANCEL_DOWNLOAD',True),
        ('downloading','DOWNLOADING',62,'PAUSE_DOWNLOAD','CANCEL_DOWNLOAD',True),
        ('download-paused','DOWNLOAD_PAUSED',62,'RESUME_DOWNLOAD','CANCEL_DOWNLOAD',True),
        ('offline-paused','DOWNLOAD_PAUSED',62,'RESUME_DOWNLOAD','CANCEL_DOWNLOAD',False),
        ('download-error','DOWNLOAD_ERROR',62,'RESUME_DOWNLOAD','CANCEL_DOWNLOAD',True),
        ('verifying','VERIFYING','indeterminate','START_INSTALL',None,False),
        ('verification-failed','VERIFICATION_FAILED',None,'START_DOWNLOAD',None,True),
        ('verified-ready','VERIFIED',None,'START_INSTALL',None,True),
        ('installing','INSTALLING',62,'PAUSE_INSTALL','CANCEL_INSTALL',True),
        ('installing-recovery','INSTALLING_RECOVERY',62,'CANCEL_INSTALL',None,True),
        ('finalizing','FINALIZING','indeterminate','PAUSE_INSTALL','CANCEL_INSTALL',True),
        ('suspended','INSTALLATION_SUSPENDED',62,'RESUME_INSTALL','CANCEL_INSTALL',True),
        ('installation-failed','INSTALLATION_FAILED',None,'START_DOWNLOAD',None,True),
        ('reboot-ready','WAITING_FOR_REBOOT',None,'REBOOT',None,True),
        ('manual-guide','VERIFIED',None,'OPEN_GUIDE',None,True),
        ('compact-large-text','DOWNLOAD_PAUSED',62,'RESUME_DOWNLOAD','CANCEL_DOWNLOAD',True),
        ('non-expressive-card','DOWNLOADING',62,'PAUSE_DOWNLOAD','CANCEL_DOWNLOAD',True),
    ]
    rows=[]
    for key,phase,progress,primary,secondary,enabled in cases:
        compact=key=='compact-large-text';width=320 if compact else 360;scale=1.5 if compact else 1
        f=Fixture(key,phase.replace('_',' '),width,scale,key!='non-expressive-card')
        m=inset('cg_rf_panel');l,t,r,b=m['padding'];item_start=16 if f.expressive else 24
        x=16+l+item_start;cw=width-l-r-item_start-16;y=44+t+(12 if f.expressive else 16)
        y=f.paragraph(x,y,'Oct 27',cw,round(20*scale))
        label=strings['list_build_version'].replace('%1$s','24.0')
        status=phases[phase]['nativeDefaultEnglish']
        if status:label+=' • '+status
        y=f.paragraph(x,y,label,cw,round(14*scale),COLD)+12
        tone=phases[phase]['proposedMaterialRole']
        if isinstance(progress,int):
            detail=[('62%',round(24*scale)),(' · '+strings['list_download_progress_newer'].replace('%1$s','620 MB').replace('%2$s','1 GB'),round(14*scale))]
            if phase not in {'DOWNLOADING','DOWNLOAD_PAUSED','DOWNLOAD_ERROR'}:detail=detail[:1]
            if phase=='DOWNLOADING':detail.append(('3 min left',round(14*scale)))
            px=x;rh=0
            for text,size in detail:
                tw=font(size).getlength(text)
                if px>x and px+tw>x+cw:y+=rh+4;px=x;rh=0
                h=math.ceil(len(wrap(text,cw,size))*size*1.35)
                f.paragraph(px,y,text,cw-(px-x),size,COLD)
                px+=tw+4;rh=max(rh,h)
            y+=rh+8
        if progress is not None:
            f.skin('cg_upd_rail',x,y,cw,12,active=tone=='ACTIVE')
            fill=EMBER if tone=='ACTIVE' else ERROR if tone=='ERROR' else COLD
            inner=cw-6
            if progress=='indeterminate':el(f.content,'rect',x=x+3+inner*.2,y=y+4,width=inner*.35,height=4,rx=2,fill=fill)
            else:el(f.content,'rect',x=x+3,y=y+4,width=inner*progress/100,height=4,rx=2,fill=fill)
            y+=24
        else:
            y=f.paragraph(x,y,strings['list_update_size'].replace('%1$s','1 GB'),cw,round(14*scale),COLD)
            note=strings['list_major_upgrade_recovery_install'].replace('%1$s',strings['brand_name']) if key=='manual-guide' else strings['list_full_install']
            el(f.content,'path',d=f'M{x} {y+8} h{cw}',stroke='#36414d',stroke_width=1);y+=20
            y=f.paragraph(x,y,note,cw,round(14*scale),COLD)+8
        ax=16+l+16;available=width-l-r-32;y+=12;px=ax;rh=0
        for i,action in enumerate([primary]+([secondary] if secondary else [])):
            text=actions[action];icon='pause' if action.startswith('PAUSE_') else 'resume' if action.startswith('RESUME_') else None
            fam='cg_rf_field' if i else 'cg_rf_button';pad=inset(fam)['padding'];minimum=inset(fam)['intrinsic']
            predicted=minimum[0] if icon else max(minimum[0],min(available,math.ceil(font(round(14*scale)).getlength(text))+pad[0]+pad[2]))
            if px>ax and px+predicted>ax+available:y+=rh+4;px=ax;rh=0
            w,h=f.button(text,px,y,available,enabled if i==0 else True,bool(i),icon);px+=w+4;rh=max(rh,h)
        # Actual MoreOptionsAction remains native; the three-dot mark is illustrative.
        if px+48>ax+available:y+=rh+4;px=ax;rh=0
        for dy in [-5,0,5]:el(f.content,'circle',cx=px+24,cy=y+24+dy,r=1.5,fill=TEXT)
        rh=max(rh,48);y+=rh+12+b
        meta={'phase':phase,'tone':tone,'expanded':True,'progress':progress,
              'primary':primary,'primaryEnabled':enabled,'secondary':secondary,
              'operationAndDataAreSamples':True,'minimumColdFrameMetrics':m,
              'actualOwnerPaths':['updates/UpdateItem.kt','updates/button/ActionBar.kt','updates/state/UpdateItemStateMapper.kt'],
              'fontAndLayoutMetricsAreDesktopApproximations':True,
              'manualInstallBlockSample':'VERSION_UNSUPPORTED' if key=='manual-guide' else None}
        rows.append(f.save(math.ceil(y-44),meta))
    previews=OUT/'previews';previews.mkdir(exist_ok=True)
    for sheet,subset in [('updater-card-states',rows[:9]),('updater-card-edge-states',rows[9:])]:
        cellw=420;row_heights=[]
        for at in range(0,len(subset),3):
            row_heights.append(max(Image.open(OUT/r['preview']).height for r in subset[at:at+3])+28)
        im=Image.new('RGB',(cellw*3,sum(row_heights)+72),'#080c11');d=ImageDraw.Draw(im)
        d.text((16,12),'FORGE / UPDATER CARD PRESENTATION',font=font(24),fill=TEXT)
        d.text((16,44),'Desktop fixtures / existing separate steel and neutral light layers',font=font(15),fill=COLD)
        for i,row in enumerate(subset):
            tile=Image.open(OUT/row['preview']).convert('RGBA');tile.thumbnail((cellw-24,row_heights[i//3]-24))
            im.paste(tile,(i%3*cellw+(cellw-tile.width)//2,72+sum(row_heights[:i//3])),tile)
        im.save(previews/(sheet+'.preview.png'))
    write_json(OUT/'card-workflow-fixtures.json',{'fixtures':rows,'sourceFrameworkCancel':native_cancel[0],
        'newDrawings':0,'deviceScreenshots':False,'wholeUpdaterWorkflowComplete':False,
        'remaining':'Scaffold/banner/preferences/dialogs/illustrations and native acceptance remain required.'})
    print({'sourceBackedCardFixtures':len(rows),'stateSheets':2,'deviceScreenshots':False,'wholeWorkflowComplete':False})

if __name__=='__main__':main()
