// Cold-off state contract, iteration 10. Reference for a renderer owner, not a hardware service.
'use strict';
function sample(flags = {}) {
  const visible = flags.visible !== false;
  const enabled = flags.enabled !== false;
  const active = enabled && !flags.cold && !!(flags.selected || flags.checked || flags.on);
  const radiating = active && !flags.emissionLockedOff;
  const focus = enabled && !!flags.focused;
  const pressed = active && !!flags.pressed;
  return {
    state: !enabled ? 'disabled' : active ? (pressed ? 'active_pressed' : 'on') : 'off',
    visible, active, focus, selection: active, baseOpacity: enabled ? 1 : .42,
    gains: {
      reflection: radiating ? (pressed ? .60 : .32) : 0,
      spill: radiating ? (pressed ? .92 : .72) : 0,
      seam: radiating ? 1 : 0,
      core: radiating ? (pressed ? 1 : .82) : 0,
      focus: focus ? 1 : 0,
      symbol: active ? 1 : 0,
    },
    // Static state change only. Reduced motion never introduces transforms or breathing.
    animate: false, scale: 1,
  };
}
module.exports = { sample };
