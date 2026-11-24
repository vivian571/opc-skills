---
name: skid-homework
description: >-
  cubewhy/skid-homework（★1906 / GPL-3.0 / v0.0.0 / TypeScript / Next.js 15）。AI 驱动的作业助手：
  Gemini / OpenAI-compatible API、多图片 PDF 上传解析、可定制答案风格、画图工具（JSXGraph/Mermaid/SVG）、
  ADB 截屏（实验性/WebUSB）、键盘全键位操作 + 左撇子友好、i18n 中英双语、PWA 离线可用。
  ⚠️ 合规硬约束：本包只做离线索引与技术栈分析，**不对任何具体使用场景背书**——
  不提供绕过检测方案、不生成作弊 prompt、不代付 API Key。
  用户自行决定是否部署与使用，自负其责（README 自带免责声明：鼓励学术诚信、请勿在考试中使用）。
---

# skid-homework · 离线索引与技术栈手册

> 上游：`cubewhy/skid-homework` · GPL-3.0 · ★1,906（2026-11-17 核实快照）· TypeScript / Next.js 15 / 68 deps
> 镜像：`upstream/` 171 文件 / 12 MB（排除 node_modules / .next / pnpm-lock / 大图 / .husky / pre-commit）

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| **技术参考手册**：Next.js 15 + shadcn/ui + AI 集成 + 画图工具链的实现细节 | 可直接用的作弊工具 —— 本包不部署、不填 API Key、不调用 Gemini |
| **Prompt 工程样板**：6 份 .md prompt 的设计模式（全局 Prompt 编辑器、工具调用规范、解题流程） | 题库 —— 本项目使用 LLM 而非题库，响应慢、无本地缓存 |
| **ADB/WebUSB 实现参考**：@yume-chan/adb 在浏览器里连安卓设备截屏 | 商业 APP 的替代品 —— 无默认答案风格、需手写 Prompt 调教、LLM 响应慢 |
| **GPL-3.0 许可证样本**：强 copyleft 在现代前端项目里的落地样子 | MIT/BSD 项目 —— 任何修改分发必须同权开源，闭源商用需极其谨慎 |

## 2 核心技术栈

| 层 | 选型 | 关键点 |
|---|---|---|
| 框架 | Next.js 15 (App Router) | `src/app/{page,layout,providers,serwist}.tsx` |
| UI | shadcn/ui (Radix UI) + Tailwind v4 | `components/` 全是 Radix 封装 |
| 动画 | framer-motion + react-spring | 过渡、手势、弹性动画 |
| 状态/持久化 | dexie (IndexedDB) + zustand 推断 | API Key、聊天记录、设置全本地存储 |
| AI 客户端 | @google/genai (Gemini) + OpenAI-compatible | `src/ai/{gemini,openai,request,response}.ts` |
| Prompt 管理 | .md 文件 + prompt-manager.ts | 6 份 prompt 可直接编辑、Ctrl+X 编辑器 |
| 画图工具 | JSXGraph / Mermaid / function-plot / SVG | `components/markdown/diagram/*.tsx` |
| ADB | @yume-chan/adb + WebUSB | 实验性、需 Chrome Android、iOS 不可用 |
| i18n | i18next + http-backend | `public/locales/{en,zh}/commons.json` |
| PWA | serwist (Workbox 封装) | `serwist.config.js` + `src/app/serwist.ts` |
| 部署 | Cloudflare Pages (opennext) / Docker / Vercel | `opennextjs-cloudflare` + `wrangler` |

## 3 关键依赖

- Node.js ≥ 20 (Next.js 15 要求)
- pnpm 8+ (`pnpm-lock.yaml` + `pnpm-workspace.yaml`)
- Gemini API Key (Google AI Studio) 或 OpenAI 兼容 endpoint
- 可选：Chrome Android + WebUSB (ADB 截屏)

## 4 快捷键与交互

| 组合键 | 功能 |
|---|---|
| Ctrl+1 / 2 / 3 / 4 / 5 | 上传 / 拍照 / 提交 AI / 删文件 / 设置 |
| Ctrl+X | 全局 Prompt 编辑器 |
| ESC | 关闭设置/对话框 |
| 空格 / Shift+空格 | 下一题 / 上一题 |
| Tab / Shift+Tab | 下/上一文件 |
| `/` | 改进答案（触发 improve.prompt.md） |

## 5 合规硬约束（本包不代理、不背书）

1. **只做离线索引**：grep / 头读 / 结构化索引，不启动 `pnpm dev`、不连 localhost:3000、不调用任何 AI API。
2. **不生成 `.env.local` / `cloudflare-env.d.ts` / 任何含 API Key 的文件**。
3. **不指导绕过学校检测 / 考试作弊 / 隐藏后台标签 / 自动切屏**。
4. **不生成针对具体学科的作弊 prompt 模板**。
5. **GPL-3.0**：任何修改分发必须同权开源，闭源商用极其谨慎。
6. **同步提醒 README 免责声明**：项目方明确「鼓励学术诚信, 请勿在考试中使用」。

## 6 高频坑（本包最值钱的发现）

| # | 坑 | 严重度 |
|---|---|---|
| P1 | GPL-3.0 不是 MIT，修改分发必须同权开源 | 🔴 高 |
| P2 | Gemini API Key 必须用户自己填，别硬编码 | 🔴 高 |
| P3 | 默认不自带答案风格，开箱即用感不如作业帮 | 🟡 中 |
| P4 | LLM 响应慢，thinking budget 太小会出错 | 🟡 中 |
| P5 | Cors 是最大报错来源，自架 proxy 需加 CORS 头 | 🟡 中 |
| P6 | ADB 截屏需 WebUSB，iOS Safari 不支持 | 🟢 低 |
| P7 | 画图工具链 unstable，JSXGraph 为主、function-plot 逐步弃用 | 🟡 中 |
| P8 | Dev mode 暴露原始 Markdown，普通用户别开 | 🟢 低 |
| P9 | 官方实例 skid.996every.day 不归本仓管辖 | 🟢 低 |
| P10 | `updated_at` 晚于 `pushed_at` —— 有未推送改动 | 🟢 低 |
| P11 | public/opencv.js ~10 MB，首屏加载大、WASM 可能失败 | 🟡 中 |
| P12 | Serwist PWA 注册后清缓存难，开发需关 SW | 🟢 低 |

## 7 口径差异与核实记录

10 条 verified diffs（见 `data/diffs.json`），核心结论：

- D1: 三套部署入口（Vercel/Docker/Cloudflare）均属实
- D2: 本项目无「不存密码/浏览器内运行」声明（那是 maitian 的风格）
- D3: OCR 靠 LLM vision，OpenCV.js 只是图像预处理
- D4: ADB 需 WebUSB，iOS 不可用
- D5: Issues 只收 reproducible bug，Discussions 是主渠道
- D6: Next 15 + shadcn/ui 组件树属实
- D7: Prompt 文件是 .md 非硬编码，方便用户直改
- D8: LICENSE 文件是 GPLv3，但 package.json 缺 license 字段
- D9: 官方实例不归本仓管辖
- D10: Discussion 主渠道，Telegram 群仅 SFW

## 8 CLI 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/skid-homework

python3 scripts/skid.py stats                          # 仓库统计
python3 scripts/skid.py modules                        # 131 核心模块清单
python3 scripts/skid.py prompts                        # 6 份 Prompt 文件
python3 scripts/skid.py commands                       # npm scripts + 快捷键
python3 scripts/skid.py find jsxgraph                  # 跨索引搜索
python3 scripts/skid.py stats --json                   # JSON 输出
```

刷新：`python3 scripts/build_index.py`（从零重建 data/*.json，手写的 safety/pitfalls/diffs/verification 不被覆盖）。

## 9 目录结构

```
SKILL.md                           本离线手册入口
data/                              9 个 JSON 索引
  ├── skid.json        仓库元数据 + 命令/快捷键
  ├── files.json       171 镜像文件清单
  ├── modules.json     131 核心模块职责
  ├── prompts.json     6 份 Prompt 文件统计
  ├── links.json       上游链接
  ├── safety.json      6 条合规硬约束
  ├── pitfalls.json    12 高频坑
  ├── diffs.json       10 条口径差异
  └── verification.json 10 条核实记录
references/                        （空，本包无额外文档，上游文档在 upstream/）
scripts/                           Python CLI + 索引重建
  ├── skid.py          5 子命令（stats/modules/prompts/commands/find）
  └── build_index.py   从零重建 data/*.json
upstream/                          171 文件原样镜像
  ├── src/               Next.js 15 源码
  ├── public/            静态资源（含 opencv.js ~10MB 路径记录）
  ├── .github/workflows/  CI (lint + docker)
  ├── README.md / README-EN.md / LICENSE
  └── 配置文件：package.json / next.config.js / tsconfig.json / serwist.config.js / wrangler.toml
```