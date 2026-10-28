'''Generate real per-library resource namespaces from linked IDs and original index maps.'''
from pathlib import Path
import re,hashlib,subprocess,zipfile,json
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';JDK=Path('C:/Program Files/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(text):
 result={}
 for line in text.splitlines():
  if not line.strip():continue
  kind,typ,name,value=line.split(' ',3);result[(typ,name)]=(kind,value)
 return result

def main():
 report=read_json(OUT/'verification/evidence/full-resource-link.json');assert report['result']=='PASS';work=Path(report['work']);global_symbols=parse((work/'R.txt').read_text(encoding='utf8'));rows=read_json(work/'library-resource-inputs.json');compiler=read_json(OUT/'source/pinned-compiler.json');sdk=read_json(OUT/'source/native-dependency-closure.json')['sdk36'];android=Path(sdk['localBuildCache'])
 p=subprocess.run([str(JDK/'bin/javap.exe'),'-constants','-classpath',str(android),'android.R$attr'],capture_output=True,text=True);assert p.returncode==0,p.stderr;framework_attrs={m[1]:int(m[2]) for m in re.finditer(r'public static final int (\w+) = (\d+);',p.stdout)};assert len(framework_attrs)>1000
 root=work/'library-r';root.mkdir();outputs=[];styleable_count=0;actual_ids=0
 for i,row in enumerate(rows):
  original=parse(row['resourceSymbols']);pkg=row['namespace']
  if not original:continue
  assert pkg and re.fullmatch(r'[\w.]+',pkg),pkg
  groups={};field_values={};arrays={name:[None for x in value.strip('{} ').split(',') if x.strip()] for (typ,name),(kind,value) in original.items() if typ=='styleable' and kind=='int[]'}
  for (typ,name),(kind,value) in original.items():
   if typ=='styleable' and kind=='int':
    owner=max((a for a in arrays if name.startswith(a+'_')),key=len);attr=name[len(owner)+1:];index=int(value);assert 0<=index<len(arrays[owner]);g=global_symbols.get(('styleable',name))
    if g:
     array=global_symbols[('styleable',owner)][1];numbers=[int(x.strip(),0) for x in array.strip('{} ').split(',') if x.strip()];identifier=numbers[int(g[1])]
    elif attr.startswith('android_'):identifier=framework_attrs[attr.removeprefix('android_')]
    else:identifier=int(global_symbols[('attr',attr)][1],0)
    assert identifier!=0,(pkg,owner,attr);arrays[owner][index]=identifier;styleable_count+=1;field_values[(typ,name)]='public static final int '+name+'='+value+';'
   elif typ!='styleable':
    assert (typ,name) in global_symbols,(pkg,typ,name);real=global_symbols[(typ,name)][1];assert int(real,0)!=0,(typ,name);actual_ids+=1;field_values[(typ,name)]='public static final int '+name+'='+real+';'
  for name,values in arrays.items():
   assert None not in values,(pkg,name,values);field_values[('styleable',name)]='public static final int[] '+name+'={'+','.join(hex(v) for v in values)+'};'
  for (typ,name),code in field_values.items():groups.setdefault(typ,[]).append(code)
  folder=root/f'{i:02}';src=folder/Path(pkg.replace('.','/'))/'R.java';src.parent.mkdir(parents=True);src.write_bytes(('package '+pkg+';public final class R{\n'+''.join('public static final class '+t+'{\n'+'\n'.join(c)+'\n}\n' for t,c in groups.items())+'}\n').encode())
  classes=folder/'classes';classes.mkdir();p=subprocess.run([str(JDK/'bin/javac.exe'),'--release','17','-proc:none','-encoding','UTF-8','-d',str(classes),str(src)],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,(pkg,p.stderr[-5000:]);jar=folder/'R.jar';p=subprocess.run([str(JDK/'bin/jar.exe'),'cf',str(jar),'-C',str(classes),'.'],capture_output=True,text=True);assert p.returncode==0
  outputs.append({'module':row['module'],'namespace':pkg,'sourceSymbolsSha256':hashlib.sha256(row['resourceSymbols'].encode()).hexdigest(),'generatedSource':str(src),'generatedSourceSha256':sha(src),'resourceJar':str(jar),'resourceJarSha256':sha(jar),'symbols':len(field_values),'libraryStyleableIndicesPreserved':True,'allResourceIdsFromActualLinkedTable':True})
 app=work/'gen/org/lineageos/glimpse/R.java';classes=work/'app-r-classes';classes.mkdir();p=subprocess.run([str(JDK/'bin/javac.exe'),'--release','17','-proc:none','-encoding','UTF-8','-d',str(classes),str(app)],capture_output=True,text=True);assert p.returncode==0,p.stderr
 write_json(work/'real-r-namespace-inputs.json',outputs);write_json(OUT/'verification/evidence/real-resource-namespace-checks.json',{'result':'PASS','libraryNamespacesGenerated':len(outputs),'realNonzeroResourceIds':actual_ids,'originalStyleableIndexEntriesPreserved':styleable_count,'appRClasses':str(classes),'frameworkAttrCount':len(framework_attrs),'sdk36Sha256':sha(android),'resourceLinkSha256':report['linkedResourcePackageSha256'],'generatedFromRealResourcesNotPlaceholderIds':True,'nativeInflation':'NOT RUN','wholeGoalComplete':False})
 print({'libraryNamespaces':len(outputs),'actualResourceIds':actual_ids,'styleableIndices':styleable_count,'appResourceClassCompile':'PASS'})
if __name__=='__main__':main()
