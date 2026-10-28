/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
import android.content.Context;
import android.text.Layout;
import android.util.AttributeSet;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.Space;
import android.widget.TextView;
import java.util.ArrayList;
/** Retains the source LinearLayout type/IDs/inset spacers while native text drives wrapping. */
public final class ForgeActionLayout extends LinearLayout {
 private final ArrayList<View> content=new ArrayList<>();
 private ForgeRowPlan.Plan plan;private int startSpace,endSpace,available,gap;
 public ForgeActionLayout(Context c,AttributeSet a){super(c,a);gap=Math.round(4*c.getResources().getDisplayMetrics().density);}
 @Override protected void onMeasure(int widthSpec,int heightSpec){
  int width=MeasureSpec.getSize(widthSpec);
  if(MeasureSpec.getMode(widthSpec)==MeasureSpec.UNSPECIFIED){
   width=getWidth()>0?getWidth():getRootView().getWidth();
   if(width<=0)width=getResources().getDisplayMetrics().widthPixels;
  }
  content.clear();startSpace=endSpace=0;
  for(int i=0;i<getChildCount();i++){
   View v=getChildAt(i);if(v.getVisibility()==GONE)continue;
   if(v instanceof Space){int w=Math.max(0,v.getLayoutParams().width);if(i==0)startSpace=w;else if(i==getChildCount()-1)endSpace=w;continue;}
   content.add(v);
  }
  available=Math.max(1,width-getPaddingLeft()-getPaddingRight()-startSpace-endSpace);
  int[] widths=new int[content.size()],heights=new int[content.size()];
  for(int i=0;i<content.size();i++){
   View v=content.get(i);MarginLayoutParams p=(MarginLayoutParams)v.getLayoutParams();
   int desired=v.getMinimumWidth(),cap=Math.max(1,available-p.leftMargin-p.rightMargin);
   if(v instanceof TextView){
    TextView t=(TextView)v;CharSequence text=t.getText();
    if(t.getTransformationMethod()!=null)text=t.getTransformationMethod().getTransformation(text,t);
    if(text!=null)desired=Math.max(desired,(int)Math.ceil(Layout.getDesiredWidth(text,t.getPaint()))+t.getCompoundPaddingLeft()+t.getCompoundPaddingRight());
    cap=Math.min(cap,t.getMaxWidth());
   }
   int w=Math.max(1,Math.min(cap,desired));
   v.measure(MeasureSpec.makeMeasureSpec(w,MeasureSpec.EXACTLY),MeasureSpec.makeMeasureSpec(0,MeasureSpec.UNSPECIFIED));
   widths[i]=v.getMeasuredWidth()+p.leftMargin+p.rightMargin;
   heights[i]=v.getMeasuredHeight()+p.topMargin+p.bottomMargin;
  }
  plan=ForgeRowPlan.pack(available,gap,widths,heights,(getGravity()&Gravity.HORIZONTAL_GRAVITY_MASK)==Gravity.CENTER_HORIZONTAL);
  setMeasuredDimension(resolveSize(width,widthSpec),resolveSize(plan.height+getPaddingTop()+getPaddingBottom(),heightSpec));
 }
 @Override protected void onLayout(boolean changed,int l,int t,int r,int b){
  if(plan==null)return;boolean rtl=getLayoutDirection()==LAYOUT_DIRECTION_RTL;
  for(int i=0;i<content.size();i++){
   View v=content.get(i);MarginLayoutParams p=(MarginLayoutParams)v.getLayoutParams();
   int total=v.getMeasuredWidth()+p.leftMargin+p.rightMargin;
   int left=getPaddingLeft()+startSpace+(rtl?available-plan.x[i]-total:plan.x[i])+p.leftMargin;
   int top=getPaddingTop()+plan.y[i]+p.topMargin;
   v.layout(left,top,left+v.getMeasuredWidth(),top+v.getMeasuredHeight());
  }
  for(int i=0;i<getChildCount();i++)if(getChildAt(i) instanceof Space){
   View v=getChildAt(i);int w=Math.max(0,v.getLayoutParams().width);
   int x=i==0?getPaddingLeft():getWidth()-getPaddingRight()-w;v.layout(x,getPaddingTop(),x+w,getHeight()-getPaddingBottom());
  }
 }
}
