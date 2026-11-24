# 本机复跑步骤（只用于学习，不代执行）

> 2026-11-17 在 macOS Apple M4 / Node v22.22.2 环境核实。**以下命令仅供阅读参考，实际运行需自行完成环境准备与凭据配置。**

## 前置条件（全部满足才可真正运行）

- [x] macOS
- [x] Node.js ≥ 22.5（本机 v22.22.2 ✅）
- [x] Google Chrome 已安装
- [ ] 专用 Chrome profile（`~/publish-hub/chrome-profile/`）— **必须独立于日常浏览器**
- [ ] 姊妹仓库 `mdldm-maitian-publisher` clone 到任意路径
- [ ] config.json 已填好（至少 pluginDir / extensionId / web.key / rootPath）
- [ ] 各平台创作者后台已在专用 Chrome 里登录过
- [ ] （可选）飞书群机器人 webhook URL
- [ ] （可选）NAS SMB 共享挂载点

## 一键安装（官方推荐）

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/CzzzzzzJ/mdldm-maitian/main/scripts/install.sh)"
```

注意：install.sh 会把两个仓库都 clone 到 `~/maitian/` 目录，之后向导会问几个问题并生成 config.json。

## 手动安装

```bash
# 1. clone 姊妹仓库（publisher 插件）
git clone https://github.com/CzzzzzzJ/mdldm-maitian-publisher.git ~/maitian/mdldm-maitian-publisher

# 2. clone 本仓库
git clone https://github.com/CzzzzzzJ/mdldm-maitian.git ~/maitian/mdldm-maitian
cd ~/maitian/mdldm-maitian

# 3. 先用假数据看效果
node src/demo.mjs   # 打开 http://localhost:8788/?key=demo

# 4. 安装向导填凭据
node src/init.mjs   # 检查环境 → 生成 config.json → 装开机自启 → 打开各平台登录页

# 5. 登录完检查状态（不上传、不填写）
node src/hub.mjs doctor
```

## Demo 运行（不需要任何凭据）

```bash
cd ~/.workbuddy/skills/maitian/upstream
node src/demo.mjs
# → http://localhost:8788/?key=demo
```

这只会展示一个带假数据的大屏页面，所有数字都是硬编码的，不涉及真实平台数据。

## 生产模式完整链路（仅说明，不代执行）

1. 写「发布素材.md」（按 skills/maitian-publish/SKILL.md 模板）
2. 生成 publish.json：`node <publisher>/tools/make-publish.mjs "<素材.md>" "<工程目录>" --require <账号名>`
3. 校验：`node <publisher>/tools/validate.mjs "<工程目录>"`，❌ 就改 md 重生成
4. 进计划：`node src/hub.mjs plan "<工程目录>"`
5. 开跑：`node src/hub.mjs run "<工程目录>"`
6. 国内平台：飞书卡片提醒你去 Chrome 里点「发布 / 定时发布」
7. 到点后：`node src/hub.mjs sync <id>` 取链接回填 md
8. 每天：`node src/hub.mjs metrics` 采流量

## 关键环境变量与路径

| 项 | 默认值 | 说明 |
|---|---|---|
| `pluginDir` | — | publisher 插件 clone 路径，必填 |
| `extensionId` | — | chrome://extensions 里看到的 ID，必填 |
| `bridge` | `http://127.0.0.1:8765` | publisher 的开发桥，保持该端口 open |
| `chromePort` | `9333` | CDP 调试端口 |
| `chromeProfile` | `~/publish-hub/chrome-profile` | 专用 profile 路径 |
| `rootPath` | — | NAS 上发布工程的根，必须有写入权限 |
| `web.key` | — | 网页访问口令，无 key 一律 401 |

## 不要做的事

- ❌ 不要把日常 Chrome profile 当专用 profile 用
- ❌ 不要反复传同一条视频到同一平台（风控重灾区）
- ❌ 不要在 config.json 里贴真实 feishuWebhook 并提交到 git
- ❌ 不要跳过 validate.mjs 直接 hub run（封面比例 / 禁词 / faststart 都会在后端报错）
