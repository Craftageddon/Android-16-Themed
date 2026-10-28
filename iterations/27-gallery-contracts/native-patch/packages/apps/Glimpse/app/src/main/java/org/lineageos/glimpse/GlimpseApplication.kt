/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.glimpse

import android.app.Application
// Craftageddon: fixed palette is defined by local activity themes.
import org.lineageos.glimpse.repository.MediaRepository

class GlimpseApplication : Application() {
    val mediaRepository by lazy { MediaRepository(applicationContext) }

    override fun onCreate() {
        super.onCreate()

        // Craftageddon: fixed cold-steel palette; media repository remains unchanged.
    }
}
