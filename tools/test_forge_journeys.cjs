// Actual offline viewer code, with a deliberately small DOM fixture.
// This tests scene navigation and every declared action, not browser rendering.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]),html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const rows=JSON.parse(fs.readFileSync(path.join(root,'flow-definitions.json'),'utf8'));
function element(){return {value:'',children:[],listeners:{},addEventListener(t,f){this.listeners[t]=f},replaceChildren(...items){this.children=items}}}
const els=Object.fromEntries(['family','state','preview','actions','svg','cold','status','restart'].map(id=>['#'+id,element()]));
const document={querySelector(s){assert.ok(els[s],s);return els[s]},createElement(tag){assert.ok(['option','button'].includes(tag));return element()}};
const context=vm.createContext({document});
vm.runInContext(html.match(/<script>([\s\S]+)<\/script>/)[1],context);
let checks=0,transitions=0;
function shown(id){const row=rows.find(r=>r.id===id);assert.equal(els['#state'].value,id);assert.equal(els['#family'].value,row.family);assert.equal(els['#preview'].src,'screens/'+id+'.png');assert.equal(els['#svg'].href,'screens/'+id+'.svg');assert.equal(els['#cold'].href,'inspections/'+id+'.cold-material.png');assert.equal(els['#actions'].children.length,row.actions.length);assert.deepEqual(els['#state'].children.map(c=>c.value),rows.filter(s=>s.family===row.family).map(s=>s.id));checks+=7}
shown(rows[0].id);
for(const row of rows){
 vm.runInContext('show('+JSON.stringify(row.id)+')',context);shown(row.id);
 const buttons=[...els['#actions'].children];
 row.actions.forEach((a,i)=>{assert.equal(buttons[i].textContent,a[1]);buttons[i].listeners.click();shown(a[2]);transitions++;checks++});
 els['#family'].value=row.family;els['#family'].listeners.change();shown(rows.find(s=>s.family===row.family).id);
 els['#state'].value=row.id;els['#state'].listeners.change();shown(row.id);
 els['#restart'].listeners.click();shown(rows.find(s=>s.family===row.family).id);
}
assert.throws(()=>vm.runInContext('show("missing-state")',context),/Unknown scene/);checks++;
assert.ok(!/\b(?:fetch|XMLHttpRequest|WebSocket|setInterval|setTimeout)\s*\(/.test(html));checks++;
console.log(JSON.stringify({result:'PASS',checks,scenes:rows.length,transitions,scenarioGroups:['initial state','all state choices','all journey choices','every action target','restart per journey','unknown state rejection','offline no-network/no-timer code'],method:'Actual viewer JavaScript in Node VM with DOM fixtures; browser rendering and native actions not exercised'}));
