/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.updater.forge;

import android.app.AlertDialog;
import android.content.res.ColorStateList;
import android.graphics.Rect;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import com.google.android.material.progressindicator.CircularProgressIndicator;

/** Presentation only. Dialog cancelability, messages, listeners and show/dismiss order stay with the owner. */
public final class ForgeDialogStyle {
    private static final int TEXT = 0xffeee7d9;
    private static final int COLD = 0xffb5bdc6;
    private static final int EMBER = 0xffe56620;

    public static AlertDialog show(AlertDialog dialog, boolean running) {
        dialog.show();
        apply(dialog, running);
        return dialog;
    }
    public static void apply(AlertDialog dialog, boolean running) {
        if (dialog.getWindow() == null) return;
        ForgeLayerDrawable panel = new ForgeLayerDrawable(dialog.getContext(), "cg_rf_panel", false);
        panel.setFeatureActive(running);
        dialog.getWindow().setBackgroundDrawable(panel);
        styleTextAndProgress(dialog.getWindow().getDecorView(), running);
        for (int which : new int[] {AlertDialog.BUTTON_POSITIVE, AlertDialog.BUTTON_NEGATIVE, AlertDialog.BUTTON_NEUTRAL}) {
            Button button = dialog.getButton(which);
            if (button == null) continue;
            ForgeLayerDrawable body = new ForgeLayerDrawable(dialog.getContext(),
                    which == AlertDialog.BUTTON_POSITIVE ? "cg_rf_button" : "cg_rf_field", true);
            button.setBackground(body);
            button.setMinWidth(Math.max(button.getMinWidth(), body.getIntrinsicWidth()));
            button.setMinHeight(Math.max(button.getMinHeight(), body.getIntrinsicHeight()));
            Rect padding = new Rect(); body.getPadding(padding);
            button.setPadding(Math.max(button.getPaddingLeft(), padding.left),
                    Math.max(button.getPaddingTop(), padding.top),
                    Math.max(button.getPaddingRight(), padding.right),
                    Math.max(button.getPaddingBottom(), padding.bottom));
            button.setTextColor(new ColorStateList(
                    new int[][] {new int[] {-android.R.attr.state_enabled}, new int[] {}},
                    new int[] {0xff8f9ba7, TEXT}));
        }
    }
    private static void styleTextAndProgress(View view, boolean running) {
        if (view instanceof TextView) ((TextView) view).setTextColor(TEXT);
        if (view instanceof CircularProgressIndicator) {
            CircularProgressIndicator indicator = (CircularProgressIndicator) view;
            indicator.setIndicatorColor(running ? EMBER : COLD);
            indicator.setTrackColor(0xff27333e);
            ForgeLayerDrawable ring = new ForgeLayerDrawable(view.getContext(), "cg_upd_switch_thumb", false);
            ring.setFeatureActive(running); view.setBackground(ring);
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) styleTextAndProgress(group.getChildAt(i), running);
        }
    }
}
