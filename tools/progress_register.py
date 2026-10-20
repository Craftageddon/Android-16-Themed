"""Retain all roadmap rows and add bounded evidence without declaring packages complete."""
from pathlib import Path
import csv
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'roadmap/Rework_Coverage_Queue.csv').open(encoding='utf-8-sig',newline='')))
partial={**{f'ES-{i:03}':'18-family material/state pilot; partial family coverage only' for i in range(2,11)},
 'TH-001':'Prompt specimen and unmeasured mapping template',
 'TH-002':'Focus/selection design and reference state tests',
 'TH-003':'Calibration screen composition only',
 'TH-005':'Explicit capture/release design contract only',
 'TH-008':'Profile identity design contract only',
 'TH-010':'Lower-screen control-center composition only',
 'TH-011':'Launch display composition only',
 'TH-015':'Fan/performance UI specimen only; no backend',
 'TH-017':'Ember lights UI specimen only; no physical lighting tested',
 'LOS-004':'Owner map and standalone prefixed XML resource samples',
 'LOS-005':'Rendering handoff and shade composition only',
 'LOS-010':'Charging visual concept only',
 'LOS-011':'Four resource files compile; no module or full-ROM build'}
target=root/'roadmap/Design_Progress_2026-10-20.csv'
with target.open('w',newline='',encoding='utf-8') as stream:
 writer=csv.DictWriter(stream,fieldnames=['id','family_or_surface','design_status','evidence_scope','native_integrated','device_verified'])
 writer.writeheader()
 for row in rows:writer.writerow({'id':row['id'],'family_or_surface':row['family_or_surface'],'design_status':'Partial pilot / handoff' if row['id'] in partial else 'Planned','evidence_scope':partial.get(row['id'],'No new implementation in these checkpoints'),'native_integrated':'No','device_verified':'No'})
assert len(rows)==103
print('Recorded all 103 roadmap IDs; none marked complete or device verified.')
