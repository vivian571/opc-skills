---
name: supervisor-skills
description: >-
  HKUSTDial/Supervisor-Skills（★13,160 / CC BY-NC-SA 4.0 / v2.1.0 / 2026-04-19 建仓）的离线索引与 CLI 手册。
  港科广骆昱宇博导把十年顶会（SIGMOD/VLDB/ICML/NeurIPS）发表与审稿经验炼成的 12 个科研 AI 技能 +
  36 份 handbook 指南。从 Idea 五维评估、综述深调、六段式 Intro、证据门控论文写作、顶会审稿自查到 Rebuttal，
  覆盖论文全生命周期。⚠️ 合规硬约束：本包只做离线索引——不调用模型、不检索、不代写代投、不写项目文件。
  CC BY-NC-SA 4.0 非商业限制；引用须用户自行联网核验。
---

# supervisor-skills · 离线索引与 CLI 手册

> 上游：`HKUSTDial/Supervisor-Skills` · CC BY-NC-SA 4.0 · ★13,160 / fork 785（2026-11-22 核实快照）
> Python + Markdown / v2.1.0 / 2026-04-19 建仓 / 港科广 骆昱宇
> 镜像：`upstream/` 128 份 md（12 技能 + 36 handbook + 12 others + 中英 README）

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **博导经验蒸馏**：十年顶会发表/审稿直觉，炼成结构化可执行技能 | 万能 Prompt —— 强调判断力与门控（when/when-not），不是套模板 |
| **Guide + Skills 双轨**：handbook 讲"道"，skills 讲"器" | 代写代投服务 —— 产出是辅助建议，学术诚信由用户负责 |
| **覆盖论文全生命周期**：Idea→调研→写作→自查→Rebuttal | 联网检索工具 —— 引用核验需用户在联网环境自行完成 |
| **离线索引 + CLI**：12 技能 + 36 文档可检索 | 模型调用器 —— 本包不调任何模型、不写项目文件 |

核心命题：**科研的"最后一公里"不是方法论缺失，而是经验、品味、判断力的综合考验。** 卓越成果无法靠万能 Prompt 催生。

## 2 核心概念

| 概念 | 含义 |
|---|---|
| **最后一公里问题** | 读了再多指南，面对自己课题仍不知如何下笔；缺的是判断力 |
| **Guide + Skills 双轨制** | handbook 系统理论 + skills 可执行 AI 技能，理解"道"才能用好"器" |
| **五维框架** | Higher / Faster / Stronger / Cheaper / Broader — Idea 评估与构思坐标系 |
| **审稿人视角** | Novel Problem / Novel Method / Nice Story / Nice Presentation 四维论文质量 |
| **证据门控** | paper-writer 每个事实声明可溯源，引用经独立核查，绝不编造 |
| **学科范式路由** | 评估/评审技能按学科范式切换框架，不用一把尺子量所有领域 |
| **条件说服模型** | rebuttal-guidance：识别审稿人心态 X → 匹配策略 Y → 生成回应 |
| **Ducktor** | Agent 原生完全体（独立项目），把科研判断讲给用户听，而非只点确认 |

## 3 12 个科研技能（按工作流）

| 阶段 | 技能 | 作用 |
|---|---|---|
| **构思与调研** | `idea-evaluator` | Idea 五维评估 + 能力匹配 + 范式转移探测 + 致命缺陷审计 |
| | `deep-research` | 综述级深调：多视角检索 + 引用核验 + MECE 综合 |
| | `vibe-research-workflow` | Vibe Coding / Figure / Writing 全流程实战 |
| **写作** | `tech-paper-template` | 技术类 Full Paper 完整逻辑链梳理 |
| | `intro-drafter` | 基于 Flowchart 思考模型，直出六段式 Intro 正文 |
| | `paper-writer` | 证据门控正文写作，每个声明可溯源 |
| | `benchmark-paper-template` | Benchmark/Eval 类论文评估逻辑与实验设计 |
| **自查与润色** | `paper-polish` | 忠于原意的润色，去 AI 腔，动含义处逐条标出 |
| | `pre-submission-reviewer` | 顶会审稿人视角全面审查 + 语法易错点 |
| **可视化** | `figure-designer` | 动机图/总览图/实验图设计建议 |
| | `drawio-reconstruction` *(others)* | 参考图重建为可编辑 .drawio |
| **投稿后** | `rebuttal-guidance` *(others)* | 条件说服模型生成逐条 Rebuttal 指导 |

`skills/` 是作者团队核心技能；`others/` 是外部作者贡献、由作者维护，用前看各自 LICENSE。

## 4 Handbook 六章（道）

| 章 | 内容 |
|---|---|
| 01 宏观认识 | 从审稿人视角看论文质量 + 博士生科研入门讲义 PDF |
| 02 Idea 构思 | 生命周期、五维思框架、颠覆式创新 |
| 03 论文写作 | 全流程、Intro 思考模型、技术类/Benchmark 模板、Checklist |
| 04 科研作图 | 动机图、总览图、实验图范式 + 绘图 Checklist |
| 05 前沿实战 | Vibe Research/Coding 入门 + 李伯岩实战经验 |
| 06 顶会案例 | Alpha-SQL (ICML'25)、AFlow (ICLR'25)、LEAD (VLDB'26) 剖析 |

每章有中英双版，共 36 份文档。`upstream/handbook/` 中文，`upstream/handbook-en/` 英文。

## 5 安装上游技能（联网环境）

把这段发给 AI 助手（Claude Code / Cursor / Codex）：
```
Help me install Supervisor-Skills from https://github.com/HKUSTDial/Supervisor-Skills with Skills.
```

Agent 原生完全体（另装）：
```
帮我安装 Ducktor 插件：https://github.com/HKUSTDial/Ducktor
照仓库 INSTALL.md 的步骤装好，装完告诉我怎么开始用。
```

本离线包不执行安装，仅供查阅与检索。

## 6 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/supervisor-skills

python3 scripts/supervisor.py stats                          # 仓库统计
python3 scripts/supervisor.py skills                         # 12 技能清单
python3 scripts/supervisor.py skills --group others          # 只看外部贡献技能
python3 scripts/supervisor.py skill idea-evaluator           # 单技能详情 + 引用文件
python3 scripts/supervisor.py handbook --chapter 03          # 按章过滤（03=写作）
python3 scripts/supervisor.py concepts                       # 核心概念
python3 scripts/supervisor.py workflow                       # 阶段→技能映射
python3 scripts/supervisor.py safety                         # 合规提示
python3 scripts/supervisor.py pitfalls                       # 高频坑
python3 scripts/supervisor.py find "证据门控"                # 跨镜像全文搜索
python3 scripts/supervisor.py stats --json                   # JSON 输出
```

索引刷新：`python3 scripts/build_index.py`（从 upstream/ 重新生成 data/*.json）。

## 7 合规硬约束（必须遵守）

1. **仅离线索引**：grep / 头读 / 检索，不调用模型、不写项目文件、不代替用户对外发投稿内容。
2. **CC BY-NC-SA 4.0**：署名-非商业-相同方式共享。商业使用需单独授权；改编须同协议并注明出处（骆昱宇 & contributors）。
3. **引用必须核验**：技能本身强调引用经真实检索核验；本离线包无联网检索，引用须用户自行在联网环境核实。**这是最大风险点。**
4. **学术诚信**：产出是辅助建议，非代写代投。用户对原创性、数据真实性、署名负全责。
5. **不替代导师**：科研判断建议仅供参考，重大方向决策仍需与真实导师/同行讨论。

## 8 高频坑

| # | 坑 | 严重度 |
|---|---|---|
| P1 | CC BY-NC 非商业限制 —— 企业内训/付费咨询/产品集成需单独授权 | 🔴 |
| P2 | 引用幻觉风险 —— 本包无联网检索，引用须用户自行核实 | 🔴 |
| P3 | 技能是方法论不是模板套用 —— 跳过 when/when-not 门控会失去价值 | 🟡 |
| P4 | `skills/` 与 `others/` 来源不同，许可成熟度可能不同 | 🟡 |
| P5 | 技能正文多为英文，中文描述是本包补的索引；执行须读 upstream 原文 | 🟡 |
| P6 | Ducktor 是独立项目，本包只含 Supervisor-Skills 本体 | ⚪ |

## 9 目录结构

```
SKILL.md                          本离线手册入口
data/
  ├── supervisor.json             仓库元数据 + 核心概念 + 工作流 + 相关项目
  ├── skills.json                 12 技能索引（名称/描述/引用文件/行数）
  └── handbook.json               36 文档索引（章节/标题/行数）
scripts/
  ├── supervisor.py               离线索引 CLI（10 子命令，支持 --json）
  └── build_index.py              从 upstream/ 重建索引
upstream/                         128 份 md 原样镜像
  ├── README.md / README.en.md    中英主说明
  ├── CHANGELOG.md                v1.0 → v2.1.0 变更
  ├── llms.txt                    上游给 LLM 的内容清单
  ├── LICENSE                     CC BY-NC-SA 4.0 全文
  ├── skills/                     10 个核心技能（SKILL.md + references/）
  ├── others/                     2 个外部贡献技能
  ├── handbook/                   中文系统指南（6 章 + PDF 讲义）
  └── handbook-en/                英文版指南
```

## 10 与以安工作流的关联

- **科研方法论**可迁移到内容选题与深度写作：五维框架（更高/更快/更强/更省/更广）本质是"改进维度穷举法"，可用于公众号选题评估。
- **证据门控**思想契合 Content OS 3.0 的事实核查要求：每个事实声明可溯源，引用独立核验。
- **条件说服模型**（Rebuttal）可迁移到评论区互动与观点回应：先识别对方心态，再匹配回应策略。
- 落地时仍遵循：AI 出稿 → 人工终审；引用须联网核实；CC BY-NC 非商业边界。
