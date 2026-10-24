# Actions #11（V0.5 Preview 002）：失败分析与隔离修复

## 真实执行结果

- Workflow run：https://github.com/lgf921375/wishcode-android/actions/runs/40104826683
- Job ID：`120904235905`
- 仅有的一次用户授权构建：分支 `build/wishcode-v05-preview002-manual-20261024-e97102cd`，固定 SHA `e97102cda51255d024e1d1c60f8626250162621e`
- 实际执行状态：Python 预检、Node 网页菜单/预览测试、GLM 流式协议测试、SDK 基础目录探测及 SHA256 固定上游源码提取均成功；第 12 步「Apply WishCode V0.5 Preview mobile adaptation」失败；真正 Gradle / Android 编译、APK 签名及上传全部**未执行**，因此本次无 APK。
- 日志精确错误：
  `File scripts/install_glm.py, line 28: if build.count('versionCode 191') != 1: raise ValueError('GLM_VERSION_DRIFT')`
- 确认原因：为避免 Debug 证书更换覆盖用户旧数据，安全并行安装版本在 `scripts/customize.py` 已正确设置 `versionCode 192` / `versionName "0.5-preview-002-dsh0.2.1-rc.2"`；但后续 `install_glm.py` 仍绑定旧基线 `191` 和 `0.5-preview-001`，触发了预期的故障保护。是本项目多步适配中的版本契约不匹配，不是 GLM API 密钥、手机或云端代码编译错误。

## 针对性隔离修复

分支：`work/wishcode-v05-actions11-glm-stage-fix-20261024`（由固定 #11 失败 SHA 创建，未修改主分支和已授权构建分支）。

- `scripts/install_glm.py`：显式要求只有一个 `versionCode 192` 和正确的 Preview 002 原始版本名；仅将版本名称标注为 `0.5-preview-002-glm53-dsh0.2.1-rc.2`，**不再从 191 自行递增到 192**。版本/上游偏移不符继续主动终止。
- `scripts/test_install_glm.py`：添加 4 项可重复运行的离线回归：Preview 002 插件安装及版本不变、旧 191 fail-closed、未来版本名偏移 fail-closed、重复安装被拒。测试使用临时模拟 Android 根目录和被 mock 的注册文件生成器，不发送任何模型请求/凭据。
- 完整脚本静态扫描发现其余 `scripts/*.py` 中不存在第二处仍在执行的旧版本 GLM 代码路径。但下一轮 Gradle 和 Android 实机编译未运行，不能宣称安装兼容或 APK 可用。

## 权限边界

- 此轮没有触发 Actions #12、没有点击 Retry/Rerun，也没有修改 #11 原分支及签名材料。
- 用户对 #11 的一次手动构建授权已被使用；**后续再次打包必须取得新的明确授权**。审核新分支并固定新的专用构建 SHA 后才可运行一次。失败绝不自动重试。
- 新包名 `app.wishcode.harnessmobile.v05trial2` 仍应与旧 `app.wishcode.harnessmobile.v05preview` 并行安装，不迁移原 APP 私有会话与 API Key。
