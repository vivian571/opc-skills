---
name: mika-android-agent
description: >-
  wangzan101/Mika（★9099 / Apache-2.0 / v0.1.47 / Kotlin Android）的离线索引与技术手册。
  Android 设备上的 AI Agent：后台虚拟屏操作任意 APP/网站完成任务——发消息、查信息、购物、定闹钟等。
  ⚠️ 合规硬约束：本包只做离线索引与上游文档查阅——不代部署、不连设备、不指导绕过第三方 APP 反自动化检测。
  用户自行决定是否安装使用，自负其责（README 明示：自动操作第三方 APP 可能违反其 ToS）。
---

# Mika · 离线索引与技术手册

> 上游：`wangzan101/Mika` · Apache-2.0 · ★9,099（2026-11-19 核实快照）· v0.1.47
> 镜像：`upstream/` 3585 文件 / 96 MB（排除 gradle-wrapper.jar / build/ / node_modules）
> **定位**：Android 原生应用，非 Web/Node/Python 项目 → macOS 无法本地运行，只能下载 APK

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **手机上的 AI Agent**：在后台虚拟屏自动操作任意 APP/网站，主屏幕照常使用 | 桌面端可运行的服务 —— 必须在 Android 设备上安装 APK 才能工作 |
| **开源参考实现**：展示 Accessibility + Virtual Display + LLM 结合的 mobile agent 架构 | 可直接复制粘贴的生产代码 —— 强依赖特定设备权限模型，移植成本高 |
| **多模型路由**：支持 20+ provider（DeepSeek/Gemini/OpenAI/Ollama/LM Studio...） | 单一模型绑定产品 —— Provider 完全由用户在 Settings 配置，无 vendor lock-in |
| **CLI + Skill 双入口**：电脑可通过 ADB 或局域网 HTTP 委托任务给手机 | 全自动无人值守工具 —— 支付/登录页面强制交给人工，Ask mode 默认开启 |

## 2 技术架构（来源：docs/dev/architecture.md）

```
┌─────────────────────────────────────────────────────┐
│                    :app (Android 宿主)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ UI Layer │  │Virtual Screen│ │  Accessibility   │   │
│  │(Chat/Web)│  │(SurfaceLayer)│ │  Service        │   │
│  └────┬─────┘  └─────┬──────┘  └────────┬────────┘   │
│       └───────────────┼──────────────────┘            │
│                       ▼                               │
│  ┌─────────────────────────────────────────────┐      │
│  │           TaskService (前台服务)              │      │
│  │  TaskCenter → RunStore → Outbox             │      │
│  └──────────────────┬──────────────────────────┘      │
│                     │                                 │
├─────────────────────┼─────────────────────────────────┤
│                     ▼                                 │
│  ┌─────────────────────────────────────────────┐      │
│  │              :core (Kotlin/JVM)               │      │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │      │
│  │  │AgentLoop│ │ToolDispatcher│ │Capability │  │      │
│  │  │(主循环) │ │(工具调度) │ │Provider    │  │      │
│  │  └─────────┘ └──────────┘ └──────────────┘  │      │
│  │                                               │      │
│  │  Capabilities: phone / web / sandbox / audio │      │
│  │               devicefiles / transcribe / mcp │      │
│  └─────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
         ▲                          ▲
         │                          │
   Phone (ADB/WiFi)          Computer (CLI/MCP)
```

### 核心设计模式

| 层 | 职责 | 关键类 |
|---|---|---|
| **AgentLoop** | 主循环：装能力→建Context→TurnPolicy→ModelCaller→工具执行 | `core/agent/AgentLoop.kt` |
| **TaskService** | 前台服务，管理 Run 的生命周期与排队 | `app/task/TaskService.kt` |
| **RunInbox** | 处理插话（Steer/Redirect/Answer/Confirm/HandBack/Cancel） | `core/run/RunInbox.kt` |
| **ToolDispatcher** | 工具调用分发，不引用 UI 状态（纯函数） | `core/tool/ToolDispatcher.kt` |
| **CapabilityProvider** | 各能力的抽象接口，核心不认识具体实现 | `core/cap/*/Capability.kt` |

### Capability 系统（互不引用）

```
core/cap/
├── phone/     # 手机控制：点击/滑动/输入/截屏
├── web/       # WebView 浏览：读取/交互/下载
├── sandbox/   # Linux 沙箱：Python/Node/Shell (arm64 only)
├── audio/     # 语音：ASR/TTS/手持对讲
├── devicefiles/# 文件操作：浏览/上传/下载
├── transcribe/ # 转录：语音转文字
└── mcp/       # MCP 客户端：远程计算机接入
```

**关键约束**：各 capability 之间互不引用，只通过 `CapabilityProvider` 接口对接核心。这是典型的六边形架构。

## 3 部署三步走

### Step 1：获取 APK
```bash
# 直接下 Release
open https://github.com/wangzan101/Mika/releases/latest
# 选 universal APK（兼容性最好）或 arm64-v8a（体积更小）
```

### Step 2：配模型
```
Settings → Model → 选 provider → 填 API Key
```
免费额度推荐：**DeepSeek**（国内直连）或 **Ollama**（本地跑）。

### Step 3：配对手机控制
```
Settings → Phone control → Pair again
```
6 步向导自动检测进度。**关键**：Step 3 无障碍权限点「Skip」让 App 自己开；Step 4 无线调试勾选「Always allow on this network」。

## 4 CLI 命令清单

```bash
# 查看连接的设备
mika devices --json

# 配对并启动 helper（需 adb 已配对）
mika connect --device <SERIAL> --json

# 健康检查（只读）
mika doctor --device <SERIAL> --json

# 提交任务
mika task --device <SERIAL> --goal "明天早上9点叫我起床"

# 查看运行记录
mika ui --device <SERIAL>

# 远程 MCP（可选，需 tools/relay/ 网关）
# 见 docs/computer.en.md
```

## 5 合规硬约束

1. **只读静态文档**：不启动 adb、不连 Android 设备、不安装 APK、不调用 mika CLI。
2. **不生成凭据**：不写 .env、不存 API Key、不创建配置文件。
3. **不指导绕过风控**：不教如何规避微信/淘宝/抖音的反自动化检测。
4. **同步提醒 ToS 风险**：README 明示「Operating third-party apps automatically may break their terms of service」。
5. **学术诚信边界**：如果是学生用此工具写作业，提醒 arXiv/会议已要求披露 AI 辅助写作（这是通用原则，不仅限于 paper-orchestra）。

## 6 高频坑（已写入 pitfalls.json）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | Android 12+ 才能控制 APP，11 只能聊天/Web | 🔴 高 |
| P2 | 无线调试切 Wi-Fi 会自动关闭，需重新配对 | 🟡 中 |
| P3 | Accessibility 手动开会变灰，必须 Skip 让 App 自己开 | 🟡 中 |
| P4 | 支付/登录页面禁止截图，Mika 主动交控制权 | 🔴 高 |
| P5 | Linux sandbox 仅 arm64，x86_64 模拟器不支持 | 🟢 低 |
| P6 | Gradle 构建需 ~2GB 内存 + 稳定网络（国内需代理） | 🟡 中 |
| P7 | 第三方 APP 自动化可能违反其 ToS | 🔴 高 |
| P8 | APK 分 universal/arm64 两版，选错可能安装失败 | 🟢 低 |

## 7 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/mika-android-agent

python3 scripts/mika.py stats                            # 仓库统计
python3 scripts/mika.py quickstart                       # 三步快速开始
python3 scripts/mika.py cli                              # CLI 命令清单
python3 scripts/mika.py docs                             # 关键文档索引
python3 scripts/mika.py find accessibility               # 全文搜索关键词
python3 scripts/mika.py stats --json                     # JSON 输出
```

刷新：`python3 scripts/build_index.py`（从零重建 data/*.json，手写数据安全文件不被覆盖）。

## 8 目录结构

```
SKILL.md                           本离线手册入口
data/                              7 个 JSON 索引
  ├── mika.json        仓库元数据 + 架构 + CLI + 部署选项
  ├── files.json       3585 镜像文件清单
  ├── docs.json        9 份关键文档摘要
  ├── links.json       上游链接
  ├── safety.json      6 条合规硬约束
  └── pitfalls.json    12 高频坑
references/                        （空，上游文档均在 upstream/docs/）
scripts/                           Python CLI + 索引重建
  ├── mika.py          5 子命令（stats/quickstart/cli/docs/find）
  └── build_index.py   从零重建 data/*.json
upstream/                          3585 文件原样镜像
  ├── core/src/main/kotlin/   纯 Kotlin/JVM 核心逻辑（平台无关）
  ├── app/src/main/java/      Android 宿主（UI/虚拟屏/无障碍）
  ├── docs/                   完整文档（中文/英文）
  ├── tools/mika/             Python CLI 源码
  ├── tools/relay/            Go 网关（远程 MCP，可选）
  ├── templates/              （无，LaTeX 模板在纸乐队 paper-orchestra）
  └── eval/                   评测任务集（待公开）
```