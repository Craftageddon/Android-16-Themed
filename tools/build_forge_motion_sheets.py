"""Build review sheets and an exact sampled-frame disposition ledger."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw,ImageFont
def build(root):
 rows=json.loads((root/'reconciliation.json').read_text(encoding='utf8'));bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',17);large=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
 for start in range(0,len(rows),20):
  board=Image.new('RGB',(1440,1350),'#080c11');draw=ImageDraw.Draw(board)
  for i,row in enumerate(rows[start:start+20]):
   phase='037' if row['id']=='cooling-fan-speed' else '050';im=Image.open(root/'desktop-frames'/f"{row['id']}.{phase}.on.png").convert('RGB');im.thumbnail((360,230));x=i%4*360;y=i//4*270;board.paste(im,(x,y+32));draw.text((x+8,y+7),row['id'],font=bold,fill='#eee7d9')
  board.save(root/'previews'/f'catalog-review-{start//20+1:02}.png')
 ids=['long-press','loading-shimmer-sync','live-update-milestones','thermal-throttling-state','analog-trigger-calibration','fingerprint-authentication','face-scan-framing','system-update-cycle','face-button-cluster']
 for start in range(0,len(ids),4):
  board=Image.new('RGB',(1440,1020),'#080c11');draw=ImageDraw.Draw(board)
  for i,id in enumerate(ids[start:start+4]):
   board.paste(Image.open(root/'desktop-frames'/f'{id}.050.on.png').convert('RGB'),((i%2)*720,(i//2)*510+40));draw.text(((i%2)*720+20,(i//2)*510+9),id,font=large,fill='#eee7d9')
  board.save(root/'previews'/f'channel-review-{start//4+1}.png')
 board=Image.new('RGB',(1440,2320),'#080c11');draw=ImageDraw.Draw(board);draw.text((24,15),'Craftageddon Ember Steel - native English wording',font=large,fill='#eee7d9');draw.text((24,52),'Cold / off',font=large,fill='#b5bdc6');draw.text((744,52),'Selected / on',font=large,fill='#b5bdc6')
 for i,(id,title) in enumerate([('keyboard-ime-slide','English keyboard'),('toast-snackbar','Saved and undo'),('thermal-throttling-state','Live temperature'),('live-update-milestones','Live update progress')]):
  y=150+i*540;draw.text((24,y-36),title,font=large,fill='#eee7d9')
  for col,state in enumerate(['off','on']):board.paste(Image.open(root/'desktop-frames'/f'{id}.050.{state}.png').convert('RGB'),(col*720,y))
 board.save(root/'previews/english-controls-cold-selected.png')
 ledger=[]
 for r in rows:
  files=sorted((root/'desktop-frames').glob(r['id']+'.*.on.png'));hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files];steady=r['disposition']=='steady-status';assert (len(set(hashes))==1 if steady else len(set(hashes))>1),r['id']
  ledger.append({'id':r['id'],'disposition':r['disposition'],'sampledSelectedFrames':[{'file':p.relative_to(root).as_posix(),'sha256':h} for p,h in zip(files,hashes)],'distinctSelectedPoses':len(set(hashes)),'review':'Representative pose on catalog sheet; automated inventory and dedicated semantic checks. Not browser or target playback.','nativeIntegrated':False,'deviceVerified':False})
 (root/'verification/evidence/desktop-dispositions.json').write_text(json.dumps({'date':'2026-10-23','recipes':ledger,'animated':sum(r['disposition']!='steady-status' for r in rows),'steady':sum(r['disposition']=='steady-status' for r in rows)},indent=2)+'\n')
 print(json.dumps({'reviewedRepresentativePoses':len(rows),'animated':103,'steadyStatus':11,'catalogSheets':6,'sampleFrames':1140}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
