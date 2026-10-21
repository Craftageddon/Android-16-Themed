package com.craftageddon.materiallab;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorFilter;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;

/** Independent state layers backed by density-selected Android NinePatchDrawables. */
public final class MaterialDrawable extends Drawable {
    private final Drawable[] layers = new Drawable[5];
    private final float[] gain = {1f, .34f, .18f, 0f, 0f};
    private int alpha = 255;
    private boolean coldInspection;

    public MaterialDrawable(Context context, String family) {
        String[] names = {"cold", "seam", "core", "focus", "symbol"};
        for (int i=0; i<names.length; i++) {
            int id=context.getResources().getIdentifier("cg_es_"+family+"_"+names[i], "drawable", context.getPackageName());
            if (id==0) throw new IllegalArgumentException("Missing material layer: "+family+"/"+names[i]);
            layers[i]=context.getResources().getDrawable(id, context.getTheme()).mutate();
            if (!(layers[i] instanceof android.graphics.drawable.NinePatchDrawable)) throw new IllegalStateException("Expected compiled nine-patch");
        }
        layers[1].setTint(Color.rgb(255,107,36)); layers[2].setTint(Color.rgb(255,192,120));
        layers[3].setTint(Color.rgb(213,231,242)); layers[4].setTint(Color.rgb(238,231,217));
    }
    public void setColdInspection(boolean value) {coldInspection=value; invalidateSelf();}
    private static boolean has(int[] states, int wanted) {for(int state:states) if(state==wanted) return true; return false;}
    @Override public boolean isStateful() {return true;}
    @Override protected boolean onStateChange(int[] states) {
        boolean enabled=has(states,android.R.attr.state_enabled), pressed=has(states,android.R.attr.state_pressed);
        boolean selected=has(states,android.R.attr.state_selected), focused=has(states,android.R.attr.state_focused), hovered=has(states,android.R.attr.state_hovered);
        gain[0]=enabled?1f:.42f;
        gain[1]=!enabled?0f:pressed?1f:selected?.72f:focused?.58f:hovered?.5f:.34f;
        gain[2]=!enabled?0f:pressed?1f:selected?.65f:focused?.45f:hovered?.35f:.18f;
        gain[3]=enabled&&focused?1f:0f; gain[4]=enabled&&selected?1f:0f;
        invalidateSelf(); return true;
    }
    @Override public void draw(Canvas canvas) {
        for(int i=0;i<layers.length;i++) {
            float value=coldInspection&&i>0?0f:gain[i];
            if(value==0) continue;
            layers[i].setAlpha(Math.round(alpha*value)); layers[i].draw(canvas);
        }
    }
    @Override protected void onBoundsChange(Rect bounds) {for(Drawable layer:layers) layer.setBounds(bounds);}
    @Override public boolean getPadding(Rect out) {return layers[0].getPadding(out);}
    @Override public int getIntrinsicWidth() {return layers[0].getIntrinsicWidth();}
    @Override public int getIntrinsicHeight() {return layers[0].getIntrinsicHeight();}
    @Override public void setAlpha(int value) {alpha=Math.max(0,Math.min(255,value));invalidateSelf();}
    @Override public void setColorFilter(ColorFilter value) {layers[0].setColorFilter(value);invalidateSelf();}
    @Override public int getOpacity() {return PixelFormat.TRANSLUCENT;}
    // Static state lighting: no frame callbacks, idle timers, bloom buffers or hidden-view animation.
}
