// Export exact sampler values for bounded desktop SVG frame review.
const fs=require('node:fs'),path=require('node:path'),motion=require('./forge_motion_v3.cjs'),parts=require('./forge_motion_parts.cjs');
const root=path.resolve(process.argv[2]),catalog=JSON.parse(fs.readFileSync(path.join(root,'source/retained-catalog.json'),'utf8')),bindings=JSON.parse(fs.readFileSync(path.join(root,'reconciliation.json'),'utf8'));
const selected=catalog.recipes.map(r=>r.id);
const rows=[];
for(const id of selected){const recipe=catalog.recipes.find(r=>r.id===id),binding=bindings.find(r=>r.id===id);if(binding.pendingArtwork.length)throw Error('Missing artwork: '+id);const r={...recipe,...binding,layers:binding.newLayers};for(const phase of id==='cooling-fan-speed'?[0,.125,.375,.625,1]:[0,.25,.5,.75,1])for(const on of [false,true]){const frame=motion.frame(r,phase*r.durationMillis,{on,playing:true});frame.layers.forEach((t,i)=>{t.partMutations=parts.mutations(r.layers[i],t);t.liveLabels=parts.labels(r.layers[i],t)});rows.push({id,phase,on,frame})}}
fs.writeFileSync(path.join(root,'verification/evidence/desktop-frame-values.json'),JSON.stringify({method:'Actual JS sampler exported to desktop SVG review; not browser/native playback',frames:rows},null,2)+'\n');console.log(JSON.stringify({recipes:selected.length,frames:rows.length}));
