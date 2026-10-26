"""Render parsed upstream VectorDrawable geometry as an audit reference sheet."""
from pathlib import Path
import json,xml.etree.ElementTree as E
from audit_os_resource_coverage import OUT
from build_pilot import resvg_py
A='{http://schemas.android.com/apk/res/android}'

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Never rewrite a packaged checkpoint'
    rows=json.loads((OUT/'confirmed-glyph-gaps.json').read_text());paths={n.get('name'):''.join(n.itertext()).strip() for n in E.parse(OUT/'source-evidence/frameworks/base/packages/SystemUI/res/values/paths.xml').getroot()}
    def resolve(value):
        if value.startswith('@string/'):return paths[value.split('/',1)[1]]
        assert not value.startswith('@'),value
        return value
    svg=E.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':'1440','height':'1120','viewBox':'0 0 1440 1120'});E.SubElement(svg,'rect',{'width':'1440','height':'1120','fill':'#080c11'})
    def text(x,y,value,size=21,color='#eee7d9'):
        E.SubElement(svg,'text',{'x':str(x),'y':str(y),'fill':color,'font-family':'Segoe UI','font-size':str(size)}).text=value
    text(26,42,'CRAFTAGEDDON / VERIFIED SOURCE GLYPH GAPS',29)
    text(26,75,'16 semantic families needing Forge treatment or approved reuse. Source tint normalized for review.',18,'#b5bdc6')
    resolved=0
    def walk(parent,node):
        nonlocal resolved
        if node.tag=='group':
            px=node.get(A+'pivotX','0');py=node.get(A+'pivotY','0');tx=float(node.get(A+'translateX','0'))+float(px);ty=float(node.get(A+'translateY','0'))+float(py)
            g=E.SubElement(parent,'g',{'transform':f"translate({tx} {ty}) rotate({node.get(A+'rotation','0')}) scale({node.get(A+'scaleX','1')} {node.get(A+'scaleY','1')}) translate(-{px} -{py})"})
            for child in node:walk(g,child)
        elif node.tag=='clip-path':
            clip_id='clip'+str(resolved);resolved+=1;defs=E.SubElement(parent,'defs');clip=E.SubElement(defs,'clipPath',{'id':clip_id});E.SubElement(clip,'path',{'d':resolve(node.get(A+'pathData'))});parent.set('clip-path','url(#'+clip_id+')')
        elif node.tag=='path':
            data=resolve(node.get(A+'pathData'));assert data and '@' not in data
            attrs={'d':data,'fill':'#dce4eb' if node.get(A+'fillColor') and node.get(A+'fillColor') not in ['#00000000','@android:color/transparent'] else 'none','fill-opacity':node.get(A+'fillAlpha','1'),'fill-rule':'evenodd' if node.get(A+'fillType')=='evenOdd' else 'nonzero'}
            if node.get(A+'strokeColor'):attrs.update({'stroke':'#dce4eb','stroke-width':node.get(A+'strokeWidth','1'),'stroke-opacity':node.get(A+'strokeAlpha','1'),'stroke-linecap':node.get(A+'strokeLineCap','butt'),'stroke-linejoin':node.get(A+'strokeLineJoin','miter')})
            E.SubElement(parent,'path',attrs);resolved+=1
    for i,row in enumerate(rows):
        x=i%4*360;y=110+i//4*244;label=row['label'].split(' - ')[0];text(x+22,y+25,row['id']+'  '+label,21)
        doc=E.parse(OUT/row['evidence']['saved']).getroot();w=float(doc.get(A+'viewportWidth'));h=float(doc.get(A+'viewportHeight'));scale=min(100/w,100/h)
        group=E.SubElement(svg,'g',{'transform':f'translate({x+130} {y+63}) scale({scale})'})
        for n in doc:walk(group,n)
        name=Path(row['evidence']['path']).stem;text(x+22,y+203,name,15,'#b5bdc6')
    text(26,1100,'These are existing upstream references, not newly redesigned assets or screenshots from a Thor.',17,'#b5bdc6')
    out=OUT/'previews';out.mkdir(exist_ok=True);source=E.tostring(svg,encoding='unicode');(out/'confirmed-source-glyph-gaps.svg').write_text(source,encoding='utf8')
    data=resvg_py.svg_to_bytes(svg_string=source,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI');(out/'confirmed-source-glyph-gaps.png').write_bytes(data)
    print(json.dumps({'renderedFamilies':len(rows),'resolvedGeometryNodes':resolved,'unresolvedPathStrings':0,'nativePixelParity':'NOT CLAIMED - tint normalized audit sheet, not Android rendering'}))

if __name__=='__main__':main()
