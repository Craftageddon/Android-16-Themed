"""Apply explicit evidence without resetting earlier roadmap progress."""
from pathlib import Path
import argparse,csv,json
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--updates',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
with a.base.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
assert len(rows)==103 and len({r['id'] for r in rows})==103
updates=json.loads(a.updates.read_text(encoding='utf8'));assert set(updates)<={r['id'] for r in rows}
for patch in updates.values():assert set(patch)<={'design_status','evidence_scope'},'Integration/device flags need a separate verified decision'
for row in rows:
 if row['id'] in updates:row.update(updates[row['id']])
with a.out.open('w',newline='',encoding='utf8') as stream:
 writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps({'retainedRoadmapRows':len(rows),'explicitlyUpdated':list(updates),'untouchedRows':len(rows)-len(updates)}))
