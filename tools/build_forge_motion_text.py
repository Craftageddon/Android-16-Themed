"""Export authored English motion wording as native Android resources."""
from pathlib import Path
import argparse,json,re,xml.etree.ElementTree as ET
FORMATS={'percent':'%1$d%%','temperature':'%1$d C','gain':'%1$s dB','selectionCount':'%1$d selected','angle':'%1$d deg','milestone':'Step %1$d of %2$d'}
def build(root):
 catalog=json.loads((root/'source/retained-catalog.json').read_text(encoding='utf8'))['recipes'];bindings=json.loads((root/'reconciliation.json').read_text(encoding='utf8'));entries=[];doc=ET.Element('resources')
 def put(key,text,owner,formatted=False):
  assert all(not c.isalpha() or c.isascii() for c in text),(key,text)
  entries.append({'key':key,'text':text,'owner':owner,'formatted':formatted})
  ET.SubElement(doc,'string',name=key,formatted=str(formatted).lower()).text=text.replace('\\','\\\\').replace("'","\\'").replace('"','\\"')
 for old,row in zip(catalog,bindings):
  prefix='motion_'+row['id'].replace('-','_')
  for k in ['title','description']:
   put(prefix+'_'+k,row.get(k,old[k]),row['id'])
  if row.get('label'):put(prefix+'_caption',row['label'],row['id'])
  for i,l in enumerate(row['newLayers']):
   for j,label in enumerate(l.get('liveLabels',[])):
    if label.get('text'):put(prefix+f'_layer_{i}_label_{j}',label['text'],row['id'])
 for key,value in FORMATS.items():put('motion_value_'+key.lower(),value,'shared live value',True)
 target=root/'native-text/res/values';target.mkdir(parents=True,exist_ok=True);ET.indent(doc,space='  ');(target/'strings.xml').write_bytes(ET.tostring(doc,encoding='utf-8',xml_declaration=True))
 (root/'english-text-catalog.json').write_text(json.dumps({'authoredLocale':'en-US','scope':'Current titles, descriptions, captions, static live labels and native formatting resources; no historical originalLabel text','labels':entries},indent=2)+'\n',encoding='utf8');print(json.dumps({'locale':'en-US','nativeStrings':len(entries)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
