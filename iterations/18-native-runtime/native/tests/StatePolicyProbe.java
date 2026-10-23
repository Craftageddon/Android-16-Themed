package com.craftageddon.thor.integration;
public final class StatePolicyProbe {
 public static void main(String[] args){
  for(int mask=0;mask<64;mask++){
   StatePolicy s=StatePolicy.resolve((mask&1)!=0,(mask&2)!=0,(mask&4)!=0,(mask&8)!=0,(mask&16)!=0,(mask&32)!=0);
   StringBuilder line=new StringBuilder().append(mask).append(",").append(s.base);for(float gain:s.gains)line.append(",").append(gain);System.out.println(line);
  }
 }
}
