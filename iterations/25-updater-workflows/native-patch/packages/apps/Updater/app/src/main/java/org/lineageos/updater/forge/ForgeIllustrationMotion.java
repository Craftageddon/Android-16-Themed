package org.lineageos.updater.forge;
/** Source animation progress drives presentation only; no clock or updater operation exists here. */
public final class ForgeIllustrationMotion {
 public static final int CHECKING=0, ERROR=1, READY=2;
 private static float unit(float v) { return Float.isFinite(v) ? Math.max(0f,Math.min(1f,v)) : 0f; }
 public static float emission(int kind,float progress) {
  float p=unit(progress);
  if(kind==READY)return 0f;
  if(kind==ERROR) {
   if(p<=0f||p>=1f)return 0f;
   double wave=Math.sin(Math.PI*p);return (float)(.8*wave*wave);
  }
  return .65f+.35f*(float)Math.sin(Math.PI*p);
 }
 public static float rotation(int kind,float progress) { return kind==CHECKING?360f*unit(progress):0f; }
}
