'''Editable Gallery workflow specimens; source owners mapped, desktop metrics only.'''
import base64,io,math,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font,resvg_py
from build_scalable_frames import stretch
import render_updater_card_fixtures as common
OUT=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';NATIVE=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res/drawable-mdpi'
NS=common.NS;el=common.el;TEXT=common.TEXT;COLD=common.COLD;LAYERS=common.LAYERS
STR={e.get('name'):''.join(e.itertext()).replace("\\'","'") for e in E.parse(UP/'app/src/main/res/values/strings.xml').getroot() if e.tag=='string'}
POLICY={}
for line in (OUT/'verification/evidence/core-policy-host.txt').read_text().splitlines():
 if line.count('|')==8:
  v=line.split('|');POLICY[v[0]]=[float(v[2]),*map(float,v[3:])]
assert set(POLICY)=={'cold','focused','hovered','pressed','on','on-locked','off-locked'}
class Scene(common.Fixture):
 def __init__(self,key,title,width=480,scale=1):
  super().__init__(key,title,width,scale);self.title=title;self.labels=[]
  self.root.find('{'+NS+'}desc').text='English editable desktop specimen; real source resource labels, synthetic media and sample values. Native pixel layout, input, accessibility and device acceptance NOT RUN.'
 def label(self,key,x,y,w,size=16,color=TEXT):
  self.labels.append(key);return self.paragraph(x,y,STR[key],w,round(size*self.scale),color)
 def skin(self,family,x,y,w,h,active=False,enabled=True,parent=None,state=None):
  state=state or ('on' if enabled else 'on-locked') if active else state or ('cold' if enabled else 'off-locked')
  gains=POLICY[state];self.seq+=1;parent=parent if parent is not None else self.content
  for i,name in enumerate(LAYERS):
   p=next(NATIVE.glob(family+'_'+name+'.*'));im=Image.open(p).convert('RGBA')
   if p.name.endswith('.9.png'):im=stretch(im,(round(w),round(h)))
   b=io.BytesIO();im.save(b,format='PNG');g=el(parent,'g',id=f'layer-{self.seq}-{name}',opacity=gains[i],data_forge_layer=name)
   if i:
    fid=f'tint-{self.seq}-{name}';f=el(self.defs,'filter',id=fid,color_interpolation_filters='sRGB');el(f,'feFlood',flood_color=common.COLORS[name]);el(f,'feComposite',in2='SourceGraphic',operator='in');g.set('filter','url(#'+fid+')')
   el(g,'image',x=x,y=y,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode())
  self.controls.append({'family':family,'bounds':[x,y,w,h],'actualFeatureSample':active,'enabledSample':enabled,'policyState':state,'actualHostPolicyGains':gains})
 def glyph(self,key,x,y,size=32,on=False,state=None):self.skin('cg_gl_'+key,x,y,size,size,active=on,state=state)
 def button(self,key,x,y,w=140,on=False,icon=None,enabled=True):
  size=round(14*self.scale);lines=common.wrap(STR[key],w-24,size);h=max(62,math.ceil(len(lines)*size*1.35)+24+(36 if icon else 0));self.skin('cg_gl_button',x,y,w,h,on,enabled)
  if icon:self.glyph(icon,x+(w-28)/2,y+12,28,on);ty=y+48
  else:ty=y+14
  self.label(key,x+12,ty,w-24,14);return h
 def finish(self,y,meta):
  h=math.ceil(y+76);self.bg.set('height',str(h));self.root.set('height',str(h));self.root.set('viewBox',f'0 0 {self.w+32} {h}')
  self.text(16,h-38,'Desktop specimen / synthetic media and sample values',12,COLD);self.text(16,h-18,'Native rendering and input remain unverified',12,COLD)
  for t in self.texts:
   width=font(t['size']).getlength(t['text']);left=t['x']-width if t['anchor']=='end' else t['x']-width/2 if t['anchor']=='middle' else t['x'];assert left>=0 and left+width<=self.w+32.1,t
  for c in self.controls:
   x,y,w,hh=c['bounds'];assert x>=0 and y>=0 and x+w<=self.w+32.1 and y+hh<=h,c
  p=OUT/'workflow-previews'/self.key;p.parent.mkdir(parents=True,exist_ok=True);svg=E.tostring(self.root,encoding='unicode');p.with_suffix('.svg').write_bytes(svg.encode());p.with_suffix('.preview.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'))
  return {'id':self.key,'title':self.title,'logicalWidth':self.w,'fontScaleSample':self.scale,'sourceMapping':meta,'englishSourceLabelKeys':self.labels,'texts':self.texts,'controls':self.controls,'svg':p.with_suffix('.svg').relative_to(OUT).as_posix(),'preview':p.with_suffix('.preview.png').relative_to(OUT).as_posix(),'nativeLayoutTest':False,'deviceScreenshot':False,'desktopBounds':'PASS'}
def photo(f,x,y,w,h,index=0,selected=False,rim=True,selection_mode=False):
 # Fictional image content only. Steel/glow is outside protected central photo pixels.
 im=Image.new('RGB',(round(w),round(h)),['#426c83','#668b76','#80656f'][index%3]);d=ImageDraw.Draw(im);d.ellipse((w*.58,h*.1,w*.78,h*.3),fill='#d6d6c0');d.polygon([(0,h*.83),(w*.3,h*.24),(w*.66,h*.91),(w,h*.4),(w,h),(0,h)],fill='#233e42');d.polygon([(0,h*.86),(w*.51,h*.55),(w,h*.84),(w,h),(0,h)],fill='#18313a')
 if selected:im=im.filter(ImageFilter.GaussianBlur(15))
 b=io.BytesIO();im.save(b,format='PNG');el(f.content,'image',x=x,y=y,width=w,height=h,href='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode())
 if selected or selection_mode:f.glyph('check_circle' if selected else 'check_circle_outline',x+8,y+8,28,selected)
 if rim:f.skin('cg_gl_media_frame',x,y,w,h,selected)
def nav(f,y,wide=False):
 labels=[('reels_title','photo_size_select_actual'),('albums_title','albums'),('library_title','library')]
 if wide:
  f.skin('cg_gl_rail',16,48,108,y-48)
  for i,(key,glyph) in enumerate(labels):f.glyph(glyph,54,100+i*100,32,i==1);f.label(key,30,138+i*100,80,13)
 else:
  f.skin('cg_gl_panel',16,y,f.w,90)
  for i,(key,glyph) in enumerate(labels):x=16+i*f.w/3;f.glyph(glyph,x+(f.w/3-32)/2,y+12,32,i==1);f.label(key,x+18,y+51,f.w/3-36,13)
def grid(key,mode='albums',wide=False):
 f=Scene(key,'Gallery / '+mode,960 if wide else 480);f.skin('cg_gl_panel',16,48,f.w,96);f.label('app_name',40,65,220,24);f.glyph('settings',f.w-20,65,32)
 start=136 if wide else 16;y=160;columns=4 if wide else 3;cw=(f.w-(start-16)-16*(columns-1))/columns
 if mode=='empty':f.glyph('no_photography',f.w/2-20,210,72);y=f.label('no_media',f.w/2-80,302,200,18)+100
 else:
  for i in range(9 if not wide else 8):
   x=start+(i%columns)*(cw+16);yy=y+(i//columns)*(cw+38);photo(f,x,yy,cw,cw,i,mode=='selection' and i in [0,4],selection_mode=mode=='selection');f.text(x+4,yy+cw+23,['Photos','Favorites','Videos'][i%3] if mode=='albums' else 'Sample '+str(i+1),14,COLD)
  y+=math.ceil((9 if not wide else 8)/columns)*(cw+38)
 if mode=='selection':f.text(start,y+22,'2 selected',18);y+=45
 if mode=='trash':y=f.label('warning_bin_time_period',start,y+12,f.w-30,14,COLD)+20
 nav(f,y,wide);return f.finish(y+(0 if wide else 90),{'owners':['MainActivity.kt','ThumbnailAdapter.kt','fragment_main.xml','fragment_main(layout-sw600dp).xml'],'sampleMode':mode,'sourceSelectionBlurPx':15,'photoContent':'Synthetic original landscape, source media loading/clip unchanged'})
def viewer(key,mode):
 f=Scene(key,'Viewer / '+mode);full=mode=='fullscreen';photo(f,16,48,f.w,400,rim=False)
 if full:return f.finish(448,{'owner':'ViewActivity.kt','sourceFullscreenBarsHidden':True,'mediaContent':'Synthetic only'})
 f.skin('cg_gl_panel',16,48,f.w,96);f.glyph('back',34,63,30);f.text(82,85,'sample-landscape.jpg',17)
 keys=[('file_action_remove_from_favorites' if mode=='favorite' else 'file_action_add_to_favorites','star' if mode=='favorite' else 'star_border',mode=='favorite'),('file_action_share','share',False),('file_action_edit','edit',False),('file_action_restore_from_trash' if mode=='trash' else 'file_action_move_to_trash','restore_from_trash' if mode=='trash' else 'delete',False)]
 if mode=='readonly':keys=[r for r in keys if r[0]=='file_action_share']
 if mode=='motion':keys.insert(2,('motion_photo_show_photo','motion_play',True))
 # Information and Use as remain in the native toolbar overflow menu.
 f.text(462,87,'...',18,COLD)
 y=464;f.skin('cg_gl_panel',16,y,f.w,246);x=28;rh=0
 for label,glyph,on in keys:
  if x+136>f.w+16:y+=rh+8;x=28;rh=0
  h=f.button(label,x,y+12,136,on,glyph);rh=max(rh,h+12);x+=148
 return f.finish(max(710,y+rh+12),{'owner':'ViewActivity.kt','sampleMode':mode,'favoriteSource':'displayedMedia.isFavorite','motionSource':'motionPhoto != null','readOnlySecureFiltering':'Original source actions and conditions retained'})
def video(key,mode):
 f=Scene(key,'Video / '+mode);photo(f,16,48,f.w,420,rim=False);playing=mode=='playing';f.skin('cg_gl_media_frame',16,408,f.w,60,playing)
 f.glyph('ic_pause_circle_filled' if mode in ['playing','buffering'] else 'ic_play_circle_filled',226,235,56)
 f.glyph('ic_rewind',66,247,32);f.glyph('icon_fastforward',394,247,32)
 f.text(36,447,'0:25 / 2:30',14,COLD);f.glyph('ic_settings',432,425,28);f.skin('cg_gl_rail',32,386,448,12,playing)
 el(f.content,'rect',x=36,y=390,width=270,height=4,fill='#596571');el(f.content,'rect',x=36,y=390,width=74,height=4,fill='#e56620' if playing else COLD)
 f.skin('cg_gl_seek_thumb',94,376,32,32,playing,enabled=mode!='unseekable')
 f.text(36,580,'Sample playback state: '+mode,16,COLD)
 return f.finish(600,{'owner':'MediaViewerAdapter.kt','sourceState':'LocalPlayerViewModel.isPlaying / ExoPlayer.isPlayingFlow','isPlayingSample':playing,'media3Controller':'Native PlayerControlView, DefaultTimeBar callbacks retained','seekingEnabledSample':mode!='unseekable','bufferingIndicator':'Native dependency/default progress drawable; further visual review pending'})
def settings(key,on=False,scale=1):
 f=Scene(key,'Gallery settings / '+('on' if on else 'off'),480,scale);y=f.label('title_activity_settings',36,60,430,24)+20
 for title,summary in [('edge_tap_navigation_enable_title','edge_tap_navigation_enabled_description'),('double_tap_to_seek_enabled_title','double_tap_to_seek_enabled_description'),('hide_native_seek_buttons_title','hide_native_seek_buttons_description'),('remember_video_playback_position_enabled_title','remember_video_playback_position_enabled_description')]:
  size=round(16*scale);sub=round(14*scale);lines=common.wrap(STR[title],320,size);slines=common.wrap(STR[summary],320,sub);h=max(116,len(lines)*size*1.35+len(slines)*sub*1.35+44);f.skin('cg_gl_panel',16,y,480,h,on);ty=f.label(title,40,y+18,320,16);f.label(summary,40,ty+6,320,14,COLD);f.skin('cg_gl_switch_track',404,y+h/2-16,52,32,on);f.skin('cg_gl_switch_thumb',424 if on else 404,y+h/2-16,32,32,on);y+=h+6
  if title=='double_tap_to_seek_enabled_title':
   f.skin('cg_gl_panel',16,y,480,150,on,enabled=on);ty=f.label('double_tap_to_seek_seconds_title',40,y+18,420,16);f.skin('cg_gl_rail',44,ty+25,340,12,on,enabled=on);f.skin('cg_gl_seek_thumb',96,ty+15,32,32,on,enabled=on);f.text(420,ty+38,'10',18,COLD);y+=156
 return f.finish(y,{'owners':['root_preferences.xml','ForgeSwitchPreference','ForgeSeekBarPreference'],'actualKeys':'All original defaults, dependency key, min5/max30/increment5 retained','featureValueSample':on,'fontScaleApproximation':scale,'scrollContentShownInFull':True})
def details(key,unknown=False,scale=1):
 f=Scene(key,'Media information / '+('unknown' if unknown else 'sample'),480,scale);f.skin('cg_gl_panel',16,48,480,650 if scale==1 else 850);y=78
 for glyph,label,value in [('image','Information','sample-landscape.jpg'),('camera','Camera','Unknown' if unknown else 'Sample camera'),('person','Artist','Unknown' if unknown else 'Sample artist'),('location_on','Location','Unknown')]:
  if unknown and label in ['Camera','Artist']:continue
  f.glyph(glyph,40,y,32);y=f.paragraph(88,y,label,360,round(16*scale))+6;y=f.paragraph(88,y,value,360,round(14*scale),COLD)+24
 y=max(y,420);f.skin('cg_gl_field',40,y,432,100);f.label('media_info_add_description_hint',60,y+30,390,16)
 return f.finish(max(y+120,710 if scale==1 else 920),{'owner':'MediaInfoBottomSheetDialog.kt','sampleMetadataOnly':True,'cameraArtistInitiallyInvisible':True,'nativeDetailsContainer':'NestedScrollView','metadataWriterGeocoderPermissions':'Original source code retained'})
def dialog(key,mode):
 f=Scene(key,'Gallery / '+mode);f.skin('cg_gl_panel',16,70,480,340)
 if mode=='permission':title='manage_media_permission_title';message='manage_media_permission_message'
 elif mode=='wallpaper':title='set_wallpaper_dialog_title';message=None
 else:title='file_action_move_to_trash';message=None
 y=f.label(title,44,96,424,22)+20
 if message:y=f.label(message,44,y,424,16,COLD)+24
 elif mode=='wallpaper':
  for k in ['set_wallpaper_home_screen','set_wallpaper_lock_screen','set_wallpaper_both']:y+=f.button(k,44,y,424)+6
 else:y=f.paragraph(44,y,'Are you sure you want to move one file to trash?',424,16)+24
 if mode!='wallpaper':
  f.skin('cg_gl_button',44,y,150,64);f.text(68,y+39,'Cancel',16);f.skin('cg_gl_button',300,y,150,64);f.text(324,y+39,'OK',16);y+=76
 return f.finish(max(y+20,440),{'owner':{'permission':'PermissionsUtils.kt','wallpaper':'SetWallpaperActivity.kt','confirmation':'MediaDialogsUtils.kt'}[mode],'actualActionsInvoked':False,'frameworkLabels':'Native Cancel and OK, no substitute actions'})
def main():
 assert not (OUT/'complete-assets.zip').exists();rows=[]
 for mode in ['albums','selection','empty','trash']:rows.append(grid('grid-'+mode,mode))
 rows.append(grid('grid-wide','albums',True))
 for mode in ['cold','favorite','motion','readonly','secure','trash','fullscreen']:rows.append(viewer('viewer-'+mode,mode))
 for mode in ['playing','paused','buffering','unseekable']:rows.append(video('video-'+mode,mode))
 rows+=[settings('settings-off'),settings('settings-on',True),settings('settings-large',True,1.5),details('details-unknown',True),details('details-sample'),details('details-large',False,1.5)]
 for mode in ['permission','wallpaper','confirmation']:rows.append(dialog('dialog-'+mode,mode))
 write_json(OUT/'workflow-fixtures.json',rows)
 sheets=[]
 for batch in range(math.ceil(len(rows)/6)):
  group=rows[batch*6:(batch+1)*6];im=Image.new('RGB',(1500,1500),'#080c11');d=ImageDraw.Draw(im);d.text((24,20),'GALLERY / SOURCE-BOUND WORKFLOW SPECIMENS '+str(batch+1),font=font(24),fill=TEXT);d.text((24,60),'Desktop approximations with sample media / native rendering remains unverified',font=font(16),fill=COLD)
  for i,r in enumerate(group):
   x=24+(i%3)*492;y=110+(i//3)*680;d.text((x,y),r['id'],font=font(18),fill=TEXT);src=Image.open(OUT/r['preview']).convert('RGBA');src.thumbnail((456,618));im.paste(src,(x,y+32),src)
  p=OUT/'previews'/('gallery-workflows-'+str(batch+1)+'.preview.png');im.save(p);sheets.append(p.relative_to(OUT).as_posix())
 write_json(OUT/'workflow-preview-sheets.json',sheets);print({'editableWorkflowFixtures':len(rows),'workflowSheets':len(sheets),'nativeLayoutTests':False})
if __name__=='__main__':main()
