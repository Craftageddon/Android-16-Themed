# Authored UI language

The user specified on 22 October 2026 that all text must be English natively. This applies to authored labels, headings, messages, keyboard examples, review previews and new native resources. The default authored locale is **English (en-US)**. Do not introduce demonstration text in other languages.

Keep text editable and native: Android string resources and live text controls, with no translated lettering or labels baked into steel rasters. Iteration 15 provides the approved English label catalog and `native-text/res/values/strings.xml`. Its source builder rejects alphabetic characters outside English ASCII letters; the catalog is also reviewed as English, since a character check alone cannot establish a language.

For native integration, use the English catalog in default `res/values`, declare the authored locale in the application, and verify actual rendered labels against it. Old preview APKs and historical checkpoints remain archived evidence; they do not establish compliance of a future native build. Native preview replacement, owner integration and physical rendering are separate pending work.

Language-neutral key symbols, numbers, punctuation, status glyphs and controller prompts remain valid. Current Forge scenes use English QWERTY, shift/caps, punctuation, email and website keyboard examples. The unpublished non-English draft was superseded before its branch publication.
