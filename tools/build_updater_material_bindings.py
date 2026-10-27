'''Reuse exact steel layers and bind actual updater card/action presentation.'''
from pathlib import Path
import hashlib,json,re,shutil,difflib
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/24-updater'
UP=OUT/'upstream/packages/apps/Updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
PREFIX='app/src/main/java/org/lineageos/updater/'
AYN=ROOT/'iterations/21-native-workflows/native-patch/hardware/ayn/packages/AynParts'
MAG=ROOT/'iterations/23-magnification/native-patch/frameworks/base/packages/SystemUI'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']

COMPOSE='''/*
 * SPDX-FileCopyrightText: 2026 Craftageddon
 * SPDX-License-Identifier: CC0-1.0
 */
package org.lineageos.updater.forge

import android.graphics.Rect
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsHoveredAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
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
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt

private val SteelText = Color(0xFFEEE7D9)
private val ColdSteel = Color(0xFFB5BDC6)
private val Ember = Color(0xFFE56620)
private val ErrorText = Color(0xFFFF8585)

@Composable
private fun frame(family: String, momentary: Boolean): ForgeLayerDrawable {
    val context = LocalContext.current
    val density = LocalDensity.current.density
    return remember(context, family, momentary, density) {
        ForgeLayerDrawable(context, family, momentary)
    }
}

@Composable
private fun insets(drawable: ForgeLayerDrawable): PaddingValues {
    val density = LocalDensity.current
    return remember(drawable, density) {
        val p = Rect()
        drawable.getPadding(p)
        with(density) { PaddingValues(p.left.toDp(), p.top.toDp(), p.right.toDp(), p.bottom.toDp()) }
    }
}

private fun Modifier.steel(
    drawable: ForgeLayerDrawable,
    active: Boolean = false,
    enabled: Boolean = true,
    focused: Boolean = false,
    pressed: Boolean = false,
): Modifier = drawBehind {
    drawable.state = buildList {
        if (enabled) add(android.R.attr.state_enabled)
        if (focused) add(android.R.attr.state_focused)
        if (pressed) add(android.R.attr.state_pressed)
    }.toIntArray()
    drawable.setFeatureActive(active)
    drawable.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
    drawable.draw(drawContext.canvas.nativeCanvas)
}

/** Card activity follows the actual operation phase. Expansion and progress presence do not activate it. */
@Composable
fun ForgeUpdateCard(
    tone: ForgeUpdateTone,
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit,
) {
    val drawable = frame("cg_rf_panel", false)
    val minimum = with(LocalDensity.current) {
        Pair(drawable.intrinsicWidth.toDp(), drawable.intrinsicHeight.toDp())
    }
    val primary = when (tone) {
        ForgeUpdateTone.ACTIVE -> Ember
        ForgeUpdateTone.ERROR -> ErrorText
        ForgeUpdateTone.COLD -> ColdSteel
    }
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = primary,
            onPrimary = Color(0xFF10151B),
            background = Color(0xFF080C11),
            surface = Color(0xFF10151B),
            surfaceBright = Color(0xFF10151B),
            onSurface = SteelText,
            onSurfaceVariant = ColdSteel,
            onBackground = SteelText,
            primaryContainer = Color(0xFF2A211B), onPrimaryContainer = SteelText,
            secondary = ColdSteel, onSecondary = Color(0xFF10151B),
            secondaryContainer = Color(0xFF1B242C), onSecondaryContainer = SteelText,
            tertiary = ColdSteel, onTertiary = Color(0xFF10151B),
            tertiaryContainer = Color(0xFF202A33), onTertiaryContainer = SteelText,
            surfaceVariant = Color(0xFF1B252E),
            outline = Color(0xFF65717D), outlineVariant = Color(0xFF36414D),
            surfaceTint = Color.Transparent, surfaceDim = Color(0xFF080C11),
            surfaceContainerLowest = Color(0xFF0B1015), surfaceContainerLow = Color(0xFF10151B),
            surfaceContainer = Color(0xFF151C23), surfaceContainerHigh = Color(0xFF1A242E),
            surfaceContainerHighest = Color(0xFF202B35),
            error = ErrorText, onError = Color(0xFF10151B),
            errorContainer = Color(0xFF3A1818), onErrorContainer = Color(0xFFFFE1DF),
        ),
        typography = MaterialTheme.typography,
        shapes = MaterialTheme.shapes,
    ) {
        Column(
            modifier = modifier.fillMaxWidth()
                .sizeIn(minWidth = minimum.first, minHeight = minimum.second)
                .steel(drawable, active = tone == ForgeUpdateTone.ACTIVE)
                .padding(insets(drawable)),
            content = content,
        )
    }
}

/** Native click, enabled state, focus, accessibility role and indication are retained. */
@Composable
fun ForgeUpdateButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    outlined: Boolean = false,
    content: @Composable RowScope.() -> Unit,
) {
    val drawable = frame(if (outlined) "cg_rf_field" else "cg_rf_button", true)
    val minimum = with(LocalDensity.current) {
        Pair(maxOf(48.dp, drawable.intrinsicWidth.toDp()), maxOf(48.dp, drawable.intrinsicHeight.toDp()))
    }
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val hovered by interaction.collectIsHoveredAsState()
    Button(
        onClick = onClick, enabled = enabled, interactionSource = interaction,
        modifier = modifier.sizeIn(minWidth = minimum.first, minHeight = minimum.second)
            .steel(drawable, enabled = enabled, focused = focused || hovered, pressed = pressed),
        contentPadding = insets(drawable),
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent, contentColor = SteelText,
            disabledContainerColor = Color.Transparent, disabledContentColor = Color(0xFF8F9BA7),
        ),
        elevation = null, shape = RectangleShape,
        content = content,
    )
}

@Composable
fun ForgeUpdateIconButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    content: @Composable () -> Unit,
) {
    val drawable = frame("cg_rf_button", true)
    val minimum = with(LocalDensity.current) {
        Pair(maxOf(48.dp, drawable.intrinsicWidth.toDp()), maxOf(48.dp, drawable.intrinsicHeight.toDp()))
    }
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val hovered by interaction.collectIsHoveredAsState()
    IconButton(
        onClick = onClick, enabled = enabled, interactionSource = interaction,
        modifier = modifier.sizeIn(minWidth = minimum.first, minHeight = minimum.second)
            .steel(drawable, enabled = enabled, focused = focused || hovered, pressed = pressed),
        content = content,
    )
}

/** Uses the caller's real fraction. Paused/error progress stays steady; no extra clock is introduced. */
@Composable
fun ForgeUpdateProgress(progress: Float?, tone: ForgeUpdateTone) {
    val drawable = frame("cg_upd_rail", false)
    val color = when (tone) {
        ForgeUpdateTone.ACTIVE -> Ember
        ForgeUpdateTone.ERROR -> ErrorText
        ForgeUpdateTone.COLD -> ColdSteel
    }
    Box(
        modifier = Modifier.fillMaxWidth().heightIn(min = 12.dp)
            .steel(drawable, active = tone == ForgeUpdateTone.ACTIVE)
            .padding(insets(drawable)),
        contentAlignment = androidx.compose.ui.Alignment.Center,
    ) {
        val indicator = Modifier.fillMaxWidth().height(4.dp)
        if (progress == null) {
            LinearProgressIndicator(modifier = indicator, color = color, trackColor = Color.Transparent)
        } else {
            LinearProgressIndicator(progress = { progress }, modifier = indicator,
                color = color, trackColor = Color.Transparent)
        }
    }
}
'''


COMPOSE += '''
/** Retains every live value while allowing long English byte/ETA strings to wrap. */
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
fun ForgeUpdateProgressInfo(progress: org.lineageos.updater.updates.state.ProgressState.Determinate) {
    androidx.compose.foundation.layout.FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(4.dp),
        verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(4.dp),
    ) {
        androidx.compose.material3.Text(
            text = progress.percent.toInt().toString() + "%",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.alignByBaseline(),
        )
        if (progress.downloadedSize.isNotEmpty()) {
            androidx.compose.material3.Text(text = " · " + progress.downloadedSize,
                modifier = Modifier.alignByBaseline())
        }
        if (progress.eta.isNotEmpty()) {
            androidx.compose.material3.Text(text = progress.eta, modifier = Modifier.alignByBaseline())
        }
    }
}
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    # Phase preparation must run first. Rebuild this unpublished stage from its known input.
    phase=read_json(OUT/'phase-binding-status.json')
    for name in ['updates/UpdateItem.kt']:
        row=next(r for r in phase['files'] if r['path']==PREFIX+name)
        snapshot=OUT/'source/phase-stage'/row['path']
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        p=PATCH/row['path']
        if sha(p)==row['sha256']:shutil.copy2(p,snapshot)
        assert snapshot.exists() and sha(snapshot)==row['sha256']
        shutil.copy2(snapshot,p)
    aliases=[]
    for density in ['mdpi','hdpi','xhdpi','xxhdpi']:
        for family in ['button','field','panel','rail']:
            for layer in LAYERS:
                source=(MAG/f'res/drawable-{density}/cg_mag_zoom_rail_{layer}.9.png' if family=='rail'
                        else AYN/f'res/drawable-{density}/cg_rf_{family}_{layer}.9.png')
                target=PATCH/f'app/src/main/res/drawable-{density}'/(('cg_upd_rail' if family=='rail' else 'cg_rf_'+family)+'_'+layer+'.9.png')
                assert source.is_file(),source
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
                assert sha(source)==sha(target)
                aliases.append({'source':source.relative_to(ROOT).as_posix(),
                                'target':target.relative_to(OUT).as_posix(),'sha256':sha(source),'unchanged':True})
    master_aliases=[]
    for group,names,base in [
        ('frames',['scalable-button.svg','scalable-field.svg','scalable-panel.svg'],ROOT/'iterations/21-native-workflows'),
        ('rail',['zoom_rail.svg'],ROOT/'iterations/23-magnification')]:
        for name in names:
            src=base/'masters'/name;dest=OUT/'masters'/group/'masters'/name
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
            master_aliases.append({'source':src.relative_to(ROOT).as_posix(),'target':dest.relative_to(OUT).as_posix(),'sha256':sha(src)})
        src=base/'source/steel-material.png';dest=OUT/'masters'/group/'source/steel-material.png'
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        master_aliases.append({'source':src.relative_to(ROOT).as_posix(),'target':dest.relative_to(OUT).as_posix(),'sha256':sha(src)})
    write_json(OUT/'editable-material-aliases.json',{'unchangedSvgMasters':4,'unchangedSourceTextures':2,'files':master_aliases})
    shutil.copy2(ROOT/'iterations/23-magnification/source/LICENSE-APACHE-2.0.txt',OUT/'source/LICENSE-APACHE-2.0.txt')
    java=PATCH/(PREFIX+'forge');java.mkdir(parents=True,exist_ok=True)
    for name in ['ForgeLayerDrawable.java','ForgeStatePolicy.java']:
        original=AYN/'src/org/lineageos/settings/ayn/forge'/name
        text=original.read_text(encoding='utf8').replace('package org.lineageos.settings.ayn.forge;',
                                                     'package org.lineageos.updater.forge;')
        if name=='ForgeLayerDrawable.java':
            needle='    @Override public int getIntrinsicWidth()'
            assert text.count(needle)==1
            text=text.replace(needle,'    @Override public boolean getPadding(Rect padding) { return layers[0].getPadding(padding); }\n'+needle)
        (java/name).write_text(text,encoding='utf8')
    resource='package org.lineageos.updater.forge;\nimport org.lineageos.updater.R;\nfinal class ForgeResources {\n static int[] layers(String family) {\n  switch(family) {\n'
    for family in ['cg_rf_button','cg_rf_field','cg_rf_panel','cg_upd_rail']:
        resource+='   case "'+family+'": return new int[] {'+', '.join('R.drawable.'+family+'_'+l for l in LAYERS)+'};\n'
    resource+='   default: throw new IllegalArgumentException("Unknown Forge family: "+family);\n  }\n }\n}\n'
    (java/'ForgeResources.java').write_text(resource,encoding='utf8')
    (java/'ForgeUpdaterCompose.kt').write_text(COMPOSE,encoding='utf8')
    edits=[]
    def change(name,ops,phase_stage=False):
        path=PREFIX+name
        source=OUT/'source/phase-stage'/path if phase_stage else UP/path
        data=source.read_bytes();text=data.decode('utf8');nl='\r\n' if b'\r\n' in data else '\n';performed=[]
        for before,after,count in ops:
            before=before.replace('\n',nl);after=after.replace('\n',nl)
            assert text.count(before)==count,(name,before,text.count(before),count)
            text=text.replace(before,after,count);performed.append({'before':before,'after':after,'count':count})
        if not phase_stage:
            before='package org.lineageos.updater'
            after='// Craftageddon: steel presentation and wrapping action layout; original callbacks retained.'+nl+before
            assert text.count(before)==1;text=text.replace(before,after,1)
            performed.append({'before':before,'after':after,'count':1})
        dest=PATCH/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(text.encode('utf8'))
        reverse=text
        for e in reversed(performed):
            assert reverse.count(e['after'])==e['count'];reverse=reverse.replace(e['after'],e['before'],e['count'])
        assert reverse.encode('utf8')==data
        edits.append({'path':path,'input':source.relative_to(OUT).as_posix(),'inputSha256':sha(source),
                      'patchedSha256':sha(dest),'operations':performed,'reverseByteParity':True})
    phase_ui=(OUT/'source/phase-stage'/(PREFIX+'updates/UpdateItem.kt')).read_text(encoding='utf8')
    row_start=phase_ui.index('                                Row(\n')
    row_end=phase_ui.index('                                LinearProgressBar(progress = progress.percent / 100f)',row_start)
    progress_row=phase_ui[row_start:row_end]
    change('updates/UpdateItem.kt',[
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.ForgeUpdateCard\nimport org.lineageos.updater.forge.ForgeUpdatePresentation\nimport org.lineageos.updater.forge.ForgeUpdateProgress\nimport org.lineageos.updater.forge.ForgeUpdateProgressInfo\n',1),
        ('    Column(\n        modifier = modifier\n            .fillMaxWidth()\n            .clip(SettingsShape.CornerExtraSmall2)\n            .background(MaterialTheme.colorScheme.surfaceBright)\n    ) {',
         '    ForgeUpdateCard(\n        tone = ForgeUpdatePresentation.tone(state.operationPhase),\n        modifier = modifier,\n    ) {',1),
        ('                                LinearProgressBar(progress = progress.percent / 100f)',
         '                                ForgeUpdateProgress(progress = progress.percent / 100f,\n                                    tone = ForgeUpdatePresentation.tone(state.operationPhase))',1),
        ('                                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())',
         '                                ForgeUpdateProgress(progress = null,\n                                    tone = ForgeUpdatePresentation.tone(state.operationPhase))',1),
        (progress_row,'                                ForgeUpdateProgressInfo(progress)\n\n',1),
    ],True)
    change('updates/button/ActionBar.kt',[
        ('import androidx.compose.foundation.layout.Row\n','import androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.ExperimentalLayoutApi\n',1),
        ('import com.android.settingslib.spa.widget.scaffold.MoreOptionsScope\n','import com.android.settingslib.spa.widget.scaffold.MoreOptionsScope\nimport org.lineageos.updater.forge.ForgeUpdateButton\nimport org.lineageos.updater.forge.ForgeUpdateIconButton\n',1),
        ('@OptIn(ExperimentalMaterial3ExpressiveApi::class)','@OptIn(ExperimentalMaterial3ExpressiveApi::class, ExperimentalLayoutApi::class)',1),
        ('    Row(\n','    FlowRow(\n',1),
        ('        verticalAlignment = Alignment.CenterVertically,\n','        verticalArrangement = Arrangement.spacedBy(SettingsSpace.extraSmall2),\n',1),
        ('is ActionBarButton.Tonal -> FilledTonalButton(','is ActionBarButton.Tonal -> ForgeUpdateButton(',1),
        ('                    shapes = ButtonDefaults.shapes(),\n','                    // Forged housing supplies the shape.\n',2),
        ('is ActionBarButton.Outlined -> OutlinedButton(','is ActionBarButton.Outlined -> ForgeUpdateButton(\n                    outlined = true,',1),
        ('is ActionBarButton.Icon -> FilledIconButton(','is ActionBarButton.Icon -> ForgeUpdateIconButton(',1),
        ('                    shapes = IconButtonDefaults.shapes(),\n','                    // Forged icon housing supplies the shape.\n',1),
        ('            Spacer(Modifier.weight(1f))\n','            // Flow layout keeps the overflow action reachable when labels wrap.\n',1),
    ])
    write_json(OUT/'unchanged-material-reuse.json',{'families':4,'nativePngConfigurations':len(aliases),
        'newDrawings':0,'resources':aliases,'coldAndNeutralMasksRemainSeparate':True})
    write_json(OUT/'owner-material-edits.json',edits)
    # A current combined text patch is distinct from the retained phase-only patch.
    current=[]
    for p in sorted(PATCH.rglob('*')):
        if p.suffix not in {'.java','.kt','.xml'}:continue
        path=p.relative_to(PATCH).as_posix();original=UP/path
        before=original.read_bytes() if original.exists() else b'';after=p.read_bytes()
        if before==after:continue
        current.append({'path':path,'sha256':sha(p),'bytes':len(after)})
    lines=[]
    for r in current:
        path=r['path'];original=UP/path
        old=original.read_bytes().decode('utf8').splitlines(keepends=True) if original.exists() else []
        new=(PATCH/path).read_bytes().decode('utf8').splitlines(keepends=True)
        for line in difflib.unified_diff(old,new,fromfile='a/'+path if original.exists() else '/dev/null',tofile='b/'+path):
            lines.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
    (OUT/'Updater-forge-source.patch').write_bytes(''.join(lines).encode('utf8'))
    write_json(OUT/'current-native-files.json',current)
    write_json(OUT/'material-binding-status.json',{'newDrawings':0,'unchangedNativePngConfigurations':len(aliases),
        'nativeCardUsesActualPhase':True,'cardExpansionDoesNotActivateLight':True,
        'actionCallbacksAndEnabledValuesPreserved':True,'actionBarWraps':True,
        'fullUpdaterWorkflowArtworkComplete':False,'compileAndVisualChecks':'NOT RUN for material stage',
        'nativeExecution':'NOT RUN','wholeGoalComplete':False})
    print(json.dumps({'unchangedNativePngConfigurations':len(aliases),'nativeTextFiles':len(current),
                      'actualPresentationOwnersChangedHere':len(edits),'newDrawings':0,
                      'materialCompileAndVisualChecks':'NOT RUN','workflowComplete':False}))

if __name__=='__main__':main()
