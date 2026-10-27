"""Compile nine actual Gallery controls using pinned Android library APIs."""
from pathlib import Path
import datetime,hashlib,subprocess,zipfile,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/26-gallery-workflows';PATCH=OUT/'native-patch/packages/apps/Glimpse'
JDK=Path('C:/Program Files/Android/Android Studio/jbr');SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 work=ROOT/'build-work'/('gallery26-controls-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);(work/'classes').mkdir();logs=[]
 def run(args):
  p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace');logs.append(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError('Exit '+str(p.returncode)+'\n'+logs[-1])
  return p.stdout
 core=sorted((ROOT/'build-work').glob('gallery26-core-*'))[-1]
 android=SDK/'platforms/android-36.1/android.jar';kotlin=next(Path('C:/Users/spencerm/Documents/Codex/2026-08-31/us/android-motion/.gradle-user/caches/modules-2/files-2.1/org.jetbrains.kotlin/kotlin-stdlib/2.3.21').rglob('*.jar'));classpath=[android,kotlin];rs=[core/'gen/org/lineageos/glimpse/R.java'];contracts=[]
 for d in read_json(OUT/'source/platform-dependencies.json')['libraries']:
  f=Path(d['classesJar']);assert sha(f)==d['classesSha256'];classpath.append(f)
  if d.get('resourceSymbols'):
   with zipfile.ZipFile(d['localBuildCache']) as z:pkg=E.fromstring(z.read('AndroidManifest.xml')).get('package')
   if pkg:contracts.append((pkg,Path(d['resourceSymbols']).read_text()))
 for d in read_json(OUT/'source-binary-dependencies.json'):
  f=OUT/d['saved'];assert sha(f)==d['sha256']
  if f.suffix=='.aar':
   with zipfile.ZipFile(f) as z:
    data=z.read('classes.jar');pkg=E.fromstring(z.read('AndroidManifest.xml')).get('package')
    if pkg and 'R.txt' in z.namelist():contracts.append((pkg,z.read('R.txt').decode()))
   jf=work/(f.stem+'.classes.jar');jf.write_bytes(data);classpath.append(jf)
  elif f.suffix=='.jar' and '/app/libs/' in d['saved']:classpath.append(f)
 aliases=[]
 # Exact original library symbols are compilation-only and never enter a device package.
 for pkg,txt in contracts:
  groups={}
  for line in txt.splitlines():
   kind,typ,name,value=line.split(' ',3);groups.setdefault(typ,[]).append('public static final '+kind+' '+name+'='+value+';')
  if not groups:continue
  target=work/'namespace-symbols'/Path(pkg.replace('.','/'))/'R.java';target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text('package '+pkg+';public final class R{'+''.join('public static final class '+typ+'{'+''.join(v)+'}' for typ,v in groups.items())+'}',encoding='utf8');rs.append(target);aliases.append({'namespace':pkg,'symbols':sum(map(len,groups.values())),'source':'Exact committed AAR R.txt, compile only'})
 java=sorted((PATCH/'app/src/main/java/org/lineageos/glimpse/forge').glob('*.java'));assert len(java)==9
 args=['--release','17','-encoding','UTF-8','-cp',';'.join(map(str,classpath)),'-d',str(work/'classes'),*map(str,java+rs)];argfile=work/'javac.args'
 argfile.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args),encoding='utf8');run([JDK/'bin/javac.exe','@'+str(argfile)])
 probe=work/'GalleryRowsProbe.java';probe.write_text('''import org.lineageos.glimpse.forge.ForgeRowPlan;
import java.util.Random;
public final class GalleryRowsProbe{
 static int n=0,cases=0;static void require(boolean ok){n++;if(!ok)throw new AssertionError("row assertion "+n);}
 public static void main(String[] args){
  Random r=new Random(260527);
  for(int width:new int[]{1,24,160,320,540,960,1920})for(int gap:new int[]{0,4,12})for(boolean center:new boolean[]{false,true})for(int count=0;count<=30;count++){
   int[] w=new int[count],h=new int[count];for(int i=0;i<count;i++){w[i]=1+r.nextInt(width);h[i]=1+r.nextInt(320);}
   ForgeRowPlan.Plan p=ForgeRowPlan.pack(width,gap,w,h,center);cases++;require(p.x.length==count&&p.y.length==count);
   if(count==0)require(p.height==0);
   for(int i=0;i<count;i++){
    require(p.x[i]>=0&&p.x[i]+w[i]<=width&&p.y[i]>=0&&p.y[i]+h[i]<=p.height);
    for(int j=0;j<i;j++)require(p.x[i]>=p.x[j]+w[j]||p.x[j]>=p.x[i]+w[i]||p.y[i]>=p.y[j]+h[j]||p.y[j]>=p.y[i]+h[i]);
    if(i>0)require(p.y[i]>=p.y[i-1]);
   }
   for(int i=0;i<count;){int j=i,max=0;while(j<count&&p.y[j]==p.y[i]){max=Math.max(max,h[j]);j++;}
    require(p.x[i]==(center?(width-(p.x[j-1]+w[j-1]-p.x[i]))/2:0));
    if(j<count)require(p.y[j]==p.y[i]+max+gap);else require(p.height==p.y[i]+max);i=j;
   }
  }
  for(int k=0;k<3;k++){boolean threw=false;try{ForgeRowPlan.pack(k==0?0:10,k==1?-1:0,new int[]{k==2?11:1},new int[]{1},false);}catch(IllegalArgumentException e){threw=true;}require(threw);}
  System.out.println("PASS wrappingCases="+cases+" geometryAssertions="+n+" syntheticMetricsOnly=true");
 }
}''',encoding='utf8')
 run([JDK/'bin/javac.exe','--release','17','-cp',work/'classes','-d',work/'classes',probe]);output=run([JDK/'bin/java.exe','-cp',work/'classes','GalleryRowsProbe'])
 evidence=OUT/'verification/evidence';(evidence/'controls-compiler.txt').write_text('\n'.join(logs),encoding='utf8');(evidence/'row-geometry-host.txt').write_text(output,encoding='utf8')
 write_json(evidence/'controls-build.json',{'result':'PASS','actualJavaClasses':len(java),'nativeSources':{p.relative_to(PATCH).as_posix():sha(p) for p in java},'classpath':[{'path':str(f),'sha256':sha(f)} for f in classpath],'compatibilityResourceNamespaces':aliases,'declaredAppSdk':36,'installedCompatibilitySdk':'36.1','allKotlinOwnersCompiled':False,'nativeXmlInflation':'NOT RUN','fullPinnedSoongBuild':'NOT RUN','deviceTests':'NOT RUN','wholeGoalComplete':False})
 print(output)
if __name__=='__main__':main()
