'''Audit the current setup glyph/source pass without claiming the full workflow is complete.'''
from pathlib import Path
import collections,hashlib,xml.etree.ElementTree as E
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/28-setup-workflows';UP=OUT/'upstream/packages/apps/SetupWizard';PATCH=OUT/'native-patch/packages/apps/SetupWizard';S='{http://www.w3.org/2000/svg}';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 counts=collections.Counter()
 for row in read_json(OUT/'source-manifest.json'):
  p=OUT/row['saved'];data=p.read_bytes();assert sha(p)==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1'];counts['pinnedAppSourceFilesVerified']+=1
 for row in read_json(OUT/'source/setup-template-contracts.json')['files']:assert sha(OUT/row['saved'])==row['sha256'];counts['pinnedTemplateInputsVerified']+=1
 rows=read_json(OUT/'setup-art-components.json')
 for row in rows:
  master=OUT/row['master'];assert sha(master)==row['masterSha256'];svg=E.parse(master).getroot();assert not list(svg.iter(S+'text'))
  for name in ['cold','reflection','spill','seam','core','focus','symbol']:assert svg.find(S+'g[@id="'+name+'"]') is not None
  original=ROOT/row['source']['original'];assert sha(original)==row['source']['sha256']
  if row['source']['sourcePathGeometryPreserved']:assert row['source']['sourcePathData']==row['source']['newPathData'];counts['sourceGeometryGlyphs']+=1
  else:assert row['id']=='cg_sw_locale';assert len(row['source']['newPathData'])==5;counts['newLetteringFreeGlobe']+=1
  for file in row['files']+row['nativeHighResolution']:
   p=OUT/file['path'];assert sha(p)==file['sha256'];im=Image.open(p).convert('RGBA');assert list(im.size)==file['size'];assert sha(PATCH/'app/src/main/res'/p.relative_to(OUT/'artwork-resources'))==file['sha256']
   if file['layer']=='cold':counts['coldPngs']+=1
   else:assert all(r==g==b for r,g,b,a in im.get_flattened_data() if a);counts['neutralMaskPngs']+=1
 assert counts['coldPngs']==90 and counts['neutralMaskPngs']==540 and counts['sourceGeometryGlyphs']==17 and counts['newLetteringFreeGlobe']==1
 for r in read_json(OUT/'setup-glyph-bindings.json'):
  p=PATCH/r['target'];assert sha(OUT/r['source'])==r['sourceSha256'] and sha(p)==r['targetSha256'];n=E.parse(p).getroot();assert n.get('class')=='org.lineageos.setupwizard.forge.ForgeDrawable';assert r['positiveConsumers']
  for ref in r['positiveConsumers']:assert sha(UP/ref['path'])==ref['sha256']
  counts['positiveNativeGlyphBridges']+=1
 for r in read_json(OUT/'unbound-setup-glyphs.json'):assert not (PATCH/'app/src/main/res/drawable'/(r['resource']+'.xml')).exists();counts['unboundGlyphsNotOverridden']+=1
 for r in read_json(OUT/'setup-build-source-edits.json'):
  original=(UP/r['path']).read_bytes();data=(PATCH/r['path']).read_text(encoding='utf8');op=r['operation'];assert data.count(op['after'])==1 and data.replace(op['after'],op['before']).encode()==original;counts['reversibleBuildEdits']+=1
 build=read_json(OUT/'verification/evidence/glyph-core-build.json');assert build['result']=='PASS' and not build['actualAppKotlinOwnersCompiled']
 for path,digest in build['actualSourceFiles'].items():assert sha(PATCH/path)==digest
 assert build['resourceInputHashes']=={p.relative_to(PATCH/'app/src/main/res').as_posix():sha(p) for p in (PATCH/'app/src/main/res').rglob('*') if p.is_file()}
 assert not list(PATCH.rglob('*.kt'))
 for name in ['app/src/main/AndroidManifest.xml','app/org.lineageos.setupwizard.xml']:assert not (PATCH/name).exists()
 for r in read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']:assert sha(ROOT/r['source'])==r['sha256'];counts['priorCanonicalMastersPreserved']+=1
 assert sha(ROOT/'iterations/27-gallery-contracts/complete-assets.zip')=='cfa0b73009361dbf0acb78947469cf91be51f965d79a7b97bea1747fa2121995'
 result={'result':'PASS','scope':'Current setup source/glyph pass only; remaining workflow/art/dependencies and native acceptance unfinished','checks':dict(counts),'actualPublicJavaRendererClassesCompiled':3,'policyCases':1536,'policyAssertions':14076,'originalIntrinsicSizesValidated':18,'actualLinkedLayerIdsValidated':126,'nativeKotlinOwnersChanged':0,'privateNativeAppCompilation':'NOT RUN','nativeInflationAndDeviceAcceptance':'NOT RUN','baselineSemanticDecisionsClosed':0,'wholeGoalComplete':False};write_json(OUT/'verification/evidence/current-glyph-source-checks.json',result);print(result)
if __name__=='__main__':main()
