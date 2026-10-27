'''Bind Gallery presentation to exact original owners; retain reversible byte edits.'''
from pathlib import Path
import hashlib,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse'
A='http://schemas.android.com/apk/res/android';P='http://schemas.android.com/apk/res-auto'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    assert not (OUT/'complete-assets.zip').exists()
    edits=[]
    def change(path,ops):
        raw=(UP/path).read_bytes();nl='\r\n' if b'\r\n' in raw else '\n';text=raw.decode('utf8')
        actual=[]
        for before,after,count in ops:
            before=before.replace('\n',nl);after=after.replace('\n',nl)
            assert text.count(before)==count,(path,before[:90],text.count(before))
            text=text.replace(before,after,count);actual.append({'before':before,'after':after,'count':count})
        dest=PATCH/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(text.encode('utf8'))
        back=text
        for op in reversed(actual):
            assert back.count(op['after'])==op['count'],(path,'reverse',op['after'][:120],back.count(op['after']))
            back=back.replace(op['after'],op['before'],op['count'])
        assert back.encode('utf8')==raw
        edits.append({'path':path,'inputSha256':sha(raw),'patchedSha256':sha(dest.read_bytes()),'operations':actual,'reverseByteParity':True})
    prefix='app/src/main/java/org/lineageos/glimpse/'
    for owner,anchor in [('utils/PermissionsUtils.kt','}.show()'),('SetWallpaperActivity.kt','}.show()')]:
        change(prefix+owner,[
          ('import com.google.android.material.dialog.MaterialAlertDialogBuilder\n','import com.google.android.material.dialog.MaterialAlertDialogBuilder\nimport org.lineageos.glimpse.forge.ForgeGallerySkin\n',1),
          (anchor,anchor+'.also { ForgeGallerySkin.dialog(it) }',1)])
    change(prefix+'GlimpseApplication.kt',[
      ('import com.google.android.material.color.DynamicColors\n','// Craftageddon: fixed palette is defined by local activity themes.\n',1),
      ('        // Observe dynamic colors changes\n        DynamicColors.applyToActivitiesIfAvailable(this)',
       '        // Craftageddon: fixed cold-steel palette; media repository remains unchanged.',1)])
    change(prefix+'ui/recyclerview/ThumbnailAdapter.kt',[
      ('            this.isSelected = isSelected\n','            this.isSelected = isSelected\n            itemView.isSelected = isSelected // Source SelectionTracker value drives only the rim.\n',1)])
    change(prefix+'ui/recyclerview/MediaViewerAdapter.kt',[
      ('import org.lineageos.glimpse.R\n','import org.lineageos.glimpse.R\nimport org.lineageos.glimpse.forge.ForgeGallerySkin\n',1),
      ('            playerControlView.player = player\n','            playerControlView.player = player\n            ForgeGallerySkin.playerControls(playerControlView, player?.isPlaying == true)\n',1),
      ('        init {\n','        init {\n            ForgeGallerySkin.installPlayerControls(playerControlView)\n',1),
      ('            observersJob = itemView.findViewTreeLifecycleOwner()?.lifecycleScope?.launch {\n',
       '            observersJob = itemView.findViewTreeLifecycleOwner()?.lifecycleScope?.launch {\n                launch {\n                    localPlayerViewModel.isPlaying.collectLatest { playing ->\n                        ForgeGallerySkin.playerControls(playerControlView,\n                            playing && playerControlView.player != null)\n                    }\n                }\n',1),
      ('            playerControlView.player = null\n','            playerControlView.player = null\n            ForgeGallerySkin.playerControls(playerControlView, false)\n',1)])
    old_measure='''        appBarLayout.measure(View.MeasureSpec.UNSPECIFIED, View.MeasureSpec.UNSPECIFIED)
        bottomSheetLinearLayout.measure(
            View.MeasureSpec.UNSPECIFIED, View.MeasureSpec.UNSPECIFIED
        )

        viewModel.setSheetsHeight(
            appBarLayout.measuredHeight,
            bottomSheetLinearLayout.measuredHeight,
        )'''
    new_measure='''        // Native layout owns the real constrained widths, wrapped rows and window insets.
        bottomSheetLinearLayout.doOnLayout {
            viewModel.setSheetsHeight(appBarLayout.height, it.height)
        }'''
    change(prefix+'ViewActivity.kt',[
      ('import androidx.core.view.ViewCompat\n','import androidx.core.view.ViewCompat\nimport androidx.core.view.doOnLayout\n',1),
      ('    override fun onCreate(savedInstanceState: Bundle?) {','''    private val forgeSheetLayoutListener = View.OnLayoutChangeListener { view, l, t, r, b, oldL, oldT, oldR, oldB ->
        if (r - l != oldR - oldL || b - t != oldB - oldT) {
            viewModel.setSheetsHeight(appBarLayout.height, view.height)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {''',1),
      ('        // Attach the adapter to the view pager','''        bottomSheetLinearLayout.addOnLayoutChangeListener(forgeSheetLayoutListener)

        // Attach the adapter to the view pager''',1),
      ('    override fun onDestroy() {','''    override fun onDestroy() {
        bottomSheetLinearLayout.removeOnLayoutChangeListener(forgeSheetLayoutListener)''',1),
      (old_measure,new_measure,1),
      ('''                    // Update info button''','''                    favoriteButton.contentDescription = favoriteButton.text

                    // Update info button''',1),
      ('''                    // Trigger a sheets height update''','''                    motionPhotoToggleButton.contentDescription = motionPhotoToggleButton.text

                    // Trigger a sheets height update''',1)])
    change(prefix+'ui/dialogs/MediaInfoBottomSheetDialog.kt',[
      ('        setContentView(R.layout.media_info_bottom_sheet_dialog)\n','''        setContentView(R.layout.media_info_bottom_sheet_dialog)
        // No sample camera/artist data is shown before real EXIF is read.
        artistInfoListItem.isVisible = false
        cameraInfoListItem.isVisible = false
''',1)])
    change(prefix+'utils/MediaDialogsUtils.kt',[
      ('import org.lineageos.glimpse.R\n','import org.lineageos.glimpse.R\nimport org.lineageos.glimpse.forge.ForgeGallerySkin\n',1),
      ('            .show()\n','            .show().also { ForgeGallerySkin.dialog(it) }\n',1),
      ('        show()\n','        ForgeGallerySkin.snackbar(this)\n        show()\n',1)])
    change('app/Android.bp',[
      ('    srcs: ["src/main/java/**/*.kt"],','''    srcs: [
        "src/main/java/**/*.kt",
        "src/main/java/**/*.java",
    ],''',1)])
    # Native photo/video loading, clipping, selected blur/scrim and all actual actions remain intact.
    change('app/src/main/res/layout/thumbnail_view.xml',[
      ('    android:padding="4dp">','    android:padding="4dp"\n    android:foreground="@drawable/cg_gl_media_frame">',1)])
    change('app/src/main/res/layout/album_thumbnail_view.xml',[
      ('    android:padding="12dp">','    android:padding="12dp"\n    android:foreground="@drawable/cg_gl_media_frame">',1)])
    path='app/src/main/res/layout/activity_view.xml'
    change(path,[
      ('    <LinearLayout\n        android:id="@+id/bottomSheetLinearLayout"','    <org.lineageos.glimpse.forge.ForgeActionLayout\n        android:id="@+id/bottomSheetLinearLayout"',1),
      ('    </LinearLayout>','    </org.lineageos.glimpse.forge.ForgeActionLayout>',1)])
    change('app/src/main/res/layout/media_view.xml',[
      ('        app:show_next_button="false"','        app:controller_layout_id="@layout/cg_gl_player_controls"\n        app:show_next_button="false"',1)])
    change('app/src/main/res/layout/list_item.xml',[
      ('    android:paddingVertical="12dp">','    android:paddingVertical="12dp"\n    android:background="@drawable/cg_gl_panel"\n    android:duplicateParentState="true">',1)])
    path='app/src/main/res/layout/media_info_bottom_sheet_dialog.xml'
    source=(UP/path).read_text(encoding='utf8')
    # Preserve IDs and editable callbacks while making full details reachable at large font scale.
    ops=[('    app:cardCornerRadius="16dp"','    app:cardCornerRadius="0dp"',1),
      ('    <LinearLayout\n','''    <androidx.core.widget.NestedScrollView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:fillViewport="false">
    <LinearLayout
''',1),
      ('        android:orientation="vertical">','        android:orientation="vertical"\n        android:background="@drawable/cg_gl_panel">',1),
      ('\n            android:background="?attr/colorSurfaceContainer"\n            android:backgroundTint="?attr/colorSurfaceContainerHighest"',
       '\n            android:background="@android:color/transparent"',1),
      ('                android:background="@android:color/transparent"','                android:background="@drawable/cg_gl_field"\n                android:minHeight="56dp"',1),
      ('</androidx.cardview.widget.CardView>','    </androidx.core.widget.NestedScrollView>\n</androidx.cardview.widget.CardView>',1)]
    for a in ['headlineText','supportingText']:
        count=source.count('app:'+a+'="')
        if count:ops.append(('app:'+a+'="','tools:'+a+'="',count))
    change(path,ops)
    for filename in ['settingslib_switch.xml','settingslib_switch_compat.xml']:
        change('app/src/main/res/layout/'+filename,[
          ('<com.google.android.material.materialswitch.MaterialSwitch','<org.lineageos.glimpse.forge.ForgeMaterialSwitch',1)])
    change('app/src/main/res/xml/root_preferences.xml',[
      ('<SwitchPreferenceCompat','<org.lineageos.glimpse.forge.ForgeSwitchPreference',4),
      ('<SeekBarPreference','<org.lineageos.glimpse.forge.ForgeSeekBarPreference',1),
      ('            app:iconSpaceReserved="false"','            app:singleLineTitle="false"\n            app:iconSpaceReserved="false"',5)])
    # All native phones, wide rails, navigation IDs, grids and fragment hosts retain their layout owners.
    for name in ['fragment_main.xml','fragment_album.xml','activity_main.xml','activity_picker.xml','activity_settings.xml']:
        path='app/src/main/res/layout/'+name
        raw=(UP/path).read_text(encoding='utf8')
        token='    <com.google.android.material.appbar.AppBarLayout'
        if token in raw:
            # Specific first AppBarLayout height line, not every view of this height.
            at=raw.index(token);end=raw.index('>',at)+1;before=raw[at:end]
            after=before.replace('android:fitsSystemWindows="true"','android:fitsSystemWindows="true"\n        android:background="@drawable/cg_gl_panel"')
            if before!=after:change(path,[(before,after,1)])
    path='app/src/main/res/layout-sw600dp/fragment_main.xml';raw=(UP/path).read_text(encoding='utf8')
    change(path,[('        android:fitsSystemWindows="true"','        android:fitsSystemWindows="true"\n        android:background="@drawable/cg_gl_panel"',1),
       ('        app:menuGravity="center"','        android:background="@drawable/cg_gl_panel"\n        app:menuGravity="center"',1)])
    # Native navigation checked state reaches the rich drawables; no whole-icon recoloring.
    path='app/src/main/res/layout/fragment_main.xml'
    # This file already has the app-bar stage above; record a separate hash-bound second stage.
    raw=(PATCH/path).read_bytes();text=raw.decode('utf8');before='        app:menu="@menu/fragment_main_bottom_app_bar"'
    assert text.count(before)==1
    after='        android:background="@drawable/cg_gl_panel"\n        app:itemIconTint="@null"\n'+before
    new=text.replace(before,after)
    (PATCH/path).write_bytes(new.encode('utf8'))
    edits.append({'path':path,'inputSha256':sha(raw),'patchedSha256':sha(new.encode('utf8')),'operations':[{'before':before,'after':after,'count':1}],'reverseByteParity':True,'stage':'navigation'})
    # Scoped overlays from the exact committed dependency, not invented playback controls.
    dep=OUT/'source/media3-ui/original-resources/res'
    overlays=[]
    for name in ['exo_player_control_view','exo_styled_settings_list','exo_styled_settings_list_item','exo_styled_sub_settings_list_item']:
        file=dep/'layout'/(name+'.xml');text=file.read_text(encoding='utf8');before=text
        if name=='exo_player_control_view':
            text=text.replace('<merge xmlns:android="http://schemas.android.com/apk/res/android">','<merge xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto">')
            text=text.replace('<View android:id="@id/exo_progress_placeholder"','<androidx.media3.ui.DefaultTimeBar android:id="@id/exo_progress"')
            text=text.replace('android:layout_height="@dimen/exo_styled_progress_layout_height"','android:layout_height="48dp"\n      app:scrubber_drawable="@drawable/cg_gl_seek_thumb"')
            target='cg_gl_player_controls'
        else:
            text=text.replace('android:background="@color/exo_black_opacity_70"','android:background="@drawable/cg_gl_panel"')
            text=text.replace('android:background="?android:attr/selectableItemBackground"','android:background="@drawable/cg_gl_panel"')
            # Native measurement can wrap English labels in its bounded, scrollable popup.
            if name=='exo_styled_settings_list_item':
                text=text.replace('        android:layout_width="wrap_content"','        android:layout_width="0dp"\n        android:layout_weight="1"',1)
            if name=='exo_styled_sub_settings_list_item':
                marker='        android:id="@+id/exo_text"\n        android:layout_width="wrap_content"'
                text=text.replace(marker,'        android:id="@+id/exo_text"\n        android:layout_width="0dp"\n        android:layout_weight="1"')
            target=name
        dest=PATCH/'app/src/main/res/layout'/(target+'.xml');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf8')
        E.fromstring(dest.read_bytes());overlays.append({'source':file.relative_to(OUT).as_posix(),'sourceSha256':sha(file.read_bytes()),'target':dest.relative_to(PATCH).as_posix(),'patchedSha256':sha(dest.read_bytes()),'retainsNativeIdsAndActions':True})
    # Settings and all three actual activity themes share fixed steel roles.
    palette={'android:colorBackground':'#080c11','colorPrimary':'#e56620','colorOnPrimary':'#120d09','colorPrimaryContainer':'#322216','colorOnPrimaryContainer':'#eee7d9','colorSecondary':'#b5bdc6','colorOnSecondary':'#080c11','colorSecondaryContainer':'#202c37','colorOnSecondaryContainer':'#eee7d9','colorSurface':'#10151b','colorOnSurface':'#eee7d9','colorOnSurfaceVariant':'#b5bdc6','colorSurfaceVariant':'#1b2732','colorSurfaceBright':'#17212a','colorSurfaceContainerLowest':'#080c11','colorSurfaceContainerLow':'#10151b','colorSurfaceContainer':'#10151b','colorSurfaceContainerHigh':'#17212a','colorSurfaceContainerHighest':'#1b2732','colorOutline':'#596571','colorError':'#ff8585','colorOnError':'#240b0c','colorControlActivated':'#e56620','android:textColorPrimary':'#eee7d9','android:textColorSecondary':'#b5bdc6','android:windowLightStatusBar':'false','android:windowLightNavigationBar':'false'}
    items='\n'.join('        <item name="'+k+'">'+v+'</item>' for k,v in palette.items())+'\n'
    changes=[]
    for style in ['Theme.Glimpse','Theme.Glimpse.MediaViewer']:
        parent='Theme.Material3.Dark.NoActionBar'
        before='<style name="'+style+'" parent="'+('Theme.Material3.DayNight.NoActionBar' if style=='Theme.Glimpse' else parent)+'">'
        after='<style name="'+style+'" parent="'+parent+'">\n'+items
        changes.append((before,after,1))
    changes.append(('        <item name="backgroundTint">@android:color/transparent</item>',
                    '        <item name="android:background">@drawable/cg_gl_button</item>\n        <item name="backgroundTint">@null</item>',1))
    change('app/src/main/res/values/themes.xml',changes)
    change('app/src/main/res/values/themes_settingslib.xml',[
      ('<style name="Theme.SettingsLib" parent="Theme.Material3Expressive.DayNight.NoActionBar">',
       '<style name="Theme.SettingsLib" parent="Theme.Material3Expressive.Dark.NoActionBar">\n'+items,1)])
    # Actual viewer sheets remain within their original UI owners.
    for name in ['bg_media_viewer_top_sheet','bg_media_viewer_bottom_sheet']:
        path='app/src/main/res/drawable/'+name+'.xml';original=(UP/path).read_text(encoding='utf8')
        new='<drawable xmlns:app="http://schemas.android.com/apk/res-auto" class="org.lineageos.glimpse.forge.ForgeDrawable" app:cg_forge_family="cg_gl_panel" app:cg_forge_momentary="false"/>\n'
        change(path,[(original,new,1)])
    change('app/src/main/res/layout/activity_set_wallpaper.xml',[
      ('        android:id="@+id/setWallpaperButton"','        android:id="@+id/setWallpaperButton"\n        android:background="@drawable/cg_gl_button"',1)])
    rulepath='app/proguard-rules.pro';source=(UP/rulepath).read_text(encoding='utf8')
    keep='\n# Craftageddon XML-inflated drawable and preference/view constructors.\n-keep class org.lineageos.glimpse.forge.ForgeDrawable { *; }\n'
    for name in ['ForgeActionLayout','ForgeMaterialSwitch','ForgeSeekBarPreference','ForgeSwitchPreference']:
        keep+='-keep class org.lineageos.glimpse.forge.'+name+' { public <init>(android.content.Context, android.util.AttributeSet); }\n'
    change(rulepath,[(source,source+keep,1)])
    values=PATCH/'app/src/main/res/values';values.mkdir(parents=True,exist_ok=True)
    (values/'cg_gallery_colors.xml').write_text('''<resources>
 <color name="cg_gl_ember">#e56620</color><color name="cg_gl_cold">#b5bdc6</color>
 <color name="cg_gl_icon_background">#080c11</color>
</resources>''',encoding='utf8')
    color=PATCH/'app/src/main/res/color';color.mkdir(parents=True,exist_ok=True)
    (color/'cg_gl_progress_color.xml').write_text('''<selector xmlns:android="http://schemas.android.com/apk/res/android">
 <item android:state_activated="true" android:state_enabled="false" android:color="#99e56620"/>
 <item android:state_activated="true" android:color="@color/cg_gl_ember"/>
 <item android:color="@color/cg_gl_cold"/>
</selector>''',encoding='utf8')
    draw=PATCH/'app/src/main/res/drawable'
    (draw/'cg_gl_seek_progress.xml').write_text('''<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
 <item android:id="@android:id/background" android:height="12dp" android:gravity="center_vertical" android:drawable="@drawable/cg_gl_rail"/>
 <item android:id="@android:id/progress" android:height="4dp" android:gravity="center_vertical">
  <clip android:clipOrientation="horizontal" android:gravity="start">
   <shape><corners android:radius="2dp"/><solid android:color="@color/cg_gl_progress_color"/></shape>
  </clip>
 </item>
</layer-list>''',encoding='utf8')
    change(prefix+'SettingsActivity.kt',[
      ('            setDisplayShowHomeEnabled(true)','            setDisplayShowHomeEnabled(true)\n            setHomeAsUpIndicator(R.drawable.ic_back)',1)])
    change('app/src/main/res/layout/set_wallpaper_dialog_item.xml',[
      ('    android:ellipsize="marquee"','    android:background="@drawable/cg_gl_button"',1),
      ('    android:minHeight="?attr/listPreferredItemHeightSmall"','    android:minHeight="56dp"',1)])
    # Native themed-icon mask remains neutral and host-tinted, with the same new photo identity.
    mono='app/src/main/res/drawable/ic_launcher_monochrome.xml'
    original_mono=(UP/mono).read_text(encoding='utf8')
    vector=E.Element('vector',{'xmlns:android':A,'android:width':'108dp','android:height':'108dp','android:viewportWidth':'108','android:viewportHeight':'108'})
    E.SubElement(vector,'path',{'android:pathData':'M24 54 A30 30 0 1 0 84 54 A30 30 0 1 0 24 54','android:strokeColor':'#ffffffff','android:strokeWidth':'1.4','android:fillColor':'#00000000'})
    group=E.SubElement(vector,'group',{'android:translateX':'40','android:translateY':'40','android:scaleX':'1.1666667','android:scaleY':'1.1666667'})
    for element in E.parse(UP/'app/src/main/res/drawable/ic_image.xml').getroot():
        assert element.tag=='path'
        attrs={'android:'+k.rsplit('}',1)[-1]:v for k,v in element.attrib.items()}
        if 'android:fillColor' in attrs:attrs['android:fillColor']='#ffffffff'
        if 'android:strokeColor' in attrs:attrs['android:strokeColor']='#ffffffff'
        E.SubElement(group,'path',attrs)
    change(mono,[(original_mono,E.tostring(vector,encoding='unicode')+'\n',1)])
    # Manifest identity remains intact; only its existing adaptive resource owner changes.
    mip=PATCH/'app/src/main/res/mipmap-anydpi';mip.mkdir(parents=True,exist_ok=True)
    original=(UP/'app/src/main/res/mipmap-anydpi/ic_launcher.xml').read_text(encoding='utf8')
    root=E.fromstring(original)
    foreground=root.find('foreground');background=root.find('background')
    assert foreground is not None and background is not None
    change('app/src/main/res/mipmap-anydpi/ic_launcher.xml',[
      (background.get('{'+A+'}drawable'),'@color/cg_gl_icon_background',1),
      (foreground.get('{'+A+'}drawable'),'@drawable/cg_gl_launcher_foreground',1)])
    (draw/'cg_gl_launcher_foreground.xml').write_text('''<inset xmlns:android="http://schemas.android.com/apk/res/android" android:drawable="@drawable/cg_gl_app_gallery_cold" android:inset="20%"/>''',encoding='utf8')
    write_json(OUT/'gallery-owner-edits.json',edits);write_json(OUT/'dependency-layout-overlays.json',overlays)
    print({'ownerEditStages':len(edits),'actualOwnerFiles':len({r['path'] for r in edits}),'nativeDependencyLayouts':len(overlays),'mediaOperationsExecuted':False})
if __name__=='__main__':main()
