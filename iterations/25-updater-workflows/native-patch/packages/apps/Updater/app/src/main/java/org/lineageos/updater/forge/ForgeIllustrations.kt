/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.updater.forge

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.*
import org.lineageos.updater.R
import kotlin.math.roundToInt

data class ForgeGesture(val enabled: Boolean = true, val pressed: Boolean = false, val focused: Boolean = false)
val LocalForgeGesture = staticCompositionLocalOf { ForgeGesture() }

@Composable
fun ForgeUpdateGlyph(family: String, description: String?, modifier: Modifier = Modifier) {
    val gesture = LocalForgeGesture.current
    val d = frame(family, true)
    val semantics = if (description == null) modifier else modifier.semantics { contentDescription = description }
    Box(semantics.drawBehind {
        d.state = buildList {
            if (gesture.enabled) add(android.R.attr.state_enabled)
            if (gesture.pressed) add(android.R.attr.state_pressed)
            if (gesture.focused) add(android.R.attr.state_focused)
        }.toIntArray()
        d.setFeatureActive(false)
        d.setBounds(0,0,size.width.roundToInt(),size.height.roundToInt())
        d.draw(drawContext.canvas.nativeCanvas)
    })
}

@Composable
fun ForgeIllustrationLayers(kind: Int, progress: Float, modifier: Modifier = Modifier) {
    val family = when(kind) {
        ForgeIllustrationMotion.ERROR -> "cg_upd_error"
        ForgeIllustrationMotion.READY -> "cg_upd_ready"
        else -> "cg_upd_scan"
    }
    val d = frame(family, false)
    val context = LocalContext.current
    val density = LocalDensity.current.density
    val marker = remember(context,density) {
        context.getDrawable(R.drawable.cg_upd_scan_motion)!!.mutate().also {
            it.setTint(0xffffd083.toInt())
        }
    }
    Box(modifier.drawBehind {
        val canvas=drawContext.canvas.nativeCanvas
        d.state=intArrayOf(android.R.attr.state_enabled)
        d.setAlertPalette(kind==ForgeIllustrationMotion.ERROR)
        d.setInputStrength(ForgeIllustrationMotion.emission(kind,progress))
        d.setBounds(0,0,size.width.roundToInt(),size.height.roundToInt())
        d.draw(canvas)
        if(kind==ForgeIllustrationMotion.CHECKING) {
            marker.setBounds(0,0,size.width.roundToInt(),size.height.roundToInt())
            marker.alpha=(255*ForgeIllustrationMotion.emission(kind,progress)).roundToInt()
            val saved=canvas.save()
            canvas.rotate(ForgeIllustrationMotion.rotation(kind,progress),size.width/2,size.height/2)
            marker.draw(canvas);canvas.restoreToCount(saved)
        }
    })
}

@Composable
fun ForgeUpdateZeroIllustration(modifier: Modifier = Modifier) {
    ForgeIllustrationLayers(ForgeIllustrationMotion.READY,1f,modifier)
}
