/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: Apache-2.0
 * Presentation semantics adapted from the preserved Apache-2.0 SPA interfaces.
 */
package org.lineageos.updater.forge

import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.interaction.collectIsHoveredAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.semantics.*
import androidx.compose.ui.unit.*
import androidx.compose.ui.window.DialogProperties
import kotlin.math.roundToInt

@Composable
fun Modifier.forgePanel(active: Boolean = false, focused: Boolean = false, pressed: Boolean = false): Modifier {
    val d = frame("cg_rf_panel", false)
    val minimum = with(LocalDensity.current) { Pair(d.intrinsicWidth.toDp(), d.intrinsicHeight.toDp()) }
    return sizeIn(minWidth = minimum.first, minHeight = minimum.second)
        .steel(d, active = active || pressed, focused = focused).padding(insets(d))
}

@Composable
fun ForgeSteelPanel(modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier.fillMaxWidth().forgePanel(), content = content)
}

@Composable
fun ForgePreferenceRow(
    title: String, summary: String, modifier: Modifier = Modifier,
    enabled: Boolean = true, featureOn: Boolean = false,
    onClick: (() -> Unit)? = null,
    toggleValue: Boolean? = null, onToggle: ((Boolean) -> Unit)? = null,
    loadingDescription: String? = null,
    titleDescription: String? = null, summaryDescription: String? = null,
    icon: (@Composable () -> Unit)? = null,
    trailing: (@Composable () -> Unit)? = null,
) {
    val interaction = remember { MutableInteractionSource() }
    val focused by interaction.collectIsFocusedAsState()
    val hovered by interaction.collectIsHoveredAsState()
    val pressed by interaction.collectIsPressedAsState()
    var row = modifier.fillMaxWidth()
    row = when {
        toggleValue != null && onToggle != null -> row.toggleable(
            value = toggleValue, enabled = enabled, role = Role.Switch,
            interactionSource = interaction, indication = androidx.compose.foundation.LocalIndication.current,
            onValueChange = onToggle)
        onClick != null -> row.clickable(
            enabled = enabled, interactionSource = interaction,
            indication = androidx.compose.foundation.LocalIndication.current, onClick = onClick)
        else -> row
    }
    if (loadingDescription != null) row = row.semantics { stateDescription = loadingDescription }
    // Interaction may be locked while the real feature remains on (e.g. AC-forced performance mode).
    Row(
        modifier = row.forgePanel(active = featureOn, focused = focused || hovered, pressed = enabled && pressed)
            .heightIn(min = 72.dp).padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        icon?.invoke()
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium,
                color = if (enabled) SteelText else ColdSteel,
                modifier = if (titleDescription == null) Modifier else Modifier.semantics {
                    contentDescription = titleDescription
                })
            if (summary.isNotEmpty()) Text(summary, style = MaterialTheme.typography.bodyMedium,
                color = ColdSteel,
                modifier = if (summaryDescription == null) Modifier else Modifier.semantics {
                    contentDescription = summaryDescription
                })
        }
        trailing?.invoke()
    }
}

/** Decorative visual only. Its parent owns the single toggle action and Role.Switch. */
@Composable
fun ForgeToggleVisual(checked: Boolean?, changeable: Boolean, modifier: Modifier = Modifier) {
    val track = frame("cg_upd_switch_track", false)
    val thumb = frame("cg_upd_switch_thumb", false)
    val rtl = LocalLayoutDirection.current == LayoutDirection.Rtl
    Box(modifier.width(52.dp).height(48.dp).drawBehind {
        val on = ForgeToggleGeometry.featureOn(checked)
        val alpha = if (changeable) 255 else 153
        for (d in listOf(track, thumb)) {
            d.state = intArrayOf(android.R.attr.state_enabled)
            d.setFeatureActive(on)
            d.alpha = alpha
        }
        val h = 32.dp.toPx()
        val top = (size.height - h) / 2f
        track.setBounds(0, top.roundToInt(), size.width.roundToInt(), (top + h).roundToInt())
        track.draw(drawContext.canvas.nativeCanvas)
        val left = ForgeToggleGeometry.thumbLeft(checked, size.width, h, rtl)
        thumb.setBounds(left.roundToInt(), top.roundToInt(), (left + h).roundToInt(), (top + h).roundToInt())
        thumb.draw(drawContext.canvas.nativeCanvas)
    })
}

@Composable
fun ForgeRadioRow(
    title: String, summary: String, selected: Boolean, enabled: Boolean,
    onClick: () -> Unit,
) {
    val ring = frame("cg_upd_switch_thumb", false)
    Row(
        Modifier.fillMaxWidth().selectable(selected = selected, enabled = enabled,
            onClick = onClick, role = Role.RadioButton).heightIn(min = 56.dp).padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Box(Modifier.size(32.dp).drawBehind {
            ring.state = intArrayOf(android.R.attr.state_enabled)
            ring.setFeatureActive(selected)
            ring.alpha = if (enabled) 255 else 153
            ring.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
            ring.draw(drawContext.canvas.nativeCanvas)
            if (selected) drawCircle(Ember, radius = 4.dp.toPx())
        })
        Column(Modifier.weight(1f)) {
            Text(title, color = if (enabled) SteelText else ColdSteel)
            if (summary.isNotEmpty()) Text(summary, style = MaterialTheme.typography.bodyMedium, color = ColdSteel)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ForgeSteelDialog(
    onDismissRequest: () -> Unit, title: String?, width: Dp,
    confirm: (@Composable () -> Unit)? = null,
    dismiss: (@Composable () -> Unit)? = null,
    icon: (@Composable () -> Unit)? = null,
    text: (@Composable () -> Unit)? = null,
) {
    AlertDialog(
        onDismissRequest = onDismissRequest,
        modifier = Modifier.width(width).forgePanel(),
        containerColor = Color.Transparent,
        shape = androidx.compose.ui.graphics.RectangleShape,
        confirmButton = { confirm?.invoke() }, dismissButton = dismiss,
        icon = icon,
        title = title?.let { { Text(it, style = MaterialTheme.typography.headlineSmall) } },
        text = text?.let { { Column(Modifier.verticalScroll(rememberScrollState())) { it() } } },
        properties = DialogProperties(usePlatformDefaultWidth = false),
    )
}
