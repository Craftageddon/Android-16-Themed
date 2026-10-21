"""Live-text controller and keyboard compositions using the reusable control masters."""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as ET
from build_pilot import SVG,el,add,render
from forge_library import state,unique,xml
from build_screens import inline_images

p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve();folder=root/'examples';folder.mkdir(exist_ok=False);states=json.loads((root/'runtime-style.json').read_text())['sampleStates'];counter=0
def text(r,x,y,value,size=20,color='#eee7d9',anchor='start'):
 add(r,'text',x=x,y=y,fill=color,font_family='sans-serif',font_size=size,text_anchor=anchor).text=value
def canvas(w,h,title,sub):
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(r,'title').text=title;add(r,'rect',width=w,height=h,fill='#090d12');text(r,35,45,title,30);text(r,35,82,sub,18,'#b5bdc6');return r
def cap(r,name,label,x,y,w,h,st='off',size=18):
 global counter
 q=ET.parse(root/'masters'/f'control-{name}.svg').getroot();q=state(q,states[st]);counter+=1;q=unique(q,f'cap{counter}-');q.set('x',str(x));q.set('y',str(y));q.set('width',str(w));q.set('height',str(h));r.append(q);text(r,x+w/2,y+h/2+size*.34,label,size,anchor='middle')
labels=['A','B','X','Y','L1','R1','L2','R2','L3','R3','Select','Start','Up','Down','Left','Right']
r=canvas(1600,900,'CRAFTAGEDDON / CONTROLLER PROMPT FAMILY','Cold and selected examples. Logical labels; physical Thor mapping is not verified.')
for i,label in enumerate(labels):
 x=35+i%8*195;y=130+i//8*340
 name='controller_cap' if len(label)==1 else 'trigger_cap' if label in ['L2','R2'] else 'shoulder_cap'
 for st,yy in [('off',y),('on',y+135)]:cap(r,name,label,x+12,yy,156,100,st,22 if len(label)<=2 else 17)
text(r,35,855,'Reusable unlabelled cap layers are production art; these labels stay editable/live.',21,'#b5bdc6')
(folder/'controller-prompts.svg').write_text(xml(r),encoding='utf8');(root/'previews/controller-prompts.png').write_bytes(render(inline_images(r,folder)))
r=canvas(1160,600,'CRAFTAGEDDON / KEYBOARD MATERIAL STUDY','Live labels on the shared letter, modifier, enter and space-key artwork. No IME is implemented.')
rows=[list('1234567890'),list('QWERTYUIOP'),list('ASDFGHJKL'),['Shift',*list('ZXCVBNM'),'Back'],['Ctrl','Alt','Space','Enter']]
for row,labels2 in enumerate(rows):
 y=120+row*85;x=35+(20 if row==2 else 0)
 for label in labels2:
  if label=='Space':name,w='keyboard_space',570
  elif label in ['Enter','Shift','Back','Ctrl','Alt']:name,w=('keyboard_enter' if label=='Enter' else 'keyboard_modifier'),110
  else:name,w='keyboard_letter',96
  cap(r,name,label,x,y,w,70,'on' if label=='Enter' else 'off',21 if len(label)==1 else 16);x+=w+9
(folder/'keyboard-layout.svg').write_text(xml(r),encoding='utf8');(root/'previews/keyboard-layout.png').write_bytes(render(inline_images(r,folder)))
print(json.dumps({'controllerLabels':16,'keyboardRows':5,'editableCompositions':2,'hardwareMappingVerified':False}))
