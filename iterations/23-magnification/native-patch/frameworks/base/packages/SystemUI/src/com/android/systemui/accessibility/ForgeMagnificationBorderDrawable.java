package com.android.systemui.accessibility;

import android.content.res.Resources;
import android.content.res.Resources.Theme;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.ComposeShader;
import android.graphics.DashPathEffect;
import android.graphics.LinearGradient;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.graphics.PorterDuff;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import com.android.systemui.res.R;

/** Native rounded/dashed geometry, cold steel, and independent runtime light.
 * No capture, view polling, timers, user-content bitmap, or input callback.
 */
public final class ForgeMagnificationBorderDrawable extends GradientDrawable {
    public static final int FULLSCREEN = 0;
    public static final int WINDOW = 1;
    public static final int WINDOW_EDIT = 2;
    private final Resources resources;
    private final Theme theme;
    private final int role;
    private final Path main = new Path(), outer = new Path(), glow = new Path();
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Bitmap material;
    private final int reflection, spill, seam, core;
    private float stroke, radius, outerStroke, outerRadius, visibleFullscreenStroke;
    private float density;
    private Shader coldShader;
    private DashPathEffect editDashes;
    private boolean dirty = true, enabled = true, featureActive = true;

    public ForgeMagnificationBorderDrawable(Resources res, Theme th, int kind) {
        resources = res; theme = th; role = kind;
        density = res.getDisplayMetrics().density;
        material = BitmapFactory.decodeResource(res, R.drawable.cg_mag_steel_material);
        reflection = res.getColor(R.color.cg_mag_reflection, th);
        spill = res.getColor(R.color.cg_mag_spill, th);
        seam = res.getColor(R.color.cg_mag_seam, th);
        core = res.getColor(R.color.cg_mag_core, th);
        super.setShape(RECTANGLE);
        super.setColor(Color.TRANSPARENT);
        if (kind == FULLSCREEN) {
            stroke = res.getDimensionPixelSize(R.dimen.magnifier_border_width_fullscreen_with_offset);
            visibleFullscreenStroke = res.getDimensionPixelSize(R.dimen.magnifier_border_width_fullscreen);
            // The actual physical display radius is supplied by the unchanged
            // FullscreenMagnificationController.applyCornerRadiusToBorder().
            radius = 0;
        } else {
            stroke = res.getDimensionPixelSize(R.dimen.magnifier_border_width);
            outerStroke = res.getDimensionPixelSize(R.dimen.magnifier_stroke_width);
            radius = res.getDimension(kind == WINDOW_EDIT ? R.dimen.magnifier_edit_corner_radius : R.dimen.magnifier_corner_radius);
            outerRadius = res.getDimension(kind == WINDOW_EDIT ? R.dimen.magnifier_edit_outer_corner_radius : R.dimen.magnifier_outer_corner_radius);
        }
        super.setStroke(Math.round(stroke), Color.WHITE);
        super.setCornerRadius(radius);
        paint.setStyle(Paint.Style.STROKE);
    }

    @Override public void setStroke(int width, int nativeColor) {
        // Preserve the native caller's exact pixel geometry. Its theme accent
        // is replaced only by the separate Forge palette, never by a bitmap.
        stroke = width;
        super.setStroke(width, Color.WHITE);
        dirty = true; invalidateSelf();
    }

    @Override public void setCornerRadius(float value) {
        radius = value;
        super.setCornerRadius(value);
        dirty = true; invalidateSelf();
    }

    public void setFeatureActive(boolean active) {
        if (featureActive != active) { featureActive = active; invalidateSelf(); }
    }

    @Override protected void onBoundsChange(Rect bounds) {
        super.onBoundsChange(bounds); dirty = true;
    }

    @Override public boolean isStateful() { return true; }

    @Override protected boolean onStateChange(int[] state) {
        boolean next = false;
        for (int value : state) if (value == android.R.attr.state_enabled) next = true;
        boolean changed = next != enabled; enabled = next;
        if (changed) invalidateSelf();
        return changed;
    }

    private static void setPath(Path path, float[] geometry, Rect bounds) {
        path.reset();
        if (geometry == null) return;
        RectF rect = new RectF(bounds.left+geometry[0], bounds.top+geometry[1],
                bounds.left+geometry[2], bounds.top+geometry[3]);
        path.addRoundRect(rect, geometry[4], geometry[4], Path.Direction.CW);
    }

    private void updatePaths() {
        Rect bounds = getBounds();
        density = resources.getDisplayMetrics().density;
        if (role == FULLSCREEN) visibleFullscreenStroke = resources.getDimensionPixelSize(R.dimen.magnifier_border_width_fullscreen);
        float[] geometry = ForgeBorderGeometry.centerline(bounds.width(), bounds.height(), stroke, radius);
        setPath(main, geometry, bounds);
        setPath(outer, ForgeBorderGeometry.centerline(bounds.width(), bounds.height(), outerStroke, outerRadius), bounds);
        float inward = role == FULLSCREEN ? Math.max(0, (stroke-visibleFullscreenStroke)*.5f) : 0;
        setPath(glow, ForgeBorderGeometry.glowline(geometry, inward), bounds);
        Shader texture = new BitmapShader(material, Shader.TileMode.REPEAT, Shader.TileMode.REPEAT);
        Matrix transform = new Matrix(); transform.setScale(density, density);
        transform.postTranslate(bounds.left, bounds.top); texture.setLocalMatrix(transform);
        Shader bevel = new LinearGradient(bounds.left, bounds.top, bounds.left, bounds.bottom,
                new int[] {0xff9da9b2,0xff394957,0xff101924,0xff576b7b,0xffb0bec8},
                new float[] {0,.22f,.52f,.78f,1}, Shader.TileMode.CLAMP);
        coldShader = new ComposeShader(texture, bevel, PorterDuff.Mode.MULTIPLY);
        if (role == WINDOW_EDIT) {
            float dash = resources.getDimension(R.dimen.magnifier_edit_dash_gap);
            editDashes = new DashPathEffect(new float[] {dash, dash}, 0);
        }
        dirty = false;
    }

    private void stroke(Canvas canvas, Path path, float width, int color, float gain) {
        if (path.isEmpty() || width <= 0 || gain <= 0) return;
        paint.setStrokeWidth(width); paint.setShader(null); paint.setColor(color);
        paint.setAlpha(Math.round(Color.alpha(color)*gain*getAlpha()/255f));
        canvas.drawPath(path, paint);
    }

    @Override public void draw(Canvas canvas) {
        if (dirty) updatePaths();
        if (main.isEmpty()) return;
        paint.setPathEffect(editDashes);
        paint.setShader(coldShader); paint.setStrokeWidth(stroke);
        paint.setColor(Color.WHITE); paint.setAlpha(Math.round(getAlpha()*(enabled ? 1f : .42f)));
        canvas.drawPath(main, paint);
        stroke(canvas, main, Math.min(density*.75f,stroke*.12f), 0xffb2bdc6, enabled?.7f:.294f);
        // Soft light is a set of independent neutral-width masks evaluated on
        // the native path. It stays inside the original shell; no magnified
        // pixels or touchable/content regions are tinted or widened.
        if (enabled && featureActive && !glow.isEmpty()) {
            float band = role == FULLSCREEN ? visibleFullscreenStroke : stroke;
            stroke(canvas, glow, band*.90f, spill, .035f);
            stroke(canvas, glow, band*.72f, spill, .065f);
            stroke(canvas, glow, band*.54f, spill, .12f);
            stroke(canvas, glow, band*.36f, spill, .22f);
            stroke(canvas, glow, band*.64f, reflection, .32f);
            stroke(canvas, glow, Math.min(density*2,band*.18f), seam, 1f);
            stroke(canvas, glow, Math.min(density*.65f,band*.055f), core, .82f);
        }
        paint.setPathEffect(null);
        stroke(canvas, outer, outerStroke, 0xff10171f, enabled ? 1f : .42f);
    }

    // A whole-object tint would destroy cold/light separation. Every light
    // color above comes from its own resource and neutral path mask.
    @Override public void setColorFilter(ColorFilter ignored) {}
    @Override public int getOpacity() { return PixelFormat.TRANSLUCENT; }

    @Override public ConstantState getConstantState() {
        final float savedStroke = stroke, savedRadius = radius;
        final int savedAlpha = getAlpha(); final boolean active = featureActive;
        final float sourceDensity = resources.getDisplayMetrics().density;
        return new Drawable.ConstantState() {
            @Override public Drawable newDrawable() { return create(resources, theme); }
            @Override public Drawable newDrawable(Resources res) { return create(res, null); }
            @Override public Drawable newDrawable(Resources res, Theme th) { return create(res, th); }
            private Drawable create(Resources res, Theme th) {
                ForgeMagnificationBorderDrawable copy = new ForgeMagnificationBorderDrawable(res, th, role);
                float scale = res.getDisplayMetrics().density/sourceDensity;
                copy.setStroke(Math.round(savedStroke*scale), Color.WHITE); copy.setCornerRadius(savedRadius*scale);
                copy.setAlpha(savedAlpha); copy.setFeatureActive(active); return copy;
            }
            @Override public int getChangingConfigurations() { return 0; }
        };
    }
}
