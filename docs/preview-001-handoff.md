# WISHCODE-ANDROID-PREVIEW-001 · 首版源码交付（2026-10-24）

## 当前结论

已实现受限的 APP 内本机 HTML 预览候选，完成主机测试和固定上游 patch。**尚未编译本版 APK，未进行 Android WebView、OnePlus 15 / ColorOS 拼音字体真机验收。** 不将源码、HTTP 200 或网页回调等同于手机功能通过。

- 独立仓库基线：`632ec8a2764b53b99e8cd9a7a23322102ecda695`。
- 分支：`work/wishcode-preview-001-20261024`，不合并 main。
- 上游：`DSH-APP/DSHA@c750348a4d4b18edcb165a93b4ca66403b040b4c`。
- 未触发 Actions 或付费构建。工作流仍仅 `workflow_dispatch`，一次授权仅构建一次，不自动重试。

## 复用与新增

复用上游聊天认证路由、工作区文件页、插件页、终端、WebFullscreenUi 安全区/键盘布局。上游 WebPreviewActivity 的真实职责是受认证的 DSH 工作台，因此没有将任意开发 URL 注入该组件。

新增：

1. 聊天页原生「预览网页」「文件 / 工具」栏，不覆盖 composer；文件、插件、终端、模型/GitHub 帮助可直接进入。
2. 用户点击聊天中的合格本机链接时进入预览确认页；没有链接时可从原生入口输入 URL。不读取或扫描聊天文本、不把模型文字视作已运行的证据。
3. `WishCodePreviewActivity`：确认地址、手动刷新、返回聊天、复制链接/错误、外部浏览器确认、360/390/430dp/适应屏幕。大于屏幕时可横向查看；旋转保留实例，进程恢复仅恢复输入，不重放请求。
4. HTTP 与网页回调分别显示，404/重定向/连接失败/JS 错误/渲染进程退出有状态。JS 错误仅记录行号，不复制任意页面输出；状态文字可点击展开。
5. 继承系统字体，启用 FontPadding/FallbackLineSpacing/行距；不替换 ColorOS 拼音字体。打开后收起地址控件，给网页留出空间。实际字体和 IME 效果待手机检查。

## 边界与已知限制

- 预览 Activity 不导出，运行在 `:wishcode_preview`。Application 在该进程选择独立 WebView 数据目录并跳过工作台/运行时/桥/备份初始化。Cookie 禁用；不清除主聊天 Cookie。
- 只接受显式 `http://127.0.0.1:<port>/path` 或严格 `localhost` 等价形式。1024–65535，排除当前聊天端口、3081、3090；入口不接受查询串、片段或用户凭据。IPv6 此版未开放。
- 逐请求 GET 传输禁用代理和重定向，不转发 Cookie/Authorization/Set-Cookie/Location。资源只能同一已确认 origin；CSP 禁止 iframe、worker、对象与外部连接。无通用 JS 原生桥、文件/内容访问、相机/麦克风授权、下载/上传通道。
- **首版适用静态 HTML/CSS/JS、DOM 点击/输入/滚动、本端口 GET。** CDN、WebSocket/HMR、iframe、POST 提交和文件上传不可用。前端表单使用 preventDefault 后在 DOM 中显示输入可用，但仍待 WebView 实测。
- 手动刷新读取最新文件，不实现自动监听/轮询。不新增 Shell 执行器，也不自动创建文件或启动服务；AI 使用现有工具和确认机制执行。
- URL 来源明确为用户输入/用户点击；工作区归属未核实，不能声称已验证具体项目或服务进程。不能由连接失败断言进程退出；用户需查看原终端。
- 此独立进程是浏览器资料隔离，不是独立 Android UID 沙箱；proot/插件的既有权限模型未改变。
- 不检测 0.0.0.0 监听状态，只在帮助中要求绑定 127.0.0.1。真实 Android 与 proot 回环互通尚待验证。
- 未实现横屏左右分栏、自动工具卡片解析、最近项目列表、受管开发进程生命周期。退出预览不停止服务，须在原终端 Ctrl+C；不按端口猜 PID 杀进程。

## 真实验证

原始日志：`evidence/preview-001/host-tests.log`。

- 24 项 Python 测试通过，包含原有 21 项及新增 3 项。
- 内嵌 Java 行为测试真实编译执行，45 个断言通过。覆盖合法/恶意 URL、origin 边界、CSP、宿主机随机端口真实 HTTP 200/404、UTF-8、重定向目标请求数为零、无 Cookie/Authorization 发送及停止服务后的连接错误。
- 5 个 Java 模板的语法解析通过；**不代表 Android 类型检查或完整编译**。
- 从固定上游 Git 对象提取实际文件，完整 patch 成功，16 个生成/修改文件有前后 SHA-256，见 `upstream-patch.json`。生成 AndroidManifest XML 可解析。
- JS `node --check` 与 `git diff --check` 通过。
- 本环境无 Android SDK / Android 真机；Playwright 包存在但 Chromium 二进制不存在。未把测试夹具当作网页渲染或触控验证。

复验：

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
node --check scripts/wishcode-mobile.js
node --check tests/fixtures/preview/app.js
```

真实固定源码 patch 的标准入口保持 `python3 scripts/customize.py <完整源码目录> --report <报告路径>`，仍由构建工作流校验原始 Release ZIP SHA-256 后调用。

## 安装与构建待授权

- 候选名称：许愿编程 · 预览测试版。
- applicationId：`app.wishcode.harnessmobile.v05preview`。
- versionCode：191；versionName：`0.5-preview-001-dsh0.2.1-rc.2`。
- 构建：现有 `.github/workflows/build-custom-apk.yml`，Standard arm64 Debug，仅手动。
- 预计产物（尚不存在）：`WishCode-v0.5-preview-arm64-debug.apk`；artifact `WishCode-V0.5-Preview-Android-APK`。
- 产物要求：签名证书报告、包名检查、APK SHA-256、patch 报告、源码完整 SHA、构建日志。
- 旧 V0.4 使用临时 debug 签名；新包名避免要求卸载旧版。两版数据/工作区/配置不自动共享；先保留旧版，只在新测试工作区验收。稳定签名升级仍未实现。
- 构建前再核对远端分支固定 SHA、是否已有本次运行及手动触发配置；拿到明确授权后只触发一次。失败仅记录日志，不自行重跑。

## 真机验收清单（全部待测）

1. OnePlus 15 保持现有 ColorOS 拼音字体，安装新包并保留 V0.4。
2. 进入新测试工作区，让模型生成 HTML/CSS/JS，并实际启动服务。要求输出实际文件与工具退出码；仅口头声称不算证据。
3. 可用 `tests/fixtures/preview/` 作确定性样本。在该目录的已授权终端运行 `python3 -m http.server 4181 --bind 127.0.0.1`（4181 仅示例；占用时由用户选择其他端口，不自动重试）。保持该终端运行。
4. 聊天「预览网页」或点击本机链接，确认 URL；记录 HTTP 状态与实际画面。点击计数、输入中文、表单 DOM 显示、滚动到底部。
5. 返回同一聊天，让模型把版本 A 改为 B；再进入预览并刷新，截图确认新文本。
6. 360/390/430dp、竖横屏、系统字体比例、输入法、回到聊天、后台返回分别检查。不能以默认字体桌面截图替代。
7. 输入不存在路径得到 404；制造 JS 错误查看状态；原终端 Ctrl+C 停服后刷新显示连接错误。核对无自动重启。
8. 验证工作台端口、3090、外部资源、跨端口与重定向拒绝；确认返回聊天后仍可正常对话，主 Cookie 不受影响。
9. 记录具体 APK SHA、设备版本、截图/日志、通过/失败/未测范围，再决定下一阶段。
