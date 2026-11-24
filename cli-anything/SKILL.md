---
name: cli-anything
description: >-
  HKUDS/CLI-Anything 的离线索引与 CLI 手册：让所有软件 Agent 原生化。
  79 个软件的 agent-harness（Blender/GIMP/Inkscape/LibreOffice/Zotero/OBS/FreeCAD/Godot/QGIS 等）
  + 24 个公共 CLI + 70 份 SKILL.md + CLI-Hub 包管理器。Apache-2.0。
  只做离线索引——不执行 cli-hub install、不连网装包、不启动任何软件 harness。
---

# cli-anything 技能包

> **一句话**：HKUDS 把「软件 → Agent 可调用 CLI」这件事标准化了。79 个软件各有一个 agent-harness，
> 命令行 + JSON 输出，让 Claude Code / Cursor / Pi 等 Agent 直接驱动真实软件产出成果。

| 项目 | 值 |
|---|---|
| 源仓库 | [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) |
| Star / Fork | **63,599 / 5,776**（2026-11-24） |
| License | **Apache-2.0** |
| 语言 | Python ≥3.10（click ≥8.0） |
| 定位 | Making ALL Software Agent-Native |
| CLI-Hub | `pip install cli-anything-hub` → `cli-hub install <name>` |
| 规模 | 79 个 harness + 24 公共 CLI + 70 SKILL.md + 31 类 |

---

## 一、这是什么（机制层）

传统软件只服务人类（GUI）。CLI-Anything 的判断：**明天的用户是 Agent**。
它给每个软件写一层 **agent-harness**——把软件能力翻译成 CLI 命令 + 结构化 JSON 输出。

```
Agent（Claude Code / Cursor / Pi）
    │  调 CLI 命令（结构化输入）
    ▼
agent-harness（本项目，Python）
    │  驱动软件内部能力（API / 脚本 / 无头模式）
    ▼
真实软件（Blender / GIMP / LibreOffice / OBS ...）
    │  产出
    ▼
成果物（3D 场景 / CAD / 图 / 字幕 / 音频 / 文档 ...）
```

**为什么是 CLI 而不是 GUI 自动化**：结构化可组合、`--help` 自描述、JSON 输出免解析、跨系统轻量、
被 Claude Code 日跑千次验证过。

---

## 二、两种用法（Quick Start）

| 目标 | 入口 |
|---|---|
| **直接用现成 CLI 生态** | `pip install cli-anything-hub` → `cli-hub browse/install <name>` |
| **给新软件造 agent-native CLI** | 装 CLI-Anything 插件/skill → 跑 **7 阶段 harness 生成器** |

**7 阶段 harness 生成器**（`skill_generation/`）：
harness 生成 → 测试 → SKILL.md 生成（Phase 6.5）→ 渐进披露文档（v0.2.0 HARNESS.md + guides/）。
每个生成的 CLI 自带 AI 可发现的 skill 定义。

---

## 三、79 个 harness 分类速览

| 类别 | 代表软件 |
|---|---|
| **3d** | Blender、FreeCAD、MeerK40t |
| **image** | GIMP、Inkscape、Krita |
| **design** | Sketch、Ink/Stitch |
| **video** | Kdenlive、Shotcut、Openscreen、VideoCaptioner、QuietShrink、Palmier |
| **audio** | Audacity、WaveTone |
| **music** | MuseScore |
| **graphics** | RenderDoc、CloudCompare、3MF、Live2D、Nsight、CloudAnalyzer |
| **office** | LibreOffice、Calibre、Zotero、Mubu |
| **knowledge** | Obsidian、Joplin、SiYuan |
| **ai** | ComfyUI、Ollama、OpenWebUI、Novita、MiniMax、Magnific、NotebookLM、Dify、AnyGen |
| **web** | Browser、Safari、clibrowser、Exa、Mailchimp、TinyFish、Web Yu-pri |
| **devops** | PM2、iTerm2、JumpServer、CC Switch、ETH2、NSLogger |
| **automation** | n8n、EEZ Studio、MacroCLI |
| **diagrams** | Draw.io、Mermaid |
| **gamedev/game** | Godot、s&box、UEAtelier、Slay the Spire 2 |
| **科学/科研** | QGIS、Uni-Mol Tools、Stata |
| **其他** | Zoom、OBS、Firefly III、ChromaDB、WireMock、Intelwatch、Tigris、AdGuardHome |

完整清单用 CLI 的 `list` / `show <name>` 查。

---

## 四、离线 CLI 用法

```bash
cd ~/.workbuddy/skills/cli-anything

# 概览
python3 scripts/cli_anything.py stats

# 列出全部 CLI（可按类筛选）
python3 scripts/cli_anything.py list
python3 scripts/cli_anything.py list --category image

# 查单个 harness 详情（安装命令/入口/skill 路径）
python3 scripts/cli_anything.py show blender

# 按关键词搜
python3 scripts/cli_anything.py find "视频"

# 分类统计 / 公共 CLI / skills 清单
python3 scripts/cli_anything.py categories
python3 scripts/cli_anything.py public
python3 scripts/cli_anything.py skills

# 合规 / 坑点 / 链接
python3 scripts/cli_anything.py safety
python3 scripts/cli_anything.py pitfalls
python3 scripts/cli_anything.py links

# 所有命令支持 --json
python3 scripts/cli_anything.py stats --json
```

---

## 五、真正的安装（需联网，本包不代跑）

```bash
# 装包管理器
pip install cli-anything-hub

# 浏览 / 搜索 / 安装 harness
cli-hub browse
cli-hub search blender
cli-hub install blender

# 或直接从源码装某个 harness
pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=blender/agent-harness

# 给 Agent 装 skill（统一入口，2026-04-18 后规范）
npx skills add HKUDS/CLI-Anything --skill <skill-name> -g -y
```

---

## 六、目录结构

```
cli-anything/
├── SKILL.md              ← 本文件（离线手册入口）
├── data/
│   ├── registry.json     79 个 harness 元数据 + 31 类归类
│   ├── public_registry.json  24 个公共 CLI
│   ├── skills.json       70 份 SKILL.md 索引
│   ├── harnesses.json    69 个 agent-harness 目录
│   ├── safety.json       合规硬约束
│   ├── pitfalls.json     已知坑点
│   └── links.json        链接
├── upstream/             源码镜像（排除二进制资产）
│   ├── registry.json / public_registry.json / matrix_registry.json
│   ├── skills/           70 个 cli-anything-*/SKILL.md
│   ├── <software>/agent-harness/   各软件 harness 源码
│   ├── cli-hub/          PyPI 包管理器源码
│   ├── skill_generation/ 7 阶段生成器
│   └── README/README_CN/LICENSE/CONTRIBUTING
└── scripts/
    ├── cli_anything.py   离线索引 CLI（12 子命令）
    └── build_index.py    从 upstream/ 重建索引
```

---

## 七、合规硬约束（必读）

1. **本包只做离线索引与手册**——不执行 `cli-hub install`、不连网装包、不启动任何软件 harness、不跑 agent-harness 命令。
2. **Apache-2.0 允许商用/修改/分发**，但须保留版权声明与 LICENSE；含专利授权，修改后标注变更。
3. **装 harness ≠ 获得宿主软件授权**。Blender/GIMP/Zoom 等各有 EULA/开源协议，用户自负。
4. **联网 harness 风险**：Zoom/Intelwatch/Mailchimp/Exa 等可能触达账号/企业/OSINT 数据。禁止未授权采集他人数据，遵守平台 ToS 与《个保法》。
5. **历史漏洞**：GIMP Script-Fu 路径注入、Sketch token 路径穿越——上游已修，二次开发勿回退。
6. **本包不存任何 API key/token/凭据**。

---

## 八、破壁人视角

- **"Agent 原生化"是真趋势还是包装？** 是真趋势，但价值不在"79 个软件"这个数字，而在**把 GUI 能力翻译成结构化 CLI + JSON 输出**这个范式。谁都能写 wrapper，难的是让 wrapper 稳定到 Agent 能日跑千次不出错——这是 2461 个通过测试 + 渐进披露文档在守的东西。
- **Apache-2.0 + 社区 PR + CLI-Hub 包管理器 = 平台打法。** 和 AiToEarn 一样，开源是获客，registry/hub 是护城河。它在赌"Agent 调软件"的入口之争。
- **对你（以安）的实际价值**：你的内容流水线若要 Agent 驱动 LibreOffice（文档）/ MuseScore（配乐）/ OBS（录屏）/ Inkscape（图），这里是现成 harness。但**别指望一键全好**——每个 harness 都要真软件在本机装好，且 macOS/Windows 兼容性参差（坑点表里 LibreOffice/Blender 都踩过）。

---

*源：HKUDS/CLI-Anything（Apache-2.0）registry.json / skills/ / README.md*
*技术报告：arXiv:2606.03854 ｜ 本包离线索引，不连网装包。*
