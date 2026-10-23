# WishCode Android · 许愿编程 V0.3

基于 [DSH-APP/DSHA](https://github.com/DSH-APP/DSHA/releases/tag/v0.2.1-rc.2) 固定版本定制的安卓本地 DeepSeek Harness。目标是简化模型配置和插件管理；**DeepSeek API Key 请只在手机应用中输入**。

## 手动编译 APK

1. 本仓库 **Actions** → **WishCode V0.3 Android APK - Manual**。
2. 点 **Run workflow** 一次。仓库不配置 `push` 或定时触发，不能自动构建；GitHub Actions 私有仓库可能产生用量或费用。
3. 仅在绿色 **Success**、签名与包名校验通过后，点击运行记录底部 **Artifacts → WishCode-V0.3-Android-APK**。
4. 解压 Artifact，安装 `WishCode-v0.3-arm64-debug.apk`（Android 11+，ARM64）。如果构建失败，先核对 Actions 错误日志，**不要把 ZIP 当作 APK**。

## 源码结构

- `.github/workflows/build-custom-apk.yml`：仅手动编译、版本锁定、SHA 验证与 APK 验证。
- `scripts/customize.py`：固定上游代码锚点的 fail-closed 补丁。
- `scripts/WishCodeHomeActivity.java`：简化中文主页，DeepSeek Flash 和插件设置引导。
- `scripts/test_customize.py`：补丁逻辑回归测试。

上游完整源码与离线资源来自公开 GitHub Release 附件 `DSHA-0.2.1-rc.2-20261022.2100-source.zip`，SHA-256 固定为 `ef134fe8713bfa4d6cf3bdea883be1591246d4b78ace16bd924f6d739188425a`。不得用缺离线运行时的 GitHub 自动源码压缩包替代。

## 当前状态与风险

截至提交时，**只有 6 项补丁单元测试通过，尚未实际编译、安装或真机测试 APK**。工作流产生调试签名包，仅供个人测试；独立包名 `app.wishcode.harnessmobile`，不会覆盖 DSHA，但也不会继承 DSHA 中的 API Key、插件或项目。请在更换测试签名或卸载前备份工作区。插件可能运行安装脚本，未经用户主动选择不安装第三方插件。

本仓库与 DNF/Godot/传奇项目完全隔离。