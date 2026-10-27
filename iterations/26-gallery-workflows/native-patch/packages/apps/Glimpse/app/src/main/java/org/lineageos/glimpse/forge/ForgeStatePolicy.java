/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
/** Source-owned values, interaction and neutral focus remain distinct. No clock or media action. */
public final class ForgeStatePolicy {
 public static final int DYNAMIC=0, TRUE_VALUE=1, FALSE_VALUE=2;
 public final boolean active; public final float base; public final float[] gains;
 private ForgeStatePolicy(boolean a,float b,float[] g){active=a;base=b;gains=g;}
 public static ForgeStatePolicy resolve(int mode,boolean enabled,boolean checked,boolean selected,
         boolean activated,boolean focused,boolean hovered,boolean pressed,boolean feature,boolean momentary){
  if(mode<0||mode>2)throw new IllegalArgumentException("Unknown source value mode");
  boolean active=mode==TRUE_VALUE || (mode==DYNAMIC &&
      (checked||selected||activated||feature||(enabled&&momentary&&pressed)));
  float[] g=new float[6];float strength=enabled?1f:.6f;
  if(active){g[0]=(enabled&&pressed?.60f:.32f)*strength;g[1]=(enabled&&pressed?.92f:.72f)*strength;
      g[2]=strength;g[3]=(enabled&&pressed?1f:.82f)*strength;g[5]=strength;}
  g[4]=enabled&&(focused||hovered)?1f:0f;
  return new ForgeStatePolicy(active,enabled?1f:.42f,g);
 }
}
