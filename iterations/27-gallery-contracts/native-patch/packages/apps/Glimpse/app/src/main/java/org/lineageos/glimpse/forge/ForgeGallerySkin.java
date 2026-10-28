/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.res.ColorStateList;
import android.graphics.Rect;
import android.view.View;
import android.widget.Button;
import androidx.appcompat.app.AlertDialog;
import androidx.media3.ui.DefaultTimeBar;
import com.google.android.material.snackbar.Snackbar;
/** Scoped view-only adapters; no file, player, repository or permission operation. */
public final class ForgeGallerySkin {
 private static final int TEXT=0xffeee7d9,COLD=0xffb5bdc6,EMBER=0xffe56620;
 private static ForgeDrawable skin(View v,String family){return new ForgeDrawable(v.getResources(),v.getContext().getTheme(),family);}
 private static void button(View v){button(v,"cg_gl_button");}
 private static void button(View v,String family){
  if(v==null)return;ForgeDrawable d=skin(v,family);Rect p=new Rect();d.getPadding(p);
  v.setBackgroundTintList(null);v.setBackground(d);
  v.setPadding(Math.max(v.getPaddingLeft(),p.left),Math.max(v.getPaddingTop(),p.top),
      Math.max(v.getPaddingRight(),p.right),Math.max(v.getPaddingBottom(),p.bottom));
 }
 public static void preference(View row,boolean actualFeature){
  row.setBackgroundTintList(null);row.setBackground(skin(row,"cg_gl_panel"));
  row.setMinimumHeight(Math.max(row.getMinimumHeight(),row.getBackground().getMinimumHeight()));
  row.setActivated(actualFeature);
 }
 public static void installPlayerControls(View root){
  View bottom=root.findViewById(androidx.media3.ui.R.id.exo_bottom_bar);
  if(bottom!=null){bottom.setBackgroundTintList(null);bottom.setBackground(skin(bottom,"cg_gl_media_frame"));}
  for(int id:new int[]{androidx.media3.ui.R.id.exo_play_pause,androidx.media3.ui.R.id.exo_rew,
      androidx.media3.ui.R.id.exo_ffwd,androidx.media3.ui.R.id.exo_rew_with_amount,
      androidx.media3.ui.R.id.exo_ffwd_with_amount,androidx.media3.ui.R.id.exo_settings,
      androidx.media3.ui.R.id.exo_subtitle,androidx.media3.ui.R.id.exo_overflow_show,
      androidx.media3.ui.R.id.exo_overflow_hide})button(root.findViewById(id),"cg_gl_media_frame");
 }
 public static void playerControls(View root,boolean isPlaying){
  View bottom=root.findViewById(androidx.media3.ui.R.id.exo_bottom_bar);
  if(bottom!=null&&bottom.getBackground() instanceof ForgeDrawable)
      ((ForgeDrawable)bottom.getBackground()).setFeatureActive(isPlaying);
  View bar=root.findViewById(androidx.media3.ui.R.id.exo_progress);
  if(bar instanceof DefaultTimeBar){
   bar.setActivated(isPlaying);DefaultTimeBar time=(DefaultTimeBar)bar;
   time.setPlayedColor(isPlaying?EMBER:COLD);time.setScrubberColor(isPlaying?EMBER:COLD);
   time.setBufferedColor(0xff596571);time.setUnplayedColor(0xff27333e);
  }
 }
 public static void dialog(AlertDialog d){
  if(d.getWindow()!=null)d.getWindow().setBackgroundDrawable(new ForgeDrawable(d.getContext().getResources(),d.getContext().getTheme(),"cg_gl_panel"));
  for(int which:new int[]{AlertDialog.BUTTON_POSITIVE,AlertDialog.BUTTON_NEGATIVE,AlertDialog.BUTTON_NEUTRAL}){
   Button b=d.getButton(which);if(b==null)continue;button(b);
   b.setMinHeight(Math.max(b.getMinHeight(),b.getBackground().getMinimumHeight()));
   b.setTextColor(new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},new int[]{0xff8f9ba7,TEXT}));
  }
 }
 public static void snackbar(Snackbar bar){
  View v=bar.getView();v.setBackgroundTintList(null);v.setBackground(skin(v,"cg_gl_panel"));
  bar.setTextColor(TEXT);bar.setActionTextColor(COLD);
 }
}
