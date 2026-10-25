# WishCode｜停用不完整的独立网页预览（2026-10-25）

## 用户设备反馈与范围

用户 OnePlus 15 / ColorOS 的 V0.5 Preview 002 实机截图显示：预览器顶部横向「返回聊天、刷新、修改地址、视口…」工具栏占位，Godot Game Engine 加载画面未完成，并显示「JavaScript 错误（第 543 行）」。用户明确表示此预览与 Claude Artifacts 不同、功能不完整、不能访问网页，请求“取消”。

原实现 `WishCodePreviewActivity` 是受限隔离浏览器，仅支持同一 localhost 端口的 GET，限制外部资源、WebSocket、POST、文件上传；**这属于设计约束**，不是通用浏览器，也不代表 Godot 游戏脚本本身一定无错误。截图没有完整 console stack 或服务器日志，无法断言第 543 行的具体原因。

## 源码变更（只影响将来编译的版本）

- `WishCodeHomeActivity.java`：移除「预览网页 · HTML 实时交互」快捷操作，首页不再标榜「预览测试版」，保留聊天、GLM/DeepSeek 模型、项目文件、GitHub、插件、终端。
- `wishcode-mobile.js`：移除聊天本机链接自动注入的「预览网页」卡片与 MutationObserver 代码，保留模型菜单限高、OFM 插件布局和 ColorOS 拼音字体行高。
- `customize.py`：不再向上游 `WebPreviewActivity` 加入强制本机 URL 拦截，普通聊天链接继续由 DSHA 原有实现决定如何处理。
- `WishCodePreviewEntry.java`：旧调用入口变为明确提示「旧网页预览已停用」，不再触发 Activity。
- `test_mobile_ux.py` 与 `test_contextual_preview.cjs`：将已过时的“必须有预览卡片”断言改为“不能再插入预览卡片、仍保留模型与字体修复”。

技术上保留未公开的旧 `WishCodePreviewActivity` 类/Manifest 注册及其限制策略，避免在未经完整 Android 编译审查时激进删除安全边界。由于没有 UI 调用方、没有 HTML 卡片、旧 `open` 明确禁用，普通使用路径不再进入该预览器。

## 验证与下一步

- 源码结构核查可以证明用户可见入口已取消，不代表运行在手机中的已安装 APK 被远程修改。
- 当前已安装的 V0.5 Preview 002 **不会自动变化**。用户立即退出预览，应点击当前窗口左上角「返回聊天」。
- 本次**没有触发 GitHub Actions、没有构建 APK、没有修改 main**；新 APK、Java/Python 全量回归及手机验收尚待单独授权。
- 不卸载现有 APP，不删除工作区、会话或 API Key。后续如要接近 Claude Artifacts，应单独设计真实文件事件驱动、可回退的预览，而不是恢复同一个受限 WebView。
