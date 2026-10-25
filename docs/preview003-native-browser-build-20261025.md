# WishCode V0.5 Preview 003：取消重复浏览器并准备手动 APK（2026-10-25）

## 来源与边界

- 基于真实成功的 V0.5 Preview 002 固定源码 SHA `e1ccad7ab50ea7a357c6f87a71be34bf990838d8`。
- 锁定 DSHA `0.2.1-rc.2` 上游源码及现有完整 SHA256 校验；保留 DeepSeek Harness / Android Standard 运行时。
- 用户取消的仅是 WishCode 额外开发的受限网页预览器，不是 DSHA 原生 `WebPreviewActivity`、原生 Web UI、Android 虚拟屏、终端、权限或模型/插件管理。
- Godot 页面中的 JavaScript 第 543 行错误的根因未验证，本版不声称修复 Godot 游戏自身。

## 实际变更

1. `WishCodeHomeActivity.java` 不再显示多余的 HTML 预览入口；聊天直达、GitHub/项目文件/终端/GLM/免费插件照旧。
2. `wishcode-mobile.js` 移除 DOM 自动预览卡片与扫描，同时保留 ColorOS 拼音行高、模型选择列表限高/滚动及 OFM 免费模型插件窄屏布局。
3. `customize.py` 不再强制拦截 DSHA 工作台中的本地链接；**完全不向 APK 注入** `WishCodePreviewActivity`、`WishCodePreviewEntry`、`WishCodePreviewHttp`、`WishCodePreviewPolicy`、第二 WebView 进程或对应 DshaApp 进程特殊分支。原上游 `WebPreviewActivity` 未改动。
4. `scripts/release_config.py` 将包名、versionCode、versionName、GLM 版本名称、APK 文件名和 artifact 名集中管理，防止 #11 出现的多脚本版本漂移。
5. `install_glm.py` 只核对配置文件指定的真实包名、版本号和版本名，不再独立递增 versionCode；发生漂移主动拒绝。
6. 本测试版独立包名 `app.wishcode.harnessmobile.v05trial3`、versionCode `193`、versionName `0.5-preview-003-glm53-dsh0.2.1-rc.2`（GLM staging 后）、桌面显示名 `许愿编程·003`。仍使用临时 Debug 签名，不承诺覆盖升级。
7. `test_release_contract.py` 新增四项发布一致性与禁用旧浏览器断言；同步调整 `test_install_glm.py`、`test_side_install.py`、`test_preview.py`、`test_customize.py`。
8. `.github/workflows/build-custom-apk.yml` 依然仅 `workflow_dispatch`、不自动推送/定时。先执行全部 Python/Node/GLM 回归，再下载上游并进行 Android SDK/Gradle 编译，最后校验包名、证书、APK SHA256 后上传 `WishCode-V0.5-Preview-003-Android-APK`。

## 证据与后续

- 本轮基于 GitHub 真实源码执行 19 项结构及发布脚本合同核对，JS V8 语法与简化 DOM 冒烟检查 PASS；**没有在真实 GitHub runner 执行全部 Python/Node 文件测试、没有本轮 Android 编译或一加 15 安装测试**。不得把静态核对称为 100% 通过。
- 本地工作容器无法解析 github.com，且没有 Android SDK/Gradle，因此不能在该容器构建。当前 ChatGPT GitHub 连接不提供新工作流 `workflow_dispatch`；Remote Desktop Commander 本月执行额度已耗尽。没有通过开启 push 或重跑旧 run 绕过手动规则。
- 用户在本次消息「继续修复优化然后编译」中授权一次性构建，但**尚未触发**。务必先确认同 SHA 没有其他 run，再从 GitHub Actions 手动启动一次。失败即停止，不重试、不修改 main。
- 新包独立安装不影响旧 `v05trial2` 的本地沙箱数据，但**不会自动继承旧模型 API Key、聊天/工作区**。旧版保留以便过渡；迁移必须在真实可用的备份/导入流程核实后进行。
- 需要实机验收：直接进入聊天、设置 GLM、模型选择滚动、打开网页使用 DSHA 原有浏览器、不再出现旧受限窗口、Godot 导出按实际 Web 可用性判断、截图/工具调用权限正常。
