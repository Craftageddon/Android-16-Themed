package com.craftageddon.thor.integration;
import android.app.Activity;
import android.content.*;
import android.content.res.Configuration;
import android.hardware.display.DisplayManager;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.util.Locale;
/** Native English controls and read-only target discovery. No hardware setters or permissions. */
public final class MainActivity extends Activity {
    private LinearLayout column;private TextView battery,details,input;private ToggleButton selected;private boolean listening;
    private static final int TEXT=0xffeee7d9,SECONDARY=0xffb5bdc6;
    private final BroadcastReceiver receiver=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent i){showBattery(i);}};
    @Override protected void attachBaseContext(Context base){
        Configuration config=new Configuration(base.getResources().getConfiguration());
        config.setLocales(LocaleList.forLanguageTags("en-US"));config.setLayoutDirection(Locale.US);
        super.attachBaseContext(base.createConfigurationContext(config));
    }
    private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
    private TextView text(int resource,int size){
        TextView v=new TextView(this);v.setText(resource);v.setTextColor(TEXT);v.setTextSize(size);
        v.setPadding(0,dp(10),0,dp(10));return v;
    }
    private void add(View view){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.bottomMargin=dp(14);column.addView(view,p);}
    private void steel(TextView view,String family,boolean locked){
        view.setBackground(new ForgeDrawable(this,family,locked));view.setBackgroundTintList(null);
        view.setTextColor(TEXT);view.setTextSize(18);view.setPadding(dp(28),dp(18),dp(28),dp(18));
        view.setMinHeight(dp(64));view.setMaxLines(3);view.setAllCaps(false);
    }
    private ToggleButton toggle(int label,boolean checked,boolean locked){
        ToggleButton v=new ToggleButton(this);String s=getString(label);v.setTextOff(s);v.setTextOn(s);
        steel(v,"button",locked);v.setChecked(checked);return v;
    }
    @Override public void onCreate(Bundle state){
        super.onCreate(state);getWindow().getDecorView().setBackgroundColor(0xff080c11);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        scroll.setOnApplyWindowInsetsListener((v,insets)->{android.graphics.Insets bars=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());v.setPadding(bars.left,bars.top,bars.right,bars.bottom);return insets;});
        column=new LinearLayout(this);column.setOrientation(LinearLayout.VERTICAL);column.setPadding(dp(24),dp(20),dp(24),dp(24));scroll.addView(column);
        add(text(R.string.app_name,26));add(text(R.string.intro,16));
        selected=toggle(R.string.selected_control,SelectionStore.get(this),false);
        selected.setOnCheckedChangeListener((button,on)->{SelectionStore.set(this,on);button.setStateDescription(getString(on?R.string.state_on:R.string.state_off));});
        selected.setStateDescription(getString(selected.isChecked()?R.string.state_on:R.string.state_off));add(selected);
        ToggleButton locked=toggle(R.string.explicit_off_control,false,true);locked.setOnCheckedChangeListener((button,on)->button.setStateDescription(getString(R.string.emission_locked)));add(locked);
        locked.setStateDescription(getString(R.string.emission_locked));
        ToggleButton unavailable=toggle(R.string.unavailable_control,false,false);unavailable.setEnabled(false);add(unavailable);
        add(text(R.string.qs_help,16));
        battery=text(R.string.battery_unknown,18);steel(battery,"field",false);add(battery);
        input=text(R.string.input_waiting,16);input.setTextColor(SECONDARY);add(input);
        details=text(R.string.details_pending,16);details.setTextColor(SECONDARY);add(details);
        Button refresh=new Button(this);refresh.setText(R.string.refresh_details);steel(refresh,"button",false);refresh.setOnClickListener(v->refreshDetails());add(refresh);
        add(text(R.string.device_limit,14));setContentView(scroll);scroll.requestApplyInsets();refreshDetails();
    }
    private void showBattery(Intent intent){
        if(intent==null){battery.setText(R.string.battery_unknown);return;}
        int level=intent.getIntExtra(BatteryManager.EXTRA_LEVEL,-1),scale=intent.getIntExtra(BatteryManager.EXTRA_SCALE,-1);
        if(level<0||scale<=0){battery.setText(R.string.battery_unknown);return;}
        int percent=Math.max(0,Math.min(100,Math.round(level*100f/scale)));int status=intent.getIntExtra(BatteryManager.EXTRA_STATUS,-1);
        boolean charging=status==BatteryManager.BATTERY_STATUS_CHARGING||status==BatteryManager.BATTERY_STATUS_FULL;
        battery.setText(String.format(Locale.US,getString(R.string.battery_value),percent,getString(charging?R.string.charging:R.string.not_charging)));
        battery.setSelected(charging);
    }
    private void refreshDetails(){
        StringBuilder s=new StringBuilder(getString(R.string.display_heading)).append('\n');
        DisplayManager manager=getSystemService(DisplayManager.class);
        if(manager!=null)for(Display display:manager.getDisplays()){
            Display.Mode mode=display.getMode();
            s.append(String.format(Locale.US,getString(R.string.display_value),display.getDisplayId(),mode.getPhysicalWidth(),mode.getPhysicalHeight(),mode.getRefreshRate())).append('\n');
        }
        int count=0;for(int id:InputDevice.getDeviceIds()){InputDevice d=InputDevice.getDevice(id);if(d!=null&&!d.isVirtual()&&(d.supportsSource(InputDevice.SOURCE_GAMEPAD)||d.supportsSource(InputDevice.SOURCE_JOYSTICK)))count++;}
        s.append(String.format(Locale.US,getString(R.string.input_value),count));details.setText(s);
    }
    @Override public boolean dispatchKeyEvent(KeyEvent event){
        if(input!=null&&(event.isFromSource(InputDevice.SOURCE_GAMEPAD)||event.isFromSource(InputDevice.SOURCE_DPAD))){
            input.setText(String.format(Locale.US,getString(R.string.input_key),event.getKeyCode(),getString(event.getAction()==KeyEvent.ACTION_UP?R.string.released:R.string.pressed)));
        }
        return super.dispatchKeyEvent(event);
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event){
        if(input!=null&&event.isFromSource(InputDevice.SOURCE_JOYSTICK)){
            input.setText(String.format(Locale.US,getString(R.string.input_axes),event.getAxisValue(MotionEvent.AXIS_X),event.getAxisValue(MotionEvent.AXIS_Y),event.getAxisValue(MotionEvent.AXIS_LTRIGGER),event.getAxisValue(MotionEvent.AXIS_RTRIGGER)));
        }
        return super.onGenericMotionEvent(event);
    }
    @Override protected void onStart(){
        super.onStart();selected.setChecked(SelectionStore.get(this));
        registerReceiver(receiver,new IntentFilter(Intent.ACTION_BATTERY_CHANGED),Context.RECEIVER_NOT_EXPORTED);listening=true;refreshDetails();
    }
    @Override protected void onStop(){
        if(listening){unregisterReceiver(receiver);listening=false;}super.onStop();
    }
}
