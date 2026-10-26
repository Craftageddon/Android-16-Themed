package org.lineageos.settings.ayn.forge;
import org.lineageos.settings.ayn.R;
/** Explicit references keep every neutral layer reachable during native resource shrinking. */
final class ForgeResources {
 static int[] layers(String family) {
  switch(family) {
   case "cg_ayn_gate": return new int[] {R.drawable.cg_ayn_gate_cold, R.drawable.cg_ayn_gate_reflection, R.drawable.cg_ayn_gate_spill, R.drawable.cg_ayn_gate_seam, R.drawable.cg_ayn_gate_core, R.drawable.cg_ayn_gate_focus, R.drawable.cg_ayn_gate_symbol};
   case "cg_ayn_dot": return new int[] {R.drawable.cg_ayn_dot_cold, R.drawable.cg_ayn_dot_reflection, R.drawable.cg_ayn_dot_spill, R.drawable.cg_ayn_dot_seam, R.drawable.cg_ayn_dot_core, R.drawable.cg_ayn_dot_focus, R.drawable.cg_ayn_dot_symbol};
   case "cg_ayn_rgb_thumb": return new int[] {R.drawable.cg_ayn_rgb_thumb_cold, R.drawable.cg_ayn_rgb_thumb_reflection, R.drawable.cg_ayn_rgb_thumb_spill, R.drawable.cg_ayn_rgb_thumb_seam, R.drawable.cg_ayn_rgb_thumb_core, R.drawable.cg_ayn_rgb_thumb_focus, R.drawable.cg_ayn_rgb_thumb_symbol};
   case "cg_rf_button": return new int[] {R.drawable.cg_rf_button_cold, R.drawable.cg_rf_button_reflection, R.drawable.cg_rf_button_spill, R.drawable.cg_rf_button_seam, R.drawable.cg_rf_button_core, R.drawable.cg_rf_button_focus, R.drawable.cg_rf_button_symbol};
   case "cg_rf_field": return new int[] {R.drawable.cg_rf_field_cold, R.drawable.cg_rf_field_reflection, R.drawable.cg_rf_field_spill, R.drawable.cg_rf_field_seam, R.drawable.cg_rf_field_core, R.drawable.cg_rf_field_focus, R.drawable.cg_rf_field_symbol};
   case "cg_rf_panel": return new int[] {R.drawable.cg_rf_panel_cold, R.drawable.cg_rf_panel_reflection, R.drawable.cg_rf_panel_spill, R.drawable.cg_rf_panel_seam, R.drawable.cg_rf_panel_core, R.drawable.cg_rf_panel_focus, R.drawable.cg_rf_panel_symbol};
   default: throw new IllegalArgumentException("Unknown Forge family: "+family);
  }
 }
}
