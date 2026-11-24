---
name: maitian
description: >-
  CzzzzzzJ/mdldm-maitian（★335 / MIT / v0.3.0 / macOS-only / Node ≥22.5）的离线索引与上游文档手册。
  麦田是个人创作者的多平台发布中控工作台：一期成片分批填好 B站/抖音/小红书/视频号/YouTube/X/Instagram，
  进「分发计划」→ 到点自动取链接 → 每天采流量数据 → 大屏 + 飞书卡片通知。
  本项目刻意不把国内四家（B站/抖音/小红书/视频号）写成全自动 —— 最后一下由人点，是主动的风控规避策略。
  ⚠️ 合规硬约束：本包只做离线索引与上游源码查阅；不代跑 hub.mjs、不启动专用 Chrome、
  不生成 config.json/chrome-profile/、不接飞书 webhook、不指导绕过任何平台 ToS。
  用户自行决定是否安装与运行，自负其责。
  关键词：麦田、mdldm-maitian、多平台发布、中控、B站、抖音、小红书、视频号、YouTube、X、
  Instagram、飞书、Chrome 插件、CDP、faststart、publish.json、demo.mjs、mit-license、macOS。
---

# mdldm-maitian · 离线索引与上游文档手册

> 上游：`CzzzzzzJ/mdldm-maitian` · v0.3.0 · MIT · ★335（2026-11-17 核实快照）· macOS only
> 镜像：`upstream/` 59 文件 / 5.1 MB（排除 screenshots/icons/docs/readme/src/*.png 大图）

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **个人创作者的多平台发布中控**：把一期成片批量填到 B站/抖音/小红书/视频号/YouTube/X/Instagram | 可复用的 npm 包或 SDK — 零 deps、纯 ESM，但没测试套件、没 release 流程 |
| **离线阅读的手册层**：上游 README / SKILL.md / config.example.json 全文镜像，结构化出 14 条命令 / 18 个核心模块 / 23 个配置字段 | 能直接跑的生产系统 — 需要专用 Chrome profile、publisher 插件、各平台登录态、飞书 webhook |
| **作者实战经验沉淀**：README 「各平台的坑实战总结」一节是核心价值，不是通用抽象 | 学术性论文或官方文档 —— README 就是权威来源，CONTRIBUTING.md 几乎不存在 |
| **MIT 授权下的参考实现** | 商业产品 — 作者麦当 mdldm 知识站（mdldm.club）的副产物，附带课程引流链接 |

## 2 架构速览

```
NAS 发布工程（publish.json + 成片.mp4 + 封面/*.png + 发布素材.md）
    │
    ▼
hub.mjs 守护进程 ── Chrome CDP (9333) ── 专用 Chrome profile ── 各平台创作者后台
    │                                                    │
    ├─ data/hub.db (SQLite)                             ├─ publisher 插件 (:8765 bridge)
    ├─ feishu.mjs ──▶ 飞书群机器人卡片                   └─ cloudflared tunnel (可选远程)
    └─ web.mjs ────▶ :8787 大屏 / :8788 demo 假数据      📱 iPhone Scriptable widget (可选)
```

关键边界：**国内四家 = manual 模式（填好就停等人点）**；其余四家（X/YouTube/IG/站点）= auto 模式（回读一致后自动提交）。

## 3 依赖与环境门槛

| 项 | 要求 | 本机状态 |
|---|---|---|
| OS | macOS 硬约束 | ✅ darwin |
| Node.js | ≥ 22.5（node:sqlite 内置） | ✅ v22.22.2 |
| Google Chrome | CDP 端口 9333 可调 | ✅ 已装 |
| 姊妹仓库 publisher | 需独立 clone 到 pluginDir | ❌ 未装 |
| 专用 Chrome profile | chrome-profile/ 必须全新隔离 | ❌ 未建 |
| 各平台登录态 | 在专用 profile 里手动扫码 | ❌ 未做 |
| NAS SMB 共享 | rootPath 指向的成片目录 | ❌ 未挂载 |
| 飞书 webhook | board/feishu 通知用 | ❌ 无 |

**结论**：基础条件三满足、运行时凭据全缺。**demo.mjs 可起假数据大屏，但真工作流无法复现**。详见 `references/test-report.md`。

## 4 三级上手路线（来自 README）

| 级别 | 能得到 | 要装的 | 时间 |
|---|---|---|---|
| L1 只看数据 | 粉丝数、播放互动、大屏、飞书日报 | 麦田本体；专用 Chrome 登录各平台；已有期用 `hub adopt` 登记 | ~30 min |
| L2 分发 | 一期一次填好七平台，定时，自动取链接 | + 麦田发布助手（publisher 插件）；+ 发布 skill（或手写 publish.json） | +1 h |
| L3 转化 | 每期带来的注册和收入归因 | + 自有站点按 `src/site.mjs` 接口接入 | 看站点 |

## 5 hub.mjs 命令全景

| 命令 | 作用 | 是否改远端状态 |
|---|---|---|
| `plan [dir]` | 登记进分发计划 | ❌ 仅本地 SQLite |
| `run <dir>` | 发一期（fill → 停 wait 人工） | ⚠️ 写 db + 驱动浏览器填写表单 |
| `status [id] [--logs]` | 查状态 | ❌ |
| `sync <id>` | 取链接、回填 md 的「已发布」行 | ⚠️ 读取各平台创作者后台页面 |
| `mark <id> <platform> <state>` | 手动修状态 | ❌ |
| `adopt <dir>` | 登记已发的期（不上传） | ❌ |
| `metrics [id]` | 采流量并发日报 | ⚠️ 读各平台公开数据 |
| `followers` | 采粉丝数 | ⚠️ |
| `review <id> [days]` | 复盘（第 1/3/7 天自动触发） | ❌ 纯计算 |
| `weekly` | 周报 | ❌ |
| `board` | 同步飞书多维表格 | ⚠️ 写外部表 |
| `daemon` | 常驻守护（装 launchd plist） | ⚠️ 长期后台 |
| `init` | 首次安装向导 | ❌ 仅生成本地 config.json |
| `demo` | 假数据大屏（:8788） | ❌ 完全离线 |

## 6 合规硬约束

1. **只读静态文档与 grep**：不启动 node 进程、不连 localhost:8765/9333/8787/8788、不开 headless browser。
2. **不生成 / 修改 config.json、chrome-profile/、data/hub.db**。
3. **不代写「发布素材.md」或 publish.json**。
4. **不输出任何飞书 webhook URL、web.key、extensionId**。
5. **不指导绕过平台反自动化机制**（如脚本点击、cookie 复用、fingerprint 伪造）。
6. MIT 授权下允许任意用途；但本包内容仅为学习参考，不对真实运行时的稳定性背书。
7. README 显式说「各平台的坑实战总结」——这是作者**亲身踩过的**，不代表官方立场，也不构成任何平台的合规保证。

## 7 高频坑（本包最值钱的发现）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | macOS only — Linux/WSL/Windows 全挂 | 🔴 高 |
| P2 | 专用 Chrome profile 必须独立于日常浏览器 | 🔴 高 |
| P3 | 国内四家不自动提交 —— 代码故意写的 | 🔴 高 |
| P4 | 成片必须 faststart（否则小红书报「无视频流信息」） | 🟡 中 |
| P5 | 同一条视频每个平台只传一次，反复重传必触发风控 | 🟡 中 |
| P6 | YouTube Studio 定时比 CDP 看到的更准，先查列表再下结论 | 🟢 低 |
| P7 | 视频号定时可能被平台偷偷改成别的时间（实测 +2h） | 🟡 中 |
| P8 | X 长文+视频帖引用长文是双步流程，走 tools/x-article-quote.mjs | 🟢 低 |
| P9 | 专用 Chrome 卡死用 `curl :9333/json/close/<id>` 关标签页，不用 browser.close() | 🟢 低 |
| P10 | demo.mjs 只能看假数据，不能当真实工作台 | 🟡 中 |
| P11 | publisher 插件是姊妹仓库，本仓不含 adapter 逻辑 | 🔴 高 |
| P12 | web.login=feishu 验证码 ≠ 免密全通，飞书挂了直接锁死 | 🟡 中 |

## 8 口径差异与核实记录

11 条 verified diffs（见 `data/diffs.json`），核心结论：

- D1: install.sh 是安全的一键安装，但之后仍需手动填凭据
- D2: manual/auto 双列表是**刻意设计**而非功能缺失
- D3: 全仓 grep password 零命中，隐私声明属实
- D4: Node ≥22.5 确实用了 node:sqlite
- D5: SKILL.md 流程 9 步顺序强制执行
- D6: widgetToken 与 web.key 分离，设计上是安全的只读隔离
- D7: x-article-quote.mjs 在 publisher 插件里，不在本仓
- D8: utm_campaign 归因链条依赖站点侧配合
- D9: NAS SMB 断连自动重试属实
- D10: 视频号定时漂移有实测案例
- D11: web.key 强制 401 拦截属实
- D12: config.example.json 凭据全是 xxx 占位符

## 9 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/maitian

python3 scripts/maitian.py stats                          # 仓库统计
python3 scripts/maitian.py modules                        # 18 个核心模块清单
python3 scripts/maitian.py commands                       # hub.mjs 14 条命令摘要
python3 scripts/maitian.py find faststart                 # 跨所有索引搜索
python3 scripts/maitian.py stats --json                   # JSON 输出便于脚本处理
```

刷新：`python3 scripts/build_index.py`（从零重建 data/*.json，手写的 safety/pitfalls/diffs/verification 不被覆盖）。

## 10 目录结构

```
SKILL.md                           本离线手册入口
data/                              8 个 JSON 索引
  ├── maitian.json     仓库元数据 + 14 条命令
  ├── files.json       59 镜像文件清单
  ├── modules.json     18 核心模块职责
  ├── config.json      23 配置字段释义
  ├── links.json       上游链接
  ├── safety.json      7 条合规硬约束
  ├── pitfalls.json    12 高频坑
  ├── diffs.json       11 条口径差异
  └── verification.json  10 条核实记录
references/                        可读文档
  ├── setup.md           本机复跑步骤（仅供阅读，不代执行）
  └── test-report.md     测试报告（demo.mjs 可跑，生产链路凭据全缺）
scripts/                           Python CLI + 索引重建
  ├── maitian.py         4 个子命令（stats/modules/commands/find）
  └── build_index.py     从零重建 data/*.json
upstream/                          59 文件原样镜像
  ├── src/               18 个 .mjs 核心模块
  ├── skills/maitian-publish/   发布 skill（167 行 SKILL.md）
  ├── config.example.json        配置字段全集（凭据均为占位符）
  ├── scripts/install*.sh        一键安装脚本
  ├── docs/screenshots/          （本包排除原图，保留路径说明）
  └── README.md              229 行完整文档
```
