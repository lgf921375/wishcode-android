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

1. `scripts/WishCodePreviewEntry.java`：保留“预览/工具”功能与原认证会话/预览路径，但把原来巨大的 56dp 双按钮替换为两项紧凑快捷入口，缩短“预览网页”为“预览”，按钮文字 14sp、最小高度 44dp、两行上限；继续通过 `font()` 继承系统字体和行距，避免干扰已有 HTML/工具功能。
2. `scripts/wishcode-mobile.js`：只在宽度小于等于 760px 的 APP 内置工作台页面应用；针对 BODY Portal 下的 `role=group` 模型菜单约束最大宽高，内部模型列表 34dvh 上限、允许纵向滚动；按钮行高/44px触摸高度，保留搜索、全部分组及原点击事件；不改推理强度菜单，不重写宿主 React/UI 包。
3. `scripts/test_mobile_ux.py`：静态回归检查菜单 DOM 锚点、滚动限制、原功能路径、Pinyin FontPadding、无第三方网络调用/密钥操作；现有 `scripts/test_customize.py` 和 `scripts/test_preview.py` 不变。

## 非完成项与不可错误承诺

- **没有实现**「自动探测每个模型可用并从选项过滤」。宿主模型选择器没有已核实的可用状态映射；插件导航的“免费模型 0”只反映某个通道当前探测，不等于其它 API、EAC、GLM 套餐和历史错误模型全不可用。不能硬编码某个模型无效或依据一次网络错误永久隐藏。下一阶段需由插件提供来源/地区/授权/可用性状态的可靠 RPC，并给用户“只显示当前可用”可撤销开关、保留查看全部的入口；在此前不得承诺自动过滤。
- 没有增加“自动翻译 AI 英文回复”。语言输出由模型/用户提示词/服务配置决定；后续应添加**用户可控制**的简中回复偏好，不应静默修改原任务或工具命令。
- **当前只有源码及静态检查，尚未打包和真机验证**；不代表 APK 已更新、模型可用，也不代表可绕过 `REGION_BLOCKED` 或 `AUTHORIZATION_REQUIRED`。
- Work 用量/订阅由 ChatGPT 管理，不属于 GitHub Actions，本轮不能恢复或充值额度。

## 后续验收

- 运行 `python3 -m unittest discover -s scripts -p 'test_*.py' -v` 与 `node --check scripts/wishcode-mobile.js`；必须保留完整日志；
- 真实 Android 构建需另外获得用户确认，仅手动一次，记录分支及完整 SHA，禁止自动重试；
- ColorOS 拼音字体下核验：预览和文件工具条高度、聊天滚动/输入框，打开模型列表是否限高并可以独立滚动、搜索和选择、退出弹窗是否恢复焦点；检查推理强度列表、EAC/免费模型页面没有回归；
- 检查真正可用模型需实际调用测试及日志，不可从候选列表可见推断服务可用。
