/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.res.Resources;
import android.content.res.TypedArray;
import org.lineageos.glimpse.R;
import android.content.res.ColorStateList;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.PixelFormat;
import android.graphics.PorterDuff;
import android.graphics.Rect;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import java.io.IOException;
/** Native XML-loadable separate layers. Whole-icon tint never recolors cold steel. */
public final class ForgeDrawable extends Drawable {
 private static final String NS="http://schemas.android.com/apk/res/android";
 private static final int[] COLORS={0xffdc5920,0xffff4908,0xffff5b0b,0xffffd083,0xffd5e7f2,0xffffe5bc};
 private final Drawable[] layers=new Drawable[7];
 private Resources resources;private String family;private boolean momentary=true,mirrored,feature;
 private int mode,alpha=255,width=-1,height=-1;
 private ForgeStatePolicy policy=ForgeStatePolicy.resolve(0,true,false,false,false,false,false,false,false,true);
 /** Required by the pinned framework DrawableInflater public no-arg constructor contract. */
 public ForgeDrawable(){}
 public ForgeDrawable(Resources r,Resources.Theme theme,String family){
     init(r,theme,family,0,true,false);
 }
 private ForgeDrawable(Resources r,Resources.Theme theme,String f,int m,boolean press,boolean mirror){
     init(r,theme,f,m,press,mirror);
 }
 private void init(Resources r,Resources.Theme theme,String f,int m,boolean press,boolean mirror){
  resources=r;family=f;mode=m;momentary=press;mirrored=mirror;
  int[] ids=ForgeResources.layers(f);
  for(int i=0;i<7;i++){
   layers[i]=r.getDrawable(ids[i],theme).mutate();
   if(i>0)layers[i].setColorFilter(COLORS[i-1],PorterDuff.Mode.SRC_IN);
  }
  width=layers[0].getIntrinsicWidth();height=layers[0].getIntrinsicHeight();
  setState(new int[]{android.R.attr.state_enabled});onStateChange(getState());
 }
 @Override public void inflate(Resources r,XmlPullParser parser,AttributeSet attrs,Resources.Theme theme)
       throws XmlPullParserException,IOException{
  super.inflate(r,parser,attrs,theme);
  TypedArray a=theme==null?r.obtainAttributes(attrs,R.styleable.ForgeDrawable):
      theme.obtainStyledAttributes(attrs,R.styleable.ForgeDrawable,0,0);
  String f;int m;boolean press;
  try{f=a.getString(R.styleable.ForgeDrawable_cg_forge_family);
      m=a.getInt(R.styleable.ForgeDrawable_cg_forge_source_value_mode,0);
      press=a.getBoolean(R.styleable.ForgeDrawable_cg_forge_momentary,true);
  }finally{a.recycle();}
  if(f==null)throw new XmlPullParserException("A Forge family is required");
  if(m<0||m>2)throw new XmlPullParserException("Invalid Forge source-value mode");
  init(r,theme,f,m,press,attrs.getAttributeBooleanValue(NS,"autoMirrored",false));
 }
 public void setFeatureActive(boolean value){
  if(feature!=value){feature=value;onStateChange(getState());}
 }
 private static boolean has(int[] s,int a){for(int v:s)if(v==a)return true;return false;}
 @Override protected boolean onStateChange(int[] s){
  policy=ForgeStatePolicy.resolve(mode,has(s,android.R.attr.state_enabled),
      has(s,android.R.attr.state_checked),has(s,android.R.attr.state_selected),
      has(s,android.R.attr.state_activated),has(s,android.R.attr.state_focused),
      has(s,android.R.attr.state_hovered),has(s,android.R.attr.state_pressed),feature,momentary);
  invalidateSelf();return true;
 }
 @Override public boolean isStateful(){return true;}
 @Override protected void onBoundsChange(Rect b){if(layers[0]!=null)for(Drawable d:layers)d.setBounds(b);}
 @Override public void draw(Canvas canvas){
  if(layers[0]==null)return;
  int saved=canvas.save();
  if(mirrored&&getLayoutDirection()==1)canvas.scale(-1f,1f,getBounds().exactCenterX(),getBounds().exactCenterY());
  layers[0].setAlpha(Math.round(alpha*policy.base));layers[0].draw(canvas);
  for(int i=1;i<7;i++)if(policy.gains[i-1]>0){
   layers[i].setAlpha(Math.round(alpha*policy.gains[i-1]));layers[i].draw(canvas);
  }
  canvas.restoreToCount(saved);
 }
 @Override public boolean getPadding(Rect p){if(layers[0]==null){p.set(0,0,0,0);return false;}return layers[0].getPadding(p);}
 @Override public int getIntrinsicWidth(){return width;}
 @Override public int getIntrinsicHeight(){return height;}
 @Override public void setAlpha(int a){alpha=Math.max(0,Math.min(255,a));invalidateSelf();}
 @Override public int getAlpha(){return alpha;}
 @Override public void setColorFilter(ColorFilter ignored){}
 @Override public void setTint(int ignored){}
 @Override public void setTintList(ColorStateList ignored){}
 @Override public void setTintMode(PorterDuff.Mode ignored){}
 @Override public int getOpacity(){return PixelFormat.TRANSLUCENT;}
 @Override public void setAutoMirrored(boolean value){mirrored=value;invalidateSelf();}
 @Override public boolean isAutoMirrored(){return mirrored;}
 @Override public boolean onLayoutDirectionChanged(int direction){invalidateSelf();return mirrored;}
 /** Every clone gets independent layer objects and cold initial state. Never cache a mutable instance. */
 @Override public ConstantState getConstantState(){
  if(resources==null)return null;
  final Resources original=resources;final String f=family;final int m=mode;
  final boolean press=momentary,mirror=mirrored;final int changing=getChangingConfigurations();
  return new ConstantState(){
   @Override public Drawable newDrawable(){return new ForgeDrawable(original,null,f,m,press,mirror);}
   @Override public Drawable newDrawable(Resources r){return new ForgeDrawable(r==null?original:r,null,f,m,press,mirror);}
   @Override public Drawable newDrawable(Resources r,Resources.Theme t){return new ForgeDrawable(r==null?original:r,t,f,m,press,mirror);}
   @Override public int getChangingConfigurations(){return changing;}
  };
 }
}
