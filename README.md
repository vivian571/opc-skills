# opc-skills — Agent Skills for Solopreneurs

离线技能索引与 CLI 手册集合。每个 skill 是单个 GitHub 仓库锻造的**离线索引包**：含 SKILL.md 手册 + data/*.json 索引 + scripts/ 命令行工具，零依赖可查。

## 结构

```
skills/<name>/
├── SKILL.md            # 离线手册入口
├── data/*.json         # 自动生成的索引
├── upstream/           # 上游仓库源码镜像（按需拉取，本仓库不托管）
└── scripts/            # 离线索引 CLI
```

## 已收录 skill

| Skill | Star | 一句话 |
|---|---|---|
| cli-anything | ★63599 | 让所有软件 Agent 原生化：79 个 harness |
| hypit | ★30780 | AI 视频克隆系统：丢参考视频，Agent 克隆整套工作流 |
| supervisor-skills | ★13160 | 港科广博导十年顶会经验的科研副导师：Idea→写作→Rebuttal 全链路 |
| zlib | — | Zstandard 压缩库离线索引手册（Python/C/Rust/Go） |
| t3code | ★68446 | 编码 Agent 控制平面：1 server → 四端统一管理 thread |
| sheerid-verify | — | SheerID 真人身份验证 API 离线索引手册 |
| 12306-mcp | ★2468 | 基于 MCP 协议接入 12306 余票/中转查询 |
| mika-android-agent | — | Android 设备自动化 agent 离线索引 |
| skid-homework | — | 作业识别与解答辅助离线手册 |
| paper-orchestra | — | 学术论文编排与管理离线手册 |
| maitian | — | 马田开源项目离线索引 |
| agent-skills | — | Agent 技能集离线索引 |

> ⚠️ 这些包只做离线索引——不执行原始命令、不连网装包、不启动上游服务。
> 真正驱动上游需自行安装对应软件/CLI，遵守各上游许可与 ToS。

## License

每个 skill 遵循其上游仓库的许可；本目录聚合逻辑由「破壁人」在 WorkBuddy 会话中生成。
