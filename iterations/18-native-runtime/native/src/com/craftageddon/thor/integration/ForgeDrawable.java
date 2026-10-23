package com.craftageddon.thor.integration;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.PixelFormat;
import android.graphics.PorterDuff;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
/** Android inflates compiled nine-patches; each neutral mask is tinted independently. */
public final class ForgeDrawable extends Drawable {
    private static final String[] NAMES={"cold","reflection","spill","seam","core","focus","symbol"};
    private static final int[] COLORS={0xffdc5920,0xffff4908,0xffff5b0b,0xffffd083,0xffd5e7f2,0xffffe5bc};
    private final Drawable[] layers=new Drawable[7];
    private final boolean lockedOff;
    private StatePolicy policy=StatePolicy.resolve(true,false,false,false,false,false);
    private int alpha=255;
    public ForgeDrawable(Context context,String family,boolean lockedOff) {
        this.lockedOff=lockedOff;
        for(int i=0;i<7;i++){
            int id=context.getResources().getIdentifier("cg_rf_"+family+"_"+NAMES[i],"drawable",context.getPackageName());
            if(id==0) throw new IllegalArgumentException("Missing steel layer: "+family+"/"+NAMES[i]);
            layers[i]=context.getResources().getDrawable(id,context.getTheme()).mutate();
            if(i>0) layers[i].setColorFilter(COLORS[i-1],PorterDuff.Mode.SRC_IN);
        }
    }
    private static boolean has(int[] states,int target){for(int s:states)if(s==target)return true;return false;}
    @Override public boolean isStateful(){return true;}
    @Override protected boolean onStateChange(int[] states){
        policy=StatePolicy.resolve(has(states,android.R.attr.state_enabled),has(states,android.R.attr.state_checked),has(states,android.R.attr.state_selected),has(states,android.R.attr.state_focused),has(states,android.R.attr.state_pressed),lockedOff);
        invalidateSelf();return true;
    }
    @Override protected void onBoundsChange(Rect bounds){for(Drawable d:layers)d.setBounds(bounds);}
    @Override public void draw(Canvas canvas){
        layers[0].setAlpha(Math.round(alpha*policy.base));layers[0].draw(canvas);
        for(int i=1;i<7;i++){float gain=policy.gains[i-1];if(gain>0){layers[i].setAlpha(Math.round(alpha*gain));layers[i].draw(canvas);}}
    }
    @Override public void setAlpha(int value){alpha=Math.max(0,Math.min(255,value));invalidateSelf();}
    // Whole-background color tint would recolor the cold steel. Only individual masks may tint.
    @Override public void setColorFilter(ColorFilter ignored){}
    @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
}
