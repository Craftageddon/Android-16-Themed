/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

// Craftageddon: explicit presentation phase; updater actions and enablement are retained.
package org.lineageos.updater.updates

import android.content.Context
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Archive
import androidx.compose.material.icons.outlined.CloudDownload
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.key
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.withStyle
import com.android.settingslib.spa.debug.UiModePreviews
import com.android.settingslib.spa.framework.theme.SettingsDimension
import com.android.settingslib.spa.framework.theme.SettingsShape
import com.android.settingslib.spa.framework.theme.SettingsSpace
import com.android.settingslib.spa.framework.theme.SettingsTheme
import com.android.settingslib.spa.widget.preference.Preference
import com.android.settingslib.spa.widget.preference.PreferenceModel
import com.android.settingslib.spa.widget.ui.LinearProgressBar
import org.lineageos.updater.R
import org.lineageos.updater.forge.ForgeUpdateCard
import org.lineageos.updater.forge.ForgeUpdatePresentation
import org.lineageos.updater.forge.ForgeUpdateProgress
import org.lineageos.updater.forge.ForgeUpdateProgressInfo
import org.lineageos.updater.forge.ForgeUpdateGlyph
import androidx.compose.foundation.layout.size
import androidx.compose.ui.unit.dp
import org.lineageos.updater.updates.action.UpdateAction
import org.lineageos.updater.updates.action.UpdateActionType
import org.lineageos.updater.updates.action.UpdateActions
import org.lineageos.updater.updates.button.ActionBar
import org.lineageos.updater.updates.button.ActionBarButton
import org.lineageos.updater.updates.state.ProgressState
import org.lineageos.updater.updates.state.UpdateItemState
import org.lineageos.updater.updates.state.UpdateOperationPhase

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun UpdateItem(
    state: UpdateItemState,
    expanded: Boolean,
    onExpandToggle: (() -> Unit)?,
    onAction: (UpdateAction) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    ForgeUpdateCard(
        tone = ForgeUpdatePresentation.tone(state.operationPhase),
        modifier = modifier,
    ) {
        key(state.downloadId) {
            Preference(model = object : PreferenceModel {
                override val title = state.buildDate
                override val summary = {
                    buildString {
                        append(state.buildVersion)
                        if (state.status.isNotEmpty()) {
                            append(" • ")
                            append(state.status)
                        }
                    }
                }
                override val onClick = onExpandToggle
                override val icon = if (!expanded) {
                    @Composable {
                        if (state.isLocal) {
                            ForgeUpdateGlyph("cg_upd_local", null, Modifier.size(32.dp))
                        } else {
                            ForgeUpdateGlyph("cg_upd_remote", null, Modifier.size(32.dp))
                        }
                    }
                } else {
                    null
                }
            })
        }

        AnimatedVisibility(visible = expanded) {
            Column {
                Column(
                    modifier = Modifier.padding(horizontal = SettingsDimension.itemPaddingStart),
                ) {
                    CompositionLocalProvider(
                        LocalContentColor provides MaterialTheme.colorScheme.onSurfaceVariant,
                        LocalTextStyle provides MaterialTheme.typography.bodySmall,
                    ) {
                        when (val progress = state.progress) {
                            is ProgressState.Determinate -> {
                                ForgeUpdateProgressInfo(progress)

                                ForgeUpdateProgress(progress = progress.percent / 100f,
                                    tone = ForgeUpdatePresentation.tone(state.operationPhase))
                            }

                            ProgressState.Indeterminate -> {
                                ForgeUpdateProgress(progress = null,
                                    tone = ForgeUpdatePresentation.tone(state.operationPhase))
                            }

                            null -> {
                                Text(text = stringResource(R.string.list_update_size, state.fileSize))
                                if (state.androidUpdateInfo.isNotEmpty()) {
                                    Text(text = state.androidUpdateInfo)
                                }
                                if (state.securityUpdate.isNotEmpty()) {
                                    Text(
                                        text = stringResource(
                                            R.string.list_security_update,
                                            state.securityUpdate,
                                        )
                                    )
                                }
                                HorizontalDivider(
                                    modifier = Modifier.padding(
                                        top = SettingsSpace.small1,
                                        bottom = SettingsSpace.extraSmall4,
                                    )
                                )
                                Text(
                                    text = if (state.installNote == R.string.list_major_upgrade_recovery_install) {
                                        stringResource(
                                            state.installNote,
                                            stringResource(R.string.brand_name),
                                        )
                                    } else {
                                        stringResource(state.installNote)
                                    },
                                    style = MaterialTheme.typography.bodySmallEmphasized,
                                )
                            }
                        }
                    }
                }

                ActionBar(
                    buttons = listOfNotNull(
                        state.actions.primary.toActionBarButton(
                            context,
                            onAction,
                            isPrimary = true
                        ),
                        state.actions.secondary?.toActionBarButton(context, onAction),
                    ),
                    menuContent = if (state.actions.overflow.isEmpty()) {
                        null
                    } else {
                        {
                            state.actions.overflow.forEach { action ->
                                MenuItem(
                                    text = action.type.title(context),
                                    enabled = action.enabled,
                                ) {
                                    onAction(action)
                                }
                            }
                        }
                    },
                )
            }
        }
    }
}

private fun UpdateAction.toActionBarButton(
    context: Context,
    onAction: (UpdateAction) -> Unit,
    isPrimary: Boolean = false,
): ActionBarButton = when (type) {
    UpdateActionType.PAUSE_DOWNLOAD,
    UpdateActionType.PAUSE_INSTALL -> ActionBarButton.Icon(
        imageVector = Icons.Outlined.Pause,
        forgeFamily = "cg_upd_pause",
        contentDescription = type.title(context),
        enabled = enabled,
        onClick = { onAction(this) },
    )

    UpdateActionType.RESUME_DOWNLOAD,
    UpdateActionType.RESUME_INSTALL -> ActionBarButton.Icon(
        imageVector = Icons.Outlined.PlayArrow,
        forgeFamily = "cg_upd_resume",
        contentDescription = type.title(context),
        enabled = enabled,
        onClick = { onAction(this) },
    )

    else -> if (isPrimary) {
        ActionBarButton.Tonal(
            text = type.title(context),
            enabled = enabled,
            onClick = { onAction(this) },
        )
    } else {
        ActionBarButton.Outlined(
            text = type.title(context),
            enabled = enabled,
            onClick = { onAction(this) },
        )
    }
}

@UiModePreviews
@Composable
private fun UpdateItemIdleCollapsedPreview() {
    SettingsTheme {
        UpdateItem(
            state = UpdateItemState(
                downloadId = "preview",
                buildDate = "Apr 27",
                buildVersion = "LineageOS 23.2",
                status = "",
                operationPhase = UpdateOperationPhase.IDLE,
                isLocal = false,
                fileSize = "1.1 GB",
                androidUpdateInfo = "Android 16",
                securityUpdate = "Jan 2026",
                installNote = R.string.list_full_install,
                progress = null,
                actions = UpdateActions(
                    primary = UpdateAction(
                        type = UpdateActionType.START_DOWNLOAD,
                    ),
                    overflow = listOf(
                        UpdateAction(
                            type = UpdateActionType.VIEW_DOWNLOADS,
                        ),
                    ),
                ),
            ),
            expanded = false,
            onExpandToggle = {},
            onAction = {},
        )
    }
}

@UiModePreviews
@Composable
private fun UpdateItemIdleExpandedPreview() {
    SettingsTheme {
        UpdateItem(
            state = UpdateItemState(
                downloadId = "preview",
                buildDate = "Apr 27",
                buildVersion = "LineageOS 23.2",
                status = "",
                operationPhase = UpdateOperationPhase.IDLE,
                isLocal = false,
                fileSize = "1.1 GB",
                androidUpdateInfo = "Major Android upgrade",
                securityUpdate = "Jan 2026",
                installNote = R.string.list_major_upgrade_recovery_install,
                progress = null,
                actions = UpdateActions(
                    primary = UpdateAction(
                        type = UpdateActionType.OPEN_GUIDE,
                    ),
                ),
            ),
            expanded = true,
            onExpandToggle = {},
            onAction = {},
        )
    }
}

@UiModePreviews
@Composable
private fun UpdateItemDownloadingPreview() {
    SettingsTheme {
        UpdateItem(
            state = UpdateItemState(
                downloadId = "preview",
                buildDate = "Apr 27",
                buildVersion = "LineageOS 23.2",
                status = "Downloading",
                operationPhase = UpdateOperationPhase.DOWNLOADING,
                isLocal = false,
                fileSize = "1.1 GB",
                androidUpdateInfo = "Android 16",
                securityUpdate = "Jan 2026",
                installNote = R.string.list_full_install,
                progress = ProgressState.Determinate(
                    percent = 65f,
                    downloadedSize = "715 MB of 1.1 GB",
                    eta = "3 min left",
                ),
                actions = UpdateActions(
                    primary = UpdateAction(
                        type = UpdateActionType.PAUSE_DOWNLOAD,
                    ),
                    secondary = UpdateAction(
                        type = UpdateActionType.CANCEL_DOWNLOAD,
                    ),
                    overflow = listOf(
                        UpdateAction(
                            type = UpdateActionType.VIEW_DOWNLOADS,
                        ),
                    ),
                ),
            ),
            expanded = true,
            onExpandToggle = {},
            onAction = {},
        )
    }
}
