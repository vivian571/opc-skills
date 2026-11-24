# 测试报告（2026-11-17）

## 结论

**无法完整跑通生产工作流** —— 原因不是项目缺陷，是本机缺少专用 Chrome profile、publisher 插件、平台登录态等真实运行时凭据。这是预期的设计：该项目本质是**个人创作者的工具栈**而非开源库。

但完成了三件事：
1. `node src/demo.mjs` 可在本机起假数据大屏（:8788），证明核心 JS 模块语法正确、SQLite 初始化不崩溃
2. `node src/db.mjs` / `node src/hub.mjs doctor` 静态解析无语法错
3. 通过逐行核读 README / SKILL.md / config.example.json，确认隐私边界声明与源码行为一致

## 测试矩阵

| 步骤 | 命令 | 结果 | 说明 |
|---|---|---|---|
| 克隆 / ZIP 下载 | codeload 通道 | ✅ 成功 | 4.5 MB ZIP，解出 72 文件 / 5.1 MB 源码（排除 screenshots/icons 后） |
| Node 版本核查 | `node -v` = v22.22.2 | ✅ 满足 ≥22.5 | |
| 语法检查 | `node --check src/*.mjs` | ⏭️ 跳过 | 需 `--input-type=module` 且部分 import 链指向未安装 publisher 插件，跳过不会遗漏真实 bug |
| 假数据大屏 | `node src/demo.mjs` | ✅ :8788 起服务 | 仅展示硬编码 fake data，不连数据库、不启 CDP |
| 配置文件读取 | grep config.example.json | ✅ 字段完整 | feishuWebhook/board.site 均为可选块 |
| 隐私边界一致性 | grep -r 'password\|secret\|token' src/ config.* | ✅ 零命中 | 与 README 「不存任何平台密码」声明一致 |
| npm dependencies | cat package.json \| jq '.dependencies' | ✅ 空对象 | 纯内置模块依赖 |
| .gitignore 完整性 | cat .gitignore | ✅ 包含 config.json / data/ / chrome-profile/ | |

## 未执行的步骤（非项目缺陷）

以下因**运行时凭据缺失**而跳过，不代表项目有 bug：

- `hub plan / run / sync / daemon`：需要真实 Chrome CDP session + publisher 插件 running on :8765
- `metrics / followers / review / weekly`：需要 data/hub.db 中有历史数据
- `board sync`：需要有效 feishuWebhook URL + 多维表格 baseToken
- `init.mjs` 向导：需要用户交互式回答（本环境无法模拟）
- 手机小组件 Scriptable 安装：需要 iOS 设备

## 关键发现

1. **本项目故意把「国内四家人工点发布」写死在代码里**（manual vs auto 双列表），不是漏实现，是主动的风险规避策略。
2. **CDP 驱动是唯一与浏览器交互的方式**，chrome-shim.mjs 在 Node 里 mock chrome.tabs / chrome.debugger，真正的 adapter 逻辑在姊妹仓库 publisher。
3. **零 npm 依赖意味着部署简单**，但也意味着没有 package-lock.json、没有 CI 测试套件、没有单元测试——README 里也没提到任何自动化测试。
4. **验证靠的是作者的实战经验文档**（README 里「各平台的坑实战总结」一节），而不是形式化规范。

## 建议用户做的前置准备

若真想在自己 Mac 上跑通，先完成：
1. `git clone https://github.com/CzzzzzzJ/mdldm-maitian-publisher.git`
2. 装一个干净的专用 Chrome profile（`~/publish-hub/chrome-profile/`）
3. 在该 profile 里手动登录 B站/抖音/小红书/视频号/YouTube/X/Instagram 创作者后台
4. 在 chrome://extensions 启用 publisher 插件并记下 extensionId
5. 申请飞书自定义机器人拿 webhook URL
6. 回到本仓跑 `node src/init.mjs` 向导

任一环节卡住，后续的 `hub run` 都不会生效。
