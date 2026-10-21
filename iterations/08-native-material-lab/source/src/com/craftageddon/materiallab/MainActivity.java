package com.craftageddon.materiallab;

import android.app.Activity;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Rect;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.ArrayList;

/** Local test surface only. No services, hardware writes, privileged APIs or network. */
public final class MainActivity extends Activity {
    private LinearLayout column;
    private Button target;
    private EditText field;
    private TextView status, panelBody, notification;
    private final ArrayList<MaterialDrawable> materials=new ArrayList<>();
    private boolean narrow=false, rtl=false, cold=false, disabled=false, selected=true;
    private int scaleIndex=0;
    private final float[] scales={1f,1.3f,1.6f,2f};
    private int dp(float v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private TextView label(String text,int sp){TextView v=new TextView(this);v.setText(text);v.setTextSize(sp);v.setTextColor(Color.rgb(238,231,217));return v;}
    private void add(View view){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.bottomMargin=dp(14);column.addView(view,p);}
    private void material(View view,String family){MaterialDrawable d=new MaterialDrawable(this,family);materials.add(d);view.setBackground(d);Rect p=new Rect();d.getPadding(p);view.setPadding(p.left,p.top,p.right,p.bottom);}
    private Button action(String title,View.OnClickListener callback){Button b=new Button(this);b.setAllCaps(false);b.setText(title);b.setTextSize(14);b.setStateListAnimator(null);b.setElevation(0);material(b,"button");b.setTextColor(Color.rgb(238,231,217));b.setOnClickListener(callback);add(b);return b;}
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        if(state!=null){narrow=state.getBoolean("narrow");rtl=state.getBoolean("rtl");cold=state.getBoolean("cold");disabled=state.getBoolean("disabled");selected=state.getBoolean("selected",true);scaleIndex=state.getInt("scale",0);}
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(Color.rgb(9,14,20));
        column=new LinearLayout(this);column.setOrientation(LinearLayout.VERTICAL);column.setPadding(dp(16),dp(16),dp(16),dp(16));scroll.addView(column);
        scroll.setOnApplyWindowInsetsListener((v,insets)->{column.setPadding(dp(16)+insets.getSystemWindowInsetLeft(),dp(16)+insets.getSystemWindowInsetTop(),dp(16)+insets.getSystemWindowInsetRight(),dp(16)+insets.getSystemWindowInsetBottom());return insets;});
        setContentView(scroll);
        add(label("CRAFTAGEDDON / MATERIAL LAB",23));
        int display=getWindowManager().getDefaultDisplay().getDisplayId();
        add(label("Standalone preview 0.1.0 · display "+display+"\nNo device controls or SystemUI changes. Lighting is static for reduced motion.",14));
        action("Cycle specimen width: full / 240dp",v->{narrow=!narrow;apply();});
        action("Cycle specimen text: 100 / 130 / 160 / 200%",v->{scaleIndex=(scaleIndex+1)%scales.length;apply();});
        action("Toggle LTR / RTL and Arabic specimen",v->{rtl=!rtl;apply();});
        action("Toggle cold inspection",v->{cold=!cold;apply();});
        action("Toggle target enabled / disabled",v->{disabled=!disabled;apply();});
        target=new Button(this);target.setAllCaps(false);target.setMinHeight(dp(64));target.setTextColor(new ColorStateList(new int[][]{new int[]{-android.R.attr.state_enabled},new int[]{}},new int[]{Color.rgb(139,146,153),Color.rgb(238,231,217)}));
        target.setStateListAnimator(null);target.setElevation(0);material(target,"button");add(target);
        target.setOnClickListener(v->{selected=!selected;apply();target.announceForAccessibility(selected?"Preview selected":"Preview deselected");});
        target.setOnFocusChangeListener((v,focus)->updateStatus());
        field=new EditText(this);field.setId(0x1060101);field.setHint("Search games or profiles — live text");field.setTextColor(Color.rgb(238,231,217));field.setHintTextColor(Color.rgb(181,189,198));field.setMinHeight(dp(64));field.setMaxLines(4);material(field,"field");add(field);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);material(panel,"panel");panel.addView(label("STEEL PANEL / live content",16));
        panelBody=label("Use D-pad to move focus. Generic Android BUTTON_A activates the focused control. BUTTON_B exits this app. Input stays inside this foreground window; no global gamepad capture.",16);panel.addView(panelBody);add(panel);
        notification=label("Notification frame\nLive text wraps independently from fixed steel corners. This is a specimen, not an Android notification replacement.",16);material(notification,"notification");add(notification);
        status=label("",14);add(status);
        add(label("All illumination is applied to neutral masks at draw time. No ROM, fan, charging, display-routing or calibration backend is present.",14));
        apply();
    }
    private void apply(){
        column.setLayoutDirection(rtl?View.LAYOUT_DIRECTION_RTL:View.LAYOUT_DIRECTION_LTR);
        target.setText(rtl?"ملف تعريف اللعبة المحدد — معاينة فقط":"Selected game profile — preview only");
        target.setTextSize(16*scales[scaleIndex]);field.setTextSize(16*scales[scaleIndex]);panelBody.setTextSize(16*scales[scaleIndex]);notification.setTextSize(16*scales[scaleIndex]);
        ViewGroup.LayoutParams p=target.getLayoutParams();p.width=narrow?dp(240):ViewGroup.LayoutParams.MATCH_PARENT;target.setLayoutParams(p);
        target.setEnabled(!disabled);target.setSelected(selected);
        for(MaterialDrawable m:materials)m.setColdInspection(cold);
        updateStatus();
    }
    private void updateStatus(){if(status!=null)status.setText("Specimen scale "+Math.round(scales[scaleIndex]*100)+"% · "+(narrow?"240dp":"full width")+" · "+(rtl?"RTL":"LTR")+"\nSelected: "+selected+" · focused: "+target.hasFocus()+" · enabled: "+!disabled+" · cold inspection: "+cold);}
    @Override public boolean dispatchKeyEvent(KeyEvent event){
        if(event.getKeyCode()==KeyEvent.KEYCODE_BUTTON_B){if(event.getAction()==KeyEvent.ACTION_UP)finish();return true;}
        if(event.getKeyCode()==KeyEvent.KEYCODE_BUTTON_A){KeyEvent mapped=new KeyEvent(event.getDownTime(),event.getEventTime(),event.getAction(),KeyEvent.KEYCODE_DPAD_CENTER,event.getRepeatCount(),event.getMetaState(),event.getDeviceId(),event.getScanCode(),event.getFlags(),event.getSource());return super.dispatchKeyEvent(mapped);}
        return super.dispatchKeyEvent(event);
    }
    @Override protected void onSaveInstanceState(Bundle state){super.onSaveInstanceState(state);state.putBoolean("narrow",narrow);state.putBoolean("rtl",rtl);state.putBoolean("cold",cold);state.putBoolean("disabled",disabled);state.putBoolean("selected",selected);state.putInt("scale",scaleIndex);}
}
