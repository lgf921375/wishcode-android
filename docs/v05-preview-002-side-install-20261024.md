# WishCode V0.5 Preview 002｜并行安装安全方案（2026-10-24）

## 实证：旧预览版的 Debug 签名每次构建不同

来自 GitHub Actions 的`apksigner --print-certs`原始构建日志：
- 成功 Run #8 https://github.com/lgf921375/wishcode-android/actions/runs/40069051493 ：Signer SHA256 `86c9ac0fe9d6025c73761075cac0e3203249449f372e494942bfb4518b1cdb90`
- 成功 Run #9 https://github.com/lgf921375/wishcode-android/actions/runs/40086450896 ：Signer SHA256 `9e2cd3784005d6ec90f3e34d999344dd3d1c7c545bd0630c5976c53b98603263`

二者包名都为 `app.wishcode.harnessmobile.v05preview`，签名不同，**Android 无法将不同签名的同包名 APK 覆盖升级**。这不是本次打包能够自动修复的；旧版本私钥没有出现在当前仓库/工作流证据中。

## 本候选：只增加一个并行测试 APP，保护用户旧版资料

在 PR #5 修复的基础上：
- 独立包名：`app.wishcode.harnessmobile.v05trial2`（不覆盖 `app.wishcode.harnessmobile.v05preview`）。
- 显示名称 `许愿编程·测试版`，与旧 APP 区分。
- versionCode `192`，versionName `0.5-preview-002-dsh0.2.1-rc.2`。
- GitHub 仅手动构建工作流验证新的包名，并发布 `WishCode-v0.5-preview-002-arm64-debug.apk`。
- 新增 `scripts/test_side_install.py`，禁止该候选误回退到旧包名。

### 不能承诺的事

1. 这是**新 APP**，不是覆盖更新：旧 APP 的模型 API 密钥、会话和工作区**不会自动迁移**。用户须保留旧版，不可为了测试卸载旧版；若想迁移数据必须基于真实已验证的备份/导入流程。
2. 此候选依旧是临时 Debug 签名，每次运行还可能改变证书。**永久同包名升级需要安全保存且稳定使用的签名私钥**，不能把私钥提交到公开仓库；此阶段不实现。
3. PR #5 修复的三处测试断言、聊天内预览、取消顶部导航和冷启动直达候选仍未通过新版完整 Android 编译和真机测试；不得标记为已验收。
4. 第 #10 次用户授权已被用掉；本分支**只提交源码、不执行任何第 #11 次 GitHub Actions**。需用户再次明确授权才可进行一次构建，失败不重试。
