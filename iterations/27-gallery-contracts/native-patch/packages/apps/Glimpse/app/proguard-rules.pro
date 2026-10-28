# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile

# Craftageddon XML-inflated drawable and preference/view constructors.
-keep class org.lineageos.glimpse.forge.ForgeDrawable { *; }
-keep class org.lineageos.glimpse.forge.ForgeActionLayout { public <init>(android.content.Context, android.util.AttributeSet); }
-keep class org.lineageos.glimpse.forge.ForgeMaterialSwitch { public <init>(android.content.Context, android.util.AttributeSet); }
-keep class org.lineageos.glimpse.forge.ForgeSeekBarPreference { public <init>(android.content.Context, android.util.AttributeSet); }
-keep class org.lineageos.glimpse.forge.ForgeSwitchPreference { public <init>(android.content.Context, android.util.AttributeSet); }
