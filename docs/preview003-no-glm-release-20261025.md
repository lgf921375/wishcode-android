# WishCode V0.5 Preview 003 / NoGLM 交接（2026-10-25）

## 用户决策
用户明确要求取消此前内置的智谱 GLM-5.3：「一点不好用。后期用再自己从模型添加」。本分支在完成原生浏览器复用与旧预览器停用的基础上，取消预装 GLM，但保留 DSHA 原生模型管理、官方 DeepSeek 接入帮助、第三方免费模型插件可选安装入口与 GitHub/终端/文件能力。

## 已实施
- 删除原生 `WishCodeGlmSettings.java`、`scripts/install_glm.py`、`scripts/test_install_glm.py`、`tests/glm.test.mjs`、`plugins/dsh-wishcode-glm/` 全部四个实际源码文件；历史审计证据保留在 `docs/` 与 `evidence/`，不会作为 APK 插件打包。
- `WishCodeHomeActivity` 不再调用 GLM 密钥设置。模型区域明确引导：进入工作台 →「设置 → 模型」按上游 DSH 支持的渠道手动配置。**不承诺所有未来型号（特别是 GLM-5.3）都可直接在当前 DSH 中添加，需按真实界面和兼容性确认。**
- 构建工作流移除 GLM 预装动作、协议测试以及 GLM Python 编译命令。使用唯一的 versionName `0.5-preview-003-dsh0.2.1-rc.2`，不添加 `-glm53-`。
- `test_release_contract.py` 改为明确拒绝打包 GLM 插件、弹窗和安装脚本；`test_mobile_ux.py` 要求 GLM 入口缺失并保留模型设置说明。
- 本包与含 GLM 的候选版本用不同的 APK/artifact 名区分：
  * 包名：`app.wishcode.harnessmobile.v05trial3`（和已成功的 trial2 并行）
  * versionCode：193
  * APK：`WishCode-v0.5-preview-003-no-glm-arm64-debug.apk`
  * artifact：`WishCode-V0.5-Preview-003-NoGLM-Android-APK`
  * 工作流：`.github/workflows/build-custom-apk.yml`，只有 `workflow_dispatch`
- 继续保留 DSHA 原生 WebView / WebPreviewActivity、聊天、模型、插件、工作区、ColorOS 字体/菜单修复。仅停用之前用户不满意的 WishCode 自制受限预览器。

## 验证范围与注意事项
- GitHub 源文件与树清单核验：项目 active `scripts/`、`plugins/`、`tests/` 目录没有 GLM 文件；只在历史文档和证据有 GLM 字样。
- **尚未在本轮执行完整 Python + Node 回归、Android Gradle 真正编译、APK 签名检测或真机验收。** 编译前必须由 Action 自动执行测试，失败即停止、不自动重试。
- **勿使用旧构建分支** `build/wishcode-v05-preview003-manual-20261025-2da3566f`：那条分支仍带 GLM 预装。本次应选择更新的 `NoGLM` 构建分支并固定 SHA。
- GitHub 工具目前只支持源码写入、查看构建及重跑已有构建，不支持 dispatch 新手动构建；无云构建自动授权路径。远程 Desktop Commander 本月额度耗尽。构建由用户 GitHub Actions 页面点击一次；不允许改成 push 自动构建。
- 旧版 `v05trial2` 的 GLM 配置、聊天和密钥**未删除**；新包独立安装、不会自动继承它们。旧版不会因为 GitHub 源码变更而远程改变。
