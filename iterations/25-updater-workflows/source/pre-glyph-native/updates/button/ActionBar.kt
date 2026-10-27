/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

// Craftageddon: steel presentation and wrapping action layout; original callbacks retained.
package org.lineageos.updater.updates.button

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import com.android.settingslib.spa.debug.UiModePreviews
import com.android.settingslib.spa.framework.theme.SettingsDimension
import com.android.settingslib.spa.framework.theme.SettingsSpace
import com.android.settingslib.spa.framework.theme.SettingsTheme
import com.android.settingslib.spa.widget.scaffold.MoreOptionsAction
import com.android.settingslib.spa.widget.scaffold.MoreOptionsScope
import org.lineageos.updater.forge.ForgeUpdateButton
import org.lineageos.updater.forge.ForgeUpdateIconButton

@OptIn(ExperimentalMaterial3ExpressiveApi::class, ExperimentalLayoutApi::class)
@Composable
fun ActionBar(
    buttons: List<ActionBarButton>,
    menuContent: (@Composable MoreOptionsScope.() -> Unit)? = null,
) {
    FlowRow(
        modifier = Modifier
            .fillMaxWidth()
            .padding(SettingsDimension.buttonPadding),
        horizontalArrangement = Arrangement.spacedBy(SettingsSpace.extraSmall2),
        verticalArrangement = Arrangement.spacedBy(SettingsSpace.extraSmall2),
    ) {
        buttons.forEach { button ->
            when (button) {
                is ActionBarButton.Tonal -> ForgeUpdateButton(
                    onClick = button.onClick,
                    // Forged housing supplies the shape.
                    enabled = button.enabled,
                ) {
                    Text(button.text)
                }

                is ActionBarButton.Outlined -> ForgeUpdateButton(
                    outlined = true,
                    onClick = button.onClick,
                    // Forged housing supplies the shape.
                    enabled = button.enabled,
                ) {
                    Text(button.text)
                }

                is ActionBarButton.Icon -> ForgeUpdateIconButton(
                    onClick = button.onClick,
                    // Forged icon housing supplies the shape.
                    enabled = button.enabled,
                ) {
                    Icon(
                        imageVector = button.imageVector,
                        contentDescription = button.contentDescription,
                        modifier = Modifier.size(SettingsDimension.itemIconSize),
                    )
                }

            }
        }

        if (menuContent != null) {
            // Flow layout keeps the overflow action reachable when labels wrap.
            MoreOptionsAction(content = menuContent)
        }
    }
}

sealed interface ActionBarButton {
    val enabled: Boolean
    val onClick: () -> Unit

    data class Tonal(
        val text: String,
        override val enabled: Boolean = true,
        override val onClick: () -> Unit,
    ) : ActionBarButton

    data class Outlined(
        val text: String,
        override val enabled: Boolean = true,
        override val onClick: () -> Unit,
    ) : ActionBarButton

    data class Icon(
        val imageVector: ImageVector,
        val contentDescription: String? = null,
        override val enabled: Boolean = true,
        override val onClick: () -> Unit,
    ) : ActionBarButton
}

@UiModePreviews
@Composable
private fun ActionBarDownloadPreview() {
    SettingsTheme {
        ActionBar(
            buttons = listOf(
                ActionBarButton.Tonal(text = "Download") {},
            ),
            menuContent = {
                MenuItem(text = "View downloads") {}
            },
        )
    }
}

@UiModePreviews
@Composable
private fun ActionBarDownloadingPreview() {
    SettingsTheme {
        ActionBar(
            buttons = listOf(
                ActionBarButton.Icon(
                    imageVector = Icons.Outlined.Pause,
                    contentDescription = "Pause",
                ) {},
                ActionBarButton.Outlined(text = "Cancel") {},
            ),
            menuContent = {
                MenuItem(text = "View downloads") {}
            },
        )
    }
}

@UiModePreviews
@Composable
private fun ActionBarPausedPreview() {
    SettingsTheme {
        ActionBar(
            buttons = listOf(
                ActionBarButton.Icon(
                    imageVector = Icons.Outlined.PlayArrow,
                    contentDescription = "Resume",
                ) {},
                ActionBarButton.Outlined(text = "Cancel") {},
            ),
            menuContent = {
                MenuItem(text = "Delete") {}
                MenuItem(text = "View downloads") {}
            },
        )
    }
}

@UiModePreviews
@Composable
private fun ActionBarInstallPreview() {
    SettingsTheme {
        ActionBar(
            buttons = listOf(
                ActionBarButton.Tonal(text = "Install") {},
            ),
            menuContent = {
                MenuItem(text = "Delete") {}
                MenuItem(text = "Export update") {}
            },
        )
    }
}
