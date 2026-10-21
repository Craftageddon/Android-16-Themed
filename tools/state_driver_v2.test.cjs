'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { sample } = require('./state_driver_v2.cjs');
const light = s => ['reflection','spill','seam','core'].map(k => s.gains[k]);
test('idle, hover, focus, press and warning alone cannot ignite an off control', () => {
  for (const flags of [{},{hovered:true},{focused:true},{pressed:true},{warning:true},
    {hovered:true,focused:true,pressed:true,warning:true}]) {
    const s = sample(flags); assert.deepEqual(light(s),[0,0,0,0]); assert.equal(s.active,false);
  }
});
test('each explicit activation state enables the same independent light layers', () => {
  for (const key of ['on','checked','selected']) {
    const s = sample({[key]:true}); assert.equal(s.active,true); assert.equal(s.selection,true);
    assert.ok(light(s).every(x => x > 0));
  }
});
test('neutral focus survives selection and active press without requiring ember', () => {
  for (const active of [false,true]) for (const pressed of [false,true]) {
    const s = sample({selected:active,focused:true,pressed}); assert.equal(s.focus,true);
    assert.equal(s.gains.focus,1); assert.equal(s.active,active);
  }
});
test('disabled and forced cold suppress emission even with contradictory active flags', () => {
  for (const override of [{enabled:false},{cold:true}]) {
    const s = sample({...override,on:true,selected:true,checked:true,pressed:true,focused:true});
    assert.deepEqual(light(s),[0,0,0,0]); assert.equal(s.selection,false);
  }
  assert.equal(sample({enabled:false,focused:true}).gains.focus,0);
});
test('press boost applies only to already active controls and retains geometric selection', () => {
  assert.deepEqual(light(sample({pressed:true})),light(sample()));
  const on=sample({on:true}), press=sample({on:true,pressed:true});
  assert.ok(press.gains.core>on.gains.core); assert.equal(press.selection,true);
});
test('off transition extinguishes every light and hidden/reduced states schedule no frames', () => {
  assert.deepEqual(light(sample({on:false,checked:false,selected:false})),[0,0,0,0]);
  for (const flags of [{on:true,reducedMotion:true},{on:true,visible:false},{on:true,pressed:true}]) {
    const s=sample(flags); assert.equal(s.animate,false); assert.equal(s.scale,1);
  }
});
test('explicit off-value artwork stays cold under selection while neutral cues survive', () => {
  const s=sample({emissionLockedOff:true,selected:true,on:true,pressed:true,focused:true});
  assert.deepEqual(light(s),[0,0,0,0]); assert.equal(s.focus,true); assert.equal(s.selection,true);
});
