/* Offline motion review stage; authored UI is English. No native commands. */
'use strict';
const data=JSON.parse(document.querySelector('#motion-data').textContent),select=document.querySelector('#recipe'),stage=document.querySelector('#stage');
const ns='http://www.w3.org/2000/svg',layers=['cold','reflection','spill','seam','core','focus','symbol'];
const colors={reflection:'#dc5920',spill:'#ff4908',seam:'#ff5b0b',core:'#ffd083',focus:'#d5e7f2',symbol:'#ffe5bc'};
let current=null,nodes=[],inView=true,liveLabel=null;
const reducedQuery=window.matchMedia('(prefers-reduced-motion: reduce)');
function flags(){return {on:document.querySelector('#on').checked,focused:document.querySelector('#focus').checked,reducedMotion:document.querySelector('#reduced').checked||reducedQuery.matches,enabled:document.querySelector('#enabled').checked,visible:!document.hidden&&inView,attached:stage.isConnected,resumed:true}}
function prefixIds(svg,prefix){const map=new Map([...svg.querySelectorAll('[id]')].map(n=>[n.id,prefix+n.id]));for(const n of svg.querySelectorAll('*'))for(const attr of [...n.attributes]){let value=attr.value;if(attr.name==='id')value=map.get(value)||value;else for(const [old,id]of map){value=value.split('url(#'+old+')').join('url(#'+id+')');if((attr.name==='href'||attr.name==='xlink:href')&&value==='#'+old)value='#'+id}n.setAttribute(attr.name,value)}}
function instance(source,index){
 const a=data.assets[source],svg=document.importNode(new DOMParser().parseFromString(a.markup,'image/svg+xml').documentElement,true);prefixIds(svg,'instance-'+index+'-');
 const defs=document.createElementNS(ns,'defs');
 for(const key of layers.filter(k=>k!=='cold')){const f=document.createElementNS(ns,'filter');f.id='tint-'+index+'-'+key;f.setAttribute('color-interpolation-filters','sRGB');f.setAttribute('x','-100%');f.setAttribute('y','-100%');f.setAttribute('width','300%');f.setAttribute('height','300%');const flood=document.createElementNS(ns,'feFlood');flood.setAttribute('flood-color',colors[key]);const composite=document.createElementNS(ns,'feComposite');composite.setAttribute('in2','SourceGraphic');composite.setAttribute('operator','in');f.append(flood,composite);defs.append(f)}
 const clip=document.createElementNS(ns,'clipPath');clip.id='reveal-'+index;clip.setAttribute('clipPathUnits','userSpaceOnUse');const rect=document.createElementNS(ns,'rect');rect.setAttribute('width',a.width);rect.setAttribute('height',a.height);clip.append(rect);defs.append(clip);svg.prepend(defs);
 svg.setAttribute('x',-a.width/2);svg.setAttribute('y',-a.height/2);svg.setAttribute('width',a.width);svg.setAttribute('height',a.height);svg.setAttribute('overflow','visible');
 const body=document.createElementNS(ns,'g');for(const n of [...svg.children])if(n.tagName.toLowerCase()!=='defs')body.append(n);body.setAttribute('clip-path','url(#reveal-'+index+')');svg.append(body);
 const owner=document.createElementNS(ns,'g');owner.append(svg);stage.append(owner);
 const maskNodes=[...svg.querySelectorAll('[data-forge-layer]')];for(const n of maskNodes){n.removeAttribute('style');const key=n.getAttribute('data-forge-layer');if(key!=='cold')n.setAttribute('filter','url(#tint-'+index+'-'+key+')')}
 const labelClip=document.createElementNS(ns,'clipPath');labelClip.id='live-label-reveal-'+index;labelClip.setAttribute('clipPathUnits','userSpaceOnUse');const labelRect=document.createElementNS(ns,'rect');labelRect.setAttribute('x',-a.width/2);labelRect.setAttribute('y',-a.height/2);labelClip.append(labelRect);defs.append(labelClip);const labelOwner=document.createElementNS(ns,'g');owner.append(labelOwner);
 return {owner,rect,maskNodes,a,labelRect,labelOwner,liveNodes:[],parts:[...svg.querySelectorAll('[data-motion-part]')]};
}
function draw(frame){for(let i=0;i<nodes.length;i++){const n=nodes[i],t=frame.layers[i],placement=current.layers[i].legacyPlacement,limits=current.layers[i].displaySize||[340,260],s=Math.min(limits[0]/n.a.width,limits[1]/n.a.height)*placement.scale*t.scale;
 const rotorOnly=current.layers[i].transformTarget==='rotor';n.owner.setAttribute('transform',`translate(${360+placement.x*2+t.x} ${215+placement.y*2+t.y}) rotate(${rotorOnly?0:t.rotation} ${current.layers[i].pivot?(current.layers[i].pivot[0]-n.a.width/2)*s:0} ${current.layers[i].pivot?(current.layers[i].pivot[1]-n.a.height/2)*s:0}) scale(${s})`);for(const part of n.parts)if(part.getAttribute('data-motion-part')==='rotor')part.setAttribute('transform',`rotate(${t.rotation} ${n.a.width/2} ${n.a.height/2})`);n.owner.setAttribute('opacity',t.visible?t.opacity*t.baseOpacity:0);n.rect.setAttribute('width',n.a.width*t.revealX);n.rect.setAttribute('height',n.a.height*t.revealY);

 n.labelRect.setAttribute('width',n.a.width*t.revealX);n.labelRect.setAttribute('height',n.a.height*t.revealY);if(t.revealX<1||t.revealY<1)n.labelOwner.setAttribute('clip-path','url(#live-label-reveal-'+i+')');else n.labelOwner.removeAttribute('clip-path');
 const descriptor=current.layers[i];
 for(const op of ForgeMotionParts.mutations(descriptor,t)){
  const targets=n.parts.filter(part=>part.getAttribute('data-motion-part')===op.part);
  if(!targets.length)throw Error('Missing motion part: '+op.part);
  for(const part of targets){if(op.layers&&!op.layers.includes(part.closest('[data-forge-layer]')?.getAttribute('data-forge-layer')))continue;for(const [name,value] of Object.entries(op.attrs))part.setAttribute(name,String(value))}
 }
 const labelRows=ForgeMotionParts.labels(descriptor,t);

 for(let j=0;j<n.liveNodes.length;j++){
  const label=labelRows[j],text=n.liveNodes[j];
  text.textContent=label.text;
  text.setAttribute('x',label.x-n.a.width/2);
  text.setAttribute('y',label.y-n.a.height/2);
  text.setAttribute('font-size',Math.min(26,Math.max(14,(label.fontSize||20)*s))/s);
  text.setAttribute('opacity',label.opacity??1);
 }

 const allowed=current.layers[i].allowedLayers||layers;
 for(const mask of n.maskNodes){const key=mask.getAttribute('data-forge-layer');mask.setAttribute('opacity',allowed.includes(key)?key==='cold'?1:t.gains[key]:0)}
 }
 if(liveLabel){const i=current.labelLayer||0,t=frame.layers[i],p=current.layers[i].legacyPlacement;liveLabel.setAttribute('x',360+p.x*2+t.x);liveLabel.setAttribute('y',223+p.y*2+t.y);liveLabel.setAttribute('opacity',t.visible?t.opacity*t.baseOpacity:0)}
 document.querySelector('#live').textContent=current?.labelAnchor==='below'?(current.label||''):'';}
const clock=new ForgeMotionClock.Clock({raf:f=>requestAnimationFrame(f),cancel:id=>cancelAnimationFrame(id),now:()=>performance.now(),draw});
function show(id){clock.stop();current=data.recipes.find(r=>r.id===id);if(!current)throw Error('Unknown recipe');stage.replaceChildren();nodes=[];document.querySelector('#title').textContent=current.title;document.querySelector('#description').textContent=current.description;
 const pending=current.pendingArtwork.length>0;document.querySelector('#play').disabled=pending;document.querySelector('#status').textContent=pending?'Specific composite artwork is still pending. Playback is blocked.':'Draft playback is wired. Visual and device acceptance remain pending.';document.querySelector('#details').textContent=pending?current.pendingArtwork.join('\n'):current.durationMillis+' ms per cycle · '+current.kind+' · '+(current.repeat.mode==='loop'?'loop, capped to two review cycles':current.repeat.count+' cycle(s)');
 liveLabel=null;
 if(!pending){nodes=current.layers.map((l,i)=>instance(l.source,i));nodes.forEach((n,i)=>{for(const label of current.layers[i].liveLabels||[]){const text=document.createElementNS(ns,'text');text.setAttribute('text-anchor','middle');text.setAttribute('font-family','Segoe UI, sans-serif');text.setAttribute('fill','#eee7d9');n.labelOwner.append(text);n.liveNodes.push(text)}});if(current.label&&current.labelAnchor==='inside'){liveLabel=document.createElementNS(ns,'text');liveLabel.setAttribute('text-anchor','middle');liveLabel.setAttribute('font-family','Segoe UI, sans-serif');liveLabel.setAttribute('font-size','24');liveLabel.setAttribute('fill','#eee7d9');liveLabel.textContent=current.label;stage.append(liveLabel)}clock.set(current,flags())}else{clock.recipe=null;document.querySelector('#live').textContent=''}
}
select.replaceChildren(...data.recipes.map(r=>{const o=document.createElement('option');o.value=r.id;o.textContent=r.title+(r.pendingArtwork.length?' — artwork pending':'');return o}));
select.addEventListener('change',()=>show(select.value));document.querySelector('#play').addEventListener('click',()=>clock.replay());document.querySelector('#stop').addEventListener('click',()=>clock.stop());
for(const id of ['on','focus','reduced','enabled'])document.querySelector('#'+id).addEventListener('change',()=>{if(current&&!current.pendingArtwork.length)clock.update(flags())});
document.addEventListener('visibilitychange',()=>clock.update(flags()));window.addEventListener('pagehide',()=>clock.stop());reducedQuery.addEventListener('change',()=>clock.update(flags()));
const observer=new IntersectionObserver(entries=>{inView=entries[0]?.isIntersecting===true;clock.update(flags())});observer.observe(stage);window.addEventListener('unload',()=>{observer.disconnect();clock.dispose()});show(data.recipes[0].id);
