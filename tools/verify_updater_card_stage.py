'''Audit the current partial Updater card stage without claiming the whole workflow.'''
from pathlib import Path
import hashlib,datetime,json,subprocess,unicodedata,xml.etree.ElementTree as E
from PIL import Image
from audit_os_resource_coverage import ROOT,read_json,write_json
from build_pilot import font
from build_scalable_frames import bounds
from check_updater_phase_binding import JDK

OUT=ROOT/'iterations/24-updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    sources=read_json(OUT/'source-manifest.json')+read_json(OUT/'source/ui-dependency-manifest.json')
    for r in sources:
        data=(OUT/r['saved']).read_bytes()
        assert sha(OUT/r['saved'])==r['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1']
    aliases=read_json(OUT/'unchanged-material-reuse.json')['resources']
    masks=0;size_checks=0;transparent_cold=0
    for r in aliases:
        p=OUT/r['target'];assert sha(p)==r['sha256']==sha(ROOT/r['source'])
        im=Image.open(p).convert('RGBA');x,y=bounds(im);w,h=im.width-2,im.height-2
        assert 0<=x[0]<x[1]<=w and 0<=y[0]<y[1]<=h
        assert w>=w-(x[1]-x[0])+1 and h>=h-(y[1]-y[0])+1;size_checks+=1
        if not p.name.endswith('_cold.9.png'):
            pixels=im.get_flattened_data() if hasattr(im,'get_flattened_data') else im.getdata()
            assert all(px[0]==px[1]==px[2] for px in pixels),p;masks+=1
        else:
            crop=im.crop((1,1,im.width-1,im.height-1))
            assert crop.getchannel('A').getextrema()==(0,255),p;transparent_cold+=1
    master_aliases=read_json(OUT/'editable-material-aliases.json')['files']
    for r in master_aliases:
        p=OUT/r['target'];assert sha(p)==r['sha256']==sha(ROOT/r['source'])
        if p.suffix=='.svg':
            root=E.fromstring(p.read_bytes())
            assert not list(root.iter('{http://www.w3.org/2000/svg}text'))
            for n in root.iter('{http://www.w3.org/2000/svg}image'):
                href=n.get('href');assert href and (p.parent/href).is_file()
    # Undo presentation-only changes first, then the preceding phase additions.
    material={r['path']:r for r in read_json(OUT/'owner-material-edits.json')}
    phase={r['path']:r for r in read_json(OUT/'owner-phase-edits.json')}
    for path in set(material)|set(phase):
        text=(PATCH/path).read_bytes().decode('utf8')
        for row in [material.get(path),phase.get(path)]:
            if row is None:continue
            assert hashlib.sha256(text.encode('utf8')).hexdigest()==row['patchedSha256']
            for e in reversed(row['operations']):
                assert text.count(e['after'])==e['count']
                text=text.replace(e['after'],e['before'],e['count'])
        assert text.encode('utf8')==(OUT/'upstream/packages/apps/Updater'/path).read_bytes()
    compiled=read_json(OUT/'verification/evidence/material-subset-build.json')
    assert compiled['result']=='PASS'
    for name,digest in compiled['nativeSources'].items():assert sha(PATCH/name)==digest
    for name,digest in compiled['jars'].items():assert sha(OUT/'verification/evidence'/name)==digest
    work=ROOT/'build-work'/('updater24-policy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True)
    probe=work/'PolicyProbe.java'
    probe.write_text('''import org.lineageos.updater.forge.ForgeStatePolicy;
public final class PolicyProbe {
 public static void main(String[] args) {
  for(int bits=0;bits<128;bits++){
   boolean[] b=new boolean[7]; for(int i=0;i<7;i++) b[i]=(bits & (1<<i))!=0;
   ForgeStatePolicy p=ForgeStatePolicy.resolve(b[0],b[1],b[2],b[3],b[4],b[5],b[6]);
   System.out.print(bits+"|"+p.active+"|"+p.base);
   for(float f:p.gains)System.out.print("|"+f); System.out.println();
  }
 }
}
''',encoding='utf8')
    jar=OUT/'verification/evidence/updater-rendering.jar'
    def run(args):
        p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
        assert p.returncode==0,p.stdout+p.stderr
        return p.stdout
    run([JDK/'bin/javac.exe','-cp',jar,'-d',work,probe])
    output=run([JDK/'bin/java.exe','-cp',str(work)+';'+str(jar),'PolicyProbe']).splitlines()
    assert len(output)==128
    for line in output:
        fields=line.split('|');bits=int(fields[0]);b=[bool(bits & (1<<i)) for i in range(7)]
        enabled,checked,selected,focused,pressed,feature,momentary=b
        active=enabled and (checked or selected or feature or (momentary and pressed))
        gains=[0.,0.,0.,0.,1. if enabled and focused else 0.,0.]
        if active:gains[0]=.6 if pressed else .32;gains[1]=.92 if pressed else .72;gains[2]=1;gains[3]=1 if pressed else .82;gains[5]=1
        assert (fields[1]=='true')==active
        assert abs(float(fields[2])-(1 if enabled else .42))<1e-6
        assert all(abs(float(a)-b)<1e-6 for a,b in zip(fields[3:],gains))
    fixtures=read_json(OUT/'card-workflow-fixtures.json')['fixtures'];texts=0
    for r in fixtures:
        root=E.fromstring((OUT/r['svg']).read_bytes());width=float(root.get('width'));height=float(root.get('height'))
        assert not r['deviceScreenshot']
        for t in r['texts']:
            assert all(not c.isalpha() or ('A'<=c<='Z' or 'a'<=c<='z') for c in t['text']),t['text']
            length=font(t['size']).getlength(t['text']);left=t['x']-length/2 if t['anchor']=='middle' else t['x']
            assert left>=0 and left+length<=width+.5,(r['id'],t,left,length,width)
            assert 0<=t['y']<=height
            texts+=1
        for c in r['controls']:
            x,y,w,h=c['bounds'];assert 0<=x and x+w<=width and 0<=y and y+h<=height
            if c['family']=='cg_rf_panel':assert c['active']==(r['sourceMapping']['tone']=='ACTIVE')
    old=read_json(ROOT/'iterations/17-forge-coverage/canonical-masters.json')['masters']
    for r in old:assert sha(ROOT/r['source'])==r['sha256']
    report={'result':'PASS','pinnedSourcesVerified':len(sources),'unchangedPngConfigurations':len(aliases),
        'neutralMaskConfigurations':masks,'transparentColdConfigurations':transparent_cold,
        'nativeFixedCapChecks':size_checks,'unchangedEditableSvgMasters':4,
        'actualOwnerReverseByteParityFiles':len(set(material)|set(phase)),
        'compiledActualPolicyCases':len(output),'hostPhaseCases':compiled['hostPhaseStateCases'],
        'strictXmlCardFixtures':len(fixtures),'englishTextEntriesChecked':texts,
        'offlineTextAndControlBounds':'PASS within desktop font approximation',
        'previousCanonicalMastersPreserved':len(old),
        'glyphsAndProgressInPreviews':'Desktop approximations; native pixel parity NOT RUN',
        'fullPinnedUpdaterSoongBuild':'NOT RUN','androidRenderingInputAccessibility':'NOT RUN',
        'wholeUpdaterWorkflowComplete':False,'openFamilyDecisions':9630,'newFamilyDecisions':0,
        'remainingOwnerScope':['Scaffold and device-info banner','Preferences and their actual controls',
            'Dialogs, importing and checking/zero/error illustrations','Actual remaining glyph/native resource bridges'],
        'finalWholeGoalDoubleCheck':'NOT RUN - required full scope is unfinished','wholeGoalComplete':False}
    write_json(OUT/'verification/evidence/card-stage-checks.json',report)
    print(json.dumps(report))

if __name__=='__main__':main()
