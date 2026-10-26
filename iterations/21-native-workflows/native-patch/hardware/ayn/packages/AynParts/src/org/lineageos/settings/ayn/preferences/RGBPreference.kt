/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.ayn.preferences

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.ShapeDrawable
import android.graphics.drawable.shapes.OvalShape
import android.util.AttributeSet
import android.view.LayoutInflater
import androidx.appcompat.app.AlertDialog
import androidx.preference.DialogPreference
import androidx.preference.PreferenceManager
import com.android.settingslib.widget.preference.app.R as settingslib_R
import com.google.android.material.slider.Slider
import org.lineageos.settings.ayn.R
import org.lineageos.settings.ayn.forge.ForgeLayerDrawable
import org.lineageos.settings.ayn.forge.ForgeRgbThumbDrawable
import org.lineageos.settings.ayn.utils.LightUtils

class RGBPreference : DialogPreference {

    var nodeString: String = ""
    var defaultValue: String = "255:255:255:255"

    var selectedColor: Int = Color.WHITE
        private set

    var selectedBrightness: Int = 255
        private set

    constructor(context: Context, attrs: AttributeSet?) : super(context, attrs) {
        setLayoutResource(settingslib_R.layout.preference_app)
    }

    constructor(context: Context) : this(context, null)

    override fun onAttachedToHierarchy(preferenceManager: PreferenceManager) {
        super.onAttachedToHierarchy(preferenceManager)
        loadPersistedState()
    }

    fun loadPersistedState() {
        val parts = getPersistedString(defaultValue).split(":")
        selectedColor = Color.rgb(parts[0].toInt(), parts[1].toInt(), parts[2].toInt())
        selectedBrightness = parts[3].toInt()

        val size = (40 * context.resources.displayMetrics.density).toInt()
        icon =
            ShapeDrawable(OvalShape()).apply {
                intrinsicWidth = size
                intrinsicHeight = size
                paint.color = selectedColor
            }
    }

    override fun onClick() {
        val view = LayoutInflater.from(context).inflate(R.layout.dialog_rgb_sliders, null)
        val redSlider = view.findViewById<Slider>(R.id.dialog_slider_red)
        val greenSlider = view.findViewById<Slider>(R.id.dialog_slider_green)
        val blueSlider = view.findViewById<Slider>(R.id.dialog_slider_blue)
        val brightnessSlider = view.findViewById<Slider>(R.id.dialog_slider_brightness)

        view.background = ForgeLayerDrawable(context, "cg_rf_panel", false)
        view.setPadding(0, 0, 0, 0) // The retained child owns the original24dp content padding.
        fun Slider.forgeThumb(channelColor: Int) {
            val thumb = ForgeRgbThumbDrawable(context, channelColor, this)
            setCustomThumbDrawable(thumb)
        }
        redSlider.forgeThumb(Color.rgb(255, 59, 48))
        greenSlider.forgeThumb(Color.rgb(52, 199, 89))
        blueSlider.forgeThumb(Color.rgb(0, 122, 255))
        brightnessSlider.forgeThumb(Color.WHITE)

        val initialColor = selectedColor
        val initialBrightness = selectedBrightness

        var liveColor = selectedColor
        var liveBrightness = selectedBrightness

        redSlider.value = Color.red(liveColor).toFloat()
        greenSlider.value = Color.green(liveColor).toFloat()
        blueSlider.value = Color.blue(liveColor).toFloat()
        brightnessSlider.value = liveBrightness.toFloat()

        val getKernelColor = { color: Int ->
            "${Color.red(color)} ${Color.green(color)} ${Color.blue(color)}"
        }

        val liveApply = {
            LightUtils.applyToHardware(nodeString, getKernelColor(liveColor), liveBrightness)
        }

        val updateColor = { red: Int, green: Int, blue: Int ->
            liveColor = Color.rgb(red, green, blue)
        }

        fun Slider.bind(onChange: (Float) -> Unit) {
            addOnChangeListener { _, value, fromUser ->
                if (fromUser) {
                    onChange(value)
                    liveApply()
                }
            }
        }

        redSlider.bind { updateColor(it.toInt(), Color.green(liveColor), Color.blue(liveColor)) }
        greenSlider.bind { updateColor(Color.red(liveColor), it.toInt(), Color.blue(liveColor)) }
        blueSlider.bind { updateColor(Color.red(liveColor), Color.green(liveColor), it.toInt()) }
        brightnessSlider.bind { liveBrightness = it.toInt() }

        val resetToInitial = {
            LightUtils.applyToHardware(nodeString, getKernelColor(initialColor), initialBrightness)
        }

        val dialog = AlertDialog.Builder(context, R.style.cg_ayn_rgb_dialog)
            .setTitle(title)
            .setView(view)
            .setPositiveButton(R.string.cg_ayn_ok) { _, _ ->
                val stringValue =
                    "${Color.red(liveColor)}:${Color.green(liveColor)}:${Color.blue(liveColor)}:$liveBrightness"
                if (callChangeListener(stringValue)) {
                    persistString(stringValue)
                    loadPersistedState()
                    liveApply()
                }
            }
            .setNegativeButton(R.string.cg_ayn_cancel) { _, _ -> resetToInitial() }
            .setOnCancelListener { resetToInitial() }
            .show()
        dialog.window?.setBackgroundDrawable(ForgeLayerDrawable(context, "cg_rf_panel", false))
        for (which in intArrayOf(AlertDialog.BUTTON_POSITIVE, AlertDialog.BUTTON_NEGATIVE)) {
            dialog.getButton(which).apply {
                background = ForgeLayerDrawable(context, "cg_rf_button", true)
                setTextColor(Color.rgb(238, 231, 217))
                minHeight = (56 * resources.displayMetrics.density).toInt()
                minWidth = (96 * resources.displayMetrics.density).toInt()
                isAllCaps = false
            }
        }
    }
}
