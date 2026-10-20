'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict');
const {sample}=require('./state_driver.cjs');
test('disabled suppresses light, focus, selection and motion',()=>{
  const s=sample({enabled:false,selected:true,focused:true,pressed:true,warning:true},0);
  assert.equal(s.opacity,0);assert.equal(s.focus,false);assert.equal(s.selection,false);assert.equal(s.animate,false);
});
test('selection and focus survive the complete press event',()=>{
  for(const ms of [0,50,159,160,400]){const s=sample({selected:true,focused:true,pressed:true},ms);assert.ok(s.focus&&s.selection);}
  assert.equal(sample({selected:true,focused:true,pressed:true},160).state,'focused');
});
test('reduced motion remains constant over a held press',()=>{
  const a=sample({pressed:true,selected:true,reducedMotion:true},0),b=sample({pressed:true,selected:true,reducedMotion:true},100);
  assert.deepEqual(a,b);assert.equal(a.scale,1);assert.equal(a.blur,0);assert.equal(a.animate,false);
});
test('hidden views never schedule frames and warning settles',()=>{
  assert.equal(sample({visible:false,pressed:true},0).animate,false);
  assert.equal(sample({visible:false,warning:true},0).animate,false);
  const s=sample({warning:true},9000);assert.equal(s.opacity,.36);assert.equal(s.animate,false);
});
test('idle stays warm while cold is unlit',()=>{
  assert.ok(sample().opacity>0);assert.equal(sample({cold:true,selected:true},0).opacity,0);
});
