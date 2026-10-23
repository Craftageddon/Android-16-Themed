"""Explicit semantic reconciliation of the retained catalog.
This decides source roles and points at current artwork; it does not assert
pixel identity with old captures or installed-package compatibility.
"""
from pathlib import Path
import argparse,csv,hashlib,json,re,collections
from forge_completion_geometry import GEOMETRY,APP_GEOMETRY
ROOT=Path(__file__).resolve().parents[1]
FOLDERS={11:'11-forge-symbol-library',12:'12-forge-controls-and-screens',13:'13-forge-android-and-thor-flows',14:'14-forge-atmosphere',15:'15-forge-journey-states',16:'16-forge-motion',17:'17-forge-coverage'}
def target(n,folder,name):return f'iterations/{FOLDERS[n]}/{folder}/{name}'
def sym(name):
 n=17 if name in GEOMETRY else 11
 return [target(n,'masters',name+'__'+k+'.svg') for k in ['compact','detailed']]
def ctrl(name):return [target(12,'masters','control-'+name+'.svg')]
def pilot(name):return [target(12,'masters','pilot-'+name+'.svg')]
def flow(name):return [target(13,'masters',name+'.svg')]
def motion(name):return [target(16,'masters',name+'.svg')]
def screen(name,n=13):return [target(n,'screens',name+'.svg')]
def atmosphere(name):return [target(14,'masters',name+'.svg')]
ALIASES={
 '4g_mobiledata':'network_4g','5g':'network_5g','lte_mobiledata':'network_lte','action_close':'close','airplane':'airplane_on','alarm':'alarm_on','attach_file':'attach','bluetooth':'bluetooth_on','browser':'network','call':'phone','camera':'camera_on','cast':'cast_on','check_circle':'check','content_copy':'copy','content_cut':'cut','content_paste':'paste','data_saver':'mobile_data_saver','data_saver_on':'mobile_data_saver','description':'document','dnd':'dnd_on','file':'document','filter_list':'filter','globe':'network','hidden':'visibility_off','hotspot':'hotspot_on','image':'photo','keyboard_backspace':'back','keyboard_return':'enter','language':'network','location':'location_on','microphone':'microphone_on','mobiledata_off':'mobile_data_off','more_horiz':'more','music':'music_note','network':'network','nfc':'nfc_on','person':'person','photo_camera':'camera_on','public':'network','push_pin':'pin','rotate':'rotation','rotate_90_degrees_ccw':'rotation','screen_rotation':'rotation','shield':'security','sim_card':'sim','sim_card_download':'sim_download','splitscreen':'app_pairs','split':'app_pairs','view_carousel':'recents','visible':'visibility','volume':'audio','volume_high':'audio','volume_low':'audio','volume_media':'audio','volume_mute':'mute','navigation_back':'back','navigation_forward':'forward','navigation_home':'home','navigation_recents':'recents','navigation_gesture':'gesture_bar','navigation_gesture_bar':'gesture_bar','nav_app_drawer':'app_drawer','nav_back':'back','nav_home':'home','nav_recents':'recents','system_lock':'lock','system_power':'power','system_refresh':'sync','system_sleep':'sleep','system_unlock':'unlock','power_lockdown':'lockdown','power_power_off':'power','power_restart':'restart','power_sleep':'sleep','power_screenshot':'screenshot','thor_screen_swap':'screen_swap','display_dual':'app_pairs','media_play':'play','media_pause':'pause','media_stop':'stop','indicator_alert':'warning','stat_sys_download':'download','stat_sys_upload':'upload','ic_audio_alarm':'alarm_on','ic_brightness':'brightness_high','ic_bt_headset_hfp':'headset','ic_gamepad':'controller','ic_lock':'lock','ic_lock_open':'unlock','ic_menu_mylocation':'location_on','ic_menu_rotate':'rotation','ic_qs_bluetooth':'bluetooth_on','ic_qs_dnd':'dnd_on','ic_qs_fan_balance':'performance_balanced','ic_qs_flashlight':'flashlight_on','ic_screenshot':'screenshot','ic_settings':'settings','ic_settings_power':'power','ic_volume':'audio','ic_volume_off':'mute',
 'launcher_apps':'app_drawer','launcher_back':'back','launcher_download':'download','launcher_favorites':'check','launcher_home':'home','launcher_recents':'recents','launcher_search':'search','launcher_system':'system','launcher_tools':'controls',
 'settings_accessibility':'accessibility','settings_apps':'apps','settings_battery':'battery_100','settings_connected_devices':'bluetooth_on','settings_controller':'controller','settings_display':'display','settings_dual_screen':'app_pairs','settings_fan':'fan','settings_network':'network','settings_notifications':'info','settings_performance':'performance','settings_privacy':'privacy','settings_security':'security','settings_sound':'audio','settings_storage':'storage','settings_system':'system'
}
CONTROL_ALIASES={
 'button':'button_primary','button_primary':'button_primary','button_accent':'button_primary','primary_button':'button_primary','button_compact':'button_primary','button_wide':'button_primary','control_button_frame':'button_primary','button_secondary':'button_secondary','button_outline':'button_secondary','button_hover':'button_secondary','checkbox':'check_empty','checkbox_unchecked':'check_empty','checkbox_checked':'check_checked','control_checkbox_empty':'check_empty','control_checkbox_checked':'check_checked','control_radio':'radio_on','control_radio_empty':'radio_off','radio':'radio_on','radio_empty':'radio_off','card':'card','card_default':'card','context_menu_panel':'menu_panel','menu_item_surface':'menu_item','dialog':'dialog','dialog_panel':'dialog','dialog_action_surface':'button_primary','control_dialog_frame':'dialog','compact_sheet':'bottom_sheet','permission_sheet':'bottom_sheet','share_sheet':'bottom_sheet','text_field':'text_field','control_screen_corners':'focus_boundary','focus_ring':'focus_boundary','selection_frame':'focus_boundary','p1_selection_frame':'focus_boundary','settings_row_surface':'settings_row','settings_section_header':'section_header','keyboard_key_letter':'keyboard_letter','keyboard_key_modifier':'keyboard_modifier','keyboard_key_enter':'keyboard_enter','keyboard_spacebar':'keyboard_space','shift':'keyboard_modifier','input_keycap':'keyboard_letter','shoulder_lb':'shoulder_cap','shoulder_rb':'shoulder_cap','button_a':'controller_cap','button_b':'controller_cap','button_x':'controller_cap','button_y':'controller_cap','button_select':'controller_cap','button_start':'controller_cap','menu_divider':'section_header','toggle':'switch_on','toggle_on':'switch_on','toggle_off':'switch_off','toggle_track':'switch_off','toggle_thumb':'switch_on','hint_back':'controller_cap','hint_menu':'controller_cap','hint_select':'controller_cap','launcher_search_field':'search_field','launcher_widget_card':'card','launcher_dock_surface':'card','launcher_app_drawer_panel':'card','launcher_page_indicator':'radio_on','lockscreen_clock_date_plate':'card','lockscreen_shortcut_ring':'icon_button','lockscreen_pin_dot_empty':'radio_off','lockscreen_pin_dot_filled':'radio_on','volume_compact_panel':'card','volume_expanded_panel':'card'
}
FLOW_ALIASES={
 'app_socket':'app_socket','icon_container':'app_socket','p1_icon_container':'app_socket','launcher_adaptive_foreground_frame':'app_socket','launcher_folder':'folder_socket','launcher_folder_frame':'folder_socket','folder':'folder_socket','launcher_icon_badge':'pattern_node','badge_count_3':'pattern_node','recents_card':'task_card','lockscreen_biometric_frame':'biometric_socket','lockscreen_pattern_node':'pattern_node','lockscreen_pin_key':'pin_key','lockscreen_media_card':'media_cell','volume_vertical_rail':'volume_rail','volume_slider_thumb':'volume_rail','ayn_control_row':'mapping_slot','ayn_control_tile':'mapping_slot','ayn_overlay_panel':'mapping_slot','ayn_overlay_tab':'mapping_slot'
}
MOTION_ALIASES={'slider_rail':'slider_rail','slider_thumb':'slider_rail','p1_slider_rail':'slider_rail','p1_slider_thumb':'slider_rail','control_slider_rail':'slider_rail','control_slider_thumb':'slider_rail','input_copy_toolbar':'copy_toolbar','input_selection_handles':'selection_handles','input_long_press':'hold_charge','input_long_press_charge':'hold_charge','loading_ring':'loading_shimmer','control_loading_shell':'loading_shimmer','control_loading_energy':'loading_shimmer','power_menu_panel':'power_actions','clipboard_card':'clipboard_panel','keyboard_panel':'english_keyboard','keyboard':'english_keyboard','dpad':'direction_cap','charging_battery_chassis':'charge_vessel','charging_energy_fill_channel':'charge_vessel','charging_percent_cradle':'charge_vessel'}
REF_NAMES={'apple_touch_icon','favicon','icon','ic_launcher','icon_192','icon_512','maskable_512','app_icon_source','logo_under_1mb','text only.','shield only','chatgpt image may 14, 2026, 10_42_19 am','image_1782831024131'}
def resolve(row):
 original=row['family_candidate'];name=original.replace('-','_');name=re.sub(r'(_default|_master)$','',name);roles=row['roles'];params={};reason='Explicit semantic family matched to current unlabelled artwork.'
 def result(paths,owner='Shared native component',decision='Rebuild material',why=reason):
  return {'decision':decision,'replacementPaths':paths,'parameters':params,'owner':owner,'reason':why}
 if roles=='Audio / font supporting source':return result([],'Audio / font track','Supporting source','Preserve supporting audio/font bytes and licenses; not an independent visual redraw.')
 if 'Candidate current' not in roles and 'Related brand / website reference' in roles:return result([],'Related project','Historical reference','Brand/website source retained outside the Android production visual count.')
 if re.match(r'logo \d+$',original) or original.startswith(('frame_','tl_','annotated_','codex image','chatgpt_image')):return result([],'Historical source archive','Historical reference','Numbered renders, annotations or launcher editor captures retain reference/provenance roles; never cropped into production assets.')
 if name.startswith('motion_battery_fill_'):
  params['fill']=int(name.split('_')[-1])/100;return result(motion('charge_vessel'),'Battery value renderer')
 if name=='motion_battery_shell':return result(motion('charge_vessel'),'Battery value renderer')
 if name=='motion_input_long_press_source':return result(motion('hold_charge'),'Hold-progress renderer')
 if name=='palette':return result(['iterations/12-forge-controls-and-screens/runtime-style.json'],'Current material/light tokens')
 if name=='system_icon_concepts_v1':return result(['iterations/11-forge-symbol-library/components.json'],'Icon catalog','Historical reference','Old concept sheet is reference-only; named current symbols replace its production role.')
 if 'atlas' in name:return result(['iterations/16-forge-motion/reconciliation.json'],'Motion catalog','Historical reference','Old atlases retain reference roles; 114 explicit current recipe bindings replace atlas-cell sampling.')
 if name in ['icon_cleanup_comparison','rc2_phone_cold']:return result([], 'Review archive','Historical reference','A comparison or whole-phone render is retained as evidence rather than a production master.')
 if name=='launcher_adaptive_background':return result(['iterations/17-forge-coverage/android/res/values/colors.xml'],'Adaptive-icon background')
 if name in REF_NAMES or original in REF_NAMES:return result(['iterations/17-forge-coverage/app-targets.json'],'Launcher identity catalog','Historical reference','Ambiguous legacy brand/launcher filenames are reference-only. New explicit authored identities avoid assuming an installed package.')
 for app in [*APP_GEOMETRY,'files','gallery','settings']:
  if name.startswith('tile_'+app) or name.startswith('utility_'+app) or name.startswith(app+'_') and app not in ['settings','gallery'] or (name==app and app not in ['settings','files','gallery']):
   return result([target(17,'masters','app-'+app+'.svg')],'Launcher / authored app identity','Redraw geometry','Explicit authored identity replaces historical background/foreground/monochrome/flattened variants; no package installation is inferred.')
 if name.startswith('pattern_forge'):return result([target(17,'masters','app-pattern_forge.svg')],'Launcher / authored app identity','Redraw geometry')
 if name.startswith('gallery_'):return result(screen('photo-picker'),'Photo picker / gallery composition','Historical reference','Gallery/editor captures are historical composition references, not reusable masters.')
 if name in ['battery_25','battery_75']:
  params['fill']=int(name.split('_')[1])/100;return result(motion('charge_vessel'),'Battery value renderer')
 if name.startswith('progress_') and name.split('_')[-1].isdigit():params['fill']=int(name.split('_')[-1])/100;return result(motion('progress_vessel'),'Progress value renderer')
 if name.startswith('ic_wifi_4_signal_'):name='wifi_'+name[-1]
 if name.startswith('signal_cellular_'):name='cellular_off' if name.endswith('off') else 'cellular_'+re.search(r'_(\d)_bar',name)[1]
 if name in ['indicator_large_on','indicator_small_on','indicator_large_off','indicator_small_off']:
  return result(sym('pin_dot_empty' if name.endswith('off') else 'pin_dot_filled'),'State indicator','Redraw geometry')
 if name in ['lockscreen_pin_dot_empty','lockscreen_pin_dot_filled']:return result(sym(name.replace('lockscreen_','')),'Native secure-input owner','Redraw geometry')
 name=ALIASES.get(name,name)
 if name in GEOMETRY:return result(sym(name),'Semantic icon renderer','Redraw geometry')
 if (ROOT/target(11,'masters',name+'__compact.svg')).is_file():return result(sym(name),'Semantic icon renderer')
 if name in CONTROL_ALIASES:return result(ctrl(CONTROL_ALIASES[name]))
 if name in FLOW_ALIASES:return result(flow(FLOW_ALIASES[name]))
 if name in MOTION_ALIASES:return result(motion(MOTION_ALIASES[name]))
 if name.startswith(('notification','p1_notification','control_notification')):return result([target(12,'masters','scalable-notification.svg')],'Native notification owner')
 if name.startswith(('quick_settings','p1_quick','control_tile')):return result(pilot('quick_tile'),'Native quick-settings owner')
 if name.startswith('qs_'):
  fields=name.split('_');key=fields[1];mapping={'wifi':'wifi_4','bluetooth':'bluetooth_on','brightness':'brightness_high','dnd':'dnd_on','flashlight':'flashlight_on','rotation':'rotation','settings':'settings','screenshot':'screenshot'}
  if key in mapping:
   state='off' if name.endswith('_off') else 'unavailable' if name.endswith('_unavailable') else 'on';params['state']=state;icon=mapping[key]
   if state=='off' and icon in ['bluetooth_on','dnd_on','flashlight_on']:icon=icon[:-2]+'off'
   return result(pilot('quick_tile')+sym(icon),'Native quick-settings owner','Rebuild material','Current tile plus semantic symbol; off/unavailable state resolves through the native state owner, not a glowing flattened bitmap.')
 if name.startswith(('boot_','splash','wordmark')):return result(atmosphere('forge_crest')+['iterations/14-forge-atmosphere/scenes/boot-ready.svg'],'Boot presentation / live English wordmark')
 if name.startswith(('charging_','charge_')):return result(atmosphere('charge_chamber')+motion('charge_vessel'),'Charging presentation / live value owner')
 if name.startswith(('wallpaper','default_wallpaper','external_','dark_clean_background','dark_forge_background')):return result(atmosphere('wallpaper-thor-upper')+atmosphere('wallpaper-thor-lower')+atmosphere('wallpaper-phone'),'Wallpaper / external-display fallback')
 if name.startswith('texture_'):
  return result(['iterations/13-forge-android-and-thor-flows/source/steel-material.png'],'Material system','Historical reference','Current cold steel is canonical. Older bronze/leather/parchment/charcoal textures retain reference roles, rather than becoming additional Android visual families.')
 if name.startswith(('panel_','ayn_')):return result([target(12,'masters','scalable-panel.svg')],'Panel owner')
 if name.startswith(('rune_','transition_')):return result(atmosphere('forge_crest')+['iterations/16-forge-motion/reconciliation.json'],'Decorative structure / motion owner','Historical reference','Old decorative rune and transition fragments are references. Current structural geometry contains no authored non-English lettering.')
 if name.startswith(('upper','lower','phone_','default_home','craft_')) or re.match(r'^\d+[_-]',original):
  choices=[('clipboard','clipboard-history'),('capture','screenshot-editor'),('picker','file-picker'),('permission','permission-camera'),('share','share-sheet'),('keyboard','keyboard-symbols'),('unlock','lock-pin'),('lock','lock-pin'),('volume','volume-output'),('power','power-menu'),('settings','settings-home'),('ayn','thor-profiles'),('drawer','app-drawer'),('library','app-drawer'),('shade','upper-quick-settings'),('quick','upper-quick-settings')]
  for word,scene in choices:
   if word in name:return result(screen(scene,12 if scene=='upper-quick-settings' else 13),'Screen composition / real platform owner','Historical reference','Earlier screen captures/compositions retain reference roles. Named current scenes and later journey states replace their appearance, without claiming those old screenshots are implemented UI.')
  return result(screen('thor-upper-launcher',12),'Launcher / screen composition','Historical reference','Earlier whole-screen render is reference-only; current layered launcher composition replaces its appearance.')
 if name in ['capture_toolbar','picker_panel','menu_panel','input_copy_toolbar']:return result(ctrl('menu_panel'),'Action menu owner')
 if name in ['lockscreen_clock_ring','widget_clock']:return result(sym('clock'),'Clock / live native text owner')
 if name.startswith(('widget_media','widget_')):return result(flow('media_cell'),'Widget content owner')
 if name.startswith('focus_'):return result(ctrl('focus_boundary'),'Interactive focus owner')
 if name.startswith(('phase','source_','bounds_','labels_','before_after','iteration_','reference_','small_size','all_compact','compact_sheet','long_press','representative_','screen_expansion','crop_contact','lighting_lab','preview','states')) or 'Review / composition reference' in roles:return result([],'Review archive','Historical reference','Whole-sheet/runtime/QA/export evidence is historical reference rather than an independent production master.')
 if 'Historical art reference' in roles:return result([],'Historical source archive','Historical reference','Retained historical art has no separately approved current semantic owner. It remains reference-only; no raster crop or stock fallback is counted as a redraw.')
 return result([],'Unassigned','Unresolved','Requires a concrete semantic target before production use; not silently counted as themed.')
def build(out):
 source=ROOT/'iterations/04-core-components/source-register';families=list(csv.DictReader((source/'family-candidates.csv').open(encoding='utf-8-sig')));files=list(csv.DictReader((source/'all-retained-files.csv').open(encoding='utf-8-sig')));results=[];byname={}
 for row in families:
  decision=resolve(row)
  for p in decision['replacementPaths']:assert (ROOT/p).is_file(),(row['family_candidate'],p)
  record={'familyId':row['family_id'],'retainedFamily':row['family_candidate'],'retainedDistinctFiles':int(row['distinct_files']),'previousRoles':row['roles'],**decision,'evidenceScope':'Semantic names and source roles reviewed; current replacement paths checked. Not a per-pixel approval of every archived image or target installation.','nativeIntegrated':False,'deviceVerified':False};results.append(record);byname[row['family_candidate']]=record
 byfile=[]
 for row in files:
  match=byname.get(row['family_candidate']) if row['integrity']!='INVALID' else None;byfile.append({'sha256':row['sha256'],'name':row['name'],'retainedFamily':row['family_candidate'],'familyId':match['familyId'] if match else None,'decision':match['decision'] if match else 'Invalid excluded','replacementPaths':'|'.join(match['replacementPaths']) if match else '', 'integrityEvidence':'Historical iteration-04 inventory: '+row['integrity']})
 (out/'family-dispositions.json').write_text(json.dumps({'sourceCatalogSha256':hashlib.sha256((source/'family-candidates.csv').read_bytes()).hexdigest(),'date':'2026-10-23','families':results},indent=2)+'\n')
 for name,rows in [('family-dispositions.csv',[{k:('|'.join(v) if isinstance(v,list) else json.dumps(v) if isinstance(v,dict) else v) for k,v in r.items()} for r in results]),('retained-file-dispositions.csv',byfile)]:
  with (out/name).open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for row in results for p in row['replacementPaths']};(out/'replacement-source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
 unresolved=[r['retainedFamily'] for r in results if r['decision']=='Unresolved'];report={'date':'2026-10-23','retainedRecords':len(files),'validFamilyGroups':len(families),'decisions':dict(collections.Counter(r['decision'] for r in results)),'unresolvedProductionFamilies':unresolved,'currentReplacementFiles':len(hashes),'method':'Explicit semantic aliases and reviewed source-role dispositions; current path/hash verification. Historical source integrity remains the earlier inventory evidence.','nativeAndInstalledAppAcceptance':'NOT RUN'};(out/'verification/evidence/coverage-reconciliation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
