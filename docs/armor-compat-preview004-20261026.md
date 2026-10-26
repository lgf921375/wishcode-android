# WishCode V0.5 Preview 004 ArmorCompat · 2026-10-26

## Goal and unchanged baseline
- Starting SHA: 48bd3b0446543698512957e93b8eadf04f0a15f5 (Preview 003 NoGLM).
- Branch: work/wishcode-armor-compat-001-20261026. Main and all DNF, Godot and Legend repositories untouched.
- DSH/DSHA upstream source remains v0.2.1-rc.2 with SHA256 ef134fe8713bfa4d6cf3bdea883be1591246d4b78ace16bd924f6d739188425a.
- No new GLM components, separate HTML renderer, automatic plugin installation or elevated permissions.
- Builds remain workflow_dispatch only, with concurrency; do not retry automatically.

## Specific compatibility diagnosis
- Reported Android tool error: "loaded skill source must be a string" while loading armor-playbook.
- Upstream DSH skill registry's SkillDefinition requires a string source and runtime contributions normally supply source metadata. The third-party plugin's lib/skills.js lacks source in the armor-playbook registration object.
- Minimal opt-in fix: insert source: "runtime" beside name and description, preserving all other plugin files. This is a source-level compatibility fix; runtime success has NOT been established.
- The AI's "硬拒 0 / 软拒 0" narrative is NOT a genuine /armor status output. Genuine output begins "purge-flash 状态" and enumerates the configured layers.

## Pinned third-party source and packaging
- Repository: jadezane6634-ops/dsh-purge-flash
- Version: 1.4.0; upstream commit: 636059f8002b060fb4dca1c1b47c02e1ef2a2f31
- Verified before patch via Git blob SHA-1:
  - lib/skills.js 5138d8d067c81a49abe431fd9489cc7d4b357eb0
  - package.json 616861cf8777a758fcc2a9fb4083a218879cc164
  - cordis.patch.yml 8a00b5154b9954bf884b928068c36107a04e1aa7
- scripts/prepare_purge_flash.py refuses symlink, traversal, oversized source, unexpected manifest/anchors.
- Build creates app/src/main/assets/wishcode/dsh-purge-flash-v1.4.0-compat.tgz.
- The APK **contains** a manually exportable plugin archive, but the plugin is not preinstalled or enabled. The archive is also published separately in the Actions artifact.
- No claim of full third-party security audit; this plugin can change prompts, provider payloads and store raw session transcripts. Use test sessions without secrets.

## Independent APK identity and outputs
- Application ID: app.wishcode.harnessmobile.v05trial4
- versionCode: 194
- versionName: 0.5-preview-004-armorcompat-dsh0.2.1-rc.2
- APK: WishCode-v0.5-preview-004-armorcompat-no-glm-arm64-debug.apk
- Actions artifact: WishCode-V0.5-Preview-004-ArmorCompat-Android-APK
- Expected extra files: armor-compat-report.json, dsh-purge-flash-v1.4.0-wishcode-compat.tgz, ARMOR-COMPAT-SHA256.txt, signature-report.txt, package-version-report.txt, SHA256SUMS.txt.
- IMPORTANT: separate application ID means previous API keys, profile, plugin install and project workspaces are NOT migrated. Keep previous installed APK; never uninstall it just to test this version.

## Build and device acceptance checklist
1. Inspect workflow: Actions > build-custom-apk.yml; manually select the exact branch work/wishcode-armor-compat-001-20261026.
2. Check no job already running and that the workflow remains workflow_dispatch only. Start exactly ONE build. Do not retry on failure without inspecting logs.
3. Require Python unit tests (including test_armor_compat.py), source SHA verification, Node JS syntax check, Gradle compile and APK signature/package checks to pass.
4. Download **Artifacts** only from a green completed run. Artifacts ZIP must be unpacked to obtain an .apk.
5. Install the independent Preview 004 APK alongside the old one, not over it.
6. Tap workbench title > "Flash 破甲插件 · 修复包（手动导入）" > "导出兼容包"; save the archive to a chosen accessible folder.
7. Tap "插件管理", select ZIP/TAR.GZ import; inspect package name dsh-purge-flash and version 1.4.0; explicitly authorize installation.
8. Restart DSH after installation; use actual slash command /armor status. Expected installed command output must begin "purge-flash 状态". Do not treat a model-generated DNF project narrative as plugin status.
9. Invoke the skill directly or through the model, verify armor-playbook loading no longer reports "loaded skill source must be a string". Inspect host logs and other plugin layers separately.
10. Any Gradle, Android runtime, plugin loading and model effect remain UNVERIFIED until recorded evidence exists.

## Execution evidence as of writing
- Isolated branch source changes and static GitHub repository content checks completed.
- Remote Desktop Commander quota shows zero; no authorized remote terminal available for cloud Actions dispatch.
- Local model container has no usable Android SDK/Gradle or direct GitHub archive network access.
- GitHub Actions run for this candidate has NOT been triggered. APK, built-in archive, and mobile runtime validation are NOT yet available.
