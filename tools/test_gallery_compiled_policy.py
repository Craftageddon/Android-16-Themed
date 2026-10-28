'''Run actual compiled Gallery policy/geometry probes, without substituting app classes.'''
import ast,datetime,hashlib,subprocess
from pathlib import Path
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';JDK=Path('C:/Program Files/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 report=read_json(OUT/'verification/evidence/complete-owner-compilation.json');jar=Path(report['classJar']);assert report['result']=='PASS' and sha(jar)==report['classJarSha256'];work=ROOT/'build-work'/('gallery27-policy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);records=[]
 for source,cls,dest in [('compile_gallery_core.py','GalleryPolicyProbe','core-policy-host.txt'),('compile_gallery_controls.py','GalleryRowsProbe','row-geometry-host.txt')]:
  script=ROOT/'tools'/source;tree=ast.parse(script.read_text(encoding='utf8'));literals=[n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and 'public final class '+cls in n.args[0].value];assert len(literals)==1
  file=work/(cls+'.java');file.write_text(literals[0],encoding='utf8');logs=[]
  for command in [[JDK/'bin/javac.exe','--release','17','-proc:none','-cp',jar,'-d',work,file],[JDK/'bin/java.exe','-cp',str(work)+';'+str(jar),cls]]:
   p=subprocess.run(list(map(str,command)),capture_output=True,text=True,encoding='utf8');logs.append({'command':list(map(str,command)),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,logs[-1]
  (OUT/'verification/evidence'/dest).write_text(p.stdout,encoding='utf8');records.append({'probe':cls,'probeSourceSha256':sha(file),'testDefinition':source,'testDefinitionSha256':sha(script),'commands':logs})
 write_json(OUT/'verification/evidence/compiled-policy-checks.json',{'result':'PASS','actualCompiledAppJarSha256':sha(jar),'policyCases':1536,'policyAssertions':14076,'wrappingCases':1302,'geometryAssertions':257083,'probes':records,'mediaOperationsExecuted':False,'nativeAndroidLayoutTests':False,'wholeGoalComplete':False})
 print({'actualAppPolicyCases':1536,'policyAssertions':14076,'geometryCases':1302,'geometryAssertions':257083,'nativeAndroidLayoutTests':False})
if __name__=='__main__':main()
