package com.craftageddon.thor.integration;
public final class StatePolicyTest {
 static void check(boolean x,String why){if(!x)throw new AssertionError(why);}
 public static void main(String[] args){
  int count=0;
  for(int mask=0;mask<64;mask++){
   boolean e=(mask&1)!=0,c=(mask&2)!=0,s=(mask&4)!=0,f=(mask&8)!=0,p=(mask&16)!=0,l=(mask&32)!=0;
   StatePolicy x=StatePolicy.resolve(e,c,s,f,p,l);boolean active=e&&!l&&(c||s);
   check(x.active==active,"activation "+mask);check(x.base==(e?1f:.42f),"disabled "+mask);
   for(int i=0;i<6;i++){check(x.gains[i]>=0&&x.gains[i]<=1,"bounds "+mask);if(i!=4&&!active)check(x.gains[i]==0,"cold invariant "+mask);}
   check(x.gains[4]==(e&&f?1:0),"neutral focus "+mask);
   if(active){check(x.gains[0]==(p?.60f:.32f),"reflection "+mask);check(x.gains[1]==(p?.92f:.72f),"spill "+mask);check(x.gains[3]==(p?1f:.82f),"core "+mask);}
   count++;
  }
  System.out.println("PASS: "+count+" exhaustive native state combinations");
 }
}
