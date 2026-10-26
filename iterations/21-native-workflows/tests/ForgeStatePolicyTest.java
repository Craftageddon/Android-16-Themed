package org.lineageos.settings.ayn.forge;

/** Exhaust every state combination and enforce independent cold/focus/disable invariants. */
public final class ForgeStatePolicyTest {
    public static void main(String[] args) {
        int tested = 0;
        for (int bits = 0; bits < 128; bits++) {
            boolean enabled = (bits & 1) != 0, checked = (bits & 2) != 0;
            boolean selected = (bits & 4) != 0, focused = (bits & 8) != 0;
            boolean pressed = (bits & 16) != 0, feature = (bits & 32) != 0;
            boolean momentary = (bits & 64) != 0;
            ForgeStatePolicy result = ForgeStatePolicy.resolve(enabled, checked, selected,
                    focused, pressed, feature, momentary);
            if (!enabled && result.active) throw new AssertionError("Disabled emission");
            if (enabled && !checked && !selected && !feature && !(momentary && pressed)
                    && result.active) throw new AssertionError("Focus/off enabled ember");
            if (enabled && (checked || selected || feature || (momentary && pressed))
                    && !result.active) throw new AssertionError("Active input lost");
            for (int channel : new int[] {0, 1, 2, 3, 5}) {
                if (!result.active && result.gains[channel] != 0) throw new AssertionError("Cold mask lit");
                if (result.active && result.gains[channel] <= 0) throw new AssertionError("Active mask missing");
            }
            if (result.gains[4] != (enabled && focused ? 1f : 0f)) throw new AssertionError("Neutral focus lost");
            if (result.base != (enabled ? 1f : .42f)) throw new AssertionError("Disabled opacity");
            tested++;
        }
        System.out.println("PASS: " + tested + " activation/input/focus/disable combinations");
    }
}
