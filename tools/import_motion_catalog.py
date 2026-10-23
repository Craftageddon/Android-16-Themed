"""Import exact retained motion definitions without executing their source.

Read UTF-8 explicitly: platform-default Windows decoding corrupts timing labels.
Legacy atlas positions are retained for reconciliation, never treated as new art.
"""
from pathlib import Path
import argparse,hashlib,json,re

EXPECTED='f5c5561735c081e155533bf3ff2758559388e8e167df386e989c6837fe366a74'

def parse(source):
 data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==EXPECTED,'Original catalog changed; review before importing';s=data.decode('utf8');rows=[]
 for block in re.findall(r'        MotionRecipe\(\n(.*?)\n        \),',s,re.S):
  def string(key):
   m=re.search(r'\b'+key+r' = ("(?:\\.|[^"\\])*")',block);return json.loads(m[1]) if m else None
  def enum(key,type):return re.search(r'\b'+key+r' = '+type+r'\.(\w+)',block)[1]
  repeat=re.search(r'\brepeat = MotionRepeat\.(Once|Loop|Count\(\d+\))',block)[1]
  layers=[{'atlas':m[0],'cell':int(m[1]),'x':float(m[2]),'y':float(m[3]),'scale':float(m[4])} for m in re.findall(r'MotionLayer\(MotionAtlas\.(\w+), (\d+), (-?[\d.]+)f, (-?[\d.]+)f, ([\d.]+)f\)',block)]
  label_match=re.search(r'\blabel = MotionLabel\(("(?:\\.|[^"\\])*")',block);label=json.loads(label_match[1]) if label_match else None
  # The old lightning letter was decorative icon text. New production uses a
  # vector glyph and an English status label, keeping the original for audit.
  visible_label={'ϟ':'On'}.get(label,label)
  for value in [string('title'),string('description'),visible_label or '']:
   assert all(not c.isalpha() or c.isascii() for c in value),('Non-English visible text',value)
  rows.append({'id':string('id'),'title':string('title'),'description':string('description'),'category':enum('category','MotionCategory'),'originalScope':enum('scope','MotionScope'),'kind':enum('kind','MotionKind'),'durationMillis':int(re.search(r'durationMillis = (\d+)',block)[1]),'timingLabel':string('timingLabel'),'repeat':{'mode':'loop' if repeat=='Loop' else 'count','count':int(re.search(r'\d+',repeat)[0]) if repeat.startswith('Count') else 1},'legacyLayers':layers,'originalLabel':label,'label':visible_label,'controllerButtons':'controllerButtons = true' in block,'meter':'meter = true' in block,'longPressCharge':'longPressCharge = true' in block})
 assert len(rows)==len({r['id'] for r in rows})==114
 assert len({r['kind'] for r in rows})==46 and len({r['category'] for r in rows})==11
 assert next(r for r in rows if r['id']=='lock-screen-aod-pulse')['timingLabel']=='850 ms ×2'
 return {'sourceVersion':'v7','sourceFile':source.name,'sourceSha256':EXPECTED,'encoding':'UTF-8','recipeCount':114,'authoredLocale':'en-US','nativeTarget':'LineageOS 24.0 / AYN odin2thor','scope':'Retained recipes for explicit Reference Forge reconciliation. Import does not establish implemented motion or target acceptance.','recipes':rows}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();report=parse(a.source);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'recipes':len(report['recipes']),'kinds':len({r['kind'] for r in report['recipes']}),'sha256':EXPECTED,'encoding':'UTF-8','out':str(a.out)}))
