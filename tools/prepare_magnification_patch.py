"""Exact-owner presentation patch; original native gestures/data paths remain."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, xml.etree.ElementTree as ET
from PIL import Image
from audit_os_resource_coverage import ROOT, read_json, write_json

OUT=ROOT/'iterations/23-magnification'
UP=OUT/'upstream/frameworks/base/packages/SystemUI'
NATIVE=OUT/'native-patch/frameworks/base/packages/SystemUI'
A='{http://schemas.android.com/apk/res/android}'
APP='{http://schemas.android.com/apk/res-auto}'


def original(path): return (UP/path).read_bytes().decode('utf8')


def replace_once(text, old, new):
    assert text.count(old)==1, (old[:100],text.count(old))
    return text.replace(old,new,1)


def save_text(path, text):
    p=NATIVE/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode('utf8'))


def xml_file(path, root, prefix=None):
    text=ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'
    if prefix is not None:
        notice='<!-- Craftageddon modification: Ember Steel assets, responsive English labels and accessible control targets. -->\n'
        text=(prefix+notice).encode('utf8')+text.split(b'?>',1)[1].lstrip(b'\n')
    p=NATIVE/'res'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text)


def main():
    assert not (OUT/'complete-assets.zip').exists()
    changes=[]
    def java(name, edits):
        p=Path('src/com/android/systemui/accessibility')/(name+'.java');before=original(p);after=before
        newline='\r\n' if '\r\n' in before else '\n'
        package='package com.android.systemui.accessibility;'
        edits=[(package,'// Craftageddon modification: Ember Steel presentation and documented accessible control targets.\n'+package)]+edits
        for old,new in edits:after=replace_once(after,old.replace('\n',newline),new.replace('\n',newline))
        save_text(p,after);changes.append({'path':p.as_posix(),'edits':[{'before':a,'after':b} for a,b in edits],
                'upstreamSha256':hashlib.sha256(before.encode()).hexdigest(),'patchedSha256':hashlib.sha256(after.encode()).hexdigest(),
                'nativeLineEndingPreserved':True})
    java('FullscreenMagnificationController',[(
        '.inflate(R.layout.fullscreen_magnification_border, null);',
        '.inflate(R.layout.fullscreen_magnification_border, null);\n            ForgeMagnificationStyle.installFullscreenBorder(mFullscreenBorder, mContext);')])
    window_edits=[(
        'mMirrorBorderView = mMirrorView.findViewById(R.id.magnification_inner_border);',
        'mMirrorBorderView = mMirrorView.findViewById(R.id.magnification_inner_border);\n        mMirrorBorderView.setBackground(ForgeMagnificationStyle.windowBorder(\n                mContext, mEditSizeEnable));'),(
        'mMirrorBorderView.setBackground(mResources.getDrawable(mEditSizeEnable\n                ? R.drawable.accessibility_window_magnification_background_change\n                : R.drawable.accessibility_window_magnification_background));',
        '// Craftageddon border treatment retains the native edit geometry.\n        mMirrorBorderView.setBackground(ForgeMagnificationStyle.windowBorder(\n                mContext, mEditSizeEnable));'),(
        'PorterDuffColorFilter filter = new PorterDuffColorFilter(\n                mContext.getColor(settingsPanelIsShown\n                        ? R.color.magnification_border_color\n                        : R.color.magnification_drag_handle_stroke),\n                PorterDuff.Mode.SRC_ATOP);\n\n        mDragView.setColorFilter(filter);',
        'mDragView.clearColorFilter();\n        mDragView.setActivated(settingsPanelIsShown);'),(
        'return mGestureDetector.onTouch(v, event);',
        'ForgeMagnificationStyle.updateGesturePresentation(v, event);\n            return mGestureDetector.onTouch(v, event);'),(
        'mCloseView.setOnTouchListener(this);',
        'mCloseView.setOnTouchListener(this);\n        // Accessibility click uses the same action as the existing touch close.\n        mCloseView.setOnClickListener(v -> setEditMagnifierSizeMode(false));')]
    window_edits.append((
        'mBottomLeftCornerView.setVisibility(View.GONE);\n        }\n    }\n\n    private boolean changeWindowSize',
        'mBottomLeftCornerView.setVisibility(View.GONE);\n        }\n        ForgeMagnificationStyle.clearHiddenGesturePresentation(mDragView, mCloseView,\n                mTopLeftCornerView, mTopRightCornerView, mBottomLeftCornerView,\n                mBottomRightCornerView);\n    }\n\n    private boolean changeWindowSize'))
    for view,area in [('mDragView','dragArea'),('mTopLeftCornerView','topLeftArea'),('mTopRightCornerView','topRightArea'),('mBottomLeftCornerView','bottomLeftArea'),('mBottomRightCornerView','bottomRightArea'),('mCloseView','closeArea')]:
        window_edits.append((f'touchableRegion.op({area}, Region.Op.UNION);',f'if ({view}.getVisibility() == View.VISIBLE) {{\n            touchableRegion.op({area}, Region.Op.UNION);\n        }}'))
    java('WindowMagnificationController',window_edits)
    java('WindowMagnificationSettings',[(
        'mSettingView.setAccessibilityDelegate(mPanelDelegate);',
        'mSettingView.setAccessibilityDelegate(mPanelDelegate);\n        ForgeMagnificationStyle.applySettings(mSettingView);'),(
        'int widthMeasureSpec = View.MeasureSpec.makeMeasureSpec(',
        'ForgeMagnificationStyle.updatePanelHeader(mSettingView, mParams.width);\n        int widthMeasureSpec = View.MeasureSpec.makeMeasureSpec(')])
    java('MagnificationModeSwitch',[(
        'return R.drawable.ic_open_in_new_window;',
        'return R.drawable.cg_mag_settings_button;')])
    java('SimpleMirrorWindowControl',[(
        'final View view = layoutInflater.inflate(R.layout.magnifier_controllers, null);',
        'final View view = layoutInflater.inflate(R.layout.magnifier_controllers, null);\n        final int target = mContext.getResources().getDimensionPixelSize(\n                R.dimen.cg_mag_min_touch_target);\n        viewSize.set(3 * target, 3 * target);'),(
        'public boolean onTouch(View v, MotionEvent event) {',
        'public boolean onTouch(View v, MotionEvent event) {\n        ForgeMagnificationStyle.updateLegacyGesturePresentation(mControlsView, event);')])
    # Source glyph names are bound by actual content, including the gear in the
    # misleading ic_open_in_new_window layer-list. Its56dp shell remains separate.
    components=read_json(OUT/'components.json')
    shared={'ic_open_in_new_window','ic_add','ic_remove','ic_open_in_full','ic_arrow_top_left_and_bottom_right','ic_arrow_top_right_and_bottom_left'}
    for name in shared:
        stale=NATIVE/'res/drawable'/(name+'.xml')
        assert stale.resolve().is_relative_to(NATIVE.resolve())
        if stale.exists():stale.unlink()  # Earlier unpublished generated aliases only; upstream copies stay intact.
    for r in components:
        native=r.get('nativeResource') if not r.get('sourcePath') else r.get('nativeResource')
        if not r.get('sourcePath'): continue
        source_name=Path(r['sourcePath']).stem
        if source_name=='ic_open_in_new_window':
            doc=ET.Element('layer-list')
            ET.SubElement(doc,'item',{A+'width':'@dimen/magnification_setting_drag_size',A+'height':'@dimen/magnification_setting_drag_size',A+'drawable':'@drawable/cg_mag_control'})
            ET.SubElement(doc,'item',{A+'gravity':'center',A+'width':'36dp',A+'height':'36dp',A+'drawable':'@drawable/cg_mag_settings_gear'})
            xml_file('drawable/cg_mag_settings_button.xml',doc)
            continue
        elif source_name in {'ic_add','ic_remove','ic_open_in_full','ic_arrow_top_left_and_bottom_right','ic_arrow_top_right_and_bottom_left'}:
            # These are shared SystemUI resources. Bind their Forge treatments
            # only to this owner; other consumers still require their review.
            continue
        else:
            doc=ET.Element('layer-list')
            if r.get('sourceAutoMirrored')=='true':doc.set(A+'autoMirrored','true')
            ET.SubElement(doc,'item',{A+'drawable':'@drawable/cg_mag_'+r['id']})
        xml_file('drawable/'+source_name+'.xml',doc)
    mappings={
        'accessibility_magnification_setting_view_bg':'panel',
        'accessibility_magnification_setting_view_image_btn_bg':'control',
        'accessibility_magnification_setting_view_image_btn_layout_bg':'control',
        'accessibility_window_magnification_button_done_bg':'control',
        'accessibility_magnifier_btn_bg':'control',
        'accessibility_window_magnification_drag_corner_background':'corner_handle',
        'accessibility_window_magnification_drag_handle_background':'drag_handle',
        'accessibility_window_magnification_drag_handle_background_change':'drag_handle',
    }
    for name,key in mappings.items():
        if key=='corner_handle':
            doc=ET.Element('inset',{A+'drawable':'@drawable/cg_mag_corner_handle'})
            for edge in ['Left','Right','Top','Bottom']:doc.set(A+'inset'+edge,'@dimen/cg_mag_resize_target_inset')
        else:
            doc=ET.Element('layer-list');ET.SubElement(doc,'item',{A+'drawable':'@drawable/cg_mag_'+key})
        xml_file('drawable/'+name+'.xml',doc)
    # Keep source inset wrappers unchanged. Their17dp inset preserves the70dp
    # drag target and36dp visible housing; actual panel visibility drives activation.
    for name in ['accessibility_window_magnification_drag_handle_background_inset','accessibility_window_magnification_drag_handle_background_change_inset']:
        src=UP/'res/drawable'/(name+'.xml');target=NATIVE/'res/drawable'/src.name;shutil.copy2(src,target)
    path='res/layout/window_magnification_settings_view.xml';before=original(path);root=ET.fromstring(before)
    for n in root.iter():
        if n.tag in {'TextView','Button'}:n.set(A+'textColor','@color/cg_mag_text_state')
        if n.tag in {'Button','ImageButton'}:
            n.set(A+'backgroundTint','@null')
            if n.tag=='ImageButton':n.set(A+'tint','@null')
        if n.get(A+'id')=='@+id/magnifier_full_button':n.set(A+'src','@drawable/cg_mag_fullscreen')
        if n.tag=='Button':
            n.set(A+'minHeight','48dp');n.set(A+'background','@drawable/cg_mag_control')
        if n.get(A+'id')=='@+id/magnifier_done_button':
            n.set(A+'layout_width','match_parent');n.set(A+'layout_height','wrap_content')
            n.set(A+'minHeight','@dimen/magnification_setting_button_done_height')
        if n.tag=='com.google.android.material.materialswitch.MaterialSwitch':
            n.set(A+'minHeight','@dimen/cg_mag_min_touch_target')
            n.set(A+'thumb','@drawable/cg_mag_switch_thumb');n.set(APP+'track','@drawable/cg_mag_switch_track')
            for name in ['thumbTint','trackTint','thumbIcon','thumbIconTint','trackDecoration','trackDecorationTint']:
                n.set(APP+name,'@null')
    xml_file('layout/window_magnification_settings_view.xml',root,before[:before.index('<LinearLayout')])
    path='res/layout/window_magnifier_view.xml';before=original(path);root=ET.fromstring(before)
    for n in root.iter():
        if n.get(A+'src')=='@drawable/ic_arrow_top_left_and_bottom_right':n.set(A+'src','@drawable/cg_mag_resize_a')
        if n.get(A+'src')=='@drawable/ic_arrow_top_right_and_bottom_left':n.set(A+'src','@drawable/cg_mag_resize_b')
        if n.get(A+'id') in {'@+id/top_left_corner','@+id/top_right_corner','@+id/bottom_left_corner','@+id/bottom_right_corner'}:
            n.set(A+'layout_width','@dimen/cg_mag_min_touch_target');n.set(A+'layout_height','@dimen/cg_mag_min_touch_target');n.set(A+'layout_margin','0dp')
        if n.get(A+'id')=='@+id/close_button':
            n.set(A+'layout_width','48dp');n.set(A+'layout_height','48dp');n.set(A+'focusable','true')
            n.set(A+'contentDescription','@string/accessibility_magnification_done');n.set(A+'backgroundTint','@null')
    xml_file('layout/window_magnifier_view.xml',root,before[:before.index('<FrameLayout')])
    path='res/layout/magnifier_controllers.xml';before=original(path);root=ET.fromstring(before)
    root.set(A+'layout_width','match_parent');root.set(A+'layout_height','match_parent')
    for n in root.iter():
        if n.tag=='RelativeLayout' or n.get(A+'id')=='@+id/controller':
            n.set(A+'layout_width','match_parent');n.set(A+'layout_height','match_parent')
        if n.get(A+'id') in {'@+id/left_control','@+id/up_control','@+id/right_control','@+id/down_control'}:
            n.set(A+'layout_width','@dimen/cg_mag_min_touch_target');n.set(A+'layout_height','@dimen/cg_mag_min_touch_target')
    xml_file('layout/magnifier_controllers.xml',root,before[:before.index('<FrameLayout')])
    progress=ET.Element('layer-list',{A+'paddingMode':'stack'})
    ET.SubElement(progress,'item',{A+'id':'@android:id/background',A+'drawable':'@drawable/cg_mag_zoom_rail'})
    for kind,color in [('secondaryProgress','#44515e'),('progress','@color/cg_mag_cold_progress')]:
        item=ET.SubElement(progress,'item',{A+'id':'@android:id/'+kind});clip=ET.SubElement(item,'clip',{A+'clipOrientation':'horizontal',A+'gravity':'start'})
        inset=ET.SubElement(clip,'inset',{A+'insetTop':'5dp',A+'insetBottom':'5dp',A+'insetLeft':'3dp',A+'insetRight':'3dp'})
        shape=ET.SubElement(inset,'shape',{A+'shape':'rectangle'});ET.SubElement(shape,'solid',{A+'color':color});ET.SubElement(shape,'corners',{A+'radius':'1dp'})
    xml_file('drawable/cg_mag_zoom_progress.xml',progress)
    source=OUT/'source/steel-material.png';im=Image.open(source).convert('RGBA');im=im.resize((76,76),Image.Resampling.LANCZOS)
    target=NATIVE/'res/drawable-nodpi/cg_mag_steel_material.png';target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
    write_json(OUT/'owner-presentation-edits.json',changes)
    all_changes=[];patch=[]
    for p in sorted(NATIVE.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(NATIVE);old=UP/rel;data=p.read_bytes()
        if old.exists() and old.read_bytes()==data:continue
        all_changes.append({'path':rel.as_posix(),'new':not old.exists(),'sourceSha256':hashlib.sha256(old.read_bytes()).hexdigest() if old.exists() else None,'sha256':hashlib.sha256(data).hexdigest(),'binary':p.suffix=='.png'})
        if p.suffix!='.png':
            before=old.read_bytes().decode('utf8').splitlines(keepends=True) if old.exists() else []
            after=data.decode('utf8').splitlines(keepends=True)
            for line in difflib.unified_diff(before,after,fromfile='a/'+rel.as_posix() if old.exists() else '/dev/null',tofile='b/'+rel.as_posix()):
                patch.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
    (OUT/'SystemUI-magnification-forge.patch').write_bytes(''.join(patch).encode('utf8'))
    write_json(OUT/'changed-files.json',all_changes)
    print(json.dumps({'changedOrNewFiles':len(all_changes),'actualOwnersPatched':len(changes),'drawings':len(components),'fullSystemUiBuild':'NOT RUN'}))


if __name__=='__main__':main()
