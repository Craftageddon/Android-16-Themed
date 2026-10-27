'''Save a bounded Gallery handoff, exact patch, dependency backlog and review notes.'''
from pathlib import Path
import collections,datetime,difflib,hashlib,shutil,subprocess,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 native=[];diff=[];texts=[]
 for p in sorted(PATCH.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(PATCH).as_posix();native.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'binary':p.suffix=='.png'})
  if p.suffix=='.png':continue
  original=UP/rel;before=original.read_bytes() if original.exists() else b'';after=p.read_bytes()
  if before==after:continue
  texts.append({'path':rel,'sourceSha256':sha(original) if original.exists() else None,'patchedSha256':sha(p)})
  for line in difflib.unified_diff(before.decode('utf8').splitlines(keepends=True),after.decode('utf8').splitlines(keepends=True),fromfile='a/'+rel if original.exists() else '/dev/null',tofile='b/'+rel):
   diff.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
 patch=OUT/'Glimpse-forge-workflows.patch';patch.write_bytes(''.join(diff).encode());write_json(OUT/'current-native-files.json',native);write_json(OUT/'changed-files.json',texts)
 work=ROOT/'build-work'/('gallery26-clean-apply-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);(work/'.gitattributes').write_bytes(b'* -text\n')
 for r in texts:
  src=UP/r['path']
  if src.exists():dest=work/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 logs=[]
 for args in [['git','init','-q'],['git','-c','core.autocrlf=false','apply','--check','--whitespace=nowarn',str(patch)],['git','-c','core.autocrlf=false','apply','--whitespace=nowarn',str(patch)]]:
  p=subprocess.run(args,cwd=work,capture_output=True,text=True);logs.append({'argv':args,'exit':p.returncode,'output':p.stdout+p.stderr});assert p.returncode==0,logs[-1]
 for r in texts:assert sha(work/r['path'])==r['patchedSha256']
 write_json(OUT/'verification/evidence/clean-patch-application.json',{'result':'PASS','textFiles':len(texts),'patchSha256':sha(patch),'patchedByteParity':True,'commands':logs,'executedDeviceOperations':False})
 media=OUT/'source/media3-ui/original-resources/res';bound={r['resource']:r for r in read_json(OUT/'gallery-resource-bindings.json') if r.get('library')};catalog=[]
 for file in sorted(media.rglob('*.xml')):
  qual=file.parent.name
  if not qual.startswith(('drawable','layout')):continue
  record={'path':file.relative_to(OUT).as_posix(),'sha256':sha(file),'xmlRoot':E.parse(file).getroot().tag,'resource':file.stem,'qualifier':qual}
  if file.stem in bound:record.update(disposition='SOURCE_GEOMETRY_TREATMENT_AUTHORED',binding=bound[file.stem],nativeAcceptance='NOT RUN')
  elif any(r['source']==record['path'] for r in read_json(OUT/'dependency-layout-overlays.json')):record.update(disposition='NATIVE_LAYOUT_ADAPTATION_AUTHORED',nativeAcceptance='NOT RUN')
  else:record.update(disposition='PENDING_DEPENDENCY_CONSUMER_REVIEW',reason='Exact dependency source retained. Requires positive default/call-site/consumer proof and scoped retain or new-art decision; no absence-based approval.')
  catalog.append(record)
 write_json(OUT/'discovered-media3-visual-scope.json',{'baselineCorpusExtended':False,'resources':catalog,'counts':dict(collections.Counter(r['disposition'] for r in catalog)),'knownSourceDefaults':[{'owner':'PlayerView.java','proof':'showBuffering = SHOW_BUFFERING_NEVER; defaultArtworkId = 0; errorMessageProvider nullable; isInEditMode() branch owns the IDE logo','source':'source/media3-ui/original-java/androidx/media3/ui/PlayerView.java','sha256':sha(OUT/'source/media3-ui/original-java/androidx/media3/ui/PlayerView.java')},{'owner':'PlayerControlView.java','proof':'showVrButton = false; setShowVrButton remains native. No global unreachability claim.','source':'source/media3-ui/original-java/androidx/media3/ui/PlayerControlView.java','sha256':sha(OUT/'source/media3-ui/original-java/androidx/media3/ui/PlayerControlView.java')}],'remainingReviewIncludes':['Other dependency visuals and native default widgets','Media3 error/buffering/legacy/VR/notification artwork consumers','Remaining Material/AppCompat dependency visuals, effective resources and library-specific layouts']})
 components=read_json(OUT/'gallery-art-components.json');kinds=dict(collections.Counter(r['kind'] for r in components));manifest=read_json(OUT/'source-manifest.json')
 inventory={'date':'2026-10-27','artTreatments':53,'treatmentKinds':kinds,'nativePngConfigs':1680,'coldPngConfigs':240,'neutralMaskPngConfigs':1440,'newExportConfigs':1484,'exactReusedConfigs':196,'nativeTextFiles':len(texts),'actualJavaClasses':9,'sourceOwnerEditStages':34,'distinctSourceOwnerFiles':33,'media3LayoutOverlays':4,'typedDrawableBindings':59,'staticResourceFamilies':60,'editableDesktopWorkflowFixtures':25,'assetSheets':4,'workflowSheets':5,'sourceFiles':len(manifest),'committedDependencyFiles':29,'extraPlatformCompatibilityLibraries':20,'preservedCanonicalMasters':472,'newAppComponentBindingBeyondOriginal20':'org.lineageos.glimpse existing native launcher identity; no manifest entry invented','nativeAcceptance':'NOT RUN','wholeGoalComplete':False}
 write_json(OUT/'asset-inventory.json',inventory)
 write_json(OUT/'WORK-IN-PROGRESS.json',{'base':'dc2fa9aa2d5e34c04bd852db548fa5d773eae885','workflow':'W-05','adaptation':'PARTIALLY AUTHORED, VERIFIED OFFLINE','sourceFiles':len(manifest),'wholeGoalComplete':False,'remaining':'See REMAINING.md and semantic-review-progress.json'})
 write_json(OUT/'owner-workflow-progress.json',{'W-05':'Partial source/art handoff: all baseline Gallery families reviewed except two legacy launcher leaves. Native Kotlin owners and full integration are uncompiled. Extra dependency consumer review remains.','authoredSourceGroups':['grid/thumbnail selection','viewer favorite/motion-photo/actions','player control housing/timebar state','metadata details','preferences','permission/confirmation/wallpaper dialogs','adaptive and neutral monochrome identity'],'remainingOwnerChecks':['All changed Kotlin owners against full exact app dependency graph','Full native library/resource linking, optimization and XML inflation','Effective overlays and installed app identity','Picker, dialogs/undo/popups and remaining dependency visual-state coverage','Native text layout, large-font viewport scrolling, input/focus and accessibility','Dual-display/rotation/Thor controller acceptance without hardware operations in this checkpoint']})
 (OUT/'README.md').write_text('''# Forge 26 — Gallery workflow artwork and source handoff

Gallery now has scoped steel glyphs, transparent selected thumbnail rims,
favorite/motion-photo state, compact player control housings, preferences,
metadata details, dialogs and a native launcher identity. Cold material and
neutral lighting masks remain separate. Actual feature values drive ember;
focus stays cool, and an on-but-disabled feature keeps attenuated ember.
Native English labels remain live. Media images and user metadata retain their
original source data/load/edit/permission owners.

## Outputs

- masters:53 layered SVG treatments, including12 reviewed donor optical
  derivatives; original donors and the472 earlier canonical masters are preserved.
- native-patch/packages/apps/Glimpse:1680 PNG configurations,240 cold and1440
  neutral masks;196 configurations are exact aliases of prior material assets.
- Glimpse-forge-workflows.patch and current-native-files.json:combined text
  changes and the full copy/hash inventory against exact source revision
  89b473594ec8ad01417624e670912450ce5df7e9.
- workflow-previews:25 editable English SVG specimens plus PNG renderings.
  previews:four asset/control sheets and five workflow sheets.
- semantic-review-delta.json:47 content-backed decisions. The complete
  10926-family/16559-variant ledger is conserved;9577 decisions remain OPEN.
- discovered-media3-visual-scope.json:dependency artwork newly found beyond
  that baseline, with unresolved consumers explicitly retained in the backlog.

The new native Gallery component is additional to the original20 component
bindings; its actual manifest already declares the launcher identity. No
installed-device fact or new manifest component is invented.

## Verification and limits

Nine actual Java presentation classes compile against real pinned AndroidX
and committed Gallery/Media3/Material APIs.1536 policy cases/14076 assertions
and1302 wrapping cases/257083 geometry assertions pass. All patch resource
formats compile; the standalone renderer bank links. Compatibility uses the
installed SDK36.1 jar while the unchanged native app declares SDK36/target36.
Library R symbol names/IDs come from original AAR R.txt files for compilation
only. This is not full app linking or a Soong build.

Source hashes,1680 PNG configurations, neutral masks,196 exact aliases,
34 reversible edit stages across33 source owners, dependency layout IDs,
transparent media centers, original preference contracts, launcher safe-circle,
472 earlier masters and the frozen Forge25 archive pass bounded checks. The
combined text patch applies to clean pinned originals with byte parity.

All Kotlin owner compilation, full pinned Soong/resource optimization,
native XML inflation/layout, installed/effective resources, Thor/controller,
accessibility/performance and V3 remain NOT RUN. Desktop font/layout samples
use approximate Segoe UI metrics and synthetic images, not Android screenshots.
W05 and the whole goal remain incomplete. See REMAINING.md.

## Apply to a source checkout

Confirm the exact Glimpse revision above. Run git apply --check and git apply
with Glimpse-forge-workflows.patch in that module. Copy every binary=true
entry of current-native-files.json from native-patch to its module-relative
path, verifying SHA-256. The patch includes the Java Soong source glob and
explicit XML-constructor retention rules. Run the full official build and
native acceptance before installation. This checkpoint executes no device,
media editing, permission, wallpaper or player operation.

Rollback is the untouched upstream snapshot plus the prior signed checkpoint;
never overwrite or flash a user device as part of this handoff.
''',encoding='utf8')
 (OUT/'REVIEW.md').write_text('''# Gallery desktop review — 27 October 2026

Reviewed the four asset sheets and five workflow sheets. English labels are
live SVG/native source text; no faux writing is generated. Cold steel and
ember layer samples remain distinct from actual source state semantics.

Corrections across passes:transparent source paths remain invisible;stroke
opacity is independent of stroke width;source transforms/fill rules retained;
small source glyph filters scale to their native viewports;thumbnail centers
remain transparent;full photos/videos receive no decorative rim;viewer
Information/Use as stay in toolbar overflow;source bottom action order and
read-only/secure conditions retained;selection indicators use source top-left
placement and cold outline/true selected states;buffering with play intent may
show Pause while isPlaying=false keeps the housing cold. Disabled custom
scrubbers remain visible according to DefaultTimeBar's real drawable branch.

Compact transparent player housings fit native controls without compressing
large fixed panel borders. The adaptive badge was inset20% after18% failed
an alpha-aware safe-circle check. The neutral monochrome identity stays a
host-tinted vector. Drawable clones create independent layers and fall back
to their original Resources when a null Resources argument is supplied.

Desktop source/visual review passes within the recorded scope. No native UI,
Inkscape roundtrip, Android screenshot or independent whole-goal V3 is claimed.
''',encoding='utf8')
 (OUT/'REMAINING.md').write_text('''# Remaining work — checkpoint26

The goal is ACTIVE.9577 original family decisions remain OPEN;that is a
semantic review count, not a count of drawings that still need creation.
Two Gallery legacy leaves,ic_launcher_background andic_launcher_foreground,
remain OPEN pending downstream consumer/reuse disposition. The newly rebound
adaptive identity does not justify approving unused originals by absence.

W05 is partial:compile all changed Kotlin owners and the complete official
module, verify native resource/style linking and XML inflation, finish new
Media3/dependency consumer decisions and any resulting artwork, then check
picker/undo/popups, native text/scrolling, accessibility, playback/focus/input,
rotation/dual-display/controller behavior and effective installed identity.

W03 setup and W07 boot/charger/recovery still need authored workflow handoffs.
W04 retains three legacy/unbound resource reviews plus exact private/SPA
owner builds and integration gates. W01/W02/W06 have source/artwork handoffs;
those do not establish final device acceptance.

Continue the full corpus and tentative-reuse/owner backlog, including any new
artwork discovered by content inspection. Preserve all original family and
variant records. A fresh independent whole-goal completeness/state/content
review must follow completion of those requirements; it is NOT RUN.

Device access was deferred. No hardware operation or flashing is part of
this checkpoint. Do not mark the full goal or V3 complete from offline checks.
''',encoding='utf8')
 (OUT/'THIRD_PARTY_SOURCES.md').write_text('''# Source provenance

Original Craftageddon artwork/code remains CC0. Pinned LineageOS/AOSP source,
Media3,Material and AndroidX dependencies retain original licenses and notices;
they are not relicensed CC0. Source SPDX headers,committed AAR notices and
provenance/hash manifests are preserved. Pinned official SDK library binaries
used only for compatibility remain in the local build cache;receipts identify
URLs,Git object identities and SHA-256. The committed Gallery dependency set
is retained with the source snapshot. No private signing material is included.
''',encoding='utf8')
 technical=read_json(OUT/'verification/evidence/gallery-source-art-checks.json');technical.update(date='2026-10-27',checkpointScope='Bounded Gallery artwork/source handoff; whole goal and native/device acceptance incomplete.',v1Scope='Actual source-backed Gallery art/state/owner bindings, immutable baseline preservation and explicit additional dependency/remaining scope.',v2Method='Pinned source/blob checks, pixel/mask transparency audit, clean patch byte parity, actual nine Java API compilation, SDK resource format/bank linking,1536 policy and1302 geometry cases, desktop rendering review')
 write_json(OUT/'verification/evidence/technical.json',technical)
 print({'nativeFiles':len(native),'textPatchFiles':len(texts),'cleanPatch':'PASS','dependencyVisualFiles':len(catalog),'dependencyCounts':dict(collections.Counter(r['disposition'] for r in catalog)),'inventory':inventory})
if __name__=='__main__':main()
