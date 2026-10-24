# WISHCODE-MOBILE-UX-002｜ColorOS 手机聊天与模型选择优化（2026-10-24）

## 用户实机反馈

设备：OnePlus 15 / Android 16 / ColorOS 16；**保留系统带拼音字体**。用户在聊天界面截屏指出：
1. 顶部「预览网页 / 文件工具」两个大型按钮侵占聊天高度；
2. 模型下拉菜单特别高，覆盖正文及输入框。分组列出 GLM-5.3（官方 API 与 Coding Plan 套餐）及 Our Free Model（MiMo、Nemotron、DeepSeek V4.1 Flash、GLM 5.3 Flash 等）；
3. 用户希望不可用模型能够自动判定并不出现在候选中，界面中文化、能快速切换；
4. ChatGPT Work 显示本次用量已耗尽，不代表许愿编程服务或 GitHub 构建额度。不要为修复 APP 擅自触发 CI。

## 固定基线与隔离

- 基于 `work/wishcode-preview-001-20261024` 的 `27bf8c83f172446060bd98460a63f690a7ec5f38`；GitHub Actions #9 已于该 SHA 成功，仅证明当时的编译签名，**不包含本修复**。
- 候选分支：`work/wishcode-mobile-ux-002-20261024`，禁止直接修改 `main`。
- DSHA 上游锁定 `c750348a4d4b18edcb165a93b4ca66403b040b4c`，菜单 DOM 证据来自 `app/src/main/assets/builtin-plugins/dsh-web-mobile/lib/client.js`：
  `DIV[class*="_7KE1Ra_menu"][role="group"]` 是 BODY Portal 下的**模型选择**菜单，内部 `DIV[class*="_7KE1Ra_groups"][role="menu"]` 可滚动；推理强度菜单是 `role="menu"`，不可误改。移动预览入口仍由 `WishCodePreviewEntry` 实现。

## 本轮已提交代码

1. **按用户后续明确反馈调整**：聊天顶部不需要任何「预览/文件工具」常驻栏，因此 `scripts/WishCodePreviewEntry.java` 已完全删除聊天头部布局注入代码；`scripts/customize.py` 不再在 `WebPreviewActivity` 启动时调用 `WishCodePreviewEntry.install(this)`。原有聊天内容区域完全保留。仅当用户在聊天中主动点击合格的 localhost HTML 链接时才进入独立 APP 内预览页；原生首页仍保留备用的手动预览入口。系统拼音字体不被覆盖。
2. `scripts/wishcode-mobile.js`：只在宽度小于等于 760px 的 APP 内置工作台页面应用；针对 BODY Portal 下的 `role=group` 模型菜单约束最大宽高，内部模型列表 34dvh 上限、允许纵向滚动；按钮行高/44px触摸高度，保留搜索、全部分组及原点击事件；不改推理强度菜单，不重写宿主 React/UI 包。
3. `scripts/test_mobile_ux.py`：静态回归检查**没有常驻导航**、只有用户主动点击本地合法链接进入预览、模型菜单 DOM 锚点、滚动限制、Pinyin FontPadding、无第三方网络调用/密钥操作；现有 `scripts/test_customize.py` 和 `scripts/test_preview.py` 不变。

## 非完成项与不可错误承诺

- **没有实现**「自动探测每个模型可用并从选项过滤」。宿主模型选择器没有已核实的可用状态映射；插件导航的“免费模型 0”只反映某个通道当前探测，不等于其它 API、EAC、GLM 套餐和历史错误模型全不可用。不能硬编码某个模型无效或依据一次网络错误永久隐藏。下一阶段需由插件提供来源/地区/授权/可用性状态的可靠 RPC，并给用户“只显示当前可用”可撤销开关、保留查看全部的入口；在此前不得承诺自动过滤。
- 没有增加“自动翻译 AI 英文回复”。语言输出由模型/用户提示词/服务配置决定；后续应添加**用户可控制**的简中回复偏好，不应静默修改原任务或工具命令。
- **当前只有源码及静态检查，尚未打包和真机验证**；不代表 APK 已更新、模型可用，也不代表可绕过 `REGION_BLOCKED` 或 `AUTHORIZATION_REQUIRED`。
- **Claude Artifacts 风格真正的对话内预览卡片仍是下一阶段功能**：当前仅支持点击经过校验的本机链接打开独立的 APP 内安全预览页。不能假称已实现“自动识别 HTML 成果并直接在聊天气泡内交互”。后续要求从真正的文件生成工具事件/预览地址显式元数据派生可点击的预览卡片，不得扫描模型文字冒充已生成文件，也不得因此添加顶部常驻导航。
- Work 用量/订阅由 ChatGPT 管理，不属于 GitHub Actions，本轮不能恢复或充值额度。

## 后续验收

- 运行 `python3 -m unittest discover -s scripts -p 'test_*.py' -v` 与 `node --check scripts/wishcode-mobile.js`；必须保留完整日志；
- 真实 Android 构建需另外获得用户确认，仅手动一次，记录分支及完整 SHA，禁止自动重试；
- ColorOS 拼音字体下核验：**聊天顶部无预览/文件工具导航**且正文和输入框完整；用户点击聊天中合法 localhost URL 后才进入 APP 内独立预览并能返回会话；模型列表限高并可以独立滚动、搜索和选择、退出弹窗恢复焦点；检查推理强度列表、EAC/免费模型页面没有回归；
- 检查真正可用模型需实际调用测试及日志，不可从候选列表可见推断服务可用。


## 下一阶段增量：聊天内上下文预览入口（用户“下一步”授权的源码开发）

- 不恢复顶部导航。仅当 Web 工作台在 `[data-chat-flow]` 消息中渲染一个合格的 `http://127.0.0.1:<port>/...` 或 `http://localhost:<port>/...` 链接，`wishcode-mobile.js` 才在相邻内容区生成一条**明确标注“尚未验证服务”**的「预览网页」操作。不会从纯文本猜测文件路径，不会读私有工作区/密钥，不会自动请求服务。
- `previewCandidate` 拒绝 HTTP 之外的协议、外网 host、用户密码、查询串、片段、无效端口及 3081/3090。真正的有效性仍由 `WishCodePreviewPolicy.normalize(url, chatPort)` 在原生端二次检查；由于 JS 不知道当前聊天端口，JS 合格不等于 native 合格。
- 链接是用户直接点击的原生 `<a href>`，遵循已有 `WebPreviewActivity.shouldOverrideUrlLoading` 的真实手势要求。原生 `WishCodePreviewEntry.open` 仅给显式聊天链接传 `from_chat_link`；首次打开且通过 native normalize 时 `WishCodePreviewActivity` 自动加载一次；原生首页的手动入口（无候选 URL）仍需要输入/确认。应用恢复不自动重新发送请求。
- 通过 `WeakSet` 和有限 MutationObserver 处理新出现的消息段落，跳过代码块、弹窗和聊天输入区。CSS 仅应用于窄屏，不换 ColorOS 系统字体，不涉及 DOM HTML 插入/模型 API/外部服务登录。
- **仍非 Claude Artifacts 的真正“从文件/工具事件自动生成预览卡”**：本轮只有“已渲染的本机链接 → 同消息操作 → 独立 APP 内 WebView”的渐进实现。最终版应通过可信文件创建/工具结果证据提供文件路径和端口元数据，而非依赖模型自行输出链接。
- 新增 `scripts/test_contextual_preview.cjs`（Node 虚拟 DOM 合同测试）和 `scripts/test_mobile_ux.py` 的额外测试：合法链接、外网/带凭据/禁止端口被拒、流式追加后出现入口、重复扫描不会重复加入、原生显式操作约束。静态脚本检查/模拟 DOM 检查不等于 Android 实机。
- 本轮不触发云编译；后续仍需在真实 OnePlus 15 证明：当消息中显示 `http://127.0.0.1:4181/` 时有同消息预览操作，点击实际打开安全预览网页；URL 无响应时显示错误，修改后刷新；聊天顶部保持无工具栏且模型弹窗可滚动。


## 实机补充：下次启动直接进入工作台（启动路径优化）

**用户 19:53 实机截图**：OnePlus 15 的 `许愿编程 · 预览测试版` 首页按「开始聊天编程」后，还进入了 DSHA 原生「启动 DSHA / 重启 / 停止」页；即使运行环境标记 READY，仍需再次点击才能到聊天。用户明确要求下次点击桌面 APP 图标后直接进入工作窗。

**已提交隔离分支的源码候选**：
1. `WishCodeHomeActivity.onCreate` 只在真正 `Intent.ACTION_MAIN + CATEGORY_LAUNCHER` 且非显式 `wishcode_show_home` 时，直接启动 `MainActivity`，携带 `open_web=true` / `wishcode_auto_start_web=true`，马上 finish；不再强制展示冗余介绍首页。原先进阶模型/插件/预览/诊断入口仍在内部首页。
2. `customize.py` 精确 patch 上游 `MainActivity`：消费独立的 `wishcode_auto_start_web` 需求，转交 `LaunchFragment`；在原生 DSHA 标题点击可显式打开旧高级首页（`wishcode_show_home=true`），以备诊断和高级配置。
3. `LaunchFragment` 复用原有 `pendingAutoEnter` 和 `webEntryUrl()` 的鉴权就绪判断，不暴露/持久化 Token。已就绪直接进入 WebPreviewActivity；冷启动未就绪时，在**可见 Fragment 内**、controller 非启动/停止/恢复、无遗留会话、无待修复环境、无用户手动停机状态下调用原有 `doStart -> FirstRunWebStart.enqueueVisible` **仅一次**；成功后等真实本机鉴权地址出现再进入聊天，失败则保留启动页/诊断供用户操作，不自动重试。
4. 用户显式点击 Stop、Activity 退后台/页面消失时清理待自动启动状态。首次安装、Welcome/Extract、恢复备份及手动权限确认流程不绕过。
5. 新增 `scripts/test_startup_entry.py` 源码合同检查。固定上游 `MainActivity.java` 5 处、`LaunchFragment.java` 6 处精确锚点均被只读核对出现 1 次；**尚未执行完整 Python、Android Java 编译或手机冷启动验收**。

**手机验收要求**（分开截图记录）：
- APP 已运行时从手机桌面点图标：不显示定制介绍页，若已鉴权应直接返回原聊天会话；
- 完全退出/系统回收进程后的冷启动：最多一次受保护启动，待真实 Web 鉴权就绪后自动进入；检查弱网下与运行环境已停止时的行为；
- 点击「停止」后不得自动重启；启动失败、权限拒绝、备份恢复/环境修复必须保留可到达的原生诊断；
- 返回/后台切换、旋转屏幕、原生标题打开高级首页，仍可调整 API/插件与读取日志；
- **保留 ColorOS 拼音字体和现有工作区/模型凭据，不要求重装或抹数据**。
- **当前手机已装 APK 不包含上述新补丁**。合并执行分支后须在用户明确授权下手动构建，不允许自动触发/自动重试，不能用静态测试替代实机判定。
