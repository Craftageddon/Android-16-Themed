"""Inventory every retained byte-distinct source without pretending automatic labels are final."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,re

RULES=[('ES-044',r'lockscreen|unlock|biometric|fingerprint|pin_key|pattern_node|pin_dot'),('ES-048',r'keyboard|spacebar|backspace|shift|key_enter|key_letter'),('ES-022',r'notification'),('ES-020',r'context_menu|menu_item|tooltip|dropdown'),('ES-023',r'dialog|confirmation|toast|compact_sheet|bottom_sheet'),('ES-011',r'primary_button|secondary_button|destructive_button|button_frame'),('ES-012',r'icon_container|app_socket|icon_socket|app_frame'),('ES-013',r'toggle|switch'),('ES-014',r'checkbox|radio_button|selection_frame|check_circle'),('ES-015',r'slider|thumb|vertical_rail'),('ES-016',r'progress|spinner'),('ES-017',r'segmented|tab_|section_header'),('ES-018',r'text_field|search_field|input_field'),('ES-019',r'list_row|settings_row|disclosure'),('ES-021',r'card|panel|widget_frame'),('ES-030',r'battery|charge|charging'),('ES-031',r'wifi|wi_fi|cellular|signal|sim_|esim|mobile_data|network_|4g|5g|lte'),('ES-032',r'bluetooth|nfc|hotspot|cast|airplane'),('ES-033',r'camera|microphone|privacy|location|vpn'),('ES-034',r'audio|sound|volume|alarm|dnd|mute|headset|vibrat|music'),('ES-035',r'usb|download|upload|sync|storage'),('ES-036',r'controller|mouse|gamepad|trigger|stick'),('ES-037',r'display|screen_route|screen_swap|split'),('ES-038',r'fan|performance|thermal|temperature'),('ES-028',r'back|home|recents|navigation|gesture'),('ES-029',r'power|restart|sleep|lockdown|screenshot'),('ES-026',r'launcher|drawer|folder|widget'),('ES-025',r'settings|category'),('ES-050',r'permission'),('ES-051',r'picker|document|photo|image|file_'),('ES-049',r'share'),('ES-052',r'clipboard|copy|paste|cut'),('ES-053',r'capture|crop|record'),('ES-056',r'wallpaper|background|ambient'),('ES-057',r'boot|startup'),('ES-058',r'motion|transition|animation'),('ES-009',r'font|cinzel|noto')]
def normalized(name):
 s=Path(name).name.lower();s=re.sub(r'\.9(?=\.png$)','',s);s=re.sub(r'\.[a-z0-9]+$','',s)
 s=re.sub(r'(@[1-4]x|_(?:base_unlit_fixed|base_unlit|source_unlit|emissive_mask_fixed|emissive_mask|neutral_mask|mask|base|cold|glow|selected|pressed|focused|idle|disabled|active|detailed|compact))+$','',s)
 s=re.sub(r'^(?:craftageddon_|cg_|motion_|status_)','',s);return s
def build(inventory,out,roadmap):
 out.mkdir(parents=True,exist_ok=True);items=json.loads(inventory.read_text());rows=[];families=collections.defaultdict(list);counts=collections.Counter()
 for item in items:
  cached=Path(item['cached']);valid=cached.exists() and item['bytes']>0
  if valid:valid=hashlib.sha256(cached.read_bytes()).hexdigest()==item['sha256']
  name=item['name'];family=normalized(name);group=item['group'];sources=item['sources'];stem=name.lower()
  if not valid:role='Invalid / excluded';action='Retain evidence; do not export'
  elif group.startswith('11'):role='Related brand / website reference';action='Reference only; outside Android production count'
  elif item['extension'] in ['.wav','.ogg','.ttf']:role='Audio / font supporting source';action='Preserve; review license and separate roadmap track'
  elif any(q in stem for q in ['contact_sheet','contact-sheet','preview','runtime_','sheet','capture_qa','screenshot']):role='Review / composition reference';action='Reference; do not crop into production masters'
  elif group.startswith(('08','10','12')):role='Historical art reference';action='Compare material and geometry; do not assume current'
  else:role='Candidate current / retained master';action='Rebuild material or redraw; manual family comparison required'
  matches=[code for code,pattern in RULES if re.search(pattern,family)]
  sources_clean=[s.replace('C:\\Users\\spencerm','%USERPROFILE%') for s in sources]
  row={'sha256':item['sha256'],'name':name,'extension':item['extension'],'bytes':item['bytes'],'source_group':group,'family_candidate':family,'role':role,'action':action,'roadmap_candidates':'|'.join(matches),'classification':'rule-assisted; requires review' if matches else 'UNRESOLVED','integrity':'verified cached bytes' if valid else 'INVALID','source_count':len(sources),'sources':json.dumps(sources_clean)}
  rows.append(row);counts[role]+=1
  if valid:families[family].append(row)
 fields=list(rows[0]);
 with (out/'all-retained-files.csv').open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 family_rows=[]
 for family,values in sorted(families.items()):
  candidate=[v for v in values if v['role']=='Candidate current / retained master'];rank=lambda v:(v['extension']!='.svg','rc2' not in v['sources'].lower(),v['bytes'])
  selected=sorted(candidate,key=rank)[0] if candidate else sorted(values,key=rank)[0]
  family_rows.append({'family_id':'CGF-'+hashlib.sha256(family.encode()).hexdigest()[:10],'family_candidate':family,'distinct_files':len(values),'formats':'|'.join(sorted({v['extension'] for v in values})),'roles':'|'.join(sorted({v['role'] for v in values})),'proposed_source_sha256':selected['sha256'],'proposed_source_name':selected['name'],'roadmap_candidates':'|'.join(sorted({c for v in values for c in v['roadmap_candidates'].split('|') if c})),'decision':'PROPOSED; not manually approved','rework_status':'Not complete'})
 with (out/'family-candidates.csv').open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=list(family_rows[0]));w.writeheader();w.writerows(family_rows)
 queue=list(csv.DictReader(roadmap.open(encoding='utf-8-sig')));coverage=[]
 for q in queue:
  match=[x for x in family_rows if q['id'] in x['roadmap_candidates'].split('|')]
  coverage.append({'id':q['id'],'family_or_surface':q['family_or_surface'],'candidate_family_count':len(match),'candidate_family_ids':'|'.join(v['family_id'] for v in match),'scope_status':'Candidate sources identified; manual comparison pending' if match else 'No automatic match; manual source/design work needed','completion':'Not complete'})
 with (out/'roadmap-source-coverage.csv').open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
 report={'retainedRecords':len(rows),'validDistinctFiles':sum(r['integrity']!='INVALID' for r in rows),'invalidExcluded':sum(r['integrity']=='INVALID' for r in rows),'candidateFamilies':len(family_rows),'roles':dict(counts),'roadmapRows':len(coverage),'method':'Byte integrity plus conservative filename/source-role rules. Family matches and chosen sources are proposals, not visual approval. Historical and format variants are not counted as new design work.'}
 (out/'scope-summary.json').write_text(json.dumps(report,indent=2)+'\n');(out/'README.md').write_text('# Full retained-library scope register\n\nEvery cached source record was accounted for and valid records were SHA-256 checked. This is a rule-assisted inventory, not a claim that every source was visually reviewed or redrawn. `all-retained-files.csv` records every file and provenance, `family-candidates.csv` proposes normalized family groupings and source candidates, and `roadmap-source-coverage.csv` retains every one of the 103 work packages with matches or an explicit unresolved state. The proposed source ranking favors SVG and RC2 sources; human visual review can override it. Preserve all historical sources.\n\nThe earlier catalog also contains website/brand references, sounds, fonts, exports, masks and captures. Do not describe its total file count as the number of independent Android visual assets. One invalid zero-byte record is retained as evidence and excluded from valid assets.\n',encoding='utf8');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inventory',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--roadmap',type=Path,required=True);a=p.parse_args();build(a.inventory,a.out,a.roadmap)
