/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: Apache-2.0
 * Uses the same pinned Updater Lottie timing inputs and iteration roles.
 */
package org.lineageos.updater.forge

import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.airbnb.lottie.compose.*
import org.lineageos.updater.R

@Composable
fun ForgeUpdateIllustration(
    resId: Int, modifier: Modifier = Modifier,
    iterations: Int = LottieConstants.IterateForever,
) {
    if (resId != R.raw.sysupdater_progress && resId != R.raw.sysupdater_error) {
        org.lineageos.updater.ui.Lottie(resId,modifier,iterations)
        return
    }
    key(resId) {
        val lifecycle = LocalLifecycleOwner.current.lifecycle
        val state by lifecycle.currentStateFlow.collectAsState()
        val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(resId))
        val animation by animateLottieCompositionAsState(
            composition, iterations = iterations,
            isPlaying = state.isAtLeast(Lifecycle.State.STARTED),
            restartOnPlay = false,
            ignoreSystemAnimatorScale = false,
            cancellationBehavior = LottieCancellationBehavior.Immediately,
        )
        ForgeIllustrationLayers(
            if(resId==R.raw.sysupdater_error) ForgeIllustrationMotion.ERROR else ForgeIllustrationMotion.CHECKING,
            animation, modifier,
        )
    }
}
