'''Save pinned native build rules used for resource and class order interpretation.'''
import hashlib,time
from audit_os_resource_coverage import ROOT,get,write_json
OUT=ROOT/'iterations/27-gallery-contracts';REV='183e59578606687d66096cbce86cb50c27f4e9d7'
def main():
 folder=OUT/'source/native-build-contracts';folder.mkdir(parents=True,exist_ok=True);rows=[]
 for rel in ['java/aar.go','java/builder.go','java/java.go','java/kotlin.go','java/config/kotlin.go']:
  url='https://raw.githubusercontent.com/LineageOS/android_build_soong/'+REV+'/'+rel;p=folder/rel;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(get(url));time.sleep(.8)
  data=p.read_bytes();rows.append({'project':'build/soong','revision':REV,'path':rel,'url':url,'saved':p.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'gitBlobSha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
 p=ROOT/'build-work/gallery27-native-dependencies/depset.go';data=p.read_bytes();target=folder/'blueprint/depset/depset.go';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);rows.append({'project':'build/blueprint','revision':'7f2058de8155b05ea3c3f8317d33bfe732cacf8b','path':'depset/depset.go','saved':target.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'gitBlobSha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
 write_json(OUT/'source/native-build-contracts.json',{'files':rows,'resourceOrderInterpretation':'Dependency-first stable order derived from the pinned AAR resource-node order and overlay reversal; both native Material providers retained.','classOrderInterpretation':'Native PREORDER transitive header/static class providers; paired real R namespace jars and original native library inputs.','actualInvocation':'Manual resource linking and real full source compilation, not official Soong, ABI generation, dex, R8 or device execution.','wholeGoalComplete':False});print({'pinnedBuildRuleSourcesSaved':len(rows),'soongExecuted':False})
if __name__=='__main__':main()
