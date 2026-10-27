package craftageddon.hostcheck

import org.lineageos.updater.forge.ForgeUpdatePresentation
import org.lineageos.updater.forge.ForgeUpdateTone
import org.lineageos.updater.updates.action.UpdateAction
import org.lineageos.updater.updates.action.UpdateActions
import org.lineageos.updater.updates.action.UpdateActionType
import org.lineageos.updater.updates.state.ProgressState
import org.lineageos.updater.updates.state.UpdateItemState
import org.lineageos.updater.updates.state.UpdateOperationPhase

fun main() {
    val active = setOf("DOWNLOADING", "VERIFYING", "INSTALLING_RECOVERY", "INSTALLING", "FINALIZING")
    val errors = setOf("DOWNLOAD_ERROR", "VERIFICATION_FAILED", "INSTALLATION_FAILED")
    val progressValues = listOf(null, ProgressState.Indeterminate, ProgressState.Determinate(62f, "620 MB of 1 GB", ""))
    var cases = 0
    for (phase in UpdateOperationPhase.entries) {
        val expected = if (phase.name in active) ForgeUpdateTone.ACTIVE else if (phase.name in errors) ForgeUpdateTone.ERROR else ForgeUpdateTone.COLD
        for (progress in progressValues) for (status in listOf("", "Downloading", "Update ready")) for (enabled in listOf(false, true)) {
            val state = UpdateItemState(
                downloadId = "host-fixture", operationPhase = phase, isLocal = false,
                buildDate = "Fixture", buildVersion = "Fixture", status = status,
                fileSize = "1 GB", androidUpdateInfo = "", securityUpdate = "", installNote = 0,
                progress = progress, actions = UpdateActions(UpdateAction(UpdateActionType.START_DOWNLOAD, enabled))
            )
            check(ForgeUpdatePresentation.tone(state.operationPhase) == expected) { "Wrong tone: $phase / $progress / $status / $enabled" }
            if (phase.name == "DOWNLOAD_PAUSED" || phase.name == "INSTALLATION_SUSPENDED") {
                check(ForgeUpdatePresentation.tone(state.operationPhase) == ForgeUpdateTone.COLD)
            }
            cases++
        }
    }
    check(cases == 234)
    println("PASS phases=" + UpdateOperationPhase.entries.size + " stateCombinations=" + cases)
}
