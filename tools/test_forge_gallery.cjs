// Exercise the actual offline gallery script with a minimal document fixture.
// This checks filtering behavior; it does not stand in for a browser render.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]);
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const rows=JSON.parse(fs.readFileSync(path.join(root,'screens/layout-metadata.json'),'utf8'));
const elements={'#search':{value:'',addEventListener(type,fn){this.listener=fn}},'#group':{value:'all',addEventListener(type,fn){this.listener=fn}},'#count':{textContent:''}};
const cards=rows.map(r=>({dataset:{group:r.group,name:r.title.toLowerCase()},hidden:false}));
const document={querySelector:s=>elements[s],querySelectorAll:s=>{assert.equal(s,'article');return cards}};
vm.runInNewContext(html.match(/<script>([\s\S]+)<\/script>/)[1],{document});
let checks=0;
function count(n){assert.equal(cards.filter(c=>!c.hidden).length,n);assert.equal(elements['#count'].textContent,n+' screens shown');checks+=2}
count(42);
elements['#group'].value='thor';elements['#group'].listener();count(17);
elements['#search'].value='TrIgGeR';elements['#search'].listener();count(1);
elements['#group'].value='android';elements['#group'].listener();count(0);
elements['#search'].value='nonexistent-example';elements['#search'].listener();count(0);
elements['#search'].value='';elements['#group'].value='all';elements['#search'].listener();count(42);
console.log(JSON.stringify({checks,scenarios:6,result:'PASS',method:'Actual gallery JavaScript in Node VM with document fixtures; no browser rendering claim'}));
