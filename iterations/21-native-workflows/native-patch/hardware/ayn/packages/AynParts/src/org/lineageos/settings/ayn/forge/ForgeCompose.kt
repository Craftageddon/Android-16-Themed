package org.lineageos.settings.ayn.forge

import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
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
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt

@Composable
fun ForgeCalibrationTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFFE56620),
            onPrimary = Color(0xFF10151B),
            background = Color(0xFF080C11),
            surface = Color(0xFF10151B),
            onSurface = Color(0xFFEEE7D9),
            onSurfaceVariant = Color(0xFFB5BDC6),
        ),
        content = content,
    )
}

@Composable
fun Modifier.forgeSteel(
    family: String,
    active: Boolean = false,
    enabled: Boolean = true,
    focused: Boolean = false,
): Modifier {
    val context = LocalContext.current
    val drawable = remember(context, family) { ForgeLayerDrawable(context, family, false) }
    val states = remember(enabled, focused) {
        buildList {
            if (enabled) add(android.R.attr.state_enabled)
            if (focused) add(android.R.attr.state_focused)
        }.toIntArray()
    }
    return drawBehind {
        drawable.state = states
        drawable.setFeatureActive(active)
        drawable.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
        drawable.draw(drawContext.canvas.nativeCanvas)
    }
}

/** Keep Material's click, enabled, keyboard and accessibility behavior; replace presentation only. */
@Composable
fun ForgeButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    outlined: Boolean = false,
    content: @Composable RowScope.() -> Unit,
) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    Button(
        onClick = onClick,
        enabled = enabled,
        interactionSource = interaction,
        modifier = modifier.widthIn(min = if (outlined) 112.dp else 96.dp).heightIn(min = 56.dp).forgeSteel(
            family = if (outlined) "cg_rf_field" else "cg_rf_button",
            active = pressed,
            enabled = enabled,
            focused = focused,
        ),
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent,
            contentColor = Color(0xFFEEE7D9),
            disabledContainerColor = Color.Transparent,
            disabledContentColor = Color(0xFF8F9BA7),
        ),
        elevation = null,
        shape = RectangleShape,
        content = content,
    )
}
