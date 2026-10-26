package org.lineageos.settings.ayn.forge;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.PixelFormat;
import android.graphics.PorterDuff;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;

/** Native compiled PNG/nine-patch layers; source geometry and light masks stay separate. */
public final class ForgeLayerDrawable extends Drawable {
    private static final int[] COLORS = {0xffdc5920, 0xffff4908, 0xffff5b0b,
            0xffffd083, 0xffd5e7f2, 0xffffe5bc};
    private final Drawable[] layers = new Drawable[7];
    private final boolean momentary;
    private final int intrinsicWidth;
    private final int intrinsicHeight;
    private boolean featureActive;
    private float featureStrength = 1f;
    private float emissionStrength = 1f;
    private int alpha = 255;
    private ForgeStatePolicy policy = ForgeStatePolicy.resolve(true, false, false, false,
            false, false, false);
    public ForgeLayerDrawable(Context context, String family, boolean momentary) {
        this(context.getResources(), context.getTheme(), family, momentary);
    }
    public ForgeLayerDrawable(Resources resources, Resources.Theme theme, String family, boolean momentary) {
        this.momentary = momentary;
        int[] ids = ForgeResources.layers(family); // Static R references survive resource shrinking.
        for (int i = 0; i < layers.length; i++) {
            layers[i] = resources.getDrawable(ids[i], theme).mutate();
            if (i > 0) layers[i].setColorFilter(COLORS[i-1], PorterDuff.Mode.SRC_IN);
        }
        intrinsicWidth = layers[0].getIntrinsicWidth();
        intrinsicHeight = layers[0].getIntrinsicHeight();
        setState(new int[] {android.R.attr.state_enabled});
    }
    public void setFeatureActive(boolean active) {
        if (featureActive != active || featureStrength != 1f) {
            featureActive = active; featureStrength = 1f; onStateChange(getState());
        }
    }
    /** Actual analog amplitude drives lighting; tiny raw-axis noise cannot flash at full gain. */
    public void setInputStrength(float strength) {
        float value = Float.isNaN(strength) ? 0f : Math.max(0f, Math.min(1f, strength));
        if (featureStrength != value || featureActive != (value > 0f)) {
            featureStrength = value; featureActive = value > 0f; onStateChange(getState());
        }
    }
    private static boolean has(int[] states, int target) {
        for (int state : states) if (state == target) return true;
        return false;
    }
    @Override public boolean isStateful() { return true; }
    @Override protected boolean onStateChange(int[] states) {
        boolean semanticSelection = has(states, android.R.attr.state_checked)
                || has(states, android.R.attr.state_selected)
                || (momentary && has(states, android.R.attr.state_pressed));
        emissionStrength = semanticSelection ? 1f : featureStrength;
        policy = ForgeStatePolicy.resolve(has(states, android.R.attr.state_enabled),
                has(states, android.R.attr.state_checked), has(states, android.R.attr.state_selected),
                has(states, android.R.attr.state_focused), has(states, android.R.attr.state_pressed),
                featureActive, momentary);
        invalidateSelf(); return true;
    }
    @Override protected void onBoundsChange(Rect bounds) {
        for (Drawable drawable : layers) drawable.setBounds(bounds);
    }
    @Override public void draw(Canvas canvas) {
        layers[0].setAlpha(Math.round(alpha * policy.base)); layers[0].draw(canvas);
        for (int i = 1; i < layers.length; i++) {
            if (policy.gains[i-1] > 0) {
                float strength = i == 5 ? 1f : emissionStrength; // Neutral focus is independent.
                layers[i].setAlpha(Math.round(alpha * policy.gains[i-1] * strength)); layers[i].draw(canvas);
            }
        }
    }
    @Override public int getIntrinsicWidth() { return intrinsicWidth; }
    @Override public int getIntrinsicHeight() { return intrinsicHeight; }
    @Override public void setAlpha(int value) { alpha = Math.max(0, Math.min(255, value)); invalidateSelf(); }
    // Whole-object tint must never recolor the cold steel; only neutral masks are tinted.
    @Override public void setColorFilter(ColorFilter ignored) {}
    @Override public int getOpacity() { return PixelFormat.TRANSLUCENT; }
}
