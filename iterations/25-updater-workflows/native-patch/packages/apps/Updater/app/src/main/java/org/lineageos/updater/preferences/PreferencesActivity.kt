/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

// Craftageddon: source-owned steel presentation; original actions/data retained.
package org.lineageos.updater.preferences

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.remember
import com.android.settingslib.spa.framework.compose.LocalNavController
import com.android.settingslib.spa.framework.compose.NavControllerWrapper
import org.lineageos.updater.forge.ForgeUpdaterTheme as SettingsTheme

class PreferencesActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle = androidx.activity.SystemBarStyle.dark(android.graphics.Color.TRANSPARENT),
            navigationBarStyle = androidx.activity.SystemBarStyle.dark(android.graphics.Color.TRANSPARENT),
        )
        setContent {
            val navController = remember {
                object : NavControllerWrapper {
                    override fun navigate(route: String, popUpCurrent: Boolean) {}
                    override fun navigateBack() = onBackPressedDispatcher.onBackPressed()
                }
            }
            CompositionLocalProvider(LocalNavController provides navController) {
                SettingsTheme {
                    PreferencesScreen()
                }
            }
        }
    }
}
