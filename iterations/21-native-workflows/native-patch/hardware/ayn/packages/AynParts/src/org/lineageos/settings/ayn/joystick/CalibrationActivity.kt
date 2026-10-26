/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.ayn.joystick

import android.content.pm.ActivityInfo
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable

class CalibrationActivity : ComponentActivity() {
    private val viewModel: CalibrationViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE

        setContent {
            DynamicTheme { CalibrationScreen(viewModel = viewModel, onFinish = { finish() }) }
        }
    }
}

@Composable
private fun DynamicTheme(content: @Composable () -> Unit) {
    org.lineageos.settings.ayn.forge.ForgeCalibrationTheme(content)
}
