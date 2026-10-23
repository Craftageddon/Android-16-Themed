/* Reference Forge motion sampler. Pure evaluation; owns no clocks or services.
 * Geometry uses uniform scale/translation/rotation only. Lighting modulates
 * separate masks, never the brightness or hue of the cold material.
 */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ForgeMotion=factory()})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const clamp=(n,a=0,b=1)=>Math.min(b,Math.max(a,n));
const ease=p=>{p=clamp(p);return p*p*(3-2*p)};
const lerp=(a,b,p)=>a+(b-a)*p;
const wave=p=>Math.sin(clamp(p)*Math.PI);
const kinds=['Back','BackCancel','Breathe','Broadcast','Bubble','Calibrate','Capture','Chip','Collapse','Curve','Dock','Equalize','Expand','Fade','Fan','Fill','Flash','Focus','Forge','Haptic','Hinge','Hold','Launch','March','Mode','Panel','Pip','Press','Progress','Pulse','Reorder','Rise','Rotate','Scan','Shimmer','Slide','Slider','Spin','Split','Stack','Stick','Swap','Swipe','Tap','Thermal','Warn'];

function track(kind,p,index,count){
 const q=ease(p),w=wave(p),rank=count>1?index/(count-1):0;
 const r={x:0,y:0,scale:1,rotation:0,opacity:1,revealX:1,revealY:1,light:1,fill:1,stroke:1,angle:0};
 switch(kind){
 case 'Forge': {const a=ease(clamp((p-index*.12)/.76));r.scale=lerp(.55,1,a);r.rotation=lerp(-28,0,a);r.opacity=a;r.light=a;break}
 case 'Launch':r.scale=lerp(.72,1,q);r.y=lerp(12,0,q);r.opacity=q;break;
 case 'Collapse':r.scale=lerp(1,.08,q);r.opacity=1-q;r.light=1-q;break;
 case 'Pulse':r.scale=1+.025*w;r.light=.72+.28*w;break;
 case 'Breathe':r.light=.65+.35*(.5-.5*Math.cos(p*2*Math.PI));break;
 case 'Warn':r.x=Math.sin(p*4*Math.PI)*3*(1-p);r.light=.78+.22*w;break;
 case 'Spin':r.rotation=360*p;break;
 case 'Fan':r.rotation=360*p;break;
 case 'Slide':if(p<.18){r.y=lerp(-42,0,ease(p/.18));r.opacity=ease(p/.18)}else if(p>.72){r.x=180*ease((p-.72)/.28);r.opacity=1-ease((p-.72)/.28)}break;
 case 'Fade':r.opacity=p<.2?ease(p/.2):p>.8?1-ease((p-.8)/.2):1;r.y=lerp(12,0,clamp(p/.2));break;
 case 'Expand':r.revealX=lerp(.18,1,q);r.revealY=lerp(.25,1,q);r.opacity=q;break;
 case 'Stack':{const a=ease(clamp((p-index*.12)/.7));r.x=lerp(32,0,a);r.y=lerp(-10,0,a);r.opacity=a;break}
 case 'Reorder':r.x=Math.sin(p*Math.PI)*(index%2?48:-48);r.y=-12*w*(1-rank);break;
 case 'Swipe':r.x=lerp(-80,170,q);r.opacity=p<.15?ease(p/.15):p>.7?1-ease((p-.7)/.3):1;break;
 case 'Press':r.scale=1-.045*w;r.y=2*w;r.light=.85+.15*w;break;
 case 'Fill':r.fill=q;r.light=.8+.2*q;break;
 case 'Progress':r.fill=q;r.stroke=q;break;
 case 'Broadcast':r.scale=.94+.06*q;r.stroke=q;r.light=.6+.4*w;break;
 case 'Back':r.x=lerp(44,0,q)*(index%2?-1:1);r.scale=lerp(.92,1,q);r.opacity=lerp(.35,1,q);break;
 case 'BackCancel':r.x=42*Math.sin(p*Math.PI);r.scale=1-.05*w;break;
 case 'Pip':r.x=lerp(-48,56,q);r.y=lerp(-28,38,q);r.scale=lerp(1,.58,q);r.opacity=lerp(.3,1,q);break;
 case 'Split':r.x=(index%2?1:-1)*28*q;r.revealY=lerp(.2,1,q);break;
 case 'Rotate':r.rotation=lerp(-90,0,q);r.scale=lerp(.85,1,q);break;
 case 'Rise':r.y=lerp(62,0,q);r.opacity=q;break;
 case 'Tap':r.scale=lerp(.3,1.3,q);r.opacity=1-q;r.stroke=q;break;
 case 'Hold':r.stroke=q;r.light=.7+.3*q;break;
 case 'Scan':r.revealY=q;r.stroke=q;break;
 case 'Haptic':r.scale=1+.012*Math.sin(p*6*Math.PI)*(1-p);r.light=.85+.15*w;break;
 case 'Focus':r.opacity=count>1?(index===0?lerp(1,.6,q):lerp(.6,1,q)):1;r.light=count>1?(index===0?1-q:q):1;break;
 case 'Flash':r.light=1-.28*w;r.opacity=1;break; // restrained contrast, no white-screen flash
 case 'Swap':r.x=Math.sin(p*Math.PI)*(index%2?60:-60);r.y=lerp(0,index%2?-44:44,q);break;
 case 'Stick':r.x=Math.sin(p*2*Math.PI)*9;r.y=-Math.sin(p*4*Math.PI)*5;break;
 case 'Mode':r.light=index===Math.min(count-1,Math.floor(q*count))?1:0;r.scale=1+.02*w;break;
 case 'Thermal':r.fill=lerp(.2,1,q);r.stroke=q;break;
 case 'Dock':r.y=lerp(38,0,q)-4*w;r.opacity=lerp(.2,1,q);break;
 case 'Slider':if(index===1)r.x=lerp(-48,28,q);else r.fill=q;break;
 case 'Chip':r.revealX=q;r.x=lerp(-16,0,q);r.opacity=q;break;
 case 'March':r.fill=q;r.stroke=q;r.light=.7+.3*clamp(q*3-index);break;
 case 'Bubble':r.scale=lerp(.25,1,q);r.x=lerp(48,0,q);r.y=lerp(38,0,q);r.opacity=q;break;
 case 'Capture':r.y=lerp(45,0,q);r.scale=lerp(.8,1,q);r.opacity=q;r.light=.75+.25*w;break;
 case 'Shimmer':r.stroke=q;r.light=.7+.3*w;break;
 case 'Hinge':r.angle=lerp(35,165,q);r.rotation=(index%2?1:-1)*lerp(-18,0,q);break;
 case 'Panel':r.x=lerp(76,0,q);r.opacity=q;break;
 case 'Calibrate':r.fill=q;r.stroke=q;r.x=index===1?lerp(-22,22,q):0;break;
 case 'Curve':r.fill=q;r.y=-4*w;r.light=.8+.2*w;break;
 case 'Equalize':r.fill=clamp(q*(.55+rank*.45));r.stroke=q;break;
 default:throw Error('Unknown motion kind: '+kind);
 }
 return r;
}

function frame(recipe,elapsedMs,flags={}){
 if(!kinds.includes(recipe.kind))throw Error('Unknown motion kind');
 if(!(recipe.durationMillis>0)||!Number.isFinite(elapsedMs)||elapsedMs<0)throw Error('Invalid motion time');
 const visible=flags.visible!==false&&flags.attached!==false&&flags.resumed!==false;
 const enabled=flags.enabled!==false,active=enabled&&!flags.cold&&!flags.focusOnly&&!!(flags.on||flags.selected||flags.checked);
 const radiating=active&&!flags.emissionLockedOff&&!recipe.focusNeutralOnly&&visible;
 const reduce=!!flags.reducedMotion||flags.animatorScale===0||!!flags.powerSave;
 const repeat=recipe.repeat||{mode:'count',count:1},count=repeat.mode==='loop'?Infinity:Math.max(1,repeat.count||1);
 const playing=visible&&enabled&&!reduce&&flags.playing===true&&(repeat.mode!=='loop'||active)&&(recipe.kind!=='Fan'||active);
 const duration=recipe.durationMillis*clamp(Number.isFinite(flags.animatorScale)?flags.animatorScale:1,.1,4),total=duration*count,finished=elapsedMs>=total;
 const p=playing?(finished?1:(elapsedMs%duration)/duration):1;
 const steady={x:0,y:0,scale:1,rotation:0,opacity:1,revealX:1,revealY:1,light:1,fill:1,stroke:1,angle:165};
 const layers=(recipe.layers||recipe.legacyLayers||[{}]).map((layer,index,all)=>{
  const t=playing?track(recipe.kind,p,index,all.length):{...steady};
  // Compact status indicators remain steady; geometry is never an idle loop.
  if(recipe.steadyStatus||flags.focusOnly)Object.assign(t,steady);

  const q=ease(p);
  if(layer.semanticRole==='back-source'){
   Object.assign(t,{x:recipe.kind==='BackCancel'?70*wave(p):72*q,y:0,scale:recipe.kind==='BackCancel'?1-.08*wave(p):1-.12*q,opacity:recipe.kind==='BackCancel'?1:1-q,revealX:1,revealY:1,light:recipe.kind==='BackCancel'?1:1-q});
  }else if(layer.semanticRole==='back-target'){
   Object.assign(t,{x:0,y:0,scale:1,opacity:1,revealX:1,revealY:1,light:recipe.kind==='BackCancel'?0:q});
  }else if(layer.semanticRole==='reorder-tile'){
   const travel=ease((p-.2)/.6);
   Object.assign(t,{x:(layer.toSlot-layer.fromSlot)*layer.slotStep*travel,y:layer.dragged?(p<.2?-130*ease(p/.2):p>.8?-130*(1-ease((p-.8)/.2)):-130):0,scale:1,opacity:1,revealX:1,revealY:1});
  }else if(layer.semanticRole==='hinge-upper'){
   Object.assign(t,{x:0,y:0,scale:1,opacity:1,revealX:1,revealY:1,rotation:-(165-t.angle)/2});
  }else if(layer.semanticRole==='screen-drag-card'){
   Object.assign(t,{x:72*wave(p),y:200*q,scale:1,opacity:1,revealX:1,revealY:1});
  }
  if(!playing&&recipe.kind==='Mode')t.light=index===(recipe.selectedIndex??all.length-1)?1:0;

  if(layer.stationary)Object.assign(t,{x:0,y:0,scale:1,rotation:0,opacity:1,revealX:1,revealY:1});
  if(flags.focusOnly)Object.assign(t,steady);
  if(layer.targetFill!==undefined){
   if(!Number.isFinite(layer.targetFill))throw Error('Invalid target fill');
   const target=clamp(layer.targetFill),start=clamp(layer.startFill??target);
   t.fill=playing?lerp(start,target,ease(p)):target;
  }
  t.phase=p;t.animating=playing&&!finished&&!recipe.steadyStatus&&!flags.focusOnly;
  const light=radiating&&layer.selected!==false?t.light:0;
  let focusOwner=recipe.focusNeutralOnly?index===(p<.5?0:all.length-1):!!flags.focused&&layer.focusable!==false;
  if(layer.semanticRole==='back-source')focusOwner=!!flags.focused&&(recipe.kind==='BackCancel'||p<1);
  if(layer.semanticRole==='back-target')focusOwner=!!flags.focused&&recipe.kind!=='BackCancel'&&p>=1;
  if(recipe.kind==='Mode'&&flags.focused)focusOwner=index===(Number.isInteger(flags.focusedIndex)?flags.focusedIndex:playing?Math.min(all.length-1,Math.floor(q*all.length)):(recipe.selectedIndex??all.length-1));
  const selected=active&&layer.selected!==false&&t.light>0;
  return {...t,baseOpacity:enabled?1:.42,visible,gains:{reflection:.32*light,spill:.72*light,seam:light,core:.82*light,focus:enabled&&focusOwner?1:0,symbol:selected&&!recipe.focusNeutralOnly?1:0}};
 });
 return {progress:p,finished,running:playing&&!finished&&!recipe.steadyStatus&&!flags.focusOnly,visible,active,reducedMotion:reduce,layers};
}
return {kinds,track,frame};
});
