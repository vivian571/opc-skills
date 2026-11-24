# 12306-mcp 离线索引与操作手册

> **源仓库**：[Joooook/12306-mcp](https://github.com/Joooook/12306-mcp) (★2,468 / MIT / TypeScript / v0.3.10 / 2025-04-14 建仓)  
> **技能路径**：`~/.workbuddy/skills/12306-mcp/`  
> **定位**：基于 Model Context Protocol (MCP) 的 12306 购票搜索服务器离线索引手册  
> **⚠️ 合规硬约束**：本包仅做离线索引与 CLI 手册 —— **不启动 MCP 服务器、不连接 12306 真实 API、不获取 Cookie、不代为购票、不存储任何敏感信息**。MIT 许可无限制，但实际使用需遵守 12306 官方服务条款。

---

## 速览

| 维度 | 说明 |
|------|------|
| **核心价值** | 让大模型通过标准 MCP 协议查询 12306 余票、中转换乘、列车经停站 |
| **MCP 工具** | 8 个（5 基础 + 3 核心），全为只读查询 |
| **数据层** | 4 个核心映射表：`STATIONS`、`CITY_STATIONS`、`CITY_CODES`、`NAME_STATIONS` |
| **部署要求** | Node.js ≥ 18、npm、12306 官网可访问（国内网络） |
| **典型用法** | `npx -y 12306-mcp` (stdio) 或 `npx -y 12306-mcp --port 8080` (HTTP) |

---

## 目录结构

```
~/.workbuddy/skills/12306-mcp/
├── SKILL.md                    # 本文件（离线手册入口）
├── data/
│   ├── 12306-mcp.json          # 仓库元数据 + 工具 + 类型 + 安装 + MCP 配置
│   ├── tools.json              # 8 个 MCP 工具索引
│   └── types.json              # TypeScript 类型定义索引
├── upstream/                   # 源码镜像（13 个文件）
│   ├── src/
│   │   ├── index.ts            # MCP 服务器主入口（含 8 个工具注册）
│   │   └── types.ts            # 完整类型定义
│   ├── docs/
│   │   ├── principle.md        # 服务原理详解（数据流、工具依赖）
│   │   └── architecture.md     # 架构图与 Mermaid 图表
│   ├── README.md               # 官方 README
│   ├── LICENSE                 # MIT 许可证
│   ├── package.json            # 依赖与脚本
│   ├── tsconfig.json           # TS 配置
│   ├── Dockerfile              # 容器化部署
│   ├── glama.json              # Glama 注册信息
│   ├── .prettierrc             # 格式化配置
│   └── .gitignore              # 忽略规则
└── scripts/
    ├── build_index.py          # 从 upstream/ 重建索引
    └── 12306_mcp.py            # 离线索引 CLI（10 子命令，支持 --json）
```

---

## CLI 使用

```bash
# 统计概览
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py stats [--json]

# 列出所有 MCP 工具
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py tools [--json]

# TypeScript 类型定义
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py types [--json]

# 安装方式与 MCP 客户端配置
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py install [--json]

# 核心概念与架构概览
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py concepts [--json]

# 详细架构设计
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py architecture [--json]

# 合规硬约束与风险提示
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py safety [--json]

# 已知坑点与限制
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py pitfalls [--json]

# 相关链接
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py links [--json]

# 关键词搜索（工具、类型、元数据）
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py find <keyword> [--limit N] [--json]
```

### 示例

```bash
# 搜索与“中转”相关的工具/类型
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py find 中转

# 获取 JSON 供脚本消费
python3 ~/.workbuddy/skills/12306-mcp/scripts/12306_mcp.py tools --json | jq '.tools[].name'
```

---

## MCP 工具速查（8 个）

### 基础工具层（5 个）—— 为核心工具提供基础数据

| 工具 | 作用 | 关键参数 |
|------|------|----------|
| `get-current-date` | 获取上海时区当前日期 (yyyy-MM-dd) | 无 |
| `get-stations-code-in-city` | 查城市所有车站 | `city`: 中文城市名 |
| `get-station-code-of-citys` | 查城市代表车站 | `citys`: 城市名，`|` 分隔多个 |
| `get-station-code-by-names` | 精确车站名转 station_code | `stationNames`: 车站名，`|` 分隔 |
| `get-station-by-telecode` | station_code 反查详细信息 | `stationTelecode`: 3 字母编码 |

### 核心工具层（3 个）—— 实际业务查询

| 工具 | 作用 | 关键参数 |
|------|------|----------|
| `get-tickets` | 余票查询 | `date`、`fromStation`、`toStation`、`trainFilterFlags` (G/D/Z/T/K/O/F/S)、时间范围、排序、输出格式 |
| `get-interline-tickets` | 中转换乘查询 | `date`、`fromStation`、`toStation`、`middleStation` (可选)、`showWZ`、车次筛选、时间范围、排序 |
| `get-train-route-stations` | 经停站查询 | `trainCode` (如 G1033)、`departDate`、输出格式 |

---

## 核心数据结构

### 4 个核心映射表（启动时从 12306 官网加载）

```
STATIONS:           station_code → 完整车站信息 (名称、拼音、城市、code 等)
CITY_STATIONS:      城市名 → 该城市所有车站 [{station_code, station_name}, ...]
CITY_CODES:         城市同名车站 → {station_code, station_name} (仅一对一)
NAME_STATIONS:      完整车站名 → {station_code, station_name}
```

### 主要 TypeScript 类型 (9 types + 1 interface)

- `TicketData` / `TicketDataKeys`：原始余票数据字段 (56 字段)
- `TicketInfo`：格式化后的车票信息 (含价格数组)
- `StationData` / `StationDataKeys`：车站信息
- `Price`：席别价格 (座位名、编码、余票、价格、折扣)
- `RouteStationData` / `RouteStationInfo`：经停站原始/格式化数据
- `InterlineData` / `InterlineInfo` / `InterlineTicketData`：中转换乘数据
- `TrainSearchData`：搜索 API 返回的车次基础信息
- `QueryResponse` / `LeftTicketsQueryResponse` / `InterlineQueryResponse` / `TrainSearchResponse` / `RouteQueryResponse`：API 响应接口

---

## 典型调用流程

```
用户："帮我查后天北京到上海的高铁"
        ↓
1. LLM 调用 get-current-date() → "2026-11-24"
2. LLM 计算后天 → "2026-11-26"
3. LLM 调用 get-station-code-of-citys("北京|上海") → {北京: BJP, 上海: SHH}
4. LLM 调用 get-tickets(date="2026-11-26", fromStation="BJP", toStation="SHH", trainFilterFlags="G")
        ↓
5. 内部：参数验证 → getCookie() → 请求 /otn/leftTicket/query → parseTicketsInfo → filter → format
        ↓
6. 返回格式化高铁列表（车次、时间、历时、各席别余票价格）
```

---

## 安装与部署

### 本地运行
```bash
# stdio 模式 (MCP 标准)
npx -y 12306-mcp

# HTTP 模式 (SSE + Streamable HTTP)
npx -y 12306-mcp --port 8080
```

### Docker
```bash
# 构建
docker build . -t 12306-mcp

# stdio
docker run --rm -it 12306-mcp npx 12306-mcp

# HTTP (端口映射)
docker run -p 8080:8080 -d 12306-mcp npx 12306-mcp --port 8080
```

### MCP 客户端配置
```json
{
  "mcpServers": {
    "12306-mcp": {
      "command": "npx",
      "args": ["-y", "12306-mcp"]
    }
  }
}
```

---

## 合规硬约束（必读）

| 约束 | 说明 |
|------|------|
| **仅离线索引** | 本技能包不启动 MCP 服务器，不连接 12306 API，不获取 Cookie，不代为购票 |
| **不存敏感信息** | 不存身份证、手机号、12306 账号密码、乘客信息 |
| **MIT 许可** | 代码层面允许商用，但**实际调用 12306 接口需遵守官方服务条款** |
| **学习用途** | 上游 README 明确：仅供学习，欢迎催更 |
| **逆向风险** | 12306 无公开 API，本项目通过页面解析+接口逆向，官网改版/风控升级随时失效 |

---

## 已知坑点与限制

| 类别 | 详情 |
|------|------|
| **车站名匹配** | 输入 "北京" 匹配到北京站(BJP)，需用 "北京南" 匹配北京南站(BJP...) |
| **城市 vs 车站** | `get-station-code-of-citys` 返回同名车站；`get-stations-code-in-city` 返回所有车站 |
| **日期格式** | 必须严格 `yyyy-MM-dd`，相对日期需先调用 `get-current-date` 计算 |
| **车次筛选** | `trainFilterFlags` 区分大小写，仅支持 G/D/Z/T/K/O/F/S 组合 |
| **Cookie 失效** | 12306 Cookie 有效期短，高频请求需处理重新获取 |
| **中转限制** | 仅支持单一中转站，只返回前 10 条结果 |
| **经停站依赖** | 需先通过搜索 API 获取 `train_no` 再查询 |
| **不支持功能** | 学生票/军人票、选座、候补、改签、退票等写操作 |

---

## 相关链接

| 链接 | 说明 |
|------|------|
| [GitHub Repo](https://github.com/Joooook/12306-mcp) | 源码、Issue、PR |
| [npm Package](https://www.npmjs.com/package/12306-mcp) | 发布版本、下载统计 |
| [Glama Registry](https://glama.ai/mcp/servers/@Joooook/12306-mcp) | MCP 服务器注册页 |
| [MCP Spec](https://github.com/modelcontextprotocol/modelcontextprotocol) | 官方协议规范 |
| [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | SDK 文档 |
| [12306-skill](https://github.com/Joooook/12306-skill) | 作者配套的 Skill 版本 |
| [作者 B 站](https://space.bilibili.com/3546386788255839) | 视频教程 |
| [作者 爱发电](https://afdian.com/item/2a0e0cdcadf911ef9f725254001e7c00) | 赞助 |

---

## 重建索引

如上游有更新，可重新生成索引：

```bash
cd ~/.workbuddy/skills/12306-mcp
python3 scripts/build_index.py
```

---

## 技术备忘

- **沙箱 gotcha**：`mkdir(exist_ok=True)` 在目录已存在时被拦截抛 `FileExistsError`（同 rsi/hypit 项目）。`build_index.py` 已用 `try/except FileExistsError` 兜底。
- **工具提取**：上游用 `registerTool()` 包装 `server.tool()`，正则需匹配 `registerTool(` 而非 `server.tool(`。
- **中文描述**：工具描述均为中文，含参数说明，适合直接喂给中文 LLM 作为 function calling 参考。