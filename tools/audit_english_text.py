"""Audit current authored SVG labels against the project's English UI contract.

The letter check catches accidental script/language fixtures. It complements,
and does not replace, reviewing English wording in the approved text catalog.
"""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as ET

def audit(roots):
 files=labels=0;issues=[]
 for root in roots:
  for f in sorted(root.rglob('*.svg')):
   files+=1
   for n in ET.parse(f).getroot().iter():
    if n.tag.endswith('}text') and n.text:
     labels+=1
     if any(c.isalpha() and not c.isascii() for c in n.text):issues.append({'file':str(f),'text':n.text})
 return {'date':'2026-10-22','authoredLocale':'en-US','svgFiles':files,'liveTextNodes':labels,'nonEnglishAlphabeticLabels':issues,'result':'FAIL' if issues else 'PASS','scope':[r.name for r in roots],'method':'Parse actual SVG text nodes; reject non-ASCII alphabetic fixtures. English catalog wording reviewed separately. Punctuation/key/status symbols are allowed. No claim about historical APK runtime text.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('roots',type=Path,nargs='+');p.add_argument('--out',type=Path,required=True);a=p.parse_args();report=audit(a.roots);a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['result']=='PASS'
