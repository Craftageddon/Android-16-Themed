"""Prepare a byte-pinned AynParts presentation patch; preserve hardware/phase owners."""
from pathlib import Path
import difflib,hashlib,json,shutil,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json

OUT=ROOT/'iterations/21-native-workflows';BASE=OUT/'upstream';PATCH=OUT/'native-patch';PACKAGE='hardware/ayn/packages/AynParts';SOURCE=PACKAGE+'/src/org/lineageos/settings/ayn';AN='{http://schemas.android.com/apk/res/android}';AP='{http://schemas.android.com/apk/res-auto}'

def main():
    assert not (OUT/'complete-assets.zip').exists();receipts={};context=read_json(ROOT/'iterations/20-semantic-review/source/context-manifest.json');indexed=read_json(ROOT/'iterations/20-semantic-review/baseline/resource-files.json');aux=read_json(ROOT/'iterations/20-semantic-review/auxiliary-source-files.json')
    for row in context:
        if row['project']!='hardware/ayn' or not row['path'].startswith('packages/AynParts/'):continue
        receipts[row['project']+'/'+row['path']]={**row,'local':ROOT/'iterations/20-semantic-review'/row['checkpointCopy']}
    for row in indexed+aux:
        if row['project']!='hardware/ayn' or not row['path'].startswith('packages/AynParts/'):continue
        sha=row['gitBlobSha1'];local=ROOT/'iterations/20-semantic-review/source/objects'/sha[:2]/sha[2:];receipts[row['project']+'/'+row['path']]={**row,'local':local,'sha256':hashlib.sha256(local.read_bytes()).hexdigest()}
    saved=[]
    for name,row in receipts.items():
        data=row['local'].read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1']
        for folder in [BASE,PATCH]:target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        saved.append({k:v for k,v in row.items() if k!='local'}|{'baseline':name})
    def replace(name,old,new,count=1):
        p=PATCH/name;text=p.read_text(encoding='utf8');assert text.count(old)==count,(name,old,text.count(old));p.write_text(text.replace(old,new),encoding='utf8')
    replace(PACKAGE+'/Android.bp','srcs: ["src/**/*.kt"],','srcs: ["src/**/*.kt", "src/**/*.java"],')
    for filename in ['joystick/PhaseIntroScreen.kt','joystick/CalibrationPhaseScreen.kt','joystick/TestScreen.kt','joystick/components/ButtonGrid.kt']:
        p=PATCH/SOURCE/filename;t=p.read_text(encoding='utf8');t=t.replace('import androidx.compose.material3.Button\n','').replace('import androidx.compose.material3.OutlinedButton\n','');t=t.replace('import org.lineageos.settings.ayn.R','import org.lineageos.settings.ayn.forge.ForgeButton\nimport org.lineageos.settings.ayn.R') if 'import org.lineageos.settings.ayn.R' in t else t.replace('import androidx.compose.ui.unit.dp','import androidx.compose.ui.unit.dp\nimport org.lineageos.settings.ayn.forge.ForgeButton');t=t.replace('OutlinedButton(', 'ForgeButton(outlined = true, ').replace('Button(', 'ForgeButton(').replace('ForgeForgeButton(', 'ForgeButton(')
        if filename!='joystick/components/ButtonGrid.kt':
            t=t.replace('import androidx.compose.runtime.Composable','import androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll\nimport androidx.compose.runtime.Composable')
            if filename=='joystick/TestScreen.kt':
                t=t.replace('import androidx.compose.foundation.layout.Box\n','').replace('    Box(modifier = Modifier.fillMaxSize().padding(24.dp)) {','    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {').replace('modifier = Modifier.fillMaxSize(),','modifier = Modifier.weight(1f).verticalScroll(rememberScrollState()),').replace('Modifier.align(Alignment.BottomEnd)','Modifier.align(Alignment.End)')
                t=t.replace('import androidx.compose.foundation.layout.Row','import androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.Row');t=t.replace('        Row(\n            modifier = Modifier.align(Alignment.End),','        FlowRow(\n            modifier = Modifier.align(Alignment.End),\n            verticalArrangement = Arrangement.spacedBy(12.dp),')
            else:t=t.replace('Modifier.fillMaxSize().padding(', 'Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(')
        else:
            t=t.replace('import androidx.compose.foundation.layout.Row','import androidx.compose.foundation.layout.FlowRow');t=t.replace('    Row(','    FlowRow(').replace('        horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.Center),','        horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.Center),\n        verticalArrangement = Arrangement.spacedBy(12.dp),')
        p.write_text(t,encoding='utf8')
    activity=PATCH/SOURCE/'joystick/CalibrationActivity.kt';t=activity.read_text(encoding='utf8');start=t.index('    val context = LocalContext.current');t=t[:start]+'''    org.lineageos.settings.ayn.forge.ForgeCalibrationTheme(content)
}
''';t=t.replace('import androidx.compose.foundation.isSystemInDarkTheme\n','').replace('import androidx.compose.material3.dynamicDarkColorScheme\n','').replace('import androidx.compose.material3.dynamicLightColorScheme\n','').replace('import androidx.compose.ui.platform.LocalContext\n','');activity.write_text(t,encoding='utf8')
    stick=PATCH/SOURCE/'joystick/components/StickVisualizer.kt';t=stick.read_text(encoding='utf8');t=t.replace('import androidx.compose.runtime.Composable','''import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.semantics.semantics
import org.lineageos.settings.ayn.R
import org.lineageos.settings.ayn.forge.ForgeLayerDrawable
import kotlin.math.roundToInt''')
    t=t.replace('    Canvas(modifier = modifier.size(120.dp)) {','''    val context = LocalContext.current
    val gate = remember(context) { ForgeLayerDrawable(context, "cg_ayn_gate", false) }
    val dot = remember(context) { ForgeLayerDrawable(context, "cg_ayn_dot", false) }
    val labelText = when (label) {
        "L" -> stringResource(R.string.cg_ayn_left_stick)
        "R" -> stringResource(R.string.cg_ayn_right_stick)
        else -> label
    }
    val position = stringResource(R.string.cg_ayn_stick_position, x, y)
    Canvas(modifier = modifier.size(120.dp).semantics {
        contentDescription = labelText
        stateDescription = position
    }) {''')
    a=t.index('        // Outer circle');b=t.index('        // Crosshair',a);t=t[:a]+'''        // The source56dp boundary remains unchanged; the frame has no static center dot.
        val inputStrength = kotlin.math.sqrt(x * x + y * y).coerceIn(0f, 1f)
        gate.setInputStrength(inputStrength)
        gate.setBounds(0, 0, size.width.roundToInt(), size.height.roundToInt())
        gate.draw(drawContext.canvas.nativeCanvas)

'''+t[b:];t=t.replace('Color.DarkGray','Color(0xFF627482)');t=t.replace('        drawCircle(color = Color.Green, radius = dotRadius, center = Offset(dotX, dotY))','''        dot.setInputStrength(inputStrength)
        dot.setBounds(-10, -10, 10, 10)
        val native = drawContext.canvas.nativeCanvas
        val saved = native.save()
        native.translate(dotX, dotY)
        native.scale(density, density)
        dot.draw(native)
        native.restoreToCount(saved)''');stick.write_text(t,encoding='utf8')
    rgb=PATCH/SOURCE/'preferences/RGBPreference.kt';t=rgb.read_text(encoding='utf8');t=t.replace('import org.lineageos.settings.ayn.R','''import org.lineageos.settings.ayn.R
import org.lineageos.settings.ayn.forge.ForgeLayerDrawable
import org.lineageos.settings.ayn.forge.ForgeRgbThumbDrawable''');needle='        val initialColor = selectedColor';assert needle in t;t=t.replace(needle,'''        view.background = ForgeLayerDrawable(context, "cg_rf_panel", false)
        view.setPadding(0, 0, 0, 0) // The retained child owns the original24dp content padding.
        fun Slider.forgeThumb(channelColor: Int) {
            val thumb = ForgeRgbThumbDrawable(context, channelColor, this)
            setCustomThumbDrawable(thumb)
        }
        redSlider.forgeThumb(Color.rgb(255, 59, 48))
        greenSlider.forgeThumb(Color.rgb(52, 199, 89))
        blueSlider.forgeThumb(Color.rgb(0, 122, 255))
        brightnessSlider.forgeThumb(Color.WHITE)

'''+needle)
    t=t.replace('        AlertDialog.Builder(context)','        val dialog = AlertDialog.Builder(context, R.style.cg_ayn_rgb_dialog)').replace('.setPositiveButton(android.R.string.ok)', '.setPositiveButton(R.string.cg_ayn_ok)').replace('.setNegativeButton(android.R.string.cancel)', '.setNegativeButton(R.string.cg_ayn_cancel)');t=t.replace('            .show()','''            .show()
        dialog.window?.setBackgroundDrawable(ForgeLayerDrawable(context, "cg_rf_panel", false))
        for (which in intArrayOf(AlertDialog.BUTTON_POSITIVE, AlertDialog.BUTTON_NEGATIVE)) {
            dialog.getButton(which).apply {
                background = ForgeLayerDrawable(context, "cg_rf_button", true)
                setTextColor(Color.rgb(238, 231, 217))
                minHeight = (56 * resources.displayMetrics.density).toInt()
                minWidth = (96 * resources.displayMetrics.density).toInt()
                isAllCaps = false
            }
        }''');rgb.write_text(t,encoding='utf8')
    E.register_namespace('android',AN[1:-1]);E.register_namespace('app',AP[1:-1]);layout=PATCH/PACKAGE/'res/layout/dialog_rgb_sliders.xml';root=E.fromstring(layout.read_bytes());assert root.tag=='LinearLayout'
    for n in list(root):
        channel=n.get(AN+'id').split('_')[-1];label=E.Element('TextView',{AN+'layout_width':'match_parent',AN+'layout_height':'wrap_content',AN+'text':'@string/cg_ayn_channel_'+channel,AN+'textColor':'#EEE7D9',AN+'labelFor':n.get(AN+'id').replace('@+id/','@id/')});root.insert(list(root).index(n),label);n.set(AN+'contentDescription','@string/cg_ayn_channel_'+channel);n.set(AN+'minHeight','48dp');n.set(AP+'thumbWidth','36dp');n.set(AP+'haloColor','#40D5E7F2')
    scroll=E.Element('ScrollView',{AN+'layout_width':'match_parent',AN+'layout_height':'wrap_content',AN+'fillViewport':'false'});scroll.append(root);layout.write_bytes(E.tostring(scroll,encoding='utf-8',xml_declaration=True))
    strings=E.Element('resources')
    for key,value in {'left_stick':'Left stick','right_stick':'Right stick','stick_position':'X %1$.3f, Y %2$.3f','channel_red':'Red','channel_green':'Green','channel_blue':'Blue','channel_brightness':'Brightness','ok':'OK','cancel':'Cancel'}.items():E.SubElement(strings,'string',name='cg_ayn_'+key,translatable='false').text=value
    dest=PATCH/PACKAGE/'res/values/cg_forge_strings.xml';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(E.tostring(strings,encoding='utf-8',xml_declaration=True))
    (dest.parent/'cg_forge_dialog.xml').write_text('<resources><style name="cg_ayn_rgb_dialog" parent="android:style/ThemeOverlay.Material.Dark"><item name="android:textColorPrimary">#EEE7D9</item><item name="android:textColorSecondary">#B5BDC6</item><item name="android:colorAccent">#E56620</item></style></resources>\n',encoding='utf8')
    source_strings=dest.parent/'strings.xml';text=source_strings.read_text(encoding='utf8');assert text.count('Next will appear once')==5;text=text.replace('Next will appear once','Next becomes available once').replace('Each step advances once enough data is collected.','Next becomes available when enough data is collected. Choose Next to continue.');source_strings.write_text(text,encoding='utf8')
    families=['cg_ayn_gate','cg_ayn_dot','cg_ayn_rgb_thumb','cg_rf_button','cg_rf_field','cg_rf_panel'];layers=['cold','reflection','spill','seam','core','focus','symbol'];code='package org.lineageos.settings.ayn.forge;\nimport org.lineageos.settings.ayn.R;\n/** Explicit references keep every neutral layer reachable during native resource shrinking. */\nfinal class ForgeResources {\n static int[] layers(String family) {\n  switch(family) {\n'
    for family in families:code+='   case "'+family+'": return new int[] {'+', '.join('R.drawable.'+family+'_'+layer for layer in layers)+'};\n'
    code+='   default: throw new IllegalArgumentException("Unknown Forge family: "+family);\n  }\n }\n}\n';(PATCH/SOURCE/'forge/ForgeResources.java').write_text(code,encoding='utf8')
    write_json(OUT/'upstream-receipts.json',saved)
    changed=[];patch=[]
    for p in sorted(PATCH.rglob('*')):
        if not p.is_file():continue
        name=p.relative_to(PATCH).as_posix();old=BASE/name;data=p.read_bytes()
        if old.exists() and old.read_bytes()==data:continue
        if p.suffix in ['.java','.kt','.xml','.bp']:
            data=data.replace(b'\r\n',b'\n').rstrip(b'\n')+b'\n'
            if old.exists() and b'\r\n' in old.read_bytes():data=data.replace(b'\n',b'\r\n')
            p.write_bytes(data)
        changed.append({'path':name,'kind':'modified' if old.exists() else 'new','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        if p.suffix in ['.png']:continue
        for line in difflib.unified_diff(old.read_bytes().decode('utf8').splitlines(True) if old.exists() else [],data.decode('utf8').splitlines(True),fromfile='a/'+name if old.exists() else '/dev/null',tofile='b/'+name):
            patch.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
    (OUT/'AynParts-forge-source.patch').write_bytes(''.join(patch).encode('utf8'));write_json(OUT/'changed-files.json',changed);print(json.dumps({'preservedSourceRecords':len(saved),'changedOrNewFiles':len(changed),'sourcePatch':'AynParts-forge-source.patch','binaryResources':'Copy the corresponding native-patch/hardware/ayn/packages/AynParts/res/drawable-* files; PNG bytes are hash-listed separately','hardwareAndPhaseStateOwners':'Unmodified; no hardware actions executed'}))

if __name__=='__main__':main()
