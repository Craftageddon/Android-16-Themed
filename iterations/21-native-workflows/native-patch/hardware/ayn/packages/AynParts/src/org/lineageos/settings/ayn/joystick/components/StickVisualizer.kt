/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.ayn.joystick.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.semantics.semantics
import org.lineageos.settings.ayn.R
import org.lineageos.settings.ayn.forge.ForgeLayerDrawable
import kotlin.math.roundToInt
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp

@Composable
fun StickVisualizer(x: Float, y: Float, label: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val gate = remember(context) { ForgeLayerDrawable(context, "cg_ayn_gate", false) }
    val dot = remember(context) { ForgeLayerDrawable(context, "cg_ayn_dot", false) }
    val labelText = when (label) {
        "L" -> stringResource(R.string.cg_ayn_left_stick)
        "R" -> stringResource(R.string.cg_ayn_right_stick)
        else -> label
    }
    val position = stringResource(R.string.cg_ayn_stick_position, x, y)
    Canvas(modifier = modifier.size(120.dp).semantics {
        contentDescription = labelText
        stateDescription = position
    }) {
        val cx = size.width / 2f
        val cy = size.height / 2f
        val radius = size.minDimension / 2f - 4.dp.toPx()

        // The source56dp boundary remains unchanged; the frame has no static center dot.
        val inputStrength = kotlin.math.sqrt(x * x + y * y).coerceIn(0f, 1f)
        gate.setInputStrength(inputStrength)
        gate.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
        gate.draw(drawContext.canvas.nativeCanvas)

        // Crosshair
        drawLine(
            color = Color(0xFF627482),
            start = Offset(cx - radius, cy),
            end = Offset(cx + radius, cy),
            strokeWidth = 1.dp.toPx(),
        )
        drawLine(
            color = Color(0xFF627482),
            start = Offset(cx, cy - radius),
            end = Offset(cx, cy + radius),
            strokeWidth = 1.dp.toPx(),
        )

        // Clamp the dot inside the circle (diagonals would overshoot otherwise)
        val dotRadius = 8.dp.toPx()
        val maxTravel = radius - dotRadius
        val rawDist = kotlin.math.sqrt(x * x + y * y).coerceAtLeast(Float.MIN_VALUE)
        val scale = if (rawDist > 1f) 1f / rawDist else 1f
        val dotX = cx + x * scale * maxTravel
        val dotY = cy + y * scale * maxTravel
        dot.setInputStrength(inputStrength)
        dot.setBounds(-10, -10, 10, 10)
        val native = drawContext.canvas.nativeCanvas
        val saved = native.save()
        native.translate(dotX, dotY)
        native.scale(density, density)
        dot.draw(native)
        native.restoreToCount(saved)
    }
}
