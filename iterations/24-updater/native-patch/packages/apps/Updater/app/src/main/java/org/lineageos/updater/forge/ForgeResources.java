package org.lineageos.updater.forge;
import org.lineageos.updater.R;
final class ForgeResources {
 static int[] layers(String family) {
  switch(family) {
   case "cg_rf_button": return new int[] {R.drawable.cg_rf_button_cold, R.drawable.cg_rf_button_reflection, R.drawable.cg_rf_button_spill, R.drawable.cg_rf_button_seam, R.drawable.cg_rf_button_core, R.drawable.cg_rf_button_focus, R.drawable.cg_rf_button_symbol};
   case "cg_rf_field": return new int[] {R.drawable.cg_rf_field_cold, R.drawable.cg_rf_field_reflection, R.drawable.cg_rf_field_spill, R.drawable.cg_rf_field_seam, R.drawable.cg_rf_field_core, R.drawable.cg_rf_field_focus, R.drawable.cg_rf_field_symbol};
   case "cg_rf_panel": return new int[] {R.drawable.cg_rf_panel_cold, R.drawable.cg_rf_panel_reflection, R.drawable.cg_rf_panel_spill, R.drawable.cg_rf_panel_seam, R.drawable.cg_rf_panel_core, R.drawable.cg_rf_panel_focus, R.drawable.cg_rf_panel_symbol};
   case "cg_upd_rail": return new int[] {R.drawable.cg_upd_rail_cold, R.drawable.cg_upd_rail_reflection, R.drawable.cg_upd_rail_spill, R.drawable.cg_upd_rail_seam, R.drawable.cg_upd_rail_core, R.drawable.cg_upd_rail_focus, R.drawable.cg_upd_rail_symbol};
   default: throw new IllegalArgumentException("Unknown Forge family: "+family);
  }
 }
}
