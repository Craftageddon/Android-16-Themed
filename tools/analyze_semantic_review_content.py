"""Parse every acquired resource and record content evidence, not reuse approvals."""
from pathlib import Path
import collections,concurrent.futures,gzip,hashlib,io,json,re,struct,xml.etree.ElementTree as ET,zipfile
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit'
REF=re.compile(r'(?P<sig>[@?])(?:(?P<pkg>[\w.]+):)?(?P<type>[A-Za-z_][\w.]*)/(?P<name>[\w.]+)')
AN='{http://schemas.android.com/apk/res/android}'

def without_json_comments(text):
    """Remove Android JSON comments without changing quoted strings or URLs."""
    result=[];i=0;quoted=False;escaped=False
    while i<len(text):
        c=text[i]
        if quoted:
            result.append(c)
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
            i+=1;continue
        if c=='"':quoted=True;result.append(c);i+=1;continue
        if text.startswith('//',i):
            end=text.find('\n',i);i=len(text) if end<0 else end;continue
        if text.startswith('/*',i):
            end=text.find('*/',i+2);assert end>=0,'Unclosed JSON comment';i=end+2;continue
        result.append(c);i+=1
    return ''.join(result)

def describe(item,example):
    p=OUT/item['object'];data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==item['sha256']
    suffix=Path(example['path']).suffix.lower();result={**item,'format':suffix,'sourceKinds':example['kind'],'references':[]}
    if not data:
        result.update({'contentClass':'Empty upstream resource','visiblePayload':False,'reviewRequirement':'Preserve as an empty upstream slot unless an owner-specific replacement is explicitly designed; empty bytes do not prove a missing visible graphic'})
    elif example.get('kind')=='owner-source':
        text=data.decode('utf8');result.update({'contentClass':'Native owner source','styleAttributes':sorted(set(re.findall(r'R\.attr\.([A-Za-z0-9_]+)',text))),'resourceConstants':sorted(set(re.findall(r'R\.(?:drawable|layout|string|color)\.([A-Za-z0-9_]+)',text))),'text':text})
    elif suffix=='.gif':
        assert data[:6] in [b'GIF87a',b'GIF89a'];width,height=struct.unpack('<HH',data[6:10]);result.update({'contentClass':'Bitmap stress fixture' if example['sourceSet']=='test-or-sample' else 'GIF','size':[width,height],'headerVerified':True,'fullPixelDecode':'Not run for oversized stress fixture','sourceSet':example['sourceSet']})
        assert example['sourceSet']=='test-or-sample' or width*height<4000000,'Large non-test GIF needs bounded decoder review'
    elif suffix=='.xml':
        root=ET.fromstring(data);nodes=list(root.iter());result.update({'contentClass':'XML','xmlRoot':root.tag,'xmlRootAttributes':dict(root.attrib),'nodeCount':len(nodes),'elementCounts':dict(collections.Counter(x.tag for x in nodes)),'references':[m.groupdict() for m in REF.finditer(data.decode('utf8'))],'stateItems':[],'paths':[],'liveTextReferences':[],'namedValues':[],'nativeUses':[],'geometryNodes':[]})
        if root.tag=='resources':
            for n in root:
                if n.get('name'):
                    result['namedValues'].append({'type':n.get('type',n.tag) if n.tag=='item' else n.tag,'declarationTag':n.tag,'name':n.get('name'),'text':''.join(n.itertext()).strip(),'attributes':dict(n.attrib),'children':[{'tag':c.tag,'attributes':dict(c.attrib),'text':''.join(c.itertext()).strip()} for c in n]})
        for n in nodes:
            if n.tag in ['item','target']:
                states={k.split('}')[-1]:v for k,v in n.attrib.items() if k.split('}')[-1].startswith('state_') or k.split('}')[-1] in ['minLevel','maxLevel','id','drawable','animation','name']}
                if states:result['stateItems'].append(states)
            if n.tag in ['path','clip-path']:
                result['paths'].append({'tag':n.tag,'attributes':dict(n.attrib)})
            if n.get(AN+'text') is not None:result['liveTextReferences'].append(n.get(AN+'text'))
            for attribute,value in n.attrib.items():
                for match in REF.finditer(value):result['nativeUses'].append({'element':n.tag,'attribute':attribute,'reference':match.groupdict()})
            if n.tag in ['size','padding','corners','gradient','stroke','solid','scale','group','clip','shape']:
                result['geometryNodes'].append({'tag':n.tag,'attributes':dict(n.attrib)})
        result['geometryDeclarationSha256']=hashlib.sha256(json.dumps([{'tag':n.tag,'attrs':{k:v for k,v in n.attrib.items() if k.split('}')[-1] in ['pathData','viewportWidth','viewportHeight','width','height','rotation','pivotX','pivotY','translateX','translateY','scaleX','scaleY','fillType']}} for n in nodes if n.tag in ['vector','group','path','clip-path']],sort_keys=True).encode()).hexdigest() if root.tag=='vector' else None
    elif suffix in ['.png','.webp','.jpg','.jpeg']:
        with Image.open(io.BytesIO(data)) as source:
            source.load();im=source.convert('RGBA');alpha=im.getchannel('A');r,g,b,_=im.split();small=im.copy();small.thumbnail((64,64));colors=im.getcolors(257);bounds=alpha.getbbox();hist=alpha.histogram();total=im.width*im.height
            result.update({'contentClass':'Bitmap','imageFormat':source.format,'mode':source.mode,'size':list(im.size),'alphaBounds':list(bounds) if bounds else None,'transparentPixels':hist[0],'opaquePixels':hist[255],'nonzeroAlphaPixels':total-hist[0],'neutralRgb':r.tobytes()==g.tobytes()==b.tobytes(),'paletteColors':len(colors) if colors is not None else 'more than256','alphaSha256':hashlib.sha256(alpha.tobytes()).hexdigest(),'rgbaSha256':hashlib.sha256(im.tobytes()).hexdigest(),'thumbnailRgbaSha256':hashlib.sha256(small.tobytes()).hexdigest(),'ninePatch':example['path'].endswith('.9.png')})
            if result['ninePatch']:
                edges={'top':[im.getpixel((x,0)) for x in range(im.width)],'left':[im.getpixel((0,y)) for y in range(im.height)],'bottom':[im.getpixel((x,im.height-1)) for x in range(im.width)],'right':[im.getpixel((im.width-1,y)) for y in range(im.height)]}
                result['ninePatchMarkers']={key:[i for i,pixel in enumerate(row) if pixel==(0,0,0,255)] for key,row in edges.items()}
                result['ninePatchOtherEdgeColors']={key:sorted(set(row)-{(0,0,0,0),(0,0,0,255)}) for key,row in edges.items()}
    elif suffix=='.json':
        try:obj=json.loads(data);result['jsonDialect']='Strict JSON'
        except json.JSONDecodeError:obj=json.loads(without_json_comments(data.decode('utf8')));result['jsonDialect']='Android lenient JSON with comments'
        result['contentClass']='JSON';result['jsonTopKeys']=list(obj) if isinstance(obj,dict) else [];result['lottie']=isinstance(obj,dict) and 'layers' in obj and ('fr' in obj or 'v' in obj)
        if result['lottie']:
            result['lottieLayers']=[{'name':x.get('nm'),'type':x.get('ty'),'start':x.get('ip'),'end':x.get('op'),'refId':x.get('refId')} for x in obj['layers']];result['frameRate']=obj.get('fr');result['range']=[obj.get('ip'),obj.get('op')];result['assets']=[{'id':x.get('id'),'path':x.get('p'),'embedded':x.get('e'),'layerCount':len(x.get('layers',[]))} for x in obj.get('assets',[])];result['textLayers']=[x.get('t') for x in obj['layers'] if x.get('ty')==5]
    elif suffix=='.zip':
        if not zipfile.is_zipfile(io.BytesIO(data)):
            assert example['sourceSet']=='test-or-sample','Malformed production ZIP';result.update({'contentClass':'Intentional malformed test fixture','headerHex':data[:32].hex(),'declaredType':'ZIP','actualType':'Non-ZIP payload','sourceSet':example['sourceSet']})
        else:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                assert z.testzip() is None;result['contentClass']='ZIP';result['members']=[{'path':n.filename,'bytes':n.file_size,'crc32':n.CRC} for n in z.infolist()]
    elif suffix=='.mp4':
        assert b'ftyp' in data[:64];result.update({'contentClass':'Video','headerHex':data[:32].hex(),'requiresTemporalOwnerReview':True})
    else:result.update({'contentClass':'Text/build contract','text':data.decode('utf8')})
    return result

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Preserve packaged checkpoints'
    acquisition=read_json(OUT/'source-acquisition.json');assert acquisition['allSourceBytesAcquired']
    files=read_json(INPUT/'resource-files.json');examples={x['gitBlobSha1']:x for x in files};objects={x['gitBlobSha1']:x for x in read_json(OUT/'source-objects.json')};aux=read_json(OUT/'auxiliary-source-files.json') if (OUT/'auxiliary-source-files.json').exists() else []
    for row in aux:
        if row['gitBlobSha1'] not in objects:objects[row['gitBlobSha1']]={**row,'exampleProject':row['project'],'examplePath':row['path'],'sourceCount':1};examples[row['gitBlobSha1']]=row
    objects=list(objects.values());results=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pending={pool.submit(describe,x,examples[x['gitBlobSha1']]):x['gitBlobSha1'] for x in objects}
        for job in concurrent.futures.as_completed(pending):
            try:results.append(job.result())
            except Exception as e:errors.append({'object':pending[job],'error':str(e)})
    results.sort(key=lambda x:x['gitBlobSha1']);write_json(OUT/'content-evidence.json',results);write_json(OUT/'content-parse-errors.json',errors)
    summary={'date':'2026-10-26','indexedFiles':len(files),'auxiliaryFileRecords':len(aux),'uniqueObjects':len(objects),'parsedObjects':len(results),'parseErrors':len(errors),'contentClasses':dict(collections.Counter(x['contentClass'] for x in results)),'xmlRoots':dict(collections.Counter(x['xmlRoot'] for x in results if x['contentClass']=='XML')),'meaningOfThisPass':'Content evidence only. Parsing is not semantic approval, visual acceptance or completion of this goal.'};write_json(OUT/'content-summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='xmlRoots'}))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
