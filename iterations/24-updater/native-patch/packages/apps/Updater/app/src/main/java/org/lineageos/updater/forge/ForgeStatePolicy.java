package org.lineageos.updater.forge;

/** Explicit feature/input activation. Focus alone never enables ember. No clock. */
public final class ForgeStatePolicy {
    public final boolean active;
    public final float base;
    public final float[] gains;
    private ForgeStatePolicy(boolean active, float base, float[] gains) {
        this.active = active; this.base = base; this.gains = gains;
    }
    public static ForgeStatePolicy resolve(boolean enabled, boolean checked, boolean selected,
            boolean focused, boolean pressed, boolean featureActive, boolean momentary) {
        boolean active = enabled && (checked || selected || featureActive || (momentary && pressed));
        float[] gains = new float[6];
        if (active) {
            gains[0] = pressed ? .60f : .32f;
            gains[1] = pressed ? .92f : .72f;
            gains[2] = 1f;
            gains[3] = pressed ? 1f : .82f;
            gains[5] = 1f;
        }
        gains[4] = enabled && focused ? 1f : 0f;
        return new ForgeStatePolicy(active, enabled ? 1f : .42f, gains);
    }
}
