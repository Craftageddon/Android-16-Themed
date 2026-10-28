'''Bind only positively located setup glyph consumers to separate cold and light layers.'''
from pathlib import Path
import hashlib,shutil,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/28-setup-workflows';UP=OUT/'upstream/packages/apps/SetupWizard';PATCH=OUT/'native-patch/packages/apps/SetupWizard';A='{http://schemas.android.com/apk/res/android}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=read_json(OUT/'setup-art-components.json');res=PATCH/'app/src/main/res';java=PATCH/'app/src/main/java/org/lineageos/setupwizard/forge';java.mkdir(parents=True,exist_ok=True);bindings=[];unbound=[]
 sources=[p for p in UP.rglob('*') if p.is_file() and p.suffix in ['.kt','.xml']]
 checked=UP/'app/src/main/java/org/lineageos/setupwizard/util/ButtonGroupUtils.kt';text=checked.read_text(encoding='utf8');assert 'button.id == checkedButtonId' in text and 'button.setIconResource(iconResId)' in text and 'button.icon = null' in text
 for row in rows:
  name='ic_'+row['id'].removeprefix('cg_sw_');hits=[]
  for p in sources:
   for i,line in enumerate(p.read_text(encoding='utf8').splitlines()):
    if 'R.drawable.'+name in line or '@drawable/'+name in line:hits.append({'path':p.relative_to(UP).as_posix(),'sha256':sha(p),'line':i+1,'text':line.strip()})
  for exported in row['files']+row['nativeHighResolution']:
   source=OUT/exported['path'];target=res/source.relative_to(OUT/'artwork-resources');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==exported['sha256']
  if not hits:
   row['nativeOwnerBinding']='PENDING - source content preserved; no positive local consumer established';unbound.append({'resource':name,'reason':'No positive local consumer established. This is not approval by absence. Source geometry artwork retained; no native override authored.'});continue
  mode=1 if name=='ic_check' else 0 if name in ['ic_accessibility','ic_arrow_forward','ic_emergency_dial'] else 2
  source=UP/'app/src/main/res/drawable'/(name+'.xml');node=E.parse(source).getroot();target=res/'drawable'/(name+'.xml');target.parent.mkdir(parents=True,exist_ok=True);target.write_text('<drawable xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto" class="org.lineageos.setupwizard.forge.ForgeDrawable" app:cg_forge_family="'+row['id']+'" app:cg_forge_source_value_mode="'+['dynamic','true_value','false_value'][mode]+'" app:cg_forge_momentary="'+str(mode==0).lower()+'" android:autoMirrored="'+str(node.get(A+'autoMirrored')=='true').lower()+'"/>\n',encoding='utf8')
  role='Actual checked group only; helper removes icon from other children' if mode==1 else 'Positive momentary action consumers; enabled does not imply on' if mode==0 else 'Cold header/cue or mixed header/action glyph; cool focus only'
  bindings.append({'resource':name,'family':row['id'],'source':source.relative_to(OUT).as_posix(),'sourceSha256':sha(source),'target':target.relative_to(PATCH).as_posix(),'targetSha256':sha(target),'sourceValueMode':mode,'modeProof':role,'positiveConsumers':hits,'extraCheckProof':{'path':checked.relative_to(UP).as_posix(),'sha256':sha(checked)} if mode==1 else None,'nativeAcceptance':'NOT RUN'})
  row['nativeOwnerBinding']='SOURCE/RESOURCE BRIDGE AUTHORED; complete native acceptance NOT RUN'
 base=ROOT/'iterations/27-gallery-contracts/native-patch/packages/apps/Glimpse/app/src/main/java/org/lineageos/glimpse/forge';reuse=[]
 for name in ['ForgeDrawable.java','ForgeStatePolicy.java']:
  src=base/name;p=java/name;data=src.read_text(encoding='utf8').replace('org.lineageos.glimpse','org.lineageos.setupwizard');
  if name=='ForgeDrawable.java':
   old='width=layers[0].getIntrinsicWidth();height=layers[0].getIntrinsicHeight();';new='int[] dp=ForgeResources.intrinsicDp(f);float density=r.getDisplayMetrics().density;\n  width=Math.round(dp[0]*density);height=Math.round(dp[1]*density);setChangingConfigurations(getChangingConfigurations()|android.content.pm.ActivityInfo.CONFIG_DENSITY);';assert data.count(old)==1;data=data.replace(old,new)
  p.write_text(data,encoding='utf8');reuse.append({'source':src.relative_to(ROOT).as_posix(),'sourceSha256':sha(src),'target':p.relative_to(PATCH).as_posix(),'targetSha256':sha(p),'changes':'Package/R namespace; Drawable uses original intrinsic dp metadata so high-resolution layers do not enlarge native layout'})
 body='package org.lineageos.setupwizard.forge;\nimport org.lineageos.setupwizard.R;\nfinal class ForgeResources {\n private ForgeResources(){}\n static int[] layers(String family){switch(family){\n'
 for row in rows:body+='case "'+row['id']+'":return new int[]{'+','.join('R.drawable.'+row['id']+'_hi_'+name for name in LAYERS)+'};\n'
 body+='default:throw new IllegalArgumentException("Unknown Forge family "+family);\n}}\n static int[] intrinsicDp(String family){switch(family){\n'
 for row in rows:body+='case "'+row['id']+'":return new int[]{'+','.join(str(round(x)) for x in row['nativeIntrinsicDp'])+'};\n'
 body+='default:throw new IllegalArgumentException("Unknown Forge family "+family);\n}}\n}\n';(java/'ForgeResources.java').write_text('/* SPDX-FileCopyrightText:2026 Craftageddon; SPDX-License-Identifier:CC0-1.0 */\n'+body,encoding='utf8')
 attrs=ROOT/'iterations/27-gallery-contracts/native-patch/packages/apps/Glimpse/app/src/main/res/values/cg_gallery_attrs.xml';(res/'values').mkdir(exist_ok=True);shutil.copy2(attrs,res/'values/cg_setup_attrs.xml')
 edits=[]
 for rel,before,after in [('app/Android.bp','srcs: ["src/main/java/**/*.kt"],','srcs: ["src/main/java/**/*.kt", "src/main/java/**/*.java"],'),('app/proguard.flags','-dontwarn androidx.**','-dontwarn androidx.**\n\n# Public no-arg XML Drawable constructor; actual optimization acceptance remains pending.\n-keep public class org.lineageos.setupwizard.forge.ForgeDrawable {\n    public <init>();\n}')]:
  src=UP/rel;data=src.read_text(encoding='utf8');assert data.count(before)==1;p=PATCH/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data.replace(before,after),encoding='utf8');assert p.read_text(encoding='utf8').replace(after,before)==data;edits.append({'path':rel,'sourceSha256':sha(src),'patchedSha256':sha(p),'operation':{'before':before,'after':after,'count':1},'reverseByteParity':True})
 assert len(bindings)==16 and {r['resource'] for r in unbound}=={'ic_dialer','ic_eye'}
 write_json(OUT/'setup-art-components.json',rows);write_json(OUT/'setup-glyph-bindings.json',bindings);write_json(OUT/'unbound-setup-glyphs.json',unbound);write_json(OUT/'setup-build-source-edits.json',edits);write_json(OUT/'source/core-renderer-reuse.json',reuse)
 art_report=read_json(OUT/'verification/evidence/setup-glyph-artwork-pass.json');art_report['nativeSourceBindings']='16 positive consumer bridges authored;2 unbound glyphs remain pending';write_json(OUT/'verification/evidence/setup-glyph-artwork-pass.json',art_report)
 wip=read_json(OUT/'WORK-IN-PROGRESS.json');wip.update(nativeGlyphBindingsAuthored=16,nativeGlyphBindingsPending=2,javaCoreClassesAuthored=3,fullPrivilegedModuleCompilation='NOT RUN',nativeKotlinOwnersChanged=0,highResolutionLayersPreserveIntrinsicDp=True,densityChangeResourceInvalidation=True);write_json(OUT/'WORK-IN-PROGRESS.json',wip);print({'positiveGlyphBridges':16,'unboundGlyphsPreserved':2,'actualCoreJavaClasses':3,'nativeCallbacksOrSettingsChanged':False,'fullPrivatePlatformBuild':'NOT RUN'})
if __name__=='__main__':main()
