package com.craftageddon.thor.integration;
/** No animation clock: unchecked, unavailable and explicit-off values stay cold. */
public final class StatePolicy {
    public final boolean active;
    public final float base;
    public final float[] gains;
    private StatePolicy(boolean active,float base,float[] gains) {this.active=active;this.base=base;this.gains=gains;}
    public static StatePolicy resolve(boolean enabled,boolean checked,boolean selected,boolean focused,boolean pressed,boolean lockedOff) {
        boolean active=enabled && !lockedOff && (checked || selected);
        float[] g=new float[6];
        if(active) {g[0]=pressed?.60f:.32f;g[1]=pressed?.92f:.72f;g[2]=1f;g[3]=pressed?1f:.82f;g[5]=1f;}
        g[4]=enabled && focused?1f:0f;
        return new StatePolicy(active,enabled?1f:.42f,g);
    }
}
