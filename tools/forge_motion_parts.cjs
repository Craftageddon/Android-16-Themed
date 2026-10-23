/* Native-shaped SVG part mutations; no cold-image hue/brightness filters. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ForgeMotionParts=factory()})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function mutations(layer,frame){
 const rows=[];
 for(const p of layer.motionParts||[]){
  const f=frame.fill;if(!Number.isFinite(f)||f<0||f>1)throw Error('Invalid fill fraction');
  let attrs;
  if(p.mode==='fill-y')attrs={x:p.x,y:p.bottom-p.height*f,width:p.width,height:p.height*f};
  else if(p.mode==='fill-x')attrs={x:p.x,y:p.y,width:p.width*f,height:p.height};
  else if(p.mode==='move-x')attrs={transform:'translate('+(p.range*f)+' 0)'};
  else if(p.mode==='move-y')attrs={transform:'translate(0 '+(p.range*f)+')'};
  else if(p.mode==='travel-x'){const q=frame.phase*frame.phase*(3-2*frame.phase);attrs={transform:'translate('+(p.from+(p.to-p.from)*q)+' 0)'}}
  else if(p.mode==='opacity'||p.mode==='emission'){const q=frame.phase*frame.phase*(3-2*frame.phase);attrs={opacity:p.from===undefined?p.value:p.from+(p.to-p.from)*q}}
  else if(p.mode==='fixed-rotate')attrs={transform:'rotate('+p.angle+' '+p.cx+' '+p.cy+')'};

  else if(p.mode==='stroke-arc')attrs={'stroke-dasharray':p.length,'stroke-dashoffset':p.length*(1-frame.stroke)};
  else if(p.mode==='needle')attrs={transform:'rotate('+(p.minAngle+(p.maxAngle-p.minAngle)*f)+' '+p.cx+' '+p.cy+')'};
  else if(p.mode==='sweep-x')attrs={x:frame.animating?-p.band+(p.size+p.band)*frame.stroke:0,width:frame.animating?p.band:p.size};
  else if(p.mode==='sweep-y')attrs={y:frame.animating?-p.band+(p.size+p.band)*frame.stroke:0,height:frame.animating?p.band:p.size};
  else if(p.mode==='step-emission')attrs={opacity:p.index<=Math.floor(f*(p.count-1)+1e-8)?1:0};

  else throw Error('Unknown part mode: '+p.mode);
  for(const value of Object.values(attrs))if(typeof value==='number'&&!Number.isFinite(value))throw Error('Invalid part dimension');
  rows.push({part:p.part,attrs,...((p.mode==='emission'||p.mode==='step-emission')?{layers:['reflection','spill','seam','core','symbol']}:{})});
 }
 return rows;
}
function labels(layer,frame){
 const f=Math.min(1,Math.max(0,frame.fill));
 return (layer.liveLabels||[]).map(label=>{
  let text=label.text;
  if(label.format==='percent')text=Math.round(f*100)+'%';
  else if(label.format==='gain'){const n=Math.round(f*20-10);text=(n>0?'+':'')+n+' dB'}
  else if(label.format==='temperature')text=Math.round(f*100)+' C';
  else if(label.format==='selectionCount')text=(frame.gains.symbol>0?label.count:0)+' selected';
  else if(label.format==='angle')text=Math.round(frame.angle)+' deg';
  else if(label.format==='milestone')text='Step '+(Math.floor(f*(label.total-1)+1e-8)+1)+' of '+label.total;
  return {...label,text,opacity:label.showAtCommit?(frame.phase>=1?1:0):(label.opacity??1)};
 });
}

return {mutations,labels};
});
