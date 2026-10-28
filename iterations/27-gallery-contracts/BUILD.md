# Reproduce the bounded source checks

Use the repository-root tools with the same pinned official manifest and saved
Glimpse source. The exact SDK/library/compiler/source acquisition receipts under
source identify revisions, URLs, Git objects and SHA256; downloaded SDK/compiler
binaries and native dependency sources stay in the ignored local build cache.
Original committed app dependencies and extracted Media3 source retain licenses.

Run the following tools with Python3.12 on the existing Windows/JDK21 toolchain,
in order. Paths to Android SDK/JDK are explicit inside the tools and may need
local adjustment on a different machine:

1. resolve_gallery_native_dependencies.py
2. fetch_gallery_native_compiler.py
3. verify_gallery_native_toolchain.py
4. fetch_gallery_native_source_inputs.py
5. compile_gallery_native_dependencies.py
6. link_gallery_complete_resources.py
7. generate_gallery_real_resource_namespaces.py
8. compile_gallery_complete_owners.py
9. test_gallery_compiled_policy.py
10. verify_gallery_alias_contracts.py
11. review_gallery_complete_contracts.py
12. verify_gallery_contract_checkpoint.py

The exact native listenablefuture binary is identified in
source/native-listener-interface.json; it must exist at its hash-verified cache
path before complete-owner compilation. It is not replaced by an invented
interface. The saved native-build-contracts sources document dependency ordering.
Both actual Material providers in the native graph are retained.

Rendering additionally uses the existing local Pillow/resvg environment via
CRAFTAGEDDON_RENDERLIB. render_gallery_contracts_review.py generates English
editable desktop specimens; it does not execute Android. Several scripts refuse
to modify a checkpoint after complete-assets.zip exists. Reproduce in a new
review copy, preserving signed checkpoints.

Earlier failed host/device compiler setup attempts are retained as diagnostic
history. The final native-dependency-compilation.json and
complete-owner-compilation.json report the successful invocations and source
hashes. No Gradle plugin script, downloaded project script, emulator or device
command was executed. These checks do not substitute for official Soong/dex/R8
or native/device acceptance.
