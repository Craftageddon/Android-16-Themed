/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: Apache-2.0
 * Public model/logging contracts and choice ordering retain the pinned SPA behavior.
 */
package org.lineageos.updater.forge

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import com.android.settingslib.spa.framework.theme.SettingsTheme
import com.android.settingslib.spa.framework.util.wrapOnClickWithLog
import com.android.settingslib.spa.framework.util.wrapOnSwitchWithLog
import com.android.settingslib.spa.widget.preference.PreferenceModel
import com.android.settingslib.spa.widget.preference.SwitchPreferenceModel
import com.android.settingslib.spa.widget.preference.ListPreferenceModel
import com.android.settingslib.spa.widget.dialog.AlertDialogButton
import com.android.settingslib.spa.widget.dialog.getDialogWidth
import org.lineageos.updater.R

@Composable
fun ForgeUpdaterTheme(content: @Composable () -> Unit) {
    SettingsTheme {
        ForgeUpdaterPalette {
            CompositionLocalProvider(androidx.compose.material3.LocalContentColor provides SteelText) { content() }
        }
    }
}

@Composable
fun ForgePreference(model: PreferenceModel, singleLineSummary: Boolean = false) {
    val click = wrapOnClickWithLog(model.onClick)
    ForgePreferenceRow(
        title = model.title, summary = model.summary().toString(), enabled = model.enabled(),
        titleDescription = model.titleContentDescription,
        summaryDescription = model.summaryContentDescription(),
        icon = model.icon, onClick = click,
    )
}

@Composable
fun ForgeSwitchPreference(model: SwitchPreferenceModel) {
    val checked = model.checked()
    val changeable = model.changeable()
    val callback = wrapOnSwitchWithLog(model.onCheckedChange)
    ForgePreferenceRow(
        title = model.title, summary = model.summary().toString(),
        enabled = changeable, featureOn = checked == true,
        toggleValue = checked, onToggle = callback, icon = model.icon,
        loadingDescription = if (checked == null) stringResource(R.string.cg_upd_loading) else null,
        trailing = { ForgeToggleVisual(checked, changeable) },
    )
}

@Composable
fun ForgeListPreference(model: ListPreferenceModel) {
    var dialogOpened by rememberSaveable { mutableStateOf(false) }
    if (dialogOpened) {
        ForgeSteelDialog(
            title = model.title, width = getDialogWidth(),
            onDismissRequest = { dialogOpened = false },
            text = {
                Column(Modifier.selectableGroup()) {
                    for (option in model.options) {
                        ForgeRadioRow(
                            title = option.text, summary = option.summary,
                            selected = option.id == model.selectedId.intValue,
                            enabled = model.enabled(),
                            onClick = { dialogOpened = false; model.onIdSelected(option.id) },
                        )
                    }
                }
            },
        )
    }
    // Preserve the actual model-derived summary, empty-options guard and logged open action.
    ForgePreference(object : PreferenceModel {
        override val title = model.title
        override val summary = { model.options.find { it.id == model.selectedId.intValue }?.text ?: "" }
        override val icon = model.icon
        override val enabled = model.enabled
        override val onClick = { dialogOpened = true }.takeIf { model.options.isNotEmpty() }
    })
}

@Composable
fun ForgeUpdaterAlertDialog(
    onDismissRequest: () -> Unit, confirmButton: AlertDialogButton?,
    dismissButton: AlertDialogButton?, title: String?, icon: ImageVector,
    text: (@Composable () -> Unit)?,
) {
    ForgeSteelDialog(
        onDismissRequest = onDismissRequest, title = title, width = getDialogWidth(),
        icon = { ForgeUpdateGlyph("cg_upd_badge", null, Modifier.size(48.dp)) },
        text = text,
        confirm = confirmButton?.let { button -> {
            ForgeUpdateButton(onClick = button.onClick, enabled = button.enabled) {
                androidx.compose.material3.Text(button.text)
            }
        } },
        dismiss = dismissButton?.let { button -> {
            ForgeUpdateButton(onClick = button.onClick, enabled = button.enabled, outlined = true) {
                androidx.compose.material3.Text(button.text)
            }
        } },
    )
}

@Composable
fun ForgeMoreOptionsAction(
    content: @Composable com.android.settingslib.spa.widget.scaffold.MoreOptionsScope.() -> Unit,
) {
    var expanded by rememberSaveable { mutableStateOf(false) }
    val onDismiss = { expanded = false }
    Box {
        ForgeUpdateIconButton(onClick = { expanded = true }) {
            ForgeUpdateGlyph("cg_upd_more",
                stringResource(androidx.appcompat.R.string.abc_action_menu_overflow_description),
                Modifier.size(24.dp))
        }
        androidx.compose.material3.DropdownMenu(
            expanded = expanded, onDismissRequest = onDismiss,
            modifier = Modifier.forgePanel(),
            shape = androidx.compose.ui.graphics.RectangleShape,
            containerColor = androidx.compose.ui.graphics.Color.Transparent,
        ) {
            val scope = remember(this) {
                object : com.android.settingslib.spa.widget.scaffold.MoreOptionsScope() {
                    override fun dismiss() { onDismiss() }
                }
            }
            scope.content()
        }
    }
}
