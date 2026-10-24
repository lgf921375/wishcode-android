# WishCode Actions #10：失败日志与隔离修复（2026-10-24）

## 原始证据

- 手动工作流（用户只授权此一次）：https://github.com/lgf921375/wishcode-android/actions/runs/40097193205
- Job: `android-apk` (ID `120881802832`)
- 构建专用分支（保持未修改）：`build/wishcode-v05-manual-20261024-38795192`
- 固定触发 SHA：`38795192a77eb44be64d82b7eb07d55724a47ec1`
- 工作流第 5 步 `Test WishCode patch logic (does not compile APK)` 失败；Python `Ran 34 tests`、`FAILED (failures=3)`。Node 设置、Android SDK、Gradle 编译、签名、APK artifact 上传步骤全部未开始。
- 本轮**没有重新运行失败工作流**，不会使用任何历史失败的 APK。

## 三项日志定位与精确改动

1. `test_customize.PatchTests.test_pinyin_web_typography_preserves_font_and_text_visibility`：旧测试 `assertNotIn('font-size:', js)` 与新增上下文预览卡 CSS `font-size:13px` 冲突。修复：仅删除 `scripts/wishcode-mobile.js` 中预览标签的固定字号，改用**系统字体/系统字号继承**；保留 `line-height:1.8` 和自动换行。这满足用户 ColorOS 拼音字体不强制替换的要求，不放宽测试。
2. `test_customize.PatchTests.test_restore_dialog_compact_copy_preserves_choice`：测试枚举补丁中的全部 `before -> after`，误要求每段 `before` 完全消失。但有些是**增量补丁**，例如 `private boolean pendingOpenWeb;` 本就保留在 `after` 中，故错误失败。修复：始终断言 `after` 必须存在；仅对 `before` 不属于 `after` 的替换要求其消失。旧备份弹窗的删除/替换断言仍保留。
3. `test_startup_entry.StartupEntryTests.test_single_protected_start_with_fail_closed_recovery`：测试用 `fixture` 仅构造待 patch 的源码锚点，不包含上游 `LaunchFragment` 原有 `doStart` 方法实现。测试错误地要求 fixture 中直接出现 `FirstRunWebStart.enqueueVisible`。修复：删除此虚假的 fixture 约束；仍断言被补丁注入的 `doStart(requireActivity()`、`controller.canAutoRestart()`、停止/恢复状态、安全保护和一次性调用条件。完整 Android 编译与真机启动仍待实测。

## 验证分级与权限

- 已完成：GitHub 真实日志读取；三处定位/源文件修改；隔离 V8 JS 语法校验通过；9 项当前源文件静态约束检查通过（含 workflow_dispatch 唯一入口）；没有更新 main、原构建分支、用户凭据或 DNF/Godot/传奇仓库。
- **未执行：** Python 全量 34 项、Node.js 实文件、Android Gradle 编译/签名、设备安装。不能称最终构建通过。
- 此修复只在 `work/wishcode-v05-actions10-testfix-20261024`，PR 待审。原用户仅授权 **一次** 手动构建，已于 #10 消耗；**没有获准第二次触发**，任何窗口不得自动重新运行/重试，也不得因为修复完成就在后台构建。
- 下一次如用户明确授权新的单次构建：先审核此 PR，与最新开发 HEAD 比对，冻结新的完整 SHA 和专用构建分支，检查重复运行/自动触发关闭，再仅一次 `workflow_dispatch`，失败仍不重试。
