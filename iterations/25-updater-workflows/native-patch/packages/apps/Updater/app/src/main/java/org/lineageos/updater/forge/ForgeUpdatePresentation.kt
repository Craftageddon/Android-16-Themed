/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: Apache-2.0
 */
package org.lineageos.updater.forge

import org.lineageos.updater.updates.state.UpdateOperationPhase

enum class ForgeUpdateTone { COLD, ACTIVE, ERROR }

/** Phase is domain data. Progress, translated status and enabled buttons do not imply activity. */
object ForgeUpdatePresentation {
    fun tone(phase: UpdateOperationPhase): ForgeUpdateTone = when (phase) {
        UpdateOperationPhase.DOWNLOADING,
        UpdateOperationPhase.VERIFYING,
        UpdateOperationPhase.INSTALLING_RECOVERY,
        UpdateOperationPhase.INSTALLING,
        UpdateOperationPhase.FINALIZING -> ForgeUpdateTone.ACTIVE

        UpdateOperationPhase.DOWNLOAD_ERROR,
        UpdateOperationPhase.VERIFICATION_FAILED,
        UpdateOperationPhase.INSTALLATION_FAILED -> ForgeUpdateTone.ERROR

        UpdateOperationPhase.IDLE,
        UpdateOperationPhase.DOWNLOAD_PAUSED,
        UpdateOperationPhase.VERIFIED,
        UpdateOperationPhase.INSTALLATION_SUSPENDED,
        UpdateOperationPhase.WAITING_FOR_REBOOT -> ForgeUpdateTone.COLD
    }
}
