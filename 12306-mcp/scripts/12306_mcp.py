#!/usr/bin/env python3
"""
12306-mcp 离线索引 CLI
基于 Model Context Protocol (MCP) 的 12306 购票搜索服务器索引
"""

import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def load(name: str):
    path = DATA / f"{name}.json"
    if not path.exists():
        return {"error": f"Index file {name}.json not found. Run build_index.py first."}
    return json.loads(path.read_text(encoding="utf-8"))

def emit(title: str, obj, as_json: bool):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        print(f"=== {title} ===")
        print(json.dumps(obj, ensure_ascii=False, indent=2))

def cmd_stats(args):
    meta = load("12306-mcp")
    summary = {
        "repo": meta.get("repo"),
        "version": meta.get("version"),
        "license": meta.get("license"),
        "language": meta.get("language"),
        "stars": meta.get("stargazers_count"),
        "forks": meta.get("forks_count"),
        "updated": meta.get("pushed_at"),
        "mcp_tools_count": len(meta.get("mcp_tools", [])),
        "type_definitions": {
            "types": len(meta.get("type_definitions", {}).get("types", [])),
            "interfaces": len(meta.get("type_definitions", {}).get("interfaces", []))
        },
        "key_files": list(meta.get("key_files", {}).keys()),
        "installation_methods": list(meta.get("installation", {}).keys())
    }
    return emit("12306-mcp 仓库统计", summary, args.json)

def cmd_tools(args):
    tools = load("tools")
    if args.json:
        print(json.dumps(tools, ensure_ascii=False, indent=2))
    else:
        print(f"=== MCP 工具列表 (共 {tools['count']} 个) ===")
        for t in tools["tools"]:
            print(f"\n🔧 {t['name']}")
            print(f"   {t['description']}")

def cmd_types(args):
    types = load("types")
    if args.json:
        print(json.dumps(types, ensure_ascii=False, indent=2))
    else:
        print("=== TypeScript 类型定义 ===")
        print(f"Types: {', '.join(types['types']) or '(none)'}")
        print(f"Interfaces: {', '.join(types['interfaces']) or '(none)'}")

def cmd_install(args):
    meta = load("12306-mcp")
    inst = meta.get("installation", {})
    mcp_cfg = meta.get("mcp_config", {})
    if args.json:
        print(json.dumps({"installation": inst, "mcp_config": mcp_cfg}, ensure_ascii=False, indent=2))
    else:
        print("=== 安装方式 ===")
        for k, v in inst.items():
            print(f"  {k}: {v}")
        print("\n=== MCP 客户端配置 ===")
        print(f"  command: {mcp_cfg.get('command')}")
        print(f"  args: {mcp_cfg.get('args')}")

def cmd_concepts(args):
    meta = load("12306-mcp")
    concepts = {
        "architecture_layers": [
            "用户层 → 大语言模型",
            "MCP 服务层 → 基础工具层 (5个) + 核心工具层 (3个)",
            "数据层 → 4个核心映射表 (STATIONS, CITY_STATIONS, CITY_CODES, NAME_STATIONS)",
            "外部服务 → 12306 API"
        ],
        "tool_dependency": "基础工具层为核心工具层提供车站id、日期等基础数据",
        "data_flow": [
            "用户自然语言查询 → LLM 调用 get-current-date",
            "LLM 调用车站查询工具获取 station_code",
            "LLM 调用核心工具 (get-tickets / get-interline-tickets / get-train-route-stations)",
            "核心工具内部: 参数验证 → Cookie 获取 → 12306 API 调用 → 格式化输出"
        ],
        "core_features": [
            "余票查询 (get-tickets): 支持车次类型筛选、时间范围、排序、多种输出格式",
            "中转换乘查询 (get-interline-tickets): 支持指定中转站、显示无座、车次筛选",
            "经停站查询 (get-train-route-stations): 返回站名、到发时间、停留时间"
        ]
    }
    return emit("核心概念与架构", concepts, args.json)

def cmd_architecture(args):
    meta = load("12306-mcp")
    arch = {
        "description": "12306-MCP 服务采用标准 MCP Server 架构",
        "components": {
            "mcp_server": "@modelcontextprotocol/sdk McpServer 实例",
            "transport": "stdio (CLI) / SSE + Streamable HTTP (--port)",
            "tools": "8 个注册工具 (5 基础 + 3 核心)",
            "resources": "1 个资源 (stations: data://all-stations)",
            "external_api": "12306 官方 API (kyfw.12306.cn, search.12306.cn)"
        },
        "key_functions": [
            "getStations(): 启动时从 12306 官网抓取车站数据",
            "getCookie(): 获取 12306 Cookie 用于鉴权",
            "make12306Request(): 统一请求封装",
            "parseTicketsInfo(): 解析余票原始数据为结构化信息",
            "filterTicketsInfo(): 按车次类型/时间/排序筛选",
            "formatTicketsInfo(): 格式化输出 (text/csv/json)"
        ],
        "deployment": {
            "node": ">=18",
            "package_manager": "npm",
            "build": "tsc → build/index.js",
            "docker": "Dockerfile 多阶段构建"
        }
    }
    return emit("架构详解", arch, args.json)

def cmd_safety(args):
    safety = {
        "合规硬约束": [
            "本包仅做离线索引与 CLI 手册，不启动 MCP 服务器",
            "不连接 12306 真实 API，不获取 Cookie，不代为购票",
            "不存储用户身份证、手机号、12306 账号密码等敏感信息",
            "MIT 许可证允许商业使用，但需遵守 12306 官方服务条款"
        ],
        "风险提示": [
            "上游 MCP 服务器运行时会访问 12306 官方接口，频繁调用可能触发风控",
            "车站数据来自 12306 官网页面解析，官网改版可能导致失效",
            "中转查询仅返回前 10 条结果，不保证全量",
            "12306 官方未提供公开 API，本项目属于逆向工程，随时可能失效"
        ],
        "使用建议": [
            "仅供学习研究使用，勿用于商业抢票",
            "实际购票请使用 12306 官方客户端/网站",
            "部署 MCP 服务器时注意频率限制，避免 IP 被封"
        ]
    }
    return emit("合规与安全", safety, args.json)

def cmd_pitfalls(args):
    pitfalls = {
        "常见问题": [
            "车站名匹配：输入 '北京' 会匹配到北京站(北京)，需用 '北京南' 匹配北京南站",
            "城市 vs 车站：get-station-code-of-citys 返回同名车站，get-stations-code-in-city 返回该城市所有车站",
            "日期格式：必须严格 'yyyy-MM-dd'，相对日期需先调用 get-current-date 计算",
            "车次筛选：trainFilterFlags 区分大小写，只支持 G/D/Z/T/K/O/F/S 组合",
            "Cookie 失效：12306 Cookie 有效期短，频繁请求需处理重新获取"
        ],
        "已知限制": [
            "中转查询仅支持单一中转站，不支持多程换乘",
            "中转查询只返回前 10 条",
            "经停站查询需要先通过搜索 API 获取 train_no",
            "不支持学生票、军人票等特殊票种查询",
            "不支持选座、候补、改签、退票等写操作"
        ]
    }
    return emit("已知坑点与限制", pitfalls, args.json)

def cmd_links(args):
    meta = load("12306-mcp")
    links = {
        "repo": meta.get("url"),
        "npm": "https://www.npmjs.com/package/12306-mcp",
        "glama": "https://glama.ai/mcp/servers/@Joooook/12306-mcp",
        "mcp_spec": "https://github.com/modelcontextprotocol/modelcontextprotocol",
        "mcp_ts_sdk": "https://github.com/modelcontextprotocol/typescript-sdk",
        "skill_repo": "https://github.com/Joooook/12306-skill",
        "author_bilibili": "https://space.bilibili.com/3546386788255839",
        "author_afdian": "https://afdian.com/item/2a0e0cdcadf911ef9f725254001e7c00"
    }
    return emit("相关链接", links, args.json)

def cmd_find(args):
    keyword = args.keyword.lower()
    meta = load("12306-mcp")
    tools_data = load("tools")
    types_data = load("types")
    
    hits = []
    
    # Search in tools
    for t in tools_data["tools"]:
        if keyword in t["name"].lower() or keyword in t["description"].lower():
            hits.append({"source": "tools", "name": t["name"], "match": t["description"][:200]})
    
    # Search in types
    for typ in types_data["types"]:
        if keyword in typ.lower():
            hits.append({"source": "types", "name": typ, "match": "Type definition"})
    for iface in types_data["interfaces"]:
        if keyword in iface.lower():
            hits.append({"source": "interfaces", "name": iface, "match": "Interface definition"})
    
    # Search in meta
    meta_str = json.dumps(meta, ensure_ascii=False).lower()
    if keyword in meta_str:
        hits.append({"source": "meta", "name": "repository metadata", "match": "Found in repo metadata"})
    
    hits = hits[:args.limit]
    return emit(f"搜索 '{args.keyword}' (前 {len(hits)} 条)", {"count": len(hits), "results": hits}, args.json)

def main():
    parser = argparse.ArgumentParser(description="12306-mcp 离线索引 CLI")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    sub.add_parser("stats", help="仓库统计信息")
    sub.add_parser("tools", help="列出所有 MCP 工具")
    sub.add_parser("types", help="列出 TypeScript 类型定义")
    sub.add_parser("install", help="安装方式与 MCP 配置")
    sub.add_parser("concepts", help="核心概念与架构概览")
    sub.add_parser("architecture", help="详细架构设计")
    sub.add_parser("safety", help="合规硬约束与风险提示")
    sub.add_parser("pitfalls", help="已知坑点与限制")
    sub.add_parser("links", help="相关链接")
    
    find_p = sub.add_parser("find", help="关键词搜索")
    find_p.add_argument("keyword", help="搜索关键词")
    find_p.add_argument("--limit", type=int, default=10, help="最大返回条数")
    
    args = parser.parse_args()
    
    cmd_map = {
        "stats": cmd_stats,
        "tools": cmd_tools,
        "types": cmd_types,
        "install": cmd_install,
        "concepts": cmd_concepts,
        "architecture": cmd_architecture,
        "safety": cmd_safety,
        "pitfalls": cmd_pitfalls,
        "links": cmd_links,
        "find": cmd_find
    }
    
    if args.cmd in cmd_map:
        cmd_map[args.cmd](args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()