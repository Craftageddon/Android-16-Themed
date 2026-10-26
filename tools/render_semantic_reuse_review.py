"""Actual source/donor review cards; invalid name-only matches stay visibly non-art."""
from pathlib import Path
import collections,copy,hashlib,io,json,math,re,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import resvg_py,font
from forge_library import xml,embed

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit';A='{http://schemas.android.com/apk/res/android}'

class SourceRenderer:
    def __init__(self):
        self.declarations=read_json(OUT/'resource-declarations.json');self.index=collections.defaultdict(list)
        for d in self.declarations:self.index[(d['project'],d['resourceRoot'],d['type'],d['name'])].append(d)
    def resolve(self,value,row):
        if not value or not value.startswith('@'):return value
        m=re.fullmatch(r'@(?:(android):)?(\w+)/(\w+)',value);assert m,value
        pkg,typ,name=m.groups();project='frameworks/base' if pkg else row['project'];root='core/res/res' if pkg else row['resourceRoot'];candidates=self.index[(project,root,typ,name)];assert candidates,(row,value)
        # An audit card renders the exact qualifier when present, then the base.
        q=row.get('qualifier','').split('-')[1:]
        def rank(d):
            suffix=d['qualifier'].split('-')[1:];return (suffix==q,all(x in q for x in suffix),-len(set(suffix)-set(q)),len(suffix))
        ranked=sorted(candidates,key=rank,reverse=True);top=rank(ranked[0]);values={x['value'] for x in ranked if rank(x)==top};assert len(values)==1,('Ambiguous path parameter',value,row,values)
        return ranked[0]['value']
    def vector(self,data,row,size=72):
        doc=E.fromstring(data);w=float(self.resolve(doc.get(A+'viewportWidth'),row));h=float(self.resolve(doc.get(A+'viewportHeight'),row));svg=E.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':f'0 0 {w} {h}','width':str(w),'height':str(h)});counter=0;notes=[]
        def opacity(value):
            if not value:return 0
            if value in ['@android:color/transparent','#00000000','@null']:return 0
            if value.startswith('#') and len(value)==9:return int(value[1:3],16)/255
            return 1
        def walk(parent,node):
            nonlocal counter
            if node.tag=='group':
                def f(key,default):return float(self.resolve(node.get(A+key,str(default)),row))
                px=f('pivotX',0);py=f('pivotY',0);g=E.SubElement(parent,'g',{'transform':f"translate({f('translateX',0)+px} {f('translateY',0)+py}) rotate({f('rotation',0)}) scale({f('scaleX',1)} {f('scaleY',1)}) translate({-px} {-py})"})
                for child in node:
                    next_parent=walk(g,child)
                    if next_parent is not None:g=next_parent
            elif node.tag=='clip-path':
                counter+=1;clip=E.SubElement(E.SubElement(svg,'defs'),'clipPath',{'id':'sourceclip'+str(counter)});E.SubElement(clip,'path',{'d':self.resolve(node.get(A+'pathData'),row),'clip-rule':'evenodd' if node.get(A+'fillType')=='evenOdd' else 'nonzero'});g=E.SubElement(parent,'g',{'clip-path':'url(#sourceclip'+str(counter)+')'});return g
            elif node.tag=='path':
                trim=[node.get(A+x,default) for x,default in [('trimPathStart','0'),('trimPathEnd','1'),('trimPathOffset','0')]]
                assert trim==['0','1','0'],('Nontrivial path trim requires native owner review',trim)
                attrs={'d':self.resolve(node.get(A+'pathData'),row),'fill':'#dce4eb','fill-opacity':str(opacity(node.get(A+'fillColor'))*float(node.get(A+'fillAlpha','1'))),'fill-rule':'evenodd' if node.get(A+'fillType')=='evenOdd' else 'nonzero'}
                if node.find('.//gradient') is not None:attrs['fill-opacity']=node.get(A+'fillAlpha','1');notes.append('Gradient normalized for geometry inspection')
                if node.get(A+'strokeColor'):attrs.update({'stroke':'#dce4eb','stroke-width':self.resolve(node.get(A+'strokeWidth','1'),row),'stroke-opacity':str(opacity(node.get(A+'strokeColor'))*float(node.get(A+'strokeAlpha','1'))),'stroke-linecap':node.get(A+'strokeLineCap','butt'),'stroke-linejoin':node.get(A+'strokeLineJoin','miter'),'stroke-miterlimit':node.get(A+'strokeMiterLimit','4')})
                E.SubElement(parent,'path',attrs)
            return parent
        parent=svg
        for node in doc:
            next_parent=walk(parent,node)
            if next_parent is not None:parent=next_parent
        return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(svg,encoding='unicode'),width=size,skip_system_fonts=True))).convert('RGBA'),notes

def main():
    rows=[x for x in read_json(OUT/'semantic-family-ledger.json') if x['previousFilenameCandidates'] and x['baselineFamily']['sourceSet']!='test-or-sample'];assert len(rows)==214
    renderer=SourceRenderer();cards=[];evidence=[];features={x['gitBlobSha1']:x for x in read_json(OUT/'content-evidence.json')}
    old_dirs={'11':'11-forge-symbol-library','17':'17-forge-coverage'}
    for row in rows:
        b=row['baselineFamily'];card=Image.new('RGB',(440,220),'#11171e');draw=ImageDraw.Draw(card);draw.text((12,8),b['name'][:42],font=font(16,True),fill='#eee7d9');draw.text((12,32),b['project'][:48],font=font(12),fill='#b5bdc6');draw.text((12,195),row['familyId'],font=font(12),fill='#b5bdc6');variant=row['evidence'][0];feature=features[variant['gitBlobSha1']];notes=[];rendered=False
        try:
            data=(OUT/feature['object']).read_bytes()
            if feature.get('xmlRoot')=='vector':source,notes=renderer.vector(data,{**b,'qualifier':variant['qualifier']});rendered=True
            elif feature['contentClass']=='Bitmap':
                source=Image.open(io.BytesIO(data)).convert('RGBA');source.thumbnail((84,84));rendered=True;notes.append('Actual source bitmap pixels')
            else:source=None;notes.append('Native '+str(feature.get('xmlRoot',feature['contentClass']))+' contract, not a standalone icon')
            if source:
                source.thumbnail((84,84));card.paste(source,(45+(84-source.width)//2,75),source)
        except Exception as error:notes.append(str(error)[:250]);source=None
        if source is None:draw.text((15,100),'Native structure',font=font(16),fill='#b5bdc6')
        donor_paths=[]
        for i,asset in enumerate(row['previousFilenameCandidates'].split(';')):
            iteration,asset_id=asset.split('/');p=ROOT/'iterations'/old_dirs[iteration]/'masters'/f'{asset_id}.svg';doc=E.parse(p).getroot()
            for image_node in doc.findall('.//{http://www.w3.org/2000/svg}image'):
                href=image_node.get('href') or image_node.get('{http://www.w3.org/1999/xlink}href')
                if href and not href.startswith('data:'):image_node.set('href','data:image/png;base64,'+__import__('base64').b64encode((p.parent/href).read_bytes()).decode())
            im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(doc,encoding='unicode'),width=80,skip_system_fonts=True))).convert('RGBA');card.paste(im,(200+i*100,72),im);donor_paths.append({'assetId':asset,'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        draw.text((32,170),'Source',font=font(13),fill='#b5bdc6');draw.text((195,170),'Forge compact / detailed',font=font(13),fill='#b5bdc6');cards.append(card)
        evidence.append({'familyId':row['familyId'],'source':b,'variants':row['evidence'],'renderedSourceVariant':variant['path'],'sourceGeometryRendered':rendered,'notes':notes,'donors':donor_paths,'sourceRenderScope':'Actual path/group/clip geometry or bitmap; vector tint normalized. Audit card is not an Android native-pixel claim.'})
    for start in range(0,len(cards),24):
        sheet=Image.new('RGB',(1800,1440),'#080c11');draw=ImageDraw.Draw(sheet);draw.text((20,15),'FORGE / SOURCE-TO-DONOR SEMANTIC REVIEW',font=font(27,True),fill='#eee7d9');draw.text((20,56),'Source geometry and exact Forge donor files. Native structures are not accepted as icon matches.',font=font(18),fill='#b5bdc6')
        for i,card in enumerate(cards[start:start+24]):sheet.paste(card,(10+i%4*450,100+i//4*220))
        sheet.save(OUT/'previews'/f'reuse-review-{start//24+1:02}.png')
    write_json(OUT/'reuse-review-evidence.json',evidence);print(json.dumps({'candidateFamilies':len(rows),'sourceGeometryRendered':sum(x['sourceGeometryRendered'] for x in evidence),'structuralOrRendererExceptions':[{'familyId':x['familyId'],'name':x['source']['name'],'notes':x['notes']} for x in evidence if not x['sourceGeometryRendered']],'reviewSheets':math.ceil(len(cards)/24)}))

if __name__=='__main__':main()
