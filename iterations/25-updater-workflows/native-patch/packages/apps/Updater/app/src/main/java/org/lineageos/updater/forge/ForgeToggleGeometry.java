package org.lineageos.updater.forge;
/** Only presentation geometry; actual checked/changeable callbacks remain in their owners. */
public final class ForgeToggleGeometry {
 public static float thumbLeft(Boolean checked, float width, float thumb, boolean rtl) {
  float travel = Math.max(0f, width - thumb);
  return checked == null ? travel / 2f : checked.booleanValue() != rtl ? travel : 0f;
 }
 public static boolean featureOn(Boolean checked) { return Boolean.TRUE.equals(checked); }
}
