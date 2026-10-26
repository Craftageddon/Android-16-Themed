"""Deliberate geometry for the confirmed source gaps; no unknown-name fallback."""
import math
from forge_completion_geometry import circle,rect

def star(fill=False):
    points=[]
    for i in range(10):
        radius=10 if i%2==0 else 4.6;angle=-math.pi/2+i*math.pi/5;points.append((12+radius*math.cos(angle),12+radius*math.sin(angle)))
    return [('M'+' L'.join(f'{x:.4f} {y:.4f}' for x,y in points)+' Z',fill)]

GEOMETRY={
 'night_light':[('M20.7 16.5 A10.3 10.3 0 1 1 8.3 2 A8.2 8.2 0 0 0 20.7 16.5 Z',True)],
 'dark_theme':[(circle(12,12,10),False),('M12 2 A10 10 0 0 1 12 22 Z',True)],
 'color_inversion':[('M12 2 C9 6 3 10 3 15 C3 24 21 24 21 15 C21 10 15 6 12 2 Z',False),('M12 4 C9 8 4 11 4 15 C4 20 8 22 12 22 Z',True)],
 'color_correction':[('M14 2 L22 10 L18 14 L15 11 L8 18 L3 20 L4 15 L11 8 L8 5 Z M11 8 L15 11 M4 15 L8 18',False)],
 'live_captions':[(rect(2,4,20,16),False),('M5 9 H8 M11 9 H19 M5 14 H13 M16 14 H19',False)],
 'live_captions_off':[(rect(2,4,20,16),False),('M5 9 H8 M11 9 H19 M5 14 H13 M16 14 H19 M2 1 L22 23',False)],
 'hearing_devices':[('M5 10 Q5 1 13 1 Q22 1 22 10 Q22 15 17 18 Q15 19 15 21 Q14 24 10 22 L6 18 M9 11 Q9 5 14 5 Q18 5 18 10 Q18 13 14 15 L12 18',False)],
 'qr_scanner':[('M1.5 7 V1.5 H7 M17 1.5 H22.5 V7 M22.5 17 V22.5 H17 M7 22.5 H1.5 V17',False),(rect(5,5,4.5,4.5),False),(rect(14.5,5,4.5,4.5),False),(rect(5,14.5,4.5,4.5),False),('M14 14 H17 V17 H20 M14 17 V20 H17 M20 14 V16 M19 19 H21',False)],
 'ethernet':[('M3 2 H21 V16 H16 V22 H8 V16 H3 Z M7 6 V11 M10 6 V11 M14 6 V11 M17 6 V11 M8 16 H16',False)],
 'work_profile':[('M8 6 V2 H16 V6 M2 6 H22 V22 H2 Z M2 11 Q12 16 22 11 M10 12 H14 V16 H10 Z',False)],
 'work_profile_paused':[('M8 6 V2 H16 V6 M2 6 H22 V22 H2 Z M2 11 H22 M9 15 V19 M15 15 V19',False)],
 'sensors_disabled':[('M1 13 H6 L9 4 L12 21 L15 7 L18 13 H23 M2 2 L22 22',False)],
 'wallet':[('M3 6 V2 H19 V6 M3 6 H22 V22 H3 Z M16 11 H23 V17 H16 Z',False),(circle(19,14,0.8),True)],
 'keyboard_backlight':[('M2 11 H22 V22 H2 Z M6 15 H8 M11 15 H13 M16 15 H18 M6 18 H18 M12 1 V6 M4 3 L7 7 M20 3 L17 7 M1 7 H4 M20 7 H23',False)],
 'printing':[('M6 9 V2 H18 V9 M6 20 H2 V9 H22 V20 H18 M6 15 H18 V23 H6 Z M17 12 H19 M9 18 H15',False)],
 'favorite':star(True),
 'favorite_outline':star(False),
}

DETAIL_WIDTH={'qr_scanner':1.35,'keyboard_backlight':1.8,'printing':1.85,'live_captions':1.9,'live_captions_off':1.9,'work_profile':2.0,'work_profile_paused':2.0,'wallet':1.9}
ALIASES={'extra_dim':('17-forge-coverage','brightness_low'),'stylus':('11-forge-symbol-library','edit')}
LABELS={'extra_dim':'Extra dim','night_light':'Night light','dark_theme':'Dark theme','color_inversion':'Color inversion','color_correction':'Color correction','live_captions':'Live captions','live_captions_off':'Captions off','hearing_devices':'Hearing devices','qr_scanner':'QR code scanner','ethernet':'Ethernet','work_profile':'Work profile','work_profile_paused':'Work profile paused','sensors_disabled':'Sensors off mode','wallet':'Wallet','keyboard_backlight':'Keyboard backlight','printing':'Printing','stylus':'Stylus','favorite':'Favorite','favorite_outline':'Not a favorite'}
