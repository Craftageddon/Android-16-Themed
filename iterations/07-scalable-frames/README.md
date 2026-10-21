# Iteration 07 — stretchable steel resources

Four original SVG frame families (button, field, panel and notification) now have real Android nine-patch layers at mdpi, hdpi, xhdpi and xxhdpi: 80 files representing 20 logical drawables. Cold steel, neutral seam, neutral hot core, neutral focus ring and neutral selection diamond are independent. SVG masters have named editable layers and no labels. Ordinary transparent PNG exports and state snapshots are included in complete-assets.zip.

Only central constant cross-section bands stretch. Decorated corners, copper joints and core accents stay outside those bands. Each nine-patch has Android's one-pixel metadata border and explicit content padding. Do not use that border as visible artwork. Declared minimum sizes preserve fixed caps; smaller icon controls need a separate family. These frames complement the earlier rich fixed-aspect art.

Copy android/res/drawable-* into a standalone test application's resources. Let Android resolve matching density. Load cold and masks as NinePatchDrawable resources, give them identical bounds, tint seam/core with shared tokens and draw live text inside the cold drawable's padding. Draw focus and selection independently so both survive a press. Disabled suppresses every mask. Desktop snapshots are static and do not prove runtime animation.

All 80 density resources compile and link against API 36.1, resolving to 20 logical drawables. Pixel tests cover constant bands, identity resizing, fixed corners, neutral masks, alpha and invalid metadata rejection. This is resource syntax/link and desktop evidence only: physical V3, color-space parity, measured Thor metrics, accessibility and performance remain pending. No SystemUI, ROM or hardware changed.

Calculated decoded-RGBA budget for all five layers of all four families: about 1.09 MiB at mdpi and 9.84 MiB at xxhdpi, excluding platform overhead and render buffers. Resolve only the needed density and cache per family, not per control instance. These are source budgets, not measured memory usage.

Reference: [Android nine-patch documentation](https://developer.android.com/studio/write/draw9patch) and [drawable resources](https://developer.android.com/guide/topics/resources/drawable-resource).
