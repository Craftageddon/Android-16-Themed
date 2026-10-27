/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.Context;
import android.util.AttributeSet;
import android.widget.SeekBar;
import androidx.preference.PreferenceManager;
import androidx.preference.PreferenceViewHolder;
import androidx.preference.SeekBarPreference;
import org.lineageos.glimpse.R;
/** Native min/max/increment, numeric value and persistence remain in SeekBarPreference. */
public final class ForgeSeekBarPreference extends SeekBarPreference {
 public ForgeSeekBarPreference(Context c,AttributeSet a){super(c,a);}
 @Override public void onBindViewHolder(PreferenceViewHolder h){
  super.onBindViewHolder(h);
  boolean feature=PreferenceManager.getDefaultSharedPreferences(getContext())
       .getBoolean("double_tap_to_seek_enabled",false);
  ForgeGallerySkin.preference(h.itemView,feature);
  SeekBar bar=(SeekBar)h.findViewById(androidx.preference.R.id.seekbar);
  if(bar==null)return;
  bar.setThumb(new ForgeDrawable(getContext().getResources(),getContext().getTheme(),"cg_gl_seek_thumb"));
  bar.setProgressDrawable(getContext().getDrawable(R.drawable.cg_gl_seek_progress));
  bar.setThumbTintList(null);bar.setProgressTintList(null);bar.setProgressBackgroundTintList(null);
  // Exact source dependency key, not progress, widget presence or generic enabled state.
  bar.setActivated(feature);
 }
}
