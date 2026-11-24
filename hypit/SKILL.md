---
name: hypit
description: >-
  hypit-ai/hypit（★30,780 / 修改版 Apache-2.0 / TypeScript / v0.3.3 / 2026-07-29 建仓）的离线索引与 CLI 手册。
  给 AI Agent（Claude Code / Codex）用的视频创作系统：丢一个参考视频，Agent 克隆整套工作流（镜头、字幕、B-roll、特效），
  时间锚定到词而非秒；一个工作流出 100 个变体。含 SVML/SVS/SVRun 语义编排语言、Studio 预览编辑、
  88 个 @hypit/* 包、69 份 reference 文件（62 md + 7 示例）、21 类 playbook、多 Provider 模型接入。
  ⚠️ 合规硬约束：本包只做离线索引与 CLI 手册——不启动 hypit、不连生成服务、不登录、不 clone/换脸/渲染、不存凭据。
  上游主打「换脸/克隆爆款视频」，用户须自行取得肖像授权、标识 AI 生成、遵守版权与平台规则，自负其责。
---

# hypit · 离线索引与 CLI 手册

> 上游：`hypit-ai/hypit` · 修改版 Apache-2.0（NOASSERTION）· ★30,780 / fork 3,633（2026-11-20 核实快照）
> TypeScript / v0.3.3 / Node>=22.15 / pnpm 10.33 / 2026-07-29 建仓
> 镜像：`upstream/` 1,595 文件 / 15 MB（排除 .git / node_modules / dist / 二进制媒体）

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **给 Coding Agent 用的视频创作语言 + 系统** | 一键出片的 SaaS —— 需自备 Agent、模型账号与凭证 |
| **离线 CLI 手册 + 结构化索引** | 可运行的渲染器 —— 本包不执行任何 build/render/clone 操作 |
| **语义编排**：时间锚定到词，改台词时序自动 reflow | 按秒硬编码的剪辑脚本 |
| **88 个 @hypit/* 包 + 69 份 reference 文件** | 黑盒 —— 每个命令、包、语法均有源码可追溯 |
| **可纯代码渲染**：字幕/MG/视觉无需生成模型 | 必须付费调模型 —— 生成模型是可选的 |

## 2 核心概念

| 概念 | 含义 |
|---|---|
| **SVML**（`.svml`）| 作品主源：Script + media + components + composition。时间锚到词。 |
| **SVS**（`.svs`）| 可复用 Recipe / Voice Design / direction 定义 |
| **SVRun**（`.svrun`）| 一次执行：选 Author Source + 已有 Outputs + 目标 |
| **A-roll / B-roll** | 承载表演的主画面 / 辅助画面 |
| **Caption** | 词级字幕，跟随语音与镜头 |
| **Component / Script** | 共享布局运动的组件 / 以意义为主的时间组织 |
| **Timeline + Canvas** | 唯一有限时间线 + 画布；Extent/Window 为媒体局部域与绝对窗口 |
| **Run / Build / Result / Output** | 一次执行 / 执行实例 / 产出结果 / 可复用素材 |
| **Studio / Profile** | 可视化预览编辑 / 能力路由配置 |
| **Provider / Kit** | 模型服务连接器 / 模型特定提示词套件 |

## 3 安装（两条独立通道）

```bash
# 通道 1：生产知识 Skill
npx skills add hypit-ai/hypit -g

# 通道 2：可执行包（CLI/组件/Runtime/Studio）——Agent 首次用时自行准备
# 源码方式（开发者）：pnpm install --frozen-lockfile && ./hypit <cmd>
# 注意：Skill 与可执行是独立安装通道，各自更新；装 Skill ≠ 能渲染
```

前置：Node >=22.15.0 · pnpm 10.33.0 · TypeScript 5.9.3。
Hypit 框架免费；Coding Agent 与图像/视频/语音模型各自计费，装包不含生成额度。

## 4 CLI 根命令（`hypit <cmd>`）

| 类别 | 命令 |
|---|---|
| **信息/诊断** | `version` `cli` `doctor` `status` `activity` |
| **创作/校验** | `check`（预检）`plan`（计划）`pricing`（报价）`build`（构建） |
| **构建历史** | `builds` `history` `inspect` `get` `logs` |
| **结果/编辑** | `result`（含 edit）`cancel` |
| **凭证** | `auth`（含 login/logout）`studio`（预览编辑）`run` |

> 命令定义见 `upstream/packages/cli/src/command.ts`（genericCliCommandNames 17 个域无关根命令）。
> 本包不执行上述任何命令，仅索引。

## 5 模型与服务

| 类型 | 代表 |
|---|---|
| **推荐托管** | HypiHub（hypit.ai，一站式 WhisperX + 图像/视频/语音） |
| **自带 Key Provider** | BeatAPI / HiAPI / Monid / Pollo / Sume / TokenDance / Pollo / Video Rebirth |
| **生成模型** | Seedance / Seedream / GPT-Image / Grok Imagine / Nano Banana / Wan / Pixverse / Minimax-H3 / BACH |
| **语音** | ElevenLabs / FishAudio / Mimo / WhisperX（词级对齐） |
| **本地** | WhisperX local / OpenCV local / HTML local / browser-capture / yt-dlp |

Provider 凭证由用户在自己环境配置；本包不记录、不生成、不存储任何密钥。

## 6 合规硬约束（必须遵守）

1. **只做离线索引**：grep / 头读 / 结构化索引，不启动 hypit、不连服务、不 build/render、不下载视频。
2. **不生成/不存凭据**：不写 `.env`、不写 API key、不存 OAuth token。
3. **肖像权与同意**：不协助克隆真人肖像、不把他人面孔换到敏感/误导场景、不冒充真人。换脸/声音克隆须当事人明确授权（中国《民法典》肖像权/声音权、《深度合成管理规定》）。
4. **版权与来源**：不协助抓取受版权保护视频作素材、不规避平台版权保护/反爬。参考视频须自有或已授权。
5. **深度合成标识**：AI 生成/换脸视频对外发布须显著标识，不用于造谣、诈骗、虚假宣传。
6. **费用与授权**：不代替用户承诺支出；商业使用注意 License 多租户/商业再分发限制。
7. **自负其责**：本包仅为离线技术索引，不背书任何具体克隆行为。

## 7 高频坑（已写入 pitfalls.json）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | Skill 与可执行是两个独立安装通道，装 Skill ≠ 能渲染 | 🔴 高 |
| P2 | 安装 Skill 不含模型额度，Agent/模型各自计费 | 🔴 高 |
| P3 | Node>=22.15 + pnpm 10.33 + TS 5.9，旧 Node 在 bootstrap 失败 | 🟡 中 |
| P4 | 源码直接跑需 `pnpm install --frozen-lockfile` | 🟡 中 |
| P5 | License 非标准 Apache-2.0：禁多租户 SaaS/商业再分发/移除 LOGO | 🔴 高 |
| P6 | `.svml`/`.svs`/`.svrun` 三后缀职能不同，混用 Build 找不到源 | 🟡 中 |
| P7 | 时间锚到词而非秒，硬编码秒失去 reflow 优势 | 🟡 中 |
| P8 | 输出可完全不调生成模型（纯代码渲染字幕/MG/视觉） | 🟡 中 |
| P9 | 换脸/克隆合规红线：授权 + 标识，不冒充/造谣/侵权 | 🔴 高 |
| P10 | 服务选择与凭证配置是两件事 | 🟡 中 |
| P11 | Studio 预览 ≠ 最终导出 | ⚪ 低 |
| P12 | monorepo 88 个 @hypit/* 包，查功能先定位包名 | ⚪ 低 |

## 8 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/hypit

python3 scripts/hypit.py stats                       # 仓库统计
python3 scripts/hypit.py commands                    # CLI 根命令清单
python3 scripts/hypit.py concepts                    # 核心概念
python3 scripts/hypit.py packages                    # 88 个包（可 --grep 过滤）
python3 scripts/hypit.py refs                        # 69 份 reference 索引
python3 scripts/hypit.py playbooks                   # 12 类 playbook
python3 scripts/hypit.py svml                        # SVML/SVS/SVRun 文件清单
python3 scripts/hypit.py docs                        # 46 份文档
python3 scripts/hypit.py safety                      # 7 条合规约束
python3 scripts/hypit.py pitfalls                    # 12 高频坑
python3 scripts/hypit.py find "caption"              # 跨索引全文搜索
python3 scripts/hypit.py stats --json                # JSON 输出
```

刷新：`python3 scripts/build_index.py`（从零重建自动索引；手写 safety/pitfalls/diffs/verification/links 不被覆盖）。

## 9 目录结构

```
SKILL.md                           本离线手册入口
data/                              13 个 JSON 索引
  ├── hypit.json       仓库元数据 + 核心概念 + CLI + 服务
  ├── files.json       1,595 镜像文件清单
  ├── packages.json    88 个 @hypit/* 包摘要
  ├── references.json  69 份 reference 文件分组
  ├── playbooks.json   21 类 playbook（craft/formats）
  ├── docs.json        46 份文档索引
  ├── svml.json        SVML/SVS/SVRun 文件清单
  ├── examples_index.json  8 个示例工程
  ├── links.json       上游链接
  ├── safety.json      7 条合规硬约束
  ├── pitfalls.json    12 高频坑
  ├── diffs.json       6 条口径差异
  └── verification.json 10 条核实记录
scripts/
  ├── hypit.py         11 子命令离线 CLI
  └── build_index.py   从零重建自动索引
upstream/                          1,595 文件原样镜像
  ├── skills/hypit/SKILL.md       上游原始 Skill（生产知识）
  ├── skills/hypit/references/    69 份创作/环境/制作/playbook 文件
  ├── packages/                   88 个 @hypit/* 包源码
  ├── docs/                       中英双语 quickstart + guide
  ├── examples/                   8 个示例工程
  ├── bin/hypit.mjs               CLI 入口
  ├── package.json / LICENSE      版本与许可
```

## 10 与内容创作工作流的对接建议

以安的内容流水线（AI 出稿→人工终审）可直接借鉴 hypit 的两个思路，但**本包不执行**：

1. **时间锚到词**：字幕/MG/B-roll 绑到 Script 的词，改稿后时序自动对齐 —— 适合支付宝「以安」理财短视频改造。
2. **一稿多变体**：复用合成结构，只重新生成变化部分（换开头、换产品、换语言）—— 适合公众号矩阵多账号分发。

落地时仍遵循人工终审 + AI 生成标识 + 肖像/版权合规。
