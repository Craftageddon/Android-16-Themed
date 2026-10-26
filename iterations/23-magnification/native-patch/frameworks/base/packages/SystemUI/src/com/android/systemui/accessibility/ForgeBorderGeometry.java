package com.android.systemui.accessibility;

/** Scalar geometry shared by the source fixtures and native border renderer. */
public final class ForgeBorderGeometry {
    private ForgeBorderGeometry() {}

    // Matches the pinned GradientDrawable.ensureValidRect/draw rectangle branch:
    // inset by half the actual stroke, then clamp one uniform radius in both axes.
    public static float[] centerline(float width, float height, float stroke, float radius) {
        if (width <= stroke || height <= stroke || stroke <= 0) return null;
        float inset = stroke * .5f;
        float clamped = Math.max(0, Math.min(radius, Math.min(width-stroke, height-stroke)*.5f));
        return new float[] {inset, inset, width-inset, height-inset, clamped};
    }

    // Fullscreen's native surface extends outside the physical display. Move
    // only the light rail into its visible stroke; the native cold footprint
    // and surface offset stay unchanged.
    public static float[] glowline(float[] base, float inward) {
        if (base == null) return null;
        float delta = Math.max(0, inward);
        if (base[2]-base[0] <= 2*delta || base[3]-base[1] <= 2*delta) return null;
        return new float[] {base[0]+delta, base[1]+delta, base[2]-delta, base[3]-delta,
                Math.max(0, base[4]-delta)};
    }
}
