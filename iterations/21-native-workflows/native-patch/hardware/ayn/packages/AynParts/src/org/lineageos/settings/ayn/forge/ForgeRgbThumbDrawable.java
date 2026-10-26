package org.lineageos.settings.ayn.forge;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.view.View;
import java.lang.ref.WeakReference;

/** A flat channel-data swatch over cold steel; gesture emission is a separate state. */
public final class ForgeRgbThumbDrawable extends Drawable implements Drawable.Callback {
    private final ForgeLayerDrawable housing;
    private final Paint channel = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final ThumbState constantState;
    private int alpha = 255;
    public ForgeRgbThumbDrawable(Context context, int channelColor, View slider) {
        this(context.getResources(), context.getTheme(), channelColor, new WeakReference<View>(slider));
    }
    private ForgeRgbThumbDrawable(Resources resources, Resources.Theme theme, int channelColor,
            WeakReference<View> owner) {
        constantState = new ThumbState(resources, theme, channelColor, owner);
        housing = new ForgeLayerDrawable(resources, theme, "cg_ayn_rgb_thumb", true);
        housing.setCallback(this); channel.setColor(channelColor);
        setState(new int[] {android.R.attr.state_enabled});
    }
    @Override public ConstantState getConstantState() { return constantState; }
    @Override public boolean isStateful() { return true; }
    @Override protected boolean onStateChange(int[] state) {
        housing.setState(state); invalidateSelf(); return true;
    }
    @Override protected void onBoundsChange(Rect bounds) { housing.setBounds(bounds); }
    @Override public void draw(Canvas canvas) {
        View slider = constantState.owner.get();
        // Material clones custom thumbs and does not forward its state to those clones.
        // Read the real owner on each requested draw; no polling or extra hardware callback.
        if (slider != null) housing.setState(slider.getDrawableState());
        housing.draw(canvas);
        Rect bounds = getBounds();
        channel.setAlpha(Math.round(alpha * ((slider != null ? slider.isEnabled() : isEnabled()) ? 1f : .42f)));
        canvas.drawCircle(bounds.exactCenterX(), bounds.exactCenterY(),
                Math.min(bounds.width(), bounds.height()) / 9f, channel);
    }
    private boolean isEnabled() {
        for (int state : getState()) if (state == android.R.attr.state_enabled) return true;
        return false;
    }
    @Override public int getIntrinsicWidth() { return housing.getIntrinsicWidth(); }
    @Override public int getIntrinsicHeight() { return housing.getIntrinsicHeight(); }
    @Override public void setAlpha(int value) {
        alpha = Math.max(0, Math.min(255, value)); housing.setAlpha(alpha); invalidateSelf();
    }
    @Override public void setColorFilter(ColorFilter ignored) {}
    @Override public int getOpacity() { return PixelFormat.TRANSLUCENT; }
    @Override public void invalidateDrawable(Drawable who) { invalidateSelf(); }
    @Override public void scheduleDrawable(Drawable who, Runnable what, long when) { scheduleSelf(what, when); }
    @Override public void unscheduleDrawable(Drawable who, Runnable what) { unscheduleSelf(what); }
    private static final class ThumbState extends ConstantState {
        final Resources resources;
        final Resources.Theme theme;
        final int color;
        final WeakReference<View> owner;
        ThumbState(Resources resources, Resources.Theme theme, int color, WeakReference<View> owner) {
            this.resources = resources; this.theme = theme; this.color = color; this.owner = owner;
        }
        @Override public Drawable newDrawable() {
            return new ForgeRgbThumbDrawable(resources, theme, color, owner);
        }
        @Override public Drawable newDrawable(Resources resources) {
            return new ForgeRgbThumbDrawable(resources, theme, color, owner);
        }
        @Override public Drawable newDrawable(Resources resources, Resources.Theme theme) {
            return new ForgeRgbThumbDrawable(resources, theme, color, owner);
        }
        @Override public int getChangingConfigurations() { return 0; }
    }
}
