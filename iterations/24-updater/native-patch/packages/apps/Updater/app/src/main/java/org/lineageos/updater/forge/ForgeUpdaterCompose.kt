/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.updater.forge

import android.graphics.Rect
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsHoveredAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt

private val SteelText = Color(0xFFEEE7D9)
private val ColdSteel = Color(0xFFB5BDC6)
private val Ember = Color(0xFFE56620)
private val ErrorText = Color(0xFFFF8585)

@Composable
private fun frame(family: String, momentary: Boolean): ForgeLayerDrawable {
    val context = LocalContext.current
    val density = LocalDensity.current.density
    return remember(context, family, momentary, density) {
        ForgeLayerDrawable(context, family, momentary)
    }
}

@Composable
private fun insets(drawable: ForgeLayerDrawable): PaddingValues {
    val density = LocalDensity.current
    return remember(drawable, density) {
        val p = Rect()
        drawable.getPadding(p)
        with(density) { PaddingValues(p.left.toDp(), p.top.toDp(), p.right.toDp(), p.bottom.toDp()) }
    }
}

private fun Modifier.steel(
    drawable: ForgeLayerDrawable,
    active: Boolean = false,
    enabled: Boolean = true,
    focused: Boolean = false,
    pressed: Boolean = false,
): Modifier = drawBehind {
    drawable.state = buildList {
        if (enabled) add(android.R.attr.state_enabled)
        if (focused) add(android.R.attr.state_focused)
        if (pressed) add(android.R.attr.state_pressed)
    }.toIntArray()
    drawable.setFeatureActive(active)
    drawable.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
    drawable.draw(drawContext.canvas.nativeCanvas)
}

/** Card activity follows the actual operation phase. Expansion and progress presence do not activate it. */
@Composable
fun ForgeUpdateCard(
    tone: ForgeUpdateTone,
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    val drawable = frame("cg_rf_panel", false)
    val minimum = with(LocalDensity.current) {
        Pair(drawable.intrinsicWidth.toDp(), drawable.intrinsicHeight.toDp())
    }
    val primary = when (tone) {
        ForgeUpdateTone.ACTIVE -> Ember
        ForgeUpdateTone.ERROR -> ErrorText
        ForgeUpdateTone.COLD -> ColdSteel
    }
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = primary,
            onPrimary = Color(0xFF10151B),
            background = Color(0xFF080C11),
            surface = Color(0xFF10151B),
            surfaceBright = Color(0xFF10151B),
            onSurface = SteelText,
            onSurfaceVariant = ColdSteel,
            onBackground = SteelText,
            primaryContainer = Color(0xFF2A211B), onPrimaryContainer = SteelText,
            secondary = ColdSteel, onSecondary = Color(0xFF10151B),
            secondaryContainer = Color(0xFF1B242C), onSecondaryContainer = SteelText,
            tertiary = ColdSteel, onTertiary = Color(0xFF10151B),
            tertiaryContainer = Color(0xFF202A33), onTertiaryContainer = SteelText,
            surfaceVariant = Color(0xFF1B252E),
            outline = Color(0xFF65717D), outlineVariant = Color(0xFF36414D),
            surfaceTint = Color.Transparent, surfaceDim = Color(0xFF080C11),
            surfaceContainerLowest = Color(0xFF0B1015), surfaceContainerLow = Color(0xFF10151B),
            surfaceContainer = Color(0xFF151C23), surfaceContainerHigh = Color(0xFF1A242E),
            surfaceContainerHighest = Color(0xFF202B35),
            error = ErrorText, onError = Color(0xFF10151B),
            errorContainer = Color(0xFF3A1818), onErrorContainer = Color(0xFFFFE1DF),
        ),
        typography = MaterialTheme.typography,
        shapes = MaterialTheme.shapes,
    ) {
        Column(
            modifier = modifier.fillMaxWidth()
                .sizeIn(minWidth = minimum.first, minHeight = minimum.second)
                .steel(drawable, active = tone == ForgeUpdateTone.ACTIVE)
                .padding(insets(drawable)),
            content = content,
        )
    }
}

/** Native click, enabled state, focus, accessibility role and indication are retained. */
@Composable
fun ForgeUpdateButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    outlined: Boolean = false,
    content: @Composable RowScope.() -> Unit,
) {
    val drawable = frame(if (outlined) "cg_rf_field" else "cg_rf_button", true)
    val minimum = with(LocalDensity.current) {
        Pair(maxOf(48.dp, drawable.intrinsicWidth.toDp()), maxOf(48.dp, drawable.intrinsicHeight.toDp()))
    }
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val hovered by interaction.collectIsHoveredAsState()
    Button(
        onClick = onClick, enabled = enabled, interactionSource = interaction,
        modifier = modifier.sizeIn(minWidth = minimum.first, minHeight = minimum.second)
            .steel(drawable, enabled = enabled, focused = focused || hovered, pressed = pressed),
        contentPadding = insets(drawable),
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent, contentColor = SteelText,
            disabledContainerColor = Color.Transparent, disabledContentColor = Color(0xFF8F9BA7),
        ),
        elevation = null, shape = RectangleShape,
        content = content,
    )
}

@Composable
fun ForgeUpdateIconButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    content: @Composable () -> Unit,
) {
    val drawable = frame("cg_rf_button", true)
    val minimum = with(LocalDensity.current) {
        Pair(maxOf(48.dp, drawable.intrinsicWidth.toDp()), maxOf(48.dp, drawable.intrinsicHeight.toDp()))
    }
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val hovered by interaction.collectIsHoveredAsState()
    IconButton(
        onClick = onClick, enabled = enabled, interactionSource = interaction,
        modifier = modifier.sizeIn(minWidth = minimum.first, minHeight = minimum.second)
            .steel(drawable, enabled = enabled, focused = focused || hovered, pressed = pressed),
        content = content,
    )
}

/** Uses the caller's real fraction. Paused/error progress stays steady; no extra clock is introduced. */
@Composable
fun ForgeUpdateProgress(progress: Float?, tone: ForgeUpdateTone) {
    val drawable = frame("cg_upd_rail", false)
    val color = when (tone) {
        ForgeUpdateTone.ACTIVE -> Ember
        ForgeUpdateTone.ERROR -> ErrorText
        ForgeUpdateTone.COLD -> ColdSteel
    }
    Box(
        modifier = Modifier.fillMaxWidth().heightIn(min = 12.dp)
            .steel(drawable, active = tone == ForgeUpdateTone.ACTIVE)
            .padding(insets(drawable)),
        contentAlignment = androidx.compose.ui.Alignment.Center,
    ) {
        val indicator = Modifier.fillMaxWidth().height(4.dp)
        if (progress == null) {
            LinearProgressIndicator(modifier = indicator, color = color, trackColor = Color.Transparent)
        } else {
            LinearProgressIndicator(progress = { progress }, modifier = indicator,
                color = color, trackColor = Color.Transparent)
        }
    }
}

/** Retains every live value while allowing long English byte/ETA strings to wrap. */
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
fun ForgeUpdateProgressInfo(progress: org.lineageos.updater.updates.state.ProgressState.Determinate) {
    androidx.compose.foundation.layout.FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(4.dp),
        verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(4.dp),
    ) {
        androidx.compose.material3.Text(
            text = progress.percent.toInt().toString() + "%",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.alignByBaseline(),
        )
        if (progress.downloadedSize.isNotEmpty()) {
            androidx.compose.material3.Text(text = " · " + progress.downloadedSize,
                modifier = Modifier.alignByBaseline())
        }
        if (progress.eta.isNotEmpty()) {
            androidx.compose.material3.Text(text = progress.eta, modifier = Modifier.alignByBaseline())
        }
    }
}
