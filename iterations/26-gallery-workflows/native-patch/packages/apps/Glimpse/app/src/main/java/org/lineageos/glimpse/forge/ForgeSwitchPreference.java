/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.Context;
import android.util.AttributeSet;
import androidx.preference.PreferenceViewHolder;
import androidx.preference.SwitchPreferenceCompat;
/** Actual native preference value drives the row; original persistence/actions stay in the base owner. */
public final class ForgeSwitchPreference extends SwitchPreferenceCompat {
 public ForgeSwitchPreference(Context c,AttributeSet a){super(c,a);}
 @Override public void onBindViewHolder(PreferenceViewHolder h){
  super.onBindViewHolder(h);ForgeGallerySkin.preference(h.itemView,isChecked());
 }
}
