'''Offline asset-layer review; source policy outputs are executed separately.'''
from pathlib import Path
import io,json,math,base64,xml.etree.ElementTree as E
from forge_library import layer,raster
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font
from build_scalable_frames import stretch
OUT=ROOT/'iterations/26-gallery-workflows';RES=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res/drawable-mdpi'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol'];COLORS=['#dc5920','#ff4908','#ff5b0b','#ffd083','#d5e7f2','#ffe5bc']
def compose(key,state='cold',size=None,detail=False):
    gain={'cold':[1,0,0,0,0,0,0],'on':[1,.32,.72,1,.82,0,1],'focused':[1,0,0,0,0,1,0],'on-locked':[.42,.192,.432,.6,.492,0,.6]}[state]
    out=None
    for i,name in enumerate(LAYERS):
        p=next(RES.glob(key+'_'+name+'.*'))
        if detail:
            root=E.fromstring((OUT/'masters'/(key+'.svg')).read_bytes())
            texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode()
            im=raster(layer(root,name),96,texture)
        else:im=Image.open(p).convert('RGBA')
        if p.name.endswith('.9.png') and not detail:im=stretch(im,size or (im.width-2,im.height-2))
        elif size:im=im.resize(size,Image.Resampling.LANCZOS)
        if out is None:out=Image.new('RGBA',im.size)
        if i:
            tint=Image.new('RGBA',im.size,COLORS[i-1]);tint.putalpha(im.getchannel('A').point(lambda v:round(v*gain[i])));im=tint
        else:im.putalpha(im.getchannel('A').point(lambda v:round(v*gain[i])))
        out.alpha_composite(im)
    return out
def main():
    assert not (OUT/'complete-assets.zip').exists()
    rows=read_json(OUT/'gallery-art-components.json');folder=OUT/'previews';folder.mkdir(exist_ok=True)
    records=[]
    for batch in range(math.ceil(len(rows)/20)):
        group=rows[batch*20:(batch+1)*20];sheet=Image.new('RGB',(1320,1100),'#080c11');d=ImageDraw.Draw(sheet)
        d.text((20,16),'FORGE / GALLERY LAYER TREATMENTS '+str(batch+1),font=font(26),fill='#eee7d9')
        d.text((20,54),'96px editable-master samples with native 24dp strips / not device screenshots',font=font(16),fill='#b5bdc6')
        for at,row in enumerate(group):
            x=20+(at%4)*330;y=100+(at//4)*195
            label=row['id'].removeprefix('cg_gl_').replace('_',' ')
            d.text((x,y),label,font=font(15),fill='#eee7d9')
            for j,state in enumerate(['cold','on']):
                key=row['id'];im=compose(key,state,detail=True)
                if im.width!=96:im=im.resize((96,96),Image.Resampling.LANCZOS)
                sheet.paste(im,(x+j*145,y+27),im)
                d.text((x+j*145,y+131),'Cold layer' if state=='cold' else 'Light masks',font=font(13),fill='#b5bdc6')
            if row['logicalSize']==24:
                tiny=compose(row['id']);sheet.paste(tiny,(x,y+157),tiny);d.text((x+36,y+160),'24dp at 1x',font=font(12),fill='#8f9ba7')
            records.append({'family':row['id'],'sheet':batch+1,'logicalSize':row['logicalSize'],'deviceScreenshot':False})
        sheet.save(folder/('gallery-layer-treatments-'+str(batch+1)+'.preview.png'))
    matrix=Image.new('RGB',(1320,720),'#080c11');d=ImageDraw.Draw(matrix)
    d.text((20,16),'FORGE / GALLERY NATIVE CONTROL MATERIALS',font=font(26),fill='#eee7d9')
    for i,(key,title,size) in enumerate([('cg_gl_media_frame','Transparent photo rim',(240,180)),('cg_gl_button','Momentary action housing',(240,80)),('cg_gl_switch_track','Switch track',(104,64))]):
        y=[90,350,550][i]
        for j,state in enumerate(['cold','focused','on','on-locked']):
            im=compose(key,state,size);x=20+j*330
            matrix.paste(im,(x,y),im);d.text((x,y+size[1]+10),title+' / '+state,font=font(13),fill='#b5bdc6')
    matrix.save(folder/'gallery-control-materials.preview.png')
    write_json(OUT/'artwork-preview-index.json',{'components':records,'materialSheet':'previews/gallery-control-materials.preview.png','assetLayerSamplesNotNativeUiStates':True,'deviceScreenshots':False})
    print({'assetSheets':math.ceil(len(rows)/20),'controlSheets':1,'productionAssetsModified':False})
if __name__=='__main__':main()
