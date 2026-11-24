---
name: t3code
description: >-
  pingdotgg/t3code（★68,446 / MIT / TypeScript / v0.1.11 / 2026-02-08 建仓）的离线索引与操作手册。
  T3 Code 是编码 Agent 的控制平面：一台服务器，桌面/网页/iOS/Android 四个客户端同时管理同一组会话，
  支持 Claude Code、Codex、Cursor、OpenCode、Grok Build、Antigravity、Kiro、Pi、Muse Code、fx 等任意 ACP agent。
  ⚠️ 合规硬约束：本包只做离线索引与查阅——不启动 t3 server、不连接 agent、不代登录、不存凭据。
  上游 MIT 许可无额外限制。
---

# t3code · 离线索引与操作手册

> 上游：`pingdotgg/t3code` · MIT License · ★68,446 / fork 11,775（2026-11-21 核实快照）
> TypeScript / v0.1.11 / pnpm monorepo / 2026-02-08 建仓
> 镜像：`upstream/` 9 份关键文档 + 内部架构笔记

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **Agent 控制平面**：一台 `t3` server → desktop/web/iOS/Android 四端统一视图 | 一次性调 AI 的 CLI —— 它是常驻服务 |
| **ACP 协议适配器**：任何支持 ACP 的 agent（Claude Code/Codex/Cursor/...）均可接入 | 只支持某一家的封闭产品 —— MIT 开源，可 fork 加 provider |
| **工作树隔离**：每个 thread 可用独立 git worktree，不影响主分支 | 全局替换你的终端 —— 原终端照常使用 |
| **离线索引**：9 份核心 user docs + internals overview | 替代官方文档 —— 完整 docs 见 <https://t3.codes/docs> |

## 2 核心概念

| 概念 | 含义 |
|---|---|
| **Control Plane** | 单 server（默认 :5555）→ 多客户端 |
| **Thread** | 一次会话，含历史、权限状态、source control 状态 |
| **Provider** | Agent 适配器；t3code 通过 ACP 协议与 agent 通信 |
| **Worktree** | Thread 可在独立 git worktree 中工作，避免污染主 repo |
| **Permission Modes** | Safe（只读）/ Suggested（建议执行）/ Elevated（直接执行） |
| **Remote Access** | Phone/app 通过局域网/Tailscale/T3 Connect 中继连回 server |
| **SnapShots** | 线程可视化状态捕获，方便 review/share |
| **ACP Registry** | Provider 注册中心，t3code ↔ agent 的标准契约 |

## 3 安装（三条通道）

```bash
# 桌面 App（推荐）
brew install --cask t3-code          # macOS
winget install T3Tools.T3Code        # Windows
yay -S t3code-bin                    # Arch Linux

# CLI 方式（启动 server + web UI）
curl -fsSL https://t3.codes/install.sh | sh

# 免安装尝试
npx t3@latest

# 手机 App
# iOS: https://apps.apple.com/us/app/t3-code-remote-claude-more/id6787819824
# Android: https://play.google.com/store/apps/details?id=com.t3tools.t3code
```

前置：已安装的 Coding Agent + 已登录（例如 `claude auth login` 或 `codex login`）。

## 4 CLI 根命令

```bash
t3                          # 启动 server（后台常驻），打开 web UI
npx t3@latest               # 免安装试用
t3 --help                   # 查看全部子命令
```

具体 subcommands 由 `apps/server/src/bin.ts` 定义，典型包括：
- `t3 status` — 查看 server/agent/provider 在线状态
- `t3 threads` — 列出所有 thread
- `t3 threads create` / `t3 threads open <id>` — 创建/切换 thread
- `t3 agents list` — 列出已注册的 providers
- `t3 auth` — 凭证管理入口（实际凭证存储在 system keychain/1Password）

本包不执行上述命令，仅索引路径。

## 5 支持的 Agent Providers

| Provider | 说明 |
|---|---|
| **Claude Code** | Anthropic 官方 terminal agent，primary focus |
| **Codex CLI** | OpenAI 出品 |
| **Cursor** | VS Code fork，内置 AI |
| **OpenCode** | oc.ai terminal agent |
| **Grok Build** | xAI coding agent |
| **Antigravity** | local-first agent（以安的项目里就有） |
| **Kiro / Pi / Muse Code / fx** | 其他 ACP-compatible agents |

## 6 目录结构

```
SKILL.md                           本离线手册入口
data/
  └── t3code.json                 仓库元数据 + 核心概念 + CLI + 架构
upstream/                          9 份关键文档镜像
  ├── install.md                  安装指南（desktop/cli/mobile）
  ├── composer.md                 消息输入与上下文编辑
  ├── permission-modes.md         三种权限模式详解
  ├── remote-access.md            手机/远程访问配置
  ├── outside-agents.md           MCP outside-agents 配置
  ├── providers-claude.md         Claude Code 接入细节
  ├── providers-codex.md          Codex CLI 接入细节
  ├── internal-overview.md        架构总览
scripts/
  └── t3code.py                   离线索引 CLI（stats/commands/providers/concepts）
```

## 7 高频坑

| # | 坑 | 严重度 |
|---|---|---|
| P1 | Skill 与可执行是两个独立通道 —— 装 Skill ≠ 能 connect agent | 🔴 高 |
| P2 | t3 server 需 agent 已登录才能起 thread（它不调凭证，用你自己的） | 🔴 高 |
| P3 | 每个 thread 共享同一个 server 进程，重启 thread = 新建会话，历史丢失 | 🟡 中 |
| P4 | Worktree 需要 git ≥ 2.25，老系统不生效 | 🟡 中 |
| P5 | Mobile app 必须能连到 server IP（默认同局域网，Tailscale 可跨网） | 🟡 中 |
| P6 | Provider 更新可能破坏 ACP 接口 —— 升级前查 release notes | 🟡 中 |
| P7 | SnapShots 只是可视 snapshot，不持久化代码变更 | ⚪ 低 |

## 8 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/t3code

python3 scripts/t3code.py stats                         # 仓库统计
python3 scripts/t3code.py commands                      # CLI 命令清单
python3 scripts/t3code.py providers                     # 支持的所有 agent provider
python3 scripts/t3code.py concepts                      # 核心概念
python3 scripts/t3code.py safety                        # 合规提示
python3 scripts/t3code.py pitfalls                      # 7 条高频坑
python3 scripts/t3code.py find "worktree"               # 跨索引全文搜索
python3 scripts/t3code.py stats --json                  # JSON 输出
```

## 9 合规提示

1. **只做离线索引**：grep / 头读 / 结构化索引，不启动 t3、不连 agent、不登录。
2. **凭证不在本包内**：t3code 用系统 keychain 或 1Password Connect，本包不记录任何密钥。
3. **MIT 无附加条件**：License 纯 MIT，商业使用/再分发/修改均自由。
4. **ACP 兼容性**：你负责确保所用 agent 版本与 t3code 版本兼容（各 provider README 内有最低要求）。
5. **隐私**：thread 内容经 server 转发给 agent，不要处理敏感机密信息在公共环境跑 t3。

## 10 源码位置参考

| 想了解什么 | 看哪里 |
|---|---|
| ACP 协议定义 | `packages/contracts/src/` + `packages/provider-core/src/client.ts` |
| 某 provider 实现 | `packages/provider-*/src/`（如 `provider-claude`、`provider-codex`）|
| Server 生命周期 | `apps/server/src/binMain.ts` |
| Desktop 入口 | `apps/desktop/src/boot.ts` |
| Web client | `apps/web/` |
| Mobile | GitHub release 里的 .ipa/.apk，源码在 `apps/mobile/`（私有仓库可见性待确认）|
| 贡献规范 | `AGENTS.md` + `CONTRIBUTING.md` |
