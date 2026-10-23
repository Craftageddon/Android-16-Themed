package com.craftageddon.thor.integration;
import android.content.Context;
/** Shared state owned by the native toggle and the OS Quick Settings service. */
public final class SelectionStore {
    private SelectionStore(){}
    public static boolean get(Context c){return c.getSharedPreferences("forge-controls",Context.MODE_PRIVATE).getBoolean("selected",false);}
    public static void set(Context c,boolean value){c.getSharedPreferences("forge-controls",Context.MODE_PRIVATE).edit().putBoolean("selected",value).apply();}
}
