# Forge22 native contract review

This checkpoint records898 content-backed preservation decisions:639 native reference/state wrappers and259 neutral motion resources, covering919 source variants. It authors no new visual assets and changes no native resource bytes. Referenced artwork remains a separate obligation.

The full goal remains active:10926 original source families and16559 file variants are conserved.9655 family decisions remain OPEN; that is a review count, not9655 confirmed missing drawings. W03 setup, W04 updater, W05 gallery, W06 magnification and W07 boot/charger/recovery adaptations remain unauthored. W01/W02 source/art handoffs were published in Forge21; their full native/device acceptance remains pending. Reuse/app-owner bindings and additional discovered art still need their recorded gates.

## What changed

- `native-contract-review.json.gz` contains exact ordered XML trees, source hashes, state truth tables, level boundaries and dependency candidates for every preserved family/qualifier.
- `semantic-review-delta.json.gz` and `semantic-family-ledger.json.gz` retain the full scope and record only the bounded decisions made here.
- `resource-reference-graph.json.gz` and `resource-declarations.json.gz` supersede the historical20 graph. The old first-res-directory lookup incorrectly indexed core/res/res and resource roots without a literal res component.22 uses the actual resource folder; flag(...) conditions stay inside their resource root and are recorded without choosing the product flag state. Array types, metadata-only declarations, private/+id/short-theme references and scalar reference matching are corrected.
- `vector-motion-contracts.json.gz` audits all254 acquired AVD variants:1149 named targets,2890 standard target/property checks and527 morph animators. All named targets resolve in the retained candidate sets, and all527 explicit endpoint sets have matching command signatures. Six static-base/explicit-endpoint differences are documented; neither geometry is silently rewritten. This is structural evidence, not native interpolation/rendering or drop-in art approval.
-79 pinned supporting interpolator files are acquired and reviewed as unchanged timing data. They do not inflate the original art inventory.
- The real cached AndroidX1.18.0 parser checks504 source paths plus7 tokenizer probes and all130816 unordered/self pairs. The SDK37 check compiles/links eight actual DocumentsUI resources with controlled read-only true/false flags, proving flagged AVDs share base animator/interpolator dependencies. Neither check executes Android or evaluates the installed product.

## Use and reproduce

Restore the signed ZIP from distribution/Restore-Archive.ps1, verify complete-assets.zip.sha256 and the detached signature against the separately pinned public identity. Full local ZIP delivery is also provided. Source/XML and reports are editable; there is no installable application in this checkpoint.

From the repository, run the tools in this order with Python3, the existing JDK, SDK37 and the recorded cached AndroidX dependency: fetch_native_interpolators.py; build_resource_graph_v22.py; review_native_contracts.py; audit_vector_motion_contracts.py; check_morph_paths_androidx.py; check_native_flag_scope.py; prepare_contract_checkpoint.py; verify_native_contract_review.py. Network acquisition reads pinned public files only. Builders refuse to rewrite a packaged checkpoint; use a new checkpoint directory for a new iteration. The SDK tool needs host execution outside the Windows sandbox in this environment; sandboxed aapt2 exits3221225477. Explicit file compilation includes flag directories that --dir scanning omitted.

Cold steel, separate neutral lighting masks, native English text and source-domain activation remain the design rules. This preservation pass introduces no emission/color mapping. Focus is not interpreted as activation. Main and all earlier signed checkpoints are preserved. No install, flashing, hardware action or device settings change occurs.

V1/V2 refer only to this bounded source/contract checkpoint. Full pinned Soong builds, Android/device execution, performance/accessibility acceptance and the final independent whole-goal double-check are NOT RUN. The goal is not complete.
