/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.ayn

import android.os.Bundle
import androidx.preference.Preference
import androidx.preference.PreferenceCategory
import com.android.settingslib.widget.SettingsBasePreferenceFragment
import org.lineageos.internal.util.ControllerUtils
import org.lineageos.settings.ayn.utils.LightUtils

class AynSettingsFragment :
    SettingsBasePreferenceFragment(), Preference.OnPreferenceChangeListener {

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.ayn_panel, rootKey)

        findPreference<Preference>(KEY_GAMEPAD_REMAPPING)?.setOnPreferenceClickListener {
            ControllerUtils.launchControllerRemapping(
                requireContext(),
                CONTROLLER_DESCRIPTOR,
                getString(R.string.builtin_controller),
            )
            true
        }

        if (!LightUtils.supportsRGB) {
            findPreference<PreferenceCategory>(KEY_GAMEPAD_LIGHTS_CATEGORY)?.let {
                preferenceScreen.removePreference(it)
            }
        }
    }

    override fun onPreferenceChange(preference: Preference, newValue: Any?): Boolean {
        return true
    }

    companion object {
        private const val KEY_GAMEPAD_REMAPPING = "gamepad_remapping"
        private const val KEY_GAMEPAD_LIGHTS_CATEGORY = "gamepad_lights_category"

        // :045e:028e:uniqueId:moorechip
        private const val CONTROLLER_DESCRIPTOR = "90dfbbe0bbbab74642c53cae4ae0aa640d40ec21"
    }
}
