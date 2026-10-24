# WishCode Android · 许愿编程 V0.4

基于 [DSH-APP/DSHA](https://github.com/DSH-APP/DSHA/releases/tag/v0.2.1-rc.2) 固定版本定制的安卓本地 DeepSeek Harness。目标是简化模型配置和插件管理；**DeepSeek API Key 请只在手机应用中输入**。

## 手动编译 APK

1. 本仓库 **Actions** → **WishCode V0.4 Android APK - Manual**。
2. 点 **Run workflow** 一次。仓库不配置 `push` 或定时触发，不能自动构建；GitHub Actions 私有仓库可能产生用量或费用。
3. 仅在绿色 **Success**、签名与包名校验通过后，点击运行记录底部 **Artifacts → WishCode-V0.4-Android-APK**。
4. 解压 Artifact，安装 `WishCode-v0.4-arm64-debug.apk`（Android 11+，ARM64）。如果构建失败，先核对 Actions 错误日志，**不要把 ZIP 当作 APK**。

## 源码结构

- `.github/workflows/build-custom-apk.yml`：仅手动编译、版本锁定、SHA 验证与 APK 验证。
- `scripts/customize.py`：固定上游代码锚点的 fail-closed 补丁。
- `scripts/WishCodeHomeActivity.java`：简化中文主页，DeepSeek Flash 和插件设置引导。
- `scripts/test_customize.py`、`scripts/test_pin_linux_aapt2.py`：定制补丁与构件 SHA-256 契约测试（运行结果需通过下一次手动构建确认）。
- `scripts/wishcode-mobile.js`：仅在 APP 的 WebView 中注入的窄屏布局保护；不注入外部浏览器页面。

上游完整源码与离线资源来自公开 GitHub Release 附件 `DSHA-0.2.1-rc.2-20261022.2100-source.zip`，SHA-256 固定为 `ef134fe8713bfa4d6cf3bdea883be1591246d4b78ace16bd924f6d739188425a`。不得用缺离线运行时的 GitHub 自动源码压缩包替代。

## 当前状态与风险

**V0.3 历史事实：** GitHub Actions #4 已成功编译并通过签名校验，用户在一加 15 实机启动了原 DSH 工作台，但反馈页面窄屏裁切和系统拼音主题影响。**V0.4 现状：** 新增源码与测试、手动工作流已提交；尚未运行 V0.4 GitHub Actions，不能把 V0.3 的成功当作 V0.4 编译/安装通过。工作流产生调试签名包，仅供个人测试；独立包名 `app.wishcode.harnessmobile.v04`，不会覆盖 DSHA，但也不会继承 DSHA 中的 API Key、插件或项目。请在更换测试签名或卸载前备份工作区。插件可能运行安装脚本，未经用户主动选择不安装第三方插件。

本仓库与 DNF/Godot/传奇项目完全隔离。

## 免费模型接入（2026-10-24 新增源码；未重新构建）

已在 `scripts/WishCodeHomeActivity.java` 的模型入口增加 **DeepSeek 直连 / 免费模型插件** 两种路径。新版本必须重新进行手动 APK 构建才能拥有这一入口；2026-10-24 第四次 Success 的 V0.3 APK 不包含该入口。

- 官方有据可查的免费渠道：Kilo Gateway 匿名只允许免费模型，限 **200 请求/小时/IP**，可能因地区不可用；`kilo-auto/free` 和 `:free` 模型由上游维护。部分服务商收集提示词/输出，请只在测试项目使用。
- OpenCode 官方虽然列有临时免费模型（包含 DeepSeek V4.1 Flash Free），但官方文档声明免费聊天模型限 OpenCode 客户端；不能保证在 DSH 中使用符合其政策或持续可用。
- 可选第三方插件项目：`Ebony-Vinyl/dsh-our-free-model`。目前只提供**用户主动确认的安装入口**，**不预装、不自动启用、不承诺无限使用**。插件功能广泛，含账号渠道、公告及自更新，尚未完成全面代码安全审计。
- 固定真实 GitHub Release：`v2.5.9` 的 `dsh-our-free-model-2.5.9.tgz`，GitHub API asset.digest SHA-256 为 `3c98427d8144041568c12dd5c61c42632d022856e8f5327e66b813fe80d269a2`，传入本地 `PluginInstallActivity` 的原生下载校验；绝对不使用 npm 同名包（原作者已警告冒名发行）。
- 已有 V0.3 也可尝试在「插件」中粘贴官方 Release URL 手工安装，**需要预览/授权**。手工从插件页面输入 URL 不自动携带固定 SHA，比 APK 内的固定 SHA 入口少了一层校验。
- 不得将私人项目、密钥、聊天中的机密资料发给不可信免费渠道。模型实际在线运行，不在手机离线推理。
- **升级签名提醒：** 第四次 Actions 构建使用临时 debug keystore，后续独立运行重新签名的 APK 很可能不能直接覆盖安装同包名原 APK。升级前必须备份工作区和用户数据；不要为解决签名冲突直接卸载并清空数据。要长期稳定升级需建立不上传明文私钥的持久签名管理方案。


## V0.4 移动端优化（已提交源码，尚未编译/实机验证）

针对 OnePlus 15 / Android 16 / ColorOS 16 的真实截图新增：
- `scripts/WishCodeHomeActivity.java`：原生可滚动聊天优先首页，按钮按“开始聊天 → 模型 → 工具 → 安全”排列；复用已有 DSH 工作区、文件、插件、终端和诊断能力。
- `scripts/wishcode-mobile.js` + `scripts/customize.py`：只注入经过认证的内置 DSH WebView，针对手机宽度的对话框、编辑输入、右侧面板、表格/代码设置行高/自动换行/可滚动边界；对上游 `OnboardingUi` 也启用拼音字体所需的 font padding 和多行按钮；不拦截请求、API Key、提示词、插件指令或工具执行。
- 官方 DeepSeek Flash 接入不变；免费模型只提供**用户主动选择的安装引导**，固定 GitHub Release v2.5.9 及 SHA-256，安装确认由原生安装器负责。插件未预装也未经过全面安全审计。
- 默认权限仍为 `workspace-write`，遇到 DEFAULT_WRITE_NOT_FULL 时先检查工作区/权限，不静默提升到 `danger-full-access`。
- **用户明确要求保留 ColorOS 拼音字体**，不能要求更换系统字体。V0.4 原生页面继承系统字体，不强制 `sans-serif`；启用 FontPadding/FallbackLineSpacing、扩大多行文本及按钮行距；WebView 为中文标题、按钮、弹窗扩展行框和自适应滚动，不隐藏溢出文字。用户截图中 DeepSeek 官网也出现拼音，属于所选字形特征而非乱码。

**避免覆盖安装冲突：** 第四次成功构建的 V0.3 使用 GitHub Runner 临时调试签名；V0.4 使用新的独立 Application ID `app.wishcode.harnessmobile.v04`，避免签名不同导致更新失败或要求清空旧版数据。两版可并存，但新版本不自动继承 API Key、配置、插件或工作区；请勿卸载 V0.3，先用测试工作区验证 V0.4。

**真实状态：** 本轮完成代码与构建配置变更，未触发任何 Actions；V0.4 APK 编译、第三方插件安装、模型调用、ColorOS 16 页面验收均待实测，不能提前宣称通过。
