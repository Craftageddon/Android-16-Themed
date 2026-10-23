"""Additional semantic symbols found by the retained-family audit.
Each symbol has deliberate geometry; unknown names reject.
"""
def circle(x,y,r):return f'M{x-r} {y} a{r} {r} 0 1 0 {r*2} 0 a{r} {r} 0 1 0 {-r*2} 0'
def rect(x,y,w,h):return f'M{x} {y} h{w} v{h} h{-w} Z'
GEOMETRY={
 'pin_dot_empty':[(circle(12,12,3),False)],
 'pin_dot_filled':[(circle(12,12,3),True)],
 'phone':[('M5 3 L9 7 L7 11 Q10 16 15 18 L18 15 L22 19 L20 23 Q8 23 2 8 L2 5 Z',False)],
 'mail':[('M2 5 H22 V20 H2 Z M2 6 L12 14 L22 6 M3 19 L9 13 M21 19 L15 13',False)],
 'photo':[('M2 3 H22 V22 H2 Z M3 19 L9 12 L13 16 L17 10 L22 17',False),(circle(8,8,2),False)],
 'filter':[('M2 4 H22 L14 13 V21 L10 18 V13 Z',False)],
 'crop':[('M6 1 V18 H23 M1 6 H18 V23 M9 3 L9 14 H21',False)],
 'draw':[('M3 21 L6 13 L17 2 L22 7 L11 18 Z M6 13 L11 18 M15 4 L20 9 M2 23 H21',False)],
 'enter':[('M21 4 V14 H4 M10 8 L4 14 L10 20',False)],
 'pin':[('M8 2 H16 L15 9 L20 14 H4 L9 9 Z M12 14 V23',False)],
 'undo':[('M9 3 L2 9 L9 15 M3 9 H14 Q24 9 21 19 Q19 23 12 21',False)],
 'redo':[('M15 3 L22 9 L15 15 M21 9 H10 Q0 9 3 19 Q5 23 12 21',False)],
 'visibility':[('M1 12 Q12 -2 23 12 Q12 26 1 12 Z',False),(circle(12,12,4),False)],
 'visibility_off':[('M2 12 Q12 0 22 12 Q17 19 11 20 M6 7 Q13 2 20 9 M3 2 L22 23',False)],
 'select_all':[('M3 7 V3 H7 M17 3 H21 V7 M21 17 V21 H17 M7 21 H3 V17 M7 7 H17 V17 H7 Z',False)],
 'media_previous':[('M4 3 V21 M20 3 L7 12 L20 21 Z',False)],
 'media_next':[('M20 3 V21 M4 3 L17 12 L4 21 Z',False)],
 'gesture_bar':[('M4 12 H20',False)],
 'music_note':[('M9 18 V4 L21 2 V16 M9 8 L21 6',False),(circle(5.5,18.5,3.5),False),(circle(17.5,16.5,3.5),False)],
 'send':[('M2 3 L23 12 L2 21 L6 12 Z M6 12 H23',False)],
 'flashlight_on':[('M7 2 H17 L20 7 L15 13 V22 H9 V13 L4 7 Z M5 7 H19 M11 16 H13',False)],
 'flashlight_off':[('M7 2 H17 L20 7 L15 13 V22 H9 V13 L4 7 Z M5 7 H19 M2 2 L22 22',False)],
 'unlock':[('M5 11 H20 V23 H5 Z M9 11 V6 Q9 0 15 2 Q19 3 19 6 M12 16 V19',False)],
 'sim_download':[('M5 2 H14 L19 7 V22 H3 V4 Z M11 7 V16 M7 12 L11 16 L15 12 M7 19 H15',False)],
 'fingerprint':[('M3 11 Q3 1 12 1 Q22 1 22 12 V16 M6 13 V10 Q6 4 12 4 Q19 4 19 11 V18 M9 17 V10 Q9 7 12 7 Q16 7 16 11 V21 M12 11 V22 M3 15 V19 M6 17 V22',False)],
 'clock':[(circle(12,12,10),False),('M12 5 V12 L17 15',False)],
 'brightness_high':[(circle(12,12,5),False),('M12 1 V3 M12 21 V23 M1 12 H3 M21 12 H23 M3.5 3.5 L5.7 5.7 M18.3 18.3 L20.5 20.5 M3.5 20.5 L5.7 18.3 M18.3 5.7 L20.5 3.5',False)],
 'brightness_low':[(circle(12,12,4),False),('M12 3 V5 M12 19 V21 M3 12 H5 M19 12 H21',False)],
}
APP_GEOMETRY={
 'forge':[('M2 9 H22 L19 12 H14 V17 H18 L20 20 H4 L6 17 H10 V12 H5 Z',False)],
 'pattern_forge':[('M4 3 H14 L21 10 L18 21 H3 Z M7 5 V19 M10 7 H12 M10 11 H15 M10 15 H13 M16 4 L20 8',False)],
 'library':[('M12 5 Q7 1 2 4 V21 Q7 18 12 22 Q17 18 22 21 V4 Q17 1 12 5 Z M12 5 V22 M5 7 L9 8 M5 11 L9 12 M16 8 L19 7 M16 12 L19 11',False)],
 'armory':[('M12 1 L22 5 V12 Q21 20 12 24 Q3 20 2 12 V5 Z M7 7 L17 18 M17 7 L7 18 M5 9 L9 5 M15 20 L19 16 M5 16 L9 20 M15 5 L19 9',False)],
 'emberchat':[('M2 3 H22 V18 H10 L4 23 V18 H2 Z M5 8 H18 M5 12 H14',False)],
 'portal':[(circle(12,12,10),False),(circle(12,12,6),False),('M12 1 V5 M12 19 V23 M1 12 H5 M19 12 H23',False)],
 'workshop':[('M3 3 L7 2 L18 15 L22 17 L21 21 L17 22 L15 18 L2 7 Z M16 3 L21 3 L19 7 L15 8 L7 19 L3 21 L2 18 L12 8 L12 4 Z',False)],
}
def geometry(name):return GEOMETRY[name] if name in GEOMETRY else APP_GEOMETRY[name]
