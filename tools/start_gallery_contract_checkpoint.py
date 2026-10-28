'''Start the next Gallery source-contract pass without changing signed Forge26.'''
from pathlib import Path
import hashlib,shutil,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
BASE=ROOT/'iterations/26-gallery-workflows';OUT=ROOT/'iterations/27-gallery-contracts';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists();OUT.mkdir()
 for name in ['upstream','native-patch','masters','source']:shutil.copytree(BASE/name,OUT/name)
 for name in ['source-manifest.json','source-binary-dependencies.json','gallery-art-components.json','gallery-art-components.json.gz','exact-native-control-reuse.json','gallery-owner-edits.json','dependency-layout-overlays.json','signing-public-key.pem']:
  shutil.copy2(BASE/name,OUT/name)
 patch=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res';base_bindings=read_json(BASE/'gallery-resource-bindings.json');bindings=[];changes=[]
 values=E.parse(BASE/'source/media3-ui/original-resources/res/values/values.xml').getroot()
 aliases={n.get('name'):n.text.removeprefix('@drawable/') for n in values if n.tag=='drawable'}
 own_aliases=E.Element('resources');legacy=[]
 for r in base_bindings:
  r=dict(r)
  if not r.get('library'):bindings.append(r);continue
  old=patch/r['qualifier']/(r['resource']+'.xml');data=old.read_bytes();assert old.resolve().is_relative_to(patch.resolve())
  new_name='cg_gl_m3_'+r['resource'];new=patch/r['qualifier']/(new_name+'.xml');new.write_bytes(data)
  old.unlink() # Only the exact Forge26 library override copy; pinned original AAR/source remains untouched.
  names=[k for k,v in aliases.items() if v==r['resource'] and k.startswith('exo_styled_controls_')];assert names
  for name in names:E.SubElement(own_aliases,'drawable',{'name':name}).text='@drawable/'+new_name
  others=[k for k,v in aliases.items() if v==r['resource'] and not k.startswith('exo_styled_controls_')]
  changes.append({'priorOverride':r['qualifier']+'/'+r['resource']+'.xml','newScopedOverride':r['qualifier']+'/'+new_name+'.xml','sharedNativeLeaf':r['resource'],'sourceLeaf':r['source'],'sourceLeafSha256':sha(BASE/r['source']),'layerFamily':r['family'],'oldBridgeBytesSha256':hashlib.sha256(data).hexdigest(),'newBridgeBytesSha256':sha(new),'styledAliasesRetargeted':names,'otherAliasesPreserved':others,'rasterLayersChanged':False})
  r['priorSharedLeaf']=r['resource'];r['resource']=new_name;r['sourceAliases']=names;bindings.append(r)
  legacy.extend(others)
 f=patch/'values/cg_gallery_media3_aliases.xml';f.write_bytes(E.tostring(own_aliases,encoding='utf-8',xml_declaration=True)+b'\n')
 write_json(OUT/'gallery-resource-bindings.json',bindings)
 write_json(OUT/'scoped-media3-alias-edits.json',changes)
 write_json(OUT/'WORK-IN-PROGRESS.json',{'baseCommit':'9249fbce95583e4addc8b110a3527622eac9f29b','purpose':'Finish source-backed media dependency review, tighten shared asset scope and compile complete native Gallery owners','sourceGlyphsRetargeted':len(changes),'styledAliasesRetargeted':len(list(own_aliases)),'legacyOrNotificationAliasesPreserved':sorted(set(legacy)),'newArtwork':'No new art in this scope correction; exact Forge26 layers retained','allKotlinOwnerCompilation':'NOT RUN','fullPinnedSoongBuild':'NOT RUN','wholeGoalComplete':False})
 print({'retargetedLibraryLeaves':len(changes),'playerAliases':len(list(own_aliases)),'sharedAliasesProtected':sorted(set(legacy)),'sourceArchive26Preserved':sha(BASE/'complete-assets.zip')=='8d43b9056dc4c917fc3c4390c9e0c53a6cc18640c3dd633da8a1580f7db614b9'})
if __name__=='__main__':main()
