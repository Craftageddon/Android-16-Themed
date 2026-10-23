/* One animation owner for a visible review stage. No autonomous idle loop.
 * Timers, lifecycle and drawing are injected for actual stop/cancel testing.
 */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory(require('./forge_motion_v3.cjs'));else root.ForgeMotionClock=factory(root.ForgeMotion)})(typeof globalThis!=='undefined'?globalThis:this,function(motion){
'use strict';
class Clock{
 constructor({raf,cancel,now,draw}){this.raf=raf;this.cancel=cancel;this.now=now;this.draw=draw;this.handle=null;this.recipe=null;this.flags={};this.start=0;this.running=false;this.disposed=false;}
 set(recipe,flags={}){this.cancelPending();this.recipe=recipe;this.flags={...flags};this.render(0,false);}
 render(elapsed,playing){if(!this.recipe||this.disposed)return null;const frame=motion.frame(this.recipe,elapsed,{...this.flags,playing});this.draw(frame);return frame;}
 replay(){if(this.disposed||!this.recipe)return;this.cancelPending();this.start=this.now();this.running=true;this.tick(this.start);}
 tick(now){
  this.handle=null;if(this.disposed||!this.running)return;
  const elapsed=Math.max(0,now-this.start),frame=this.render(elapsed,true);
  // Review loops show two cycles; the retained native recipe remains explicit.
  const cap=this.recipe.repeat?.mode==='loop'?this.recipe.durationMillis*2*(Number.isFinite(this.flags.animatorScale)?Math.min(4,Math.max(.1,this.flags.animatorScale)):1):Infinity;
  if(frame.running&&elapsed<cap){this.handle=this.raf(t=>this.tick(t));}else{this.running=false;if(elapsed>=cap)this.render(elapsed,false);}
 }
 update(flags){this.flags={...this.flags,...flags};this.stop();}
 seek(fraction){this.cancelPending();this.running=false;if(this.recipe)this.render(Math.max(0,Math.min(1,fraction))*this.recipe.durationMillis,true);}
 cancelPending(){if(this.handle!==null){this.cancel(this.handle);this.handle=null;}this.running=false;}
 stop(){this.cancelPending();this.render(0,false);}
 dispose(){this.cancelPending();this.disposed=true;this.recipe=null;}
}
return {Clock};
});
