/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.glimpse.forge;
/** Pure wrapping geometry; inputs are measured native children, never guessed text metrics. */
public final class ForgeRowPlan {
 public static final class Plan {
  public final int[] x,y;public final int height;
  private Plan(int[] x,int[] y,int h){this.x=x;this.y=y;height=h;}
 }
 public static Plan pack(int available,int gap,int[] widths,int[] heights,boolean center){
  if(available<=0||gap<0||widths.length!=heights.length)throw new IllegalArgumentException("Invalid row geometry");
  int[] x=new int[widths.length],y=new int[widths.length];int at=0,top=0;
  while(at<widths.length){
   int end=at,used=0,rh=0;
   while(end<widths.length){
    if(widths[end]<0||heights[end]<0||widths[end]>available)throw new IllegalArgumentException("Unconstrained native child");
    int next=used+(end==at?0:gap)+widths[end];
    if(end>at&&next>available)break;
    used=next;rh=Math.max(rh,heights[end]);end++;
   }
   int left=center?(available-used)/2:0;
   for(int i=at;i<end;i++){x[i]=left;y[i]=top;left+=widths[i]+gap;}
   top+=rh+(end<widths.length?gap:0);at=end;
  }
  return new Plan(x,y,top);
 }
}
