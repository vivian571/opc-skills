---
name: agent-skills
description: >-
  Addy Osmani 出品的 25 个工程方法论技能集合：覆盖 Define → Plan → Build → Verify → Review → Ship 全生命周期，含 9 条 slash commands、Tier-2 trigger/routing 评测框架与 SessionStart hook。
  本包只做离线索引与上游文档查阅——不运行 run-evals.js、不部署 hooks、不代写 SPEC.md/tasks/plan.md/CONSTRAINTS.md；用户可自行决定何时触发某个 skill。
  常见坑：per-skill npx install 会缺根 references/ 目录；marketplace 默认走 SSH 需配 key；/build auto 单审批后仍会在高风险步骤停下等 sign-off；spec path 严格匹配 README 不算 spec；constraint-driven-development 中的约束不是建议而是 enforced gate。
---

# agent-skills · 离线索引与上游文档手册

> 上游：`addyosmani/agent-skills` · MIT / ★118,007（核实快照）· 25 skills / 9 commands / Tier-2+3 evals
> 镜像：`upstream/` 275 文件 / 1.5 MB（排除 evals/fixtures 与 hooks 的重复路径），完整上游见 `https://github.com/addyosmani/agent-skills`

## 1 这是什么 / 不是什么

**是**：Addy Osmani 出品的一套「生产级工程工作流 skill」集合，按 SDLC 六阶段组织 25 个独立 skill，每个都带标准 YAML frontmatter + 六大章节（Overview / When to Use / Process / Common Rationalizations / Red Flags / Verification）。配套 9 条 slash commands、Tier-2 trigger/routing 评测框架、可插拔 Tier-3 behavioral eval、hooks/session-start.sh 做 meta-skill 注入。

**不是**：可运行的 SDK 或业务代码库——这是方法论参考库，价值在于让 agent "跟着流程走"而非 "跑起来看结果"。本包不做任何自动化执行，只提供离线查阅能力。

## 2 收录口径

1. **元数据**：GitHub API 取 star/fork/pushed_at/license/default_branch，codeload ZIP 镜像所有上游源码与文档。
2. **Skill 清单**：解析 25 个 `skills/*/SKILL.md` 的 YAML frontmatter，提取 name/description，标注所属 Phase。
3. **命令文件**：索引 `commands/*.toml` 与 `.claude/commands/*.md`，读取 description 前 100 字符。
4. **评测用例**：解析 `evals/cases/*.json`，统计 positive/negative prompts 与 eval case 数。
5. **合规边界**：核读 `README.md` / `CLAUDE.md` / `CONTRIBUTING.md` + 本包 hard rules，明确只做离线查阅，不代理执行。

## 3 25 个 Skill 按 Phase 分布

| Phase | Skill |
|---|---|
| **Define** | interview-me / idea-refine / spec-driven-development |
| **Plan** | planning-and-task-breakdown |
| **Build** | incremental-implementation / test-driven-development / context-engineering / source-driven-development / doubt-driven-development / frontend-ui-engineering / api-and-interface-design |
| **Verify** | browser-testing-with-devtools / debugging-and-error-recovery |
| **Review** | code-review-and-quality / code-simplification / security-and-hardening / performance-optimization |
| **Ship** | git-workflow-and-versioning / ci-cd-and-automation / deprecation-and-migration / documentation-and-adrs / observability-and-instrumentation / shipping-and-launch |
| **Meta** | using-agent-skills |

## 4 9 条 Slash Commands

| Command | Phase | 核心原则 |
|---|---|---|
| `/spec` | Define | Spec before code |
| `/plan` | Plan | Small, atomic tasks |
| `/build` | Build | One slice at a time |
| `/build auto` | Build | 单审批跑完整个 plan（仍需人工放行高风险步骤） |
| `/test` | Verify | Tests are proof |
| `/constraints` | Review | Decide it once, enforce it everywhere |
| `/review` | Review | Improve code health |
| `/webperf` | Review | Measure before you optimize |
| `/code-simplify` | Review | Clarity over cleverness |
| `/ship` | Ship | Faster is safer |

Claude Code 中若内置命令重名（如 `/review`），使用 namespaced 形式：`/agent-skills:review`。

## 5 评测体系

- **Tier-2（CI 级）**：TF-IDF cosine similarity + rank-1 floor，检查 trigger 是否命中、routing 是否撞车。确定性、零 token 开销。
- **Tier-3（可选）**：headless claude 跑 `evals/fixtures/<skill>/` 下 fixture，打分期望行为。消耗 token，不在 CI 中运行。
- **Runner**：`scripts/run-evals.js`（Node.js 18+，零 npm deps）。

## 6 合规硬约束

1. 只跑本地静态读取与 grep，**不启动任何 agent host**（Claude Code / Codex / Copilot / Cline 等）。
2. **不运行 `run-evals.js --behavioral`**（会调用 Claude API 消费 token）。
3. **不部署 hooks**（`hooks/session-start.sh` 只是离线快照）。
4. **不生成 SPEC.md / tasks/plan.md / CONSTRAINTS.md**（用户自行决定何时创建）。
5. MIT 授权下允许任意用途；本包仅做学习参考，不对上游质量做任何背书。

## 7 关键坑（已写入 pitfalls.json）

- per-skill `npx skills add --skill <x>` 只会复制 `skills/<x>/`，**缺根 `references/` 目录**（路径失效）。整体安装或手动 cp 绕过。
- marketplace `add` 默认走 SSH clone，无 SSH key 报 Permission denied。改用 HTTPS URL 或 `git config url."https://github.com/".insteadOf git@github.com:`。
- `/build auto` **不是全自动**：单次审批后仍会在测试失败、spec 歧义、高风险操作（auth/迁移/支付/删除/密钥）时停下等 sign-off。
- spec 路径**严格匹配**（SPEC.md / docs/SPEC.md / spec/*），README 或其他 doc **不算 spec**。找不到就停并提示先跑 `/spec`。
- `constraint-driven-development` 里的约束是 **hard enforced gate**，不是软建议。违反即 stop。

## 8 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/agent-skills
python3 scripts/agent_skills.py stats                          # 仓库/索引统计
python3 scripts/agent_skills.py list                           # 25 技能清单（按 phase/search 过滤）
python3 scripts/agent_skills.py list --phase build             # 只看构建期 7 个 skill
python3 scripts/agent_skills.py evals                          # 25 份评测用例结构摘要
python3 scripts/agent_skills.py commands                       # 18 个命令文件摘要
python3 scripts/agent_skills.py find constraint                # 全文搜索关键词
python3 scripts/agent_skills.py stats --json                   # JSON 输出便于脚本处理
```

刷新：`python3 scripts/build_index.py`（从零网络重建索引，手写的 safety.json / pitfalls.json 不被覆盖）。

## 9 目录结构

```
SKILL.md                                  本离线手册入口
data/                                     7 个结构化索引 JSON
  ├── skills.json         25 skill 元数据 + phase 归属
  ├── evals.json          25 份 eval cases 统计
  ├── commands.json       9 toml + 9 claude md 摘要
  ├── links.json          上游链接
  ├── files.json          275 镜像文件清单
  ├── safety.json         6 条合规硬约束
  └── pitfalls.json       10 个高频坑
scripts/                                  离线 CLI + 索引重建
  ├── agent_skills.py       5 个子命令 CLI
  └── build_index.py        从零重建 data/*.json
references/                               （本包无外部 reference 需要，上游 references/ 在 upstream/ 内）
upstream/                                 275 文件原样镜像（跳过 evals/fixtures/ 与 hooks/ 去重）
  ├── skills/         25 个 SKILL.md
  ├── commands/       9 个 .toml
  ├── .claude/commands/   9 个 .md
  ├── evals/          评测框架与 fixtures
  ├── scripts/        run-evals.js + validate-*.js
  ├── hooks/          session-start.sh 等
  ├── agents/         4 个 persona markdown
  ├── references/     6 个 checklist
  └── docs/           setup guides
```
