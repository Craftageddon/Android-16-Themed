'''Offline compositing of actual exported neutral layers; not device screenshots.'''
from pathlib import Path
import json,math
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font
OUT=ROOT/'iterations/25-updater-workflows'
RES=OUT/'native-patch/packages/apps/Updater/app/src/main/res/drawable-mdpi'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
NORMAL=['#dc5920','#ff4908','#ff5b0b','#ffd083','#d5e7f2','#ffe5bc']
ALERT=['#b83d39','#e13d3d','#ff8585','#ffd6ce','#d5e7f2','#ffb0a8']
def composite(key,active=False,error=False,strength=1):
    layers={n:Image.open(RES/(key+'_'+n+'.png')).convert('RGBA') for n in LAYERS}
    out=layers['cold'].copy()
    if active:
        gains=[.32,.72,1,.82,0,1]
        for name,color,gain in zip(LAYERS[1:],ALERT if error else NORMAL,gains):
            if not gain:continue
            tint=Image.new('RGBA',out.size,color)
            tint.putalpha(layers[name].getchannel('A').point(lambda a:round(a*gain*strength)))
            out.alpha_composite(tint)
    return out
def main():
    assert not (OUT/'complete-assets.zip').exists()
    rows=read_json(OUT/'workflow-art-components.json')
    out=OUT/'previews';out.mkdir(exist_ok=True);saved=[]
    sheet=Image.new('RGB',(1320,940),'#080c11');d=ImageDraw.Draw(sheet)
    d.text((24,16),'FORGE / UPDATER ARTWORK',font=font(30),fill='#eee7d9')
    d.text((24,56),'Cold steel and separate runtime light masks / desktop previews',font=font(17),fill='#b5bdc6')
    specs=[('cg_upd_scan','Checking'),('cg_upd_error','Error'),('cg_upd_ready','Ready'),
           ('cg_upd_pause','Pause'),('cg_upd_resume','Resume'),('cg_upd_badge','Updater identity')]
    for i,(key,label) in enumerate(specs):
        x=(i%3)*440;y=100+(i//3)*390
        d.text((x+24,y),label,font=font(21),fill='#eee7d9')
        for j,active in enumerate([False,True]):
            # Ready and app icons stay cold in their actual owner, shown that way here.
            on=active and key not in ['cg_upd_ready','cg_upd_badge']
            im=composite(key,on,key=='cg_upd_error',.65 if key=='cg_upd_scan' else .8)
            standalone=out/(key+('-active' if on else '-cold')+'.preview.png')
            im.save(standalone)
            view=im.resize((144,144),Image.Resampling.LANCZOS)
            sheet.paste(view,(x+24+j*192,y+54),view)
            d.text((x+24+j*192,y+215),'Active' if on else 'Cold',font=font(15),fill='#b5bdc6')
            saved.append({'family':key,'active':on,'preview':standalone.relative_to(OUT).as_posix()})
        if key in ['cg_upd_ready','cg_upd_badge']:
            d.text((x+24,y+250),'Steady cold in the actual owner',font=font(15),fill='#b5bdc6')
        if key in ['cg_upd_pause','cg_upd_resume']:
            native=composite(key);sheet.paste(native,(x+24,y+285),native)
            d.text((x+76,y+290),'32dp export at 1x',font=font(14),fill='#b5bdc6')
    sheet.save(out/'updater-artwork.preview.png')
    glyphs=Image.new('RGB',(1320,380),'#10151b');d=ImageDraw.Draw(glyphs)
    d.text((24,16),'Actual-size glyphs and enlarged material detail',font=font(24),fill='#eee7d9')
    for i,key in enumerate(['cg_upd_local','cg_upd_remote','cg_upd_expand','cg_upd_collapse','cg_upd_more']):
        x=24+i*252;im=composite(key);glyphs.paste(im,(x,80),im)
        big=im.resize((128,128),Image.Resampling.LANCZOS);glyphs.paste(big,(x,150),big)
        d.text((x,310),key.replace('cg_upd_',''),font=font(17),fill='#b5bdc6')
    glyphs.save(out/'updater-glyph-detail.preview.png')
    write_json(OUT/'artwork-preview-index.json',{'previews':saved,'deviceScreenshots':False,'productionGlowsBaked':False})
    print({'artworkSheets':2,'productionAssetsUnchanged':True,'deviceScreenshots':False})
if __name__=='__main__':main()
