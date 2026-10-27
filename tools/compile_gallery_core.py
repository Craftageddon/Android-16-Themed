'''Compile actual Gallery core renderer and exercise only its pure presentation policy.'''
from pathlib import Path
import datetime,hashlib,subprocess,shutil,json
from audit_os_resource_coverage import ROOT,read_json,write_json
SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk')
JDK=Path('C:/Program Files/Android/Android Studio/jbr')
OUT=ROOT/'iterations/26-gallery-workflows';PATCH=OUT/'native-patch/packages/apps/Glimpse'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    work=ROOT/'build-work'/('gallery26-core-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True)
    (work/'gen').mkdir();(work/'classes').mkdir();evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
    logs=[]
    def run(args):
        p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace')
        logs.append(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError('Exit '+str(p.returncode)+'\n'+logs[-1])
        return p.stdout
    android=SDK/'platforms/android-36.1/android.jar';aapt=SDK/'build-tools/37.0.0/aapt2.exe'
    # Standalone renderer bank excludes owner layouts requiring real external libraries.
    bank=work/'renderer-res'
    for p in (PATCH/'app/src/main/res').rglob('*'):
        if not p.is_file():continue
        if p.name.startswith('cg_gl_') or p.name in ['cg_gallery_attrs.xml','cg_gallery_colors.xml']:
            if p.parent.name.startswith(('drawable','color')) or p.name in ['cg_gallery_attrs.xml','cg_gallery_colors.xml']:
                target=bank/p.relative_to(PATCH/'app/src/main/res');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    run([aapt,'compile','--dir',PATCH/'app/src/main/res','-o',work/'all-patch-resources.zip'])
    run([aapt,'compile','--dir',bank,'-o',work/'resources.zip'])
    manifest=work/'AndroidManifest.xml';manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.lineageos.glimpse"><uses-sdk android:minSdkVersion="30" android:targetSdkVersion="36"/><application/></manifest>',encoding='utf8')
    run([aapt,'link','-I',android,'--manifest',manifest,'--java',work/'gen','-o',work/'bank.ap_',work/'resources.zip'])
    source=PATCH/'app/src/main/java/org/lineageos/glimpse/forge'
    java=[source/n for n in ['ForgeStatePolicy.java','ForgeResources.java','ForgeDrawable.java']]
    run([JDK/'bin/javac.exe','--release','17','-encoding','UTF-8','-cp',android,'-d',work/'classes',*java,*list((work/'gen').rglob('*.java'))])
    probe=work/'GalleryPolicyProbe.java'
    probe.write_text('''import org.lineageos.glimpse.forge.ForgeStatePolicy;
public final class GalleryPolicyProbe{
 static int n=0;static void require(boolean b){n++;if(!b)throw new AssertionError("case "+n);}
 public static void main(String[] args){
  for(int mode=0;mode<3;mode++)for(int bits=0;bits<512;bits++){
   boolean[] b=new boolean[9];for(int i=0;i<9;i++)b[i]=(bits&(1<<i))!=0;
   ForgeStatePolicy p=ForgeStatePolicy.resolve(mode,b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8]);
   if(mode==2){require(!p.active);for(int i:new int[]{0,1,2,3,5})require(p.gains[i]==0);}
   if(mode==1)require(p.active&&p.gains[2]>0);
   if(mode==0&&(b[1]||b[2]||b[3]||b[7]))require(p.active);
   if(mode==0&&!b[1]&&!b[2]&&!b[3]&&!b[7]&&!(b[0]&&b[6]&&b[8]))require(!p.active);
   if(!b[0])require(p.gains[4]==0&&p.base<1f);
   for(float x:p.gains)require(Float.isFinite(x)&&x>=0&&x<=1);
  }
  for(String key:new String[]{"cold","focused","hovered","pressed","on","on-locked","off-locked"}){
   boolean on=key.equals("on")||key.equals("on-locked");boolean enabled=!key.endsWith("locked");
   ForgeStatePolicy p=ForgeStatePolicy.resolve(0,enabled,false,on,false,key.equals("focused"),key.equals("hovered"),key.equals("pressed"),false,true);
   System.out.print(key+"|"+p.active+"|"+p.base);for(float v:p.gains)System.out.print("|"+v);System.out.println();
  }
  System.out.println("PASS policyAssertions="+n+" cases=1536 mediaOperations=0");
 }
}''',encoding='utf8')
    run([JDK/'bin/javac.exe','-cp',work/'classes','-d',work/'classes',probe])
    output=run([JDK/'bin/java.exe','-cp',work/'classes','GalleryPolicyProbe'])
    assert 'PASS policyAssertions=' in output
    (evidence/'core-policy-host.txt').write_text(output,encoding='utf8')
    run([JDK/'bin/jar.exe','cf',work/'gallery-core.jar','-C',work/'classes','.'])
    shutil.copy2(work/'gallery-core.jar',evidence/'gallery-core.jar');shutil.copy2(work/'resources.zip',evidence/'core-resources.zip')
    (evidence/'core-compiler.txt').write_text('\n'.join(logs),encoding='utf8')
    write_json(evidence/'core-build.json',{'result':'PASS','actualRendererClasses':3,'actualPolicyCases':1536,'nativeSources':{p.relative_to(PATCH).as_posix():sha(p) for p in java},'sdkJar':str(android),'sdkJarSha256':sha(android),'libraryJarSha256':sha(evidence/'gallery-core.jar'),'actualAppOwnersCompiled':False,'fullPinnedSoongBuild':'NOT RUN','nativeXmlInflation':'NOT RUN','wholeGoalComplete':False})
    print(output)
if __name__=='__main__':main()
