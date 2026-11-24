---
name: zlib
description: >-
  heartleo/zlib（★2,516 / MIT / Go / v0.0.11+ / 2026-04-10 建仓）的离线索引与 CLI 手册。
  Z-Library 的现代化命令行/TUI 客户端：搜索/下载/浏览/收藏/历史/配额/网络诊断，
  发送到 Kindle（SMTP）/ WeRead，元数据编辑，TUI 交互，MCP Server + Agent 插件（Claude/Codex/Grok/Claude Code）。
  ⚠️ 合规硬约束：本包只做离线索引与 CLI 手册——不代执行下载/登录/投递/编辑操作，不存凭据，不指导绕过版权/反爬虫。
  用户自行决定是否使用，自负其责（Z-Library 自身版权争议大，下载受版权保护内容可能违法）。
---

# zlib · 离线索引与 CLI 手册

> 上游：`heartleo/zlib` · MIT · ★2,516（2026-11-20 核实快照）· Go / v0.0.11+ / 2026-04-10 建仓
> 镜像：`upstream/` 444 文件 / 6.2 MB（排除 .git / build / node_modules / 二进制）

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **Z-Library 官方无、社区最强 CLI/TUI 客户端** | Z-Library 官方产品 —— 社区维护，非官方背书 |
| **离线 CLI 手册 + 结构化索引** | 可直接运行的下载器 —— 本包不执行任何下载/登录/投递操作 |
| **AI Agent 集成框架**：MCP Server + 7 个 Skill（Claude/Codex/Grok/Claude Code） | 黑盒魔法 —— 每个命令、退出码、环境变量均可追溯源码 |
| **多模型 Provider 无关**：CLI 只管 Z-Library 交互，模型由 Agent 侧配置 | 模型绑定产品 —— 模型完全由上层 Agent 决定，CLI 无感知 |

## 2 核心功能

| 类别 | 命令 | 关键参数 |
|---|---|---|
| **搜索/浏览** | `zlib search "query" --json --count 10 [--ext epub\|pdf]` | `--page` 分页、`--ext` 多值过滤 |
| **收藏/推荐** | `zlib favorites/recommended/most-popular --json` | `--page` 分页 |
| **历史/配额** | `zlib history/profile --json` | `history --format epub`、`profile --json` 含 quota |
| **网络诊断** | `zlib doctor --json [--proxy "proxy-url"]` | 只查域名可达性，不验证登录 |
| **登录** | `zlib login --domain <URL> [--cookies ./cookies.txt]` | 支持 cookies 导入 |
| **下载** | `zlib download "id:hash" [--dir <dir>] --json [--send-to-kindle\|--send-to-weread]` | 退出码 0/1/3/4/5/130 语义明确 |
| **Kindle 投递** | `zlib kindle send <file> [--json]` | 需 ZLIB_SMTP_PWD，仅 EPUB/PDF/AZW3/TXT |
| **WeRead 导入** | `zlib weread import <file> --json` | exit 3 需用户手机验证码，额度限制不可重试 |
| **元数据编辑** | `zlib meta <file> [--fetch --edit --json]` | CLI/MCP 双路径，`--fetch --edit --json` 完整流程 |
| **TUI 交互** | `zlib tui` | 需 TTY，键位 `/` `j/k` `←→` `Enter` `Ctrl+F` `Esc` `/quit` |
| **MCP Server** | `zlib mcp [--read-only]` | stdio，需 PATH 有 zlib 且已登录 |

## 3 安装方式（4 选 1）

```bash
# 1. Homebrew（推荐 macOS/Linux）
brew install heartleo/tap/zlib-cli    # 注意公式名是 zlib-cli，不是 zlib

# 2. 一键安装脚本（可能需 sudo）
curl -fsSL https://raw.githubusercontent.com/heartleo/zlib/main/install.sh | sh

# 3. Windows winget
winget install --id heartleo.zlib --exact

# 4. Go 源码构建
go build ./cmd/zlib
```

## 4 关键环境变量

| 变量 | 用途 | 优先级 |
|---|---|---|
| `ZLIB_DOWNLOAD_DIR` | 下载目录（默认当前目录） | 环境变量 > .env > ~/.config/zlib/.env |
| `ZLIB_SMTP_PWD` | Kindle SMTP 密码（发送必填） | 同上 |
| `ZLIB_PROXY` | HTTP 代理（仅 HTTP，不影响 SMTP） | 同上 |
| `ZLIB_DOMAIN` | 默认域名（login 时更新 .env） | 同上 |

## 5 退出码语义（必须处理）

| 码 | 含义 | 处理建议 |
|---|---|---|
| 0 | 成功 | 继续 |
| 1 | 普通错误 | 读 stderr |
| 3 | 需重新登录 | 提示用户 `zlib login` |
| 4 | 网络/镜像问题 | 建议 `zlib doctor` |
| 5 | 文件保存成功但投递失败 | 读 JSON `kindle.error`/`weread.error` |
| 130 | 用户取消 | 正常中断 |

## 6 合规硬约束

1. **只做离线索引**：grep / 头读 / 结构化索引，不启动 `zlib` CLI、不连 Z-Library、不登录、不下载、不发邮件。
2. **不生成凭据**：不写 `.env`、不存 `ZLIB_SMTP_PWD` / 会话 cookies / 密码。
3. **不绕过风控**：不指导如何绕过 Z-Library 反爬虫、域名封锁、登录限制。
4. **不侵犯版权**：不代下载受版权保护电子书、不协助规避版权保护。
5. **同步提醒**：Z-Library 自身版权争议大，下载受版权保护内容可能违法；Kindle/WeRead 投递有额度与验证限制。

## 6 高频坑（已写入 pitfalls.json）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | Homebrew 公式名已改为 `zlib-cli`，旧命令 `brew install zlib` 装错包 | 🔴 高 |
| P2 | `zlib doctor` 只查域名可达性，不验证登录状态 | 🔴 高 |
| P3 | 登录失败三大原因：域名失效/密码错/需导入 cookies | 🔴 高 |
| P4 | 配置优先级：环境变量 > .env > ~/.config/zlib/.env | 🟡 中 |
| P5 | `ZLIB_PROXY` 仅影响 HTTP，不影响 Kindle SMTP | 🟡 中 |
| P6 | Kindle 仅接受 EPUB/PDF/AZW3/TXT，拒绝 MOBI；大小限制 | 🟡 中 |
| P7 | Kindle 发送成功 ≠ Kindle 收到（需查白名单/垃圾箱） | 🔴 高 |
| P8 | WeRead 导入 exit 3 需用户手机验证码，额度限制不可重试 | 🟡 中 |
| P9 | `zlib tui` 必须有 TTY，CI/脚本里跑会报错 | 🟡 中 |
| P10 | Google Books 查询无 Key 会被限流（exit 4） | 🟡 中 |
| P11 | WeRead 导入失败不可重试，`already_existed: true` 说明已存在 | 🟡 中 |
| P12 | MCP Server 需 zlib 在 PATH 且已登录 | 🟡 中 |

## 7 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/zlib

python3 scripts/zlib.py stats                          # 仓库统计
python3 scripts/zlib.py commands                       # 14 条 CLI 命令清单
python3 scripts/zlib.py skills                         # 6 个 Skill 模块
python3 scripts/zlib.py env                            # 4 个环境变量
python3 scripts/zlib.py codes                          # 6 个退出码
python3 scripts/zlib.py keys                           # 6 个 TUI 键位
python3 scripts/zlib.py agents                         # 4 种 Agent 集成方式
python3 scripts/zlib.py find smtp                      # 全文搜索关键词
python3 scripts/zlib.py stats --json                   # JSON 输出
```

刷新：`python3 scripts/build_index.py`（从零重建 data/*.json，手写的 safety/pitfalls/diffs/verification 不被覆盖）。

## 8 目录结构

```
SKILL.md                           本离线手册入口
data/                              9 个 JSON 索引
  ├── zlib.json        仓库元数据 + 功能 + CLI + 环境变量 + 退出码
  ├── files.json       444 镜像文件清单
  ├── skills.json      7 个 Skill 模块摘要
  ├── docs.json        13 份文档索引
  ├── links.json       上游链接
  ├── safety.json      7 条合规硬约束
  ├── pitfalls.json    16 高频坑
  ├── diffs.json       10 条口径差异
  └── verification.json 10 条核实记录
scripts/                           Python CLI + 索引重建
  ├── zlib.py          8 子命令（stats/commands/skills/env/codes/keys/agents/find）
  └── build_index.py   从零重建 data/*.json
upstream/                          444 文件原样镜像
  ├── cmd/zlib/main.go        CLI 入口
  ├── internal/cli/           TUI、各命令实现
  ├── internal/cli/book_*.go  TUI 组件
  ├── docs/                   13 份详细文档
  ├── .agents/skills/         7 个 Skill（zlib/kindle/metadata/...）
  ├── docs/*.md / *.gif       文档与演示 GIF
  └── go.mod / Makefile       Go 模块与构建脚本
```