/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.Context;
import android.util.AttributeSet;
import com.google.android.material.materialswitch.MaterialSwitch;
/** Existing preference owns checked state, dependency enablement and callbacks. */
public final class ForgeMaterialSwitch extends MaterialSwitch {
 public ForgeMaterialSwitch(Context c,AttributeSet a){
  super(c,a);
  setThumbIconDrawable(null);setTrackDecorationDrawable(null);
  setThumbIconTintList(null);setTrackDecorationTintList(null);
  setThumbTintList(null);setTrackTintList(null);
  setThumbDrawable(new ForgeDrawable(c.getResources(),c.getTheme(),"cg_gl_switch_thumb"));
  setTrackDrawable(new ForgeDrawable(c.getResources(),c.getTheme(),"cg_gl_switch_track"));
  setSwitchMinWidth(Math.round(52*c.getResources().getDisplayMetrics().density));
 }
}
