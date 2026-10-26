package com.android.systemui.accessibility;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.view.MotionEvent;
import android.view.View;
import android.view.Gravity;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.TextView;
import com.android.systemui.res.R;

/** Presentation-only bindings to the real magnification view IDs. */
public final class ForgeMagnificationStyle {
    private ForgeMagnificationStyle() {}

    public static void installFullscreenBorder(View border, Context context) {
        Drawable original = border.getBackground();
        // Retain the existing Wear/custom-background exception. This renderer
        // supports the exact uniform-radius rectangular source contract.
        if (!(original instanceof GradientDrawable)) return;
        GradientDrawable shape = (GradientDrawable) original;
        if (shape.getShape() != GradientDrawable.RECTANGLE || shape.getCornerRadii() != null) return;
        ForgeMagnificationBorderDrawable next = new ForgeMagnificationBorderDrawable(
                context.getResources(), context.getTheme(), ForgeMagnificationBorderDrawable.FULLSCREEN);
        next.setCornerRadius(shape.getCornerRadius()); next.setAlpha(shape.getAlpha());
        border.setBackground(next);
    }

    public static Drawable windowBorder(Context context, boolean editSize) {
        return new ForgeMagnificationBorderDrawable(context.getResources(), context.getTheme(),
                editSize ? ForgeMagnificationBorderDrawable.WINDOW_EDIT : ForgeMagnificationBorderDrawable.WINDOW);
    }

    public static void applySettings(View root) {
        // This is called before the original owner installs its scale and
        // callback. No range, value, listener or secure-setting write occurs.
        SeekBar zoom = root.findViewById(R.id.seekbar);
        if (zoom != null) {
            zoom.setThumbTintList(null); zoom.setProgressTintList(null);
            zoom.setSecondaryProgressTintList(null); zoom.setProgressBackgroundTintList(null);
            zoom.setThumb(root.getContext().getDrawable(R.drawable.cg_mag_seek_thumb));
            zoom.setProgressDrawable(root.getContext().getDrawable(R.drawable.cg_mag_zoom_progress));
        }
        configureIcon(root, R.id.icon_start, R.id.icon_start_frame, R.drawable.cg_mag_zoom_out);
        configureIcon(root, R.id.icon_end, R.id.icon_end_frame, R.drawable.cg_mag_zoom_in);
    }

    private static void configureIcon(View root, int iconId, int frameId, int drawable) {
        ImageView icon = root.findViewById(iconId); View frame = root.findViewById(frameId);
        if (icon == null || frame == null) return;
        icon.setImageTintList(null); icon.clearColorFilter(); icon.setBackground(null);
        icon.setImageResource(drawable); icon.setDuplicateParentStateEnabled(true);
        frame.setBackgroundTintList(null);
        frame.setBackground(root.getContext().getDrawable(R.drawable.cg_mag_control));
    }

    public static void updateGesturePresentation(View view, MotionEvent event) {
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN) view.setPressed(true);
        else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) view.setPressed(false);
    }

    public static void updateLegacyGesturePresentation(View root, MotionEvent event) {
        if (root == null) return;
        View graphic = root.findViewById(R.id.controller);
        if (graphic != null) updateGesturePresentation(graphic, event);
    }

    public static void clearHiddenGesturePresentation(View... controls) {
        for (View control : controls) {
            if (control != null && control.getVisibility() != View.VISIBLE) control.setPressed(false);
        }
    }

    public static void updatePanelHeader(View root, int panelWidth) {
        LinearLayout row = root.findViewById(R.id.magnifier_size_view);
        TextView title = root.findViewById(R.id.magnifier_size_title);
        TextView edit = root.findViewById(R.id.magnifier_edit_button);
        if (row == null || title == null || edit == null) return;
        int available = panelWidth - 2*root.getResources().getDimensionPixelSize(
                R.dimen.magnification_setting_background_padding);
        int gap = root.getResources().getDimensionPixelSize(
                R.dimen.magnification_setting_view_item_horizontal_spacing);
        float editWidth = Math.max(edit.getMinimumWidth(), edit.getPaint().measureText(
                edit.getText().toString()) + edit.getCompoundPaddingLeft() + edit.getCompoundPaddingRight());
        boolean stacked = title.getPaint().measureText(title.getText().toString()) + editWidth + gap > available;
        int orientation = stacked ? LinearLayout.VERTICAL : LinearLayout.HORIZONTAL;
        if (row.getOrientation() == orientation) return;
        row.setOrientation(orientation);
        LinearLayout.LayoutParams titleParams = (LinearLayout.LayoutParams) title.getLayoutParams();
        titleParams.width = stacked ? LinearLayout.LayoutParams.MATCH_PARENT : 0;
        titleParams.weight = stacked ? 0 : 1;
        title.setLayoutParams(titleParams);
        LinearLayout.LayoutParams editParams = (LinearLayout.LayoutParams) edit.getLayoutParams();
        editParams.gravity = stacked ? Gravity.END : Gravity.CENTER_VERTICAL;
        edit.setLayoutParams(editParams);
    }
}
