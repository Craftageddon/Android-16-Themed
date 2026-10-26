/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.ayn.joystick.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.lineageos.settings.ayn.forge.ForgeButton

@Composable
fun ButtonGrid(
    buttons: List<Pair<String, () -> Unit>>,
    modifier: Modifier = Modifier,
    outlined: Set<Int> = emptySet(),
) {
    FlowRow(
        horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterHorizontally),
        modifier = modifier.fillMaxWidth(),
    ) {
        buttons.forEachIndexed { index, (label, onClick) ->
            if (index in outlined) {
                ForgeButton(outlined = true, onClick = onClick) { Text(label) }
            } else {
                ForgeButton(onClick = onClick) { Text(label) }
            }
        }
    }
}
