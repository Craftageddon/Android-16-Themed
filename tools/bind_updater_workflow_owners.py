'''Style actual pinned updater owners; preserve their data/actions and source bytes.'''
from pathlib import Path
import hashlib,json,difflib
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/25-updater-workflows'
UP=OUT/'upstream/packages/apps/Updater'
PATCH=OUT/'native-patch/packages/apps/Updater'
BASE=ROOT/'iterations/24-updater/native-patch/packages/apps/Updater'
PRE='app/src/main/java/org/lineageos/updater/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    edits=[]
    def change(name,operations,java=True):
        path=(PRE if java else '')+name
        src=BASE/path if (BASE/path).exists() else UP/path
        original=src.read_bytes();text=original.decode('utf8');nl='\r\n' if b'\r\n' in original else '\n';actual=[]
        for before,after,count in operations:
            before=before.replace('\n',nl);after=after.replace('\n',nl)
            assert text.count(before)==count,(name,before,text.count(before),count)
            text=text.replace(before,after,count);actual.append({'before':before,'after':after,'count':count})
        marker='package org.lineageos.updater' if java else '<LinearLayout'
        notice='// Craftageddon: source-owned steel presentation; original actions/data retained.'+nl if java else '<!-- Craftageddon: wrapping live import label; original operation retained. -->'+nl
        before=marker;after=notice+marker
        assert text.count(before)==1;text=text.replace(before,after,1)
        actual.append({'before':before,'after':after,'count':1})
        dst=PATCH/path;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(text.encode('utf8'))
        reverse=text
        for e in reversed(actual):
            assert reverse.count(e['after'])==e['count'],(name,e['after'])
            reverse=reverse.replace(e['after'],e['before'],e['count'])
        assert reverse.encode('utf8')==original
        edits.append({'path':path,'input':src.relative_to(ROOT).as_posix(),'inputSha256':sha(src),
                      'patchedSha256':sha(dst),'operations':actual,'reverseByteParity':True})
    theme_old='import com.android.settingslib.spa.framework.theme.SettingsTheme\n'
    theme_new='import org.lineageos.updater.forge.ForgeUpdaterTheme as SettingsTheme\n'
    bars_old='        enableEdgeToEdge()\n'
    bars_new='''        enableEdgeToEdge(
            statusBarStyle = androidx.activity.SystemBarStyle.dark(android.graphics.Color.TRANSPARENT),
            navigationBarStyle = androidx.activity.SystemBarStyle.dark(android.graphics.Color.TRANSPARENT),
        )
'''
    change('UpdatesScaffoldActivity.kt',[
        (theme_old,theme_new,1),(bars_old,bars_new,1),
        ('import com.android.settingslib.spa.widget.preference.Preference\n',
         'import org.lineageos.updater.forge.ForgePreference as Preference\n',1)])
    change('preferences/PreferencesActivity.kt',[(theme_old,theme_new,1),(bars_old,bars_new,1)])
    change('preferences/PreferencesScreen.kt',[
        ('import com.android.settingslib.spa.widget.preference.ListPreference\n',
         'import org.lineageos.updater.forge.ForgeListPreference as ListPreference\n',1),
        ('import com.android.settingslib.spa.widget.preference.SwitchPreference\n',
         'import org.lineageos.updater.forge.ForgeSwitchPreference as SwitchPreference\n',1)])
    change('deviceinfo/UpdaterCard.kt',[
        ('import androidx.compose.foundation.layout.Row\n','import androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.ExperimentalLayoutApi\n',1),
        ('@Composable\nfun UpdaterCard(', '@OptIn(ExperimentalLayoutApi::class)\n@Composable\nfun UpdaterCard(',1),
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.ForgeSteelPanel\n',1),
        ('''    Card(
        modifier = modifier.fillMaxWidth(),
        shape = shape,
        colors = CardDefaults.cardColors(
            containerColor = Color.Transparent,
            contentColor = onBrandColor,
        ),
    ) {''','''    ForgeSteelPanel(
        modifier = modifier.fillMaxWidth(),
    ) {''',1),
        ('''                .background(brandColor)
                .updaterHeaderPattern(
                    patternColor = patternColor,
                    sheenColor = sheenColor,
                ),''','''                .background(Color.Transparent), // Native mark/version geometry stays unchanged.''',1),
        ('                Row(\n','                FlowRow(\n',2)])
    actions=UP/(PRE+'deviceinfo/actions/DeviceInfoActionButtons.kt')
    raw=actions.read_text(encoding='utf8');a=raw.index('            .clip(\n');b=raw.index('            .padding(SettingsDimension.itemPaddingAround)',a)
    change('deviceinfo/actions/DeviceInfoActionButtons.kt',[
        ('import androidx.compose.foundation.layout.Row\n','import androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.ExperimentalLayoutApi\n',1),
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.ForgeUpdateButton\n',1),
        ('@Composable\nfun DeviceInfoActionButtons(', '@OptIn(ExperimentalLayoutApi::class)\n@Composable\nfun DeviceInfoActionButtons(',1),
        ('    Row(\n','    FlowRow(\n',1),
        (raw[a:b],'            // Each button retains its own fixed-corner steel housing.\n',1),
        ('        horizontalArrangement = Arrangement.spacedBy(small1),\n',
         '        horizontalArrangement = Arrangement.spacedBy(small1),\n        verticalArrangement = Arrangement.spacedBy(small1),\n',1),
        ('        TextButton(\n','        ForgeUpdateButton(\n            outlined = true,\n',2),
        ('            colors = buttonColors,\n','            // Runtime neutral masks replace only the presentation.\n',2)])
    change('deviceinfo/actions/DeviceInfoTvAction.kt',[
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.forgePanel\n',1),
        ('        modifier = modifier\n            .fillMaxWidth()\n',
         '        modifier = modifier\n            .fillMaxWidth()\n            .forgePanel()\n',1)])
    change('ui/CollapseBar.kt',[
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.forgePanel\n',1),
        ('            .clickable { onExpandedChange(!expanded) }\n',
         '            .clickable { onExpandedChange(!expanded) }\n            .forgePanel()\n',1)])
    check=UP/(PRE+'updatescheck/UpdatesCheck.kt');raw=check.read_text(encoding='utf8')
    before='''        colors = ButtonDefaults.filledTonalButtonColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerHighest,
        ),
'''
    change('updatescheck/UpdatesCheck.kt',[
        ('import org.lineageos.updater.R\n','import org.lineageos.updater.R\nimport org.lineageos.updater.forge.ForgeUpdateButton\nimport org.lineageos.updater.forge.ForgeUpdateIllustration\n',1),
        ('    FilledTonalButton(\n','    ForgeUpdateButton(\n',1),
        (before,'        // The original click and full-width behavior are retained.\n',1),
        ('        Lottie(\n','        ForgeUpdateIllustration(\n',1)])
    change('updates/UpdateZeroStatePreference.kt',[
        ('import com.android.settingslib.spa.framework.theme.SettingsTheme\n',
         'import com.android.settingslib.spa.framework.theme.SettingsTheme\nimport org.lineageos.updater.forge.ForgeUpdateZeroIllustration\n',1),
        ('''        Icon(
            imageVector = Icons.Filled.Verified,
            contentDescription = null,
            modifier = Modifier.size(IconSize),
            tint = colorScheme.primary,
        )''','''        ForgeUpdateZeroIllustration(modifier = Modifier.size(IconSize))''',1)])
    change('updates/action/UpdateActionDialog.kt',[
        ('import com.android.settingslib.spa.widget.dialog.SettingsAlertDialogWithIcon\n',
         'import org.lineageos.updater.forge.ForgeUpdaterAlertDialog as SettingsAlertDialogWithIcon\n',1)])
    change('UpdatesActivity.java',[
        ('import android.app.AlertDialog;\n','import android.app.AlertDialog;\nimport org.lineageos.updater.forge.ForgeDialogStyle;\n',1),
        ('        importDialog.show();\n','        importDialog.show();\n        ForgeDialogStyle.apply(importDialog, true);\n',1),
        ('''            new AlertDialog.Builder(this)
                    .setTitle(R.string.local_update_import)
                    .setMessage(R.string.local_update_import_failure)
                    .setPositiveButton(android.R.string.ok, null)
                    .show();''','''            ForgeDialogStyle.show(new AlertDialog.Builder(this)
                    .setTitle(R.string.local_update_import)
                    .setMessage(R.string.local_update_import_failure)
                    .setPositiveButton(android.R.string.ok, null).create(), false);''',1),
        ('''        new AlertDialog.Builder(this)
                .setTitle(R.string.local_update_import_success_title)
                .setMessage(getString(
                        R.string.local_update_import_success_message,
                        StringUtil.formatBuildDate(this, update.getTimestamp())))
                .setPositiveButton(android.R.string.ok, null)
                .show();''','''        ForgeDialogStyle.show(new AlertDialog.Builder(this)
                .setTitle(R.string.local_update_import_success_title)
                .setMessage(getString(
                        R.string.local_update_import_success_message,
                        StringUtil.formatBuildDate(this, update.getTimestamp())))
                .setPositiveButton(android.R.string.ok, null).create(), false);''',1)])
    change('app/src/main/res/layout/progress_dialog.xml',[
        ('''    <TextView
        android:layout_width="wrap_content"''','''    <TextView
        android:layout_width="0dp"
        android:layout_weight="1"''',1),
        ('        android:layout_gravity="center"\n','        android:layout_gravity="center_vertical"\n',1)],False)
    write_json(OUT/'workflow-owner-edits.json',edits)
    print(json.dumps({'actualSourceOwnersAdapted':len(edits),'reverseByteParity':True,
                      'illustrationAndGlyphImplementationPending':True,'fullWorkflowComplete':False}))
if __name__=='__main__':main()
