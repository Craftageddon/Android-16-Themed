'''Editable desktop approximations of source-owned updater screens.
Production inputs stay layered. These are not Android screenshots or layout tests.
'''
from pathlib import Path
import base64,io,math,hashlib,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font,resvg_py
import render_updater_card_fixtures as cards
from preview_updater_workflow_art import composite
OUT=ROOT/'iterations/25-updater-workflows'
UP=OUT/'upstream/packages/apps/Updater'
NATIVE=OUT/'native-patch/packages/apps/Updater/app/src/main/res/drawable-mdpi'
cards.OUT=OUT;cards.NATIVE=NATIVE
el=cards.el;wrap=cards.wrap;NS=cards.NS
TEXT=cards.TEXT;COLD=cards.COLD;EMBER=cards.EMBER
ANDROID='{http://schemas.android.com/apk/res/android}'
STR={e.get('name'):''.join(e.itertext()).replace("\\'","'").replace('\\n','\n').replace('\\u2026','…') for e in E.parse(UP/'app/src/main/res/values/strings.xml').getroot() if e.tag=='string'}
def st(key,*args):
    value=STR[key]
    for i,arg in enumerate(args,1):value=value.replace('%'+str(i)+'$s',str(arg)).replace('%'+str(i)+'$d',str(arg))
    return value.replace('%%','%')
class Scene(cards.Fixture):
    def __init__(self,key,title,width=360,scale=1):
        super().__init__(key,title,width,scale)
        self.title=title;self.metadata={};self.bottom=50;self.issues=[]
        self.root.find('{'+NS+'}desc').text='Editable source-backed desktop presentation, sample values only. Segoe UI font/layout approximations; not Android rendering, a connected device, or installed acceptance.'
    def png(self,im,x,y,w=None,h=None):
        w=w or im.width;h=h or im.height
        b=io.BytesIO();im.save(b,format='PNG')
        el(self.content,'image',x=x,y=y,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode())
    def glyph(self,key,x,y,size=32,on=False,error=False,strength=1):
        self.png(composite(key,on,error,strength),x,y,size,size)
    def button(self,label,x,y,max_width,enabled=True,secondary=False,icon=None):
        if not icon:return super().button(label,x,y,max_width,enabled,secondary)
        fam='cg_rf_field' if secondary else 'cg_rf_button';m=cards.inset(fam);w,h=m['intrinsic']
        self.skin(fam,x,y,w,h,enabled=enabled)
        self.glyph('cg_upd_pause' if icon=='pause' else 'cg_upd_resume',x+(w-24)/2,y+(h-24)/2,24)
        self.controls[-1].update(accessibleLabel=label,richSourceGlyph=True)
        return w,h
    def finish(self,y,meta):
        height=math.ceil(y+64);self.bg.set('height',str(height));self.root.set('height',str(height));self.root.set('viewBox',f'0 0 {self.w+32} {height}')
        self.text(16,height-30,'Desktop fixture / sample data',12,'#8f9ba7')
        self.text(16,height-12,'Native rendering and input remain unverified',11,'#8f9ba7')
        p=OUT/'workflow-previews'/self.key;p.parent.mkdir(exist_ok=True,parents=True)
        svg=E.tostring(self.root,encoding='unicode');E.fromstring(svg)
        p.with_suffix('.svg').write_text(svg,encoding='utf8')
        p.with_suffix('.preview.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'))
        # Exact desktop text bounds only; not native font/accessibility acceptance.
        for t in self.texts:
            if not t['text']:continue
            w=font(t['size']).getlength(t['text'])
            left=t['x']-w if t['anchor']=='end' else t['x']-w/2 if t['anchor']=='middle' else t['x']
            if left < -.1 or left+w>self.w+32.1:self.issues.append({'text':t['text'],'left':left,'right':left+w})
        assert not self.issues,self.issues
        for c in self.controls:
            x,y,w,h=c['bounds'];assert x>=0 and y>=0 and x+w<=self.w+32.1 and y+h<=height
        return {'id':self.key,'title':self.title,'logicalWidth':self.w,'fontScale':self.scale,
                'sourceMapping':meta,'texts':self.texts,'controls':self.controls,
                'svg':p.with_suffix('.svg').relative_to(OUT).as_posix(),
                'preview':p.with_suffix('.preview.png').relative_to(OUT).as_posix(),
                'deviceScreenshot':False,'nativeLayoutTest':False,'desktopTextBounds':'PASS'}
def para(f,x,y,text,w,size=14,color=TEXT):return f.paragraph(x,y,text,w,round(size*f.scale),color)
def toggle(f,x,y,checked,changeable=True,rtl=False):
    # Source primitive: 52 x 48dp decorative visual; parent owns one Role.Switch action.
    f.skin('cg_upd_switch_track',x,y+8,52,32,active=checked is True)
    left=10 if checked is None else 20 if checked!=rtl else 0
    f.glyph('cg_upd_switch_thumb',x+left,y+8,32,on=checked is True)
    if not changeable:
        # Same 153/255 visual attenuation as native primitive.
        el(f.content,'rect',x=x,y=y,width=52,height=48,fill='#080c11',opacity=102/255)
def pref(f,y,title,summary='',checked='none',changeable=True):
    x=16;w=f.w;pad=27;toggle_w=68 if checked!='none' else 0
    cw=w-2*pad-toggle_w
    size=round(16*f.scale);sub=round(14*f.scale)
    lines=wrap(title,cw,size);slines=wrap(summary,cw,sub) if summary else []
    h=max(110,math.ceil(len(lines)*size*1.35+len(slines)*sub*1.35+58))
    f.skin('cg_rf_panel',x,y,w,h,active=checked is True)
    ty=para(f,x+pad,y+27,title,cw,16,TEXT if changeable else COLD)
    if summary:para(f,x+pad,ty+4,summary,cw,14,COLD)
    if checked!='none':toggle(f,x+w-pad-52,y+(h-48)/2,checked,changeable)
    f.controls[-1].update(actualFeatureOn=checked is True,changeable=changeable,
                           parentOwnsAction=True,sourceSwitchValue=None if checked=='none' else checked)
    return y+h+4
def banner(f,x,y,w):
    # Preserve source mark paths and FlowRow ordering. Desktop metrics are approximate.
    vector=E.parse(UP/'app/src/main/res/drawable/lineage_mark_tight.xml').getroot()
    g=el(f.content,'g',transform=f'translate({x+27},{y+28}) scale(.28)')
    for child in vector:
        target=el(g,'g',transform='translate(-48,-48)')
        for p in child:el(target,'path',d=p.get(ANDROID+'pathData'),fill='#ffffff')
    f.text(x+135,y+66,'24.0',round(48*f.scale),TEXT)
    yy=y+108;cw=w-54;px=x+27;rowheight=0
    data=[(st('header_build_version','24.0'),st('header_android_version','17')),
          (st('build_date'),'Oct 19'),(st('security_update'),'Oct 2026')]
    for label,value in data:
        need=min(cw,max(font(round(14*f.scale)).getlength(label),font(round(16*f.scale)).getlength(value)))
        if px>x+27 and px+need>x+w-27:yy+=rowheight+16;px=x+27;rowheight=0
        end=para(f,px,yy,label,need,14,COLD)
        end=para(f,px,end+4,value,need,16)
        rowheight=max(rowheight,end-yy);px+=need+16
    h=yy-y+rowheight+27;f.skin('cg_rf_panel',x,y,w,h,parent=f.card);y+=h+6
    px=x;rh=0
    for label in [st('show_changelog'),st('report_issues')]:
        need=max(112,min(w,math.ceil(font(round(14*f.scale)).getlength(label))+22))
        if px>x and px+need>x+w:y+=rh+4;px=x;rh=0
        bw,bh=f.button(label,px,y,w,secondary=True);px+=bw+8;rh=max(rh,bh)
    return y+rh+12
def status(f,x,y,w,mode,ready=False):
    if mode!='Idle':
        f.glyph('cg_upd_scan' if mode=='Checking' else 'cg_upd_error',x+(w-160)/2,y,160,
                on=True,error=mode!='Checking',strength=.65 if mode=='Checking' else .8)
        y+=176
        key={'Checking':'checking_for_updates','Error':'updates_check_failed','NoInternet':'check_your_internet_connection'}[mode]
        y=para(f,x,y,st(key),w,14)+16
    if mode!='Checking':
        _,h=f.button(st('check_for_updates'),x,y,w);y+=h+16
    y=para(f,x,y,st('header_last_updates_check_time','1:23 PM'),w,12,COLD)+16
    if ready and mode=='Idle':
        f.glyph('cg_upd_ready',x+(w-96)/2,y,96);y+=112
        y=para(f,x,y,st('updates_zero_state_title'),w,18)+4
        y=para(f,x,y,st('updates_zero_state_description'),w,14,COLD)+20
    return y
def main_screen(key,width=360,mode='Idle',scale=1):
    f=Scene(key,mode.upper()+' / SYSTEM UPDATES',width,scale)
    y=52
    if width>=600:
        gap=24;pw=(width-gap)/2
        l=banner(f,16,y,pw);r=status(f,16+pw+gap,y,pw,mode,True)
        for k in ['local_update_import','menu_preferences']:r=pref_in_column(f,r,16+pw+gap,pw,st(k),st('local_update_import_summary') if k=='local_update_import' else '')
        y=max(l,r)
    else:
        y=banner(f,16,y,width)
        y=status(f,32,y,width-32,mode,True)
        y=pref(f,y,st('local_update_import'),st('local_update_import_summary'))
        y=pref(f,y,st('menu_preferences'))
    return f.finish(y,{'owner':'UpdatesScaffoldActivity.kt','breakpointDp':600,'panes':'equal independent scroll columns' if width>=600 else 'single scrolling column',
                      'checkOwner':'updatescheck/UpdatesCheck.kt','checkState':mode,'zeroStateShown':mode=='Idle',
                      'headerValues':'SAMPLE - not device build claims','animationFrame':'checking p=0 / error peak p=0.5','modeAndCapabilitiesAreSamples':True})
def pref_in_column(f,y,x,w,title,summary):
    h=140 if summary else 112;f.skin('cg_rf_panel',x,y,w,h)
    yy=para(f,x+27,y+27,title,w-54,16)
    if summary:para(f,x+27,yy+4,summary,w-54,14,COLD)
    return y+h+4
def preferences(key,ab=True,ac=False,periodic=True,recovery=False,scale=1,width=360):
    f=Scene(key,st('menu_preferences'),width,scale);y=58
    y=para(f,32,y,st('pref_category_background_sync'),width-32,14,COLD)+10
    y=pref(f,y,st('menu_auto_updates_check'),st('menu_auto_updates_check_summary'),periodic)
    y=pref(f,y,st('menu_auto_updates_check_interval'),st('time_unit_week'),'none',periodic)
    y=para(f,32,y+16,st('pref_category_download_install'),width-32,14,COLD)+10
    key1='stream_updates' if ab else 'auto_delete_updates'
    y=pref(f,y,st('menu_'+key1),st('menu_'+key1+'_summary'),True)
    y=pref(f,y,st('menu_metered_network_warning'),st('menu_metered_network_warning_summary'),False)
    if ab:y=pref(f,y,st('menu_ab_perf_mode'),st('menu_ab_perf_mode_summary_charging' if ac else 'menu_ab_perf_mode_summary'),ac,not ac)
    if recovery:y=pref(f,y,st('menu_update_recovery'),st('menu_update_recovery_summary'),False)
    return f.finish(y,{'owner':'preferences/PreferencesScreen.kt','isABDevice':ab,'isAcCharging':ac,'periodicCheckEnabled':periodic,
                      'showRecoveryUpdate':recovery,'deviceCapabilitiesAreSamples':True,'acForcedOn':ac,'sourceCallbackBodiesChanged':False})
def dialog(key,title,message,labels=('Cancel','OK'),width=360,scale=1,importing=False):
    f=Scene(key,'DIALOG / '+title,width,scale);x=16+width*.075;w=width*.85;y=58
    # Original getDialogWidth gives 85% portrait; matching 65% landscape covered separately.
    legacy=key.startswith('import-')
    if not legacy:f.glyph('cg_upd_badge',x+(w-48)/2,y+27,48)
    ty=y+(27 if legacy else 91)
    ty=para(f,x+35,ty,title,w-70,24)+16
    if importing:
        f.glyph('cg_upd_switch_thumb',x+35,ty,40,True)
        el(f.content,'circle',cx=x+55,cy=ty+20,r=12,fill='none',stroke='#27333e',stroke_width=3)
        el(f.content,'path',d=f'M{x+55} {ty+8} A12 12 0 0 1 {x+67} {ty+20}',fill='none',stroke=EMBER,stroke_width=3)
        ty=max(ty+40,para(f,x+91,ty,message,w-126,16))+24
    else:ty=para(f,x+35,ty,message,w-70,16)+24
    bx=x+35;rh=0;avail=w-70
    for i,label in enumerate(labels):
        fam='cg_rf_field' if i==0 else 'cg_rf_button';minimum=cards.inset(fam)['intrinsic'][0]
        predicted=max(minimum,min(avail,math.ceil(font(round(14*scale)).getlength(label))+22))
        if bx>x+35 and bx+predicted>x+w-35:ty+=rh+4;bx=x+35;rh=0
        bw,bh=f.button(label,bx,ty,avail,secondary=i==0);bx+=bw+4;rh=max(rh,bh)
    ty+=rh+27;f.skin('cg_rf_panel',x,y,w,ty-y,active=importing,parent=f.card)
    return f.finish(ty,{'owner':'updates/action/UpdateActionDialog.kt' if not key.startswith('import') else 'UpdatesActivity.java',
                       'message':message,'dialogPortraitWidthRatio':.85 if not legacy else 'platform-owned, desktop approximation','callbackBodiesChanged':False,'cancelable':not importing,
                       'importerOrInstallerExecuted':False,'illustratedClock':'native circular indicator snapshot approximation' if importing else None})
def list_dialog(key,selected=1,enabled=True,scale=1):
    f=Scene(key,'INTERVAL CHOICES / '+('ENABLED' if enabled else 'DISABLED'),360,scale);x=43;w=306;y=58
    ty=para(f,x+27,y+27,st('menu_auto_updates_check_interval'),w-54,24)+24
    for i,k in enumerate(['time_unit_day','time_unit_week','time_unit_month']):
        f.glyph('cg_upd_switch_thumb',x+27,ty,32,on=i==selected)
        if i==selected:el(f.content,'circle',cx=x+43,cy=ty+16,r=4,fill=EMBER)
        ty=para(f,x+75,ty,st(k),w-102,16,TEXT if enabled else COLD)+30
    f.skin('cg_rf_panel',x,y,w,ty-y,parent=f.card)
    return f.finish(ty,{'owner':'ForgeListPreference + pinned ListPreferenceModel','selectedOrdinal':selected,'enabled':enabled,
                       'sourceOptionIds':[0,1,2],'closeBeforeOnIdSelected':True,'parentRole':'RadioButton','actualCallbacksExecuted':False})
def controls():
    f=Scene('control-state-matrix','CONTROL STATES / REAL MODEL SEMANTICS',600);y=58
    for label,value,change in [('Off',False,True),('On',True,True),('On, locked by AC',True,False),('Off, locked',False,False),('Loading',None,False)]:
        y=pref(f,y,label,'Single parent switch action; decorative thumb',value,change)
    for label,focus,on in [('Keyboard focus: cool',True,False),('Pressed: momentary ember',False,True)]:
        f.skin('cg_rf_field',16,y,600,72,active=on)
        if focus:
            mask=Image.open(NATIVE/'cg_rf_field_focus.9.png').convert('RGBA')
            mask=cards.stretch(mask,(600,72));tint=Image.new('RGBA',mask.size,'#d5e7f2');tint.putalpha(mask.getchannel('A'));f.png(tint,16,y)
        f.text(43,y+44,label,16,TEXT);y+=80
    return f.finish(y,{'primitive':'ForgeUpdaterControls.kt','knownValues':[False,True],'unknownIsNotFalse':True,
                       'focusActivatesEmber':False,'checkedNotInteractionEnabledOwnsSteadyEmber':True,'disabledAlpha':153,
                       'nativeInputExecuted':False})
def icon_preview():
    f=Scene('adaptive-icon-safe-area','ADAPTIVE ICON / COLD IDENTITY',600);y=60
    im=composite('cg_upd_badge')
    # Draw a 108dp adaptive foreground with 18% inset, then clip to 72dp launcher viewport.
    canvas=Image.new('RGBA',(432,432),'#080c11');badge=im.resize((276,276),Image.Resampling.LANCZOS);canvas.alpha_composite(badge,(78,78))
    visible=canvas.crop((72,72,360,360))
    for i,name in enumerate(['Circle','Rounded square','Squircle approximation']):
        tile=visible.copy();mask=Image.new('L',tile.size);d=ImageDraw.Draw(mask)
        if i==0:d.ellipse((0,0,287,287),fill=255)
        else:d.rounded_rectangle((0,0,287,287),radius=68 if i==1 else 112,fill=255)
        tile.putalpha(mask);f.png(tile,22+i*200,y,184,184);f.text(22+i*200,y+212,name,13,COLD)
    f.glyph('cg_upd_badge',32,y+260,96)
    f.text(150,y+300,'Cold source artwork; no selection glow baked in',14,TEXT)
    f.text(32,y+382,'Native adaptive/monochrome rendering and installed selection: NOT RUN',13,COLD)
    return f.finish(y+400,{'manifestIcon':'@mipmap/ic_launcher','foregroundInsetPercent':18,'foregroundScale':.64,
                           'safeCircleDiameterOverViewport':66/108,'coldSourceSize':128,'monochromeSourcePreserved':True,
                           'masksAreDesktopApproximations':True})
def sheets(rows):
    groups=[('updater-main-screens',[r for r in rows if r['id'].startswith('main-')]),
            ('updater-preferences',[r for r in rows if r['id'].startswith('prefs-')]),
            ('updater-dialogs',[r for r in rows if r['id'].startswith(('dialog-','import-','interval-'))])]
    previews=OUT/'previews';previews.mkdir(exist_ok=True)
    for name,group in groups:
        columns=3;cw=420;heights=[]
        for start in range(0,len(group),columns):
            heights.append(max(min(Image.open(OUT/r['preview']).height,1000) for r in group[start:start+columns])+52)
        sheet=Image.new('RGB',(columns*cw,sum(heights)+76),'#080c11');d=ImageDraw.Draw(sheet)
        d.text((16,12),'FORGE / '+name.upper().replace('-',' '),font=font(23),fill=TEXT)
        d.text((16,46),'Source-backed desktop fixtures / sample data / native layout not run',font=font(14),fill=COLD)
        for i,r in enumerate(group):
            tile=Image.open(OUT/r['preview']).convert('RGBA');tile.thumbnail((cw-26,1000))
            xx=i%columns*cw+(cw-tile.width)//2;yy=76+sum(heights[:i//columns]);sheet.paste(tile,(xx,yy),tile)
        sheet.save(previews/(name+'.preview.png'))
def main():
    assert not (OUT/'complete-assets.zip').exists()
    rows=[]
    for mode in ['Idle','Checking','NoInternet','Error']:rows.append(main_screen('main-'+mode.lower(),mode=mode))
    rows.append(main_screen('main-wide',width=720,mode='Checking'))
    # Full banner at 2x text gets its own 600dp source-breakpoint fixture; narrow preferences/dialogs test wrapping below.
    for args in [('prefs-ab',True,False,True,False,1,360),('prefs-ac-locked',True,True,True,False,1,360),
                 ('prefs-non-ab-recovery',False,False,True,True,1,360),('prefs-periodic-off',True,False,False,False,1,360),
                 ('prefs-large-text',True,True,True,True,2,320)]:
        rows.append(preferences(*args))
    for k in ['confirm_cancel','confirm_delete']:
        rows.append(dialog('dialog-'+k,st(k+'_dialog_title'),st(k+'_dialog_message')))
    rows.append(dialog('dialog-install-ab',st('apply_update_dialog_title'),st('apply_update_dialog_message_ab','LineageOS 24.0 / Oct 27','OK')))
    rows.append(dialog('dialog-install-recovery',st('apply_update_dialog_title'),st('apply_update_dialog_message','LineageOS 24.0 / Oct 27','OK'),scale=2,width=320))
    rows.append(dialog('dialog-battery',st('dialog_battery_low_title'),st('dialog_battery_low_message_pct',30,20),('OK',)))
    rows.append(dialog('dialog-metered',st('update_over_metered_network_title'),st('update_over_metered_network_message')))
    rows.append(dialog('import-running',st('local_update_import'),st('local_update_import_progress'),(),importing=True))
    rows.append(dialog('import-success',st('local_update_import_success_title'),st('local_update_import_success_message','Oct 27'),('OK',)))
    rows.append(dialog('import-error',st('local_update_import'),st('local_update_import_failure'),('OK',)))
    for i in range(3):rows.append(list_dialog('interval-'+str(i),i))
    rows.append(list_dialog('interval-disabled',1,False,2))
    rows.extend([controls(),icon_preview()])
    sheets(rows)
    write_json(OUT/'workflow-screen-fixtures.json',{'fixtures':rows,'screens':len(rows),'deviceScreenshots':False,
                'sourceDefaultEnglish':True,'font':'Segoe UI approximation; actual Android typography NOT RUN',
                'tvQr':'Unchanged native generator; intentionally not simulated as a working QR code',
                'sourceCode':{'scaffold':'UpdatesScaffoldActivity.kt','preferences':'preferences/PreferencesScreen.kt','dialogs':'updates/action/UpdateActionHandler.kt'},
                'allProductionInputsRemainSeparate':True})
    print({'workflowScreenFixtures':len(rows),'comparisonSheets':3,'desktopTextBounds':'PASS','nativeLayout':'NOT RUN'})
if __name__=='__main__':main()
