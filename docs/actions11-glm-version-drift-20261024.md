# WishCode APK 手动构建 #11：GLM_VERSION_DRIFT 复盘与隔离修复
日期：2026-10-24

## 已证实的失败
- GitHub Actions #11：https://github.com/lgf921375/wishcode-android/actions/runs/40104826683
- job `android-apk`：120904235905；固定源码 SHA：`e97102cda51255d024e1d1c60f8626250162621e`
- 第 1–11 步均成功（Python 回归、Node 模型菜单/上下文预览、GLM 协议测试、SDK 检查、固定上游源码与 SHA256 校验）；第 12 步 `Apply WishCode V0.5 Preview mobile adaptation` 调用 `scripts/install_glm.py` 失败：
  `ValueError: GLM_VERSION_DRIFT`；当时的判断是 `build.count('versionCode 191') != 1`。
- Preview 002 的 `scripts/customize.py` 正确将上游 `versionCode 190` 改成 `192` 并使用独立包名 `app.wishcode.harnessmobile.v05trial2`。GLM 脚本仍只支持旧版 Preview 001 的 `191`，因此两个阶段的版本协议冲突。
- **实际没有进入 Gradle 编译、APK 签名和产物上传；#11 无新 APK。**

## 本次源码修复（绝不重新触发构建）
- 隔离分支 `work/wishcode-actions11-glm-version-fix-20261024` 仅从 #11 固定 SHA 创建，不修改旧的 build 分支或 main。
- `scripts/install_glm.py` 严格验证输入为 `versionCode 192`、`versionName "0.5-preview-002-dsh0.2.1-rc.2"`、`applicationId "app.wishcode.harnessmobile.v05trial2"`，只将版本名称更新为 `0.5-preview-002-glm53-dsh0.2.1-rc.2`。不再第二次改 versionCode，遇到意外值立即停止。
- 新增 `scripts/test_install_glm.py`，构造临时项目、模拟上游注册表/受管运行资源和工具调用；检查插件能正确注册、复制、本次版本不变、包名不变；旧版本/错误包名/重复安装都 fail closed。此测试由已有 `python3 -m unittest discover -s scripts -p 'test_*.py' -v` 自动纳入前置测试。
- 目前已做 GitHub 真实源码静态检查 10 项（全部通过），**没有执行真实 Python 全量测试、Gradle 编译、安卓实机测试**。不可把静态检查等同于 CI PASS。
- GitHub 连接缺少新工作流启动操作，远程终端额度耗尽。用户在 #11 的一次构建授权已消耗；**后续任何人不得擅自点击 Re-run jobs 或触发 #12**，除非用户重新明确授权一次新构建。

## 安装与数据
- 新版仍使用独立包名 `app.wishcode.harnessmobile.v05trial2` 与旧版并行安装。
- 不会自动带入旧版聊天记录、模型 API Key 和工作区；不得卸载旧 APP。Debug 私钥不稳定，不得宣称未来支持直接覆盖升级。
