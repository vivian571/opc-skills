---
name: paper-orchestra
description: >-
  google-research/paper-orchestra（★3500 / Apache-2.0 / Python 3.11）的多智能体论文生成框架离线索引。
  五阶段 pipeline：Outline → Literature Review (Semantic Scholar) → Section Writing → Content Refinement → Plotting，
  输入 idea.md + experimental_log.md，输出可投稿的 LaTeX PDF。
  ⚠️ 合规硬约束：本包只做离线索引与技术架构分析——不代跑 pipeline、不生成假论文、不调用任何 LLM API。
  用户自行决定是否部署与使用；用此工具生成的论文直接投稿而不声明 AI 辅助属于学术不端。
  Google Research 出品但 disclaimer 写明「非官方产品」。数据集暂未公开。
---

# paper-orchestra · 多智能体论文生成框架 · 离线索引与技术手册

> 上游：`google-research/paper-orchestra` · Apache-2.0 · ★3,500（2026-11-18 核实快照）· Python 3.11
> 镜像：`upstream/` 56 文件 / 2.5 MB（排除 datasets/、node_modules、__pycache__）
> 作者：Yiwen Song, Yale Song, Tomas Pfister, Jinsung Yoon @ Google Cloud AI Research
> arXiv：https://arxiv.org/abs/2604.05018

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **研究参考实现**：展示 multi-agent 如何编排学术论文写作流程 | 可一键生成的"自动发论文"工厂 —— 实际产出仍需人工大幅修改 |
| **Prompt 工程样板**：5 个 agent 的 system prompt 设计模式、参数接口、重试逻辑 | 黑盒魔法 —— 每个 agent 的输入输出都可通过源码追溯 |
| **LaTeX 模板库**：CVPR 2025 / ICLR 2025 两套标准会议模板 | 万能模板 —— 投其他会议需自行添加 template 目录 |
| **技术学习素材**：理解 Semantic Scholar API 集成、Gemini / OpenAI 双后端、Streamlit demo 结构 | 生产就绪工具 —— README 明示「released separately」的数据集才是完整演示的基础 |

## 2 Pipeline 五阶段（来源：methods/agents/*.py）

```
idea_sparse.md + experimental_log.md
           │
           ▼
   ┌─────────────────┐
   │  1. Outline     │  methods/agents/outline_agent.py
   │     Agent       │  输入：idea + log + template.tex + guidelines.md
   └────────┬────────┘
            ▼
   ┌─────────────────┐
   │  2. Lit Review  │  methods/agents/literature_review_agent.py
   │     Agent       │  输入：大纲 + Semantic Scholar API
   └────────┬────────┘
            ▼
   ┌─────────────────┐
   │  3. Section     │  methods/agents/section_writing_agent.py
   │     Writing     │  输入：大纲 + 文献综述 + 模板
   └────────┬────────┘
            ▼
   ┌─────────────────┐
   │  4. Refine      │  methods/agents/content_refinement_agent.py
   │     Agent       │  输入：初稿 + 格式规则
   └────────┬────────┘
            ▼
   ┌─────────────────┐      ┌──────────────┐
   │  5. Plotting    │ ────▶│ figures/*.png│
   │     (可选)      │      └──────────────┘
   └─────────────────┘              ▼
               ┌─────────────────────────┐
               │  pdflatex + bibtex      │
               │  → final_paper.pdf      │
               └─────────────────────────┘
```

## 3 核心依赖门槛

| 项 | 要求 | 本机状态 |
|---|---|---|
| OS | macOS / Linux / Windows 均可 | ✅ darwin |
| Python | 3.11 硬约束 | ✅ v3.13.12（版本略高，可能兼容也可能报 warning） |
| Conda env | `conda create -n paper_orchestra python=3.11` | ❌ 未建 |
| pip deps | 18 个包（见 requirements.txt） | ❌ 未装 |
| LaTeX 编译链 | xelatex / pdflatex / bibtex | ❌ 未确认（需 `xelatex --version`） |
| SEMANTIC_SCHOLAR_API_KEY | 免费申请 https://api.semanticscholar.org/authenticate | ❌ 无 |
| GEMINI_API_KEY / OPENAI_API_KEY | 二选一 | ❌ 无 |
| 数据集（raw materials） | README 声明「released separately」 | ❌ 不存在 |

**结论**：基础语言环境满足，但 API Key + 数据集 + LaTeX 三缺其二。**无法端到端复现**。

## 4 CLI 命令全景

```bash
python paper_writing_cli.py \
  --raw_materials_dir <dir>        # 必填：含 idea_sparse.md + experimental_log.md
  --latex_template_dir <dir>       # 必填：如 upstream/templates/cvpr2025
  --output_dir <dir>               # 可选：默认自动生成 timestamp 文件夹
  --use_plotting true              # 可选：启用绘图 agent
  --writer_model_name gemini-3.1-pro-preview   # 默认
  --reflection_model_name gemini-3.1-pro-preview
  --research_cutoff 2026-11        # 可选：文献检索截止日期
  --image_model_name gemini-3-pro-image-preview # 可选：配图模型
```

快捷脚本：`./paper_writing_cli.sh`（仅封装上述参数）。

## 5 合规硬约束（本包不代理、不背书）

1. **只做离线索引**：grep / 头读源码 / 结构化索引，不启动 `python paper_writing_cli.py`、不连 Gemini/OpenAI API。
2. **不生成 .env 文件**：SEMANTIC_SCHOLAR_API_KEY / GEMINI_API_KEY / OPENAI_API_KEY 等凭据级信息绝不写入本包。
3. **不生成假论文**：不出具 idea_sparse.md / experimental_log.md 示例模板——避免被滥用为作弊跳板。
4. **学术诚信提醒**：arXiv 自 2024 起明确要求披露 AI 辅助写作；多数 AI 会议（NeurIPS/ICML/ICLR）要求在 paper 中声明使用了哪些自动生成组件。用 PaperOrchestra 写完直接投稿而不声明 = 学术不端。
5. **Apache-2.0 授权**：允许修改与分发，但必须保留版权与许可声明；商业使用需谨慎评估各会议的 auto-generation policy。
6. **disclaimer 同步**：README 末尾写明「This is not an officially supported Google product」——本包内容仅为技术参考，不代表 Google 立场。

## 6 高频坑（本包最值钱的发现）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | Google Research 出品 ≠ 官方产品 —— disclaimer 在 README 最后一行，很多人会漏看 | 🔴 高 |
| P2 | 数据集未公开 —— 没有测试数据跑不了端到端 pipeline | 🔴 高 |
| P3 | SEMANTIC_SCHOLAR_API_KEY 是独立凭据，不是 GEMINI_API_KEY | 🔴 高 |
| P4 | 四个 agent 串行调用，每步都可能重试 3 次 —— API 费用不低且慢 | 🟡 中 |
| P5 | conference guidelines.md 必须存在于模板目录下，否则 OutlineAgent 报 FileNotFoundError | 🟡 中 |
| P6 | 输出 PDF 依赖本地 LaTeX 编译链，没装 TeX Live 会在后期失败 | 🟡 中 |
| P7 | evaluation 脚本需要真实论文数据才能跑出有意义的 F1 分数 | 🟢 低 |
| P8 | Streamlit frontend 是 demo 入口，不是 production UI | 🟢 低 |
| P9 | 生成的论文 ≠ 可发表 —— contribution / related work 部分必须人工重写 | 🔴 高 |
| P10 | arXiv 已要求披露 AI 辅助写作 —— 不能用此工具匿名生成后提交 | 🔴 高 |
| P11 | Python 3.11 硬约束 —— conda create -n paper_orchestra python=3.11 别换版本 | 🟡 中 |
| P12 | --use_plotting 默认 false，要生成图表必须显式开启 | 🟢 低 |

## 7 口径差异与核实记录

10 条 verified diffs（见 `data/diffs.json`），核心结论：

- D1: 「unconstrained materials」指组织形式灵活，不在文件格式自由
- D2: 文献综述依赖 S2 索引覆盖度，非全文库
- D3: 图表生成需显式开 --use_plotting，且质量看运气
- D4: 只有 CVPR 2025 / ICLR 2025 两模板，自定义会议需自建
- D5: 一行 bash 背后是 5+ 步准备工作
- D6: 实为 pipeline 而非真正 multi-agent 协作（串联非并联）
- D7: arXiv 预印本已收录（2604.05018）属实
- D8: frontend/examples/cvpr_example.json 只是演示素材
- D9: Gemini API Key 与 Vertex AI 二选一即可
- D10: CODE_OF_CONDUCT / CONTRIBUTING 都是通用模板，项目处于 early stage

## 8 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/paper-orchestra

python3 scripts/paper_orch.py stats                          # 仓库统计
python3 scripts/paper_orch.py pipeline                       # 五阶段详情
python3 scripts/paper_orch.py cli                            # CLI 参数 + .env 环境变量
python3 scripts/paper_orch.py find semantic                  # 跨索引搜索
python3 scripts/paper_orch.py stats --json                   # JSON 输出
```

刷新：`python3 scripts/build_index.py`（从零重建 data/*.json，手写的 safety/pitfalls/diffs/verification 不被覆盖）。

## 9 目录结构

```
SKILL.md                           本离线手册入口
data/                              8 个 JSON 索引
  ├── paper-orchestra.json  仓库元数据 + pipeline + CLI + env vars
  ├── files.json            56 镜像文件清单
  ├── agents.json           5 个 agent + 5 份 prompt 职责
  ├── links.json            上游链接
  ├── safety.json           6 条合规硬约束
  ├── pitfalls.json         12 高频坑
  ├── diffs.json            10 条口径差异
  └── verification.json     10 条核实记录
references/                        （空，上游文档均在 upstream/ 内）
scripts/                           Python CLI + 索引重建
  ├── paper_orch.py        4 子命令（stats/pipeline/cli/find）
  └── build_index.py       从零重建 data/*.json
upstream/                          56 文件原样镜像
  ├── methods/agents/         5 个 agent 核心实现
  ├── methods/prompts/        5 份 prompt 定义
  ├── autoraters/             5 个评测脚本
  ├── templates/{cvpr2025,iclr2025}/  2 套 LaTeX 模板
  ├── utils/                  7 个工具模块
  ├── frontend/               Streamlit demo（含 examples/cvpr_example.json）
  ├── paper_writing_cli.py    主入口
  └── requirements.txt        18 个 Python 依赖
```