// Design reference for a native owner. Not an Android input or hardware service.
'use strict';
function sample(flags={},ms=0,tokens={states:{idle:.14,selected:.36},previewEmissionGain:2.8}) {
  const reduced=!!flags.reducedMotion, visible=flags.visible!==false;
  const base={state:'idle',opacity:tokens.states.idle,focus:false,selection:false,scale:1,blur:0,animate:false,visible};
  if(flags.enabled===false)return {...base,state:'disabled',opacity:0,baseOpacity:.42};
  if(flags.cold)return {...base,state:'cold',opacity:0,baseOpacity:1};
  base.focus=!!flags.focused;base.selection=!!flags.selected;base.baseOpacity=1;
  if(flags.selected||flags.focused){base.state=flags.focused?'focused':'selected';base.opacity=tokens.states.selected;}
  // A press is a bounded event, never an animation that loops while a key is held.
  if(flags.pressed&&ms>=0&&ms<160&&!reduced&&visible){
    const envelope=1-ms/160;base.state='pressed';base.opacity+=(.7-base.opacity)*envelope;base.scale=1-.015*envelope;base.animate=true;
  }
  if(flags.warning){base.state='warning';base.opacity=ms<360&&!reduced&&visible?.55:.36;base.animate=ms<360&&!reduced&&visible;}
  base.blur=reduced||!visible?0:.9;
  base.displayOpacity=Math.min(1,base.opacity*(tokens.previewEmissionGain||1));
  return base;
}
module.exports={sample};
