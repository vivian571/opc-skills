#!/usr/bin/env python3
"""Build index JSON files from upstream source."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "upstream"
DATA = ROOT / "data"

def extract_tools_from_index_ts():
    """Extract MCP tool definitions from src/index.ts"""
    index_ts = UPSTREAM / "src" / "index.ts"
    content = index_ts.read_text(encoding="utf-8")
    
    tools = []
    
    # Pattern to find registerTool() calls
    tool_pattern = re.compile(
        r'registerTool\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]*)[\'"]',
        re.DOTALL
    )
    
    for match in tool_pattern.finditer(content):
        name = match.group(1)
        desc = match.group(2)
        tools.append({
            "name": name,
            "description": desc
        })
    
    return tools


def extract_types_from_types_ts():
    """Extract type definitions from src/types.ts"""
    types_ts = UPSTREAM / "src" / "types.ts"
    content = types_ts.read_text(encoding="utf-8")
    
    # Extract type names
    type_names = re.findall(r'export type (\w+)', content)
    interface_names = re.findall(r'export interface (\w+)', content)
    
    return {
        "types": type_names,
        "interfaces": interface_names
    }


def main():
    # Extract tools
    tools = extract_tools_from_index_ts()
    
    # Extract types
    types_info = extract_types_from_types_ts()
    
    # Build main index
    repo_meta = {
        "repo": "Joooook/12306-mcp",
        "name": "12306-mcp",
        "description": "基于 Model Context Protocol (MCP) 的 12306 购票搜索服务器，提供查询余票、中转换乘、经停站等功能",
        "url": "https://github.com/Joooook/12306-mcp",
        "license": "MIT",
        "version": "0.3.10",
        "language": "TypeScript",
        "stargazers_count": 2468,
        "forks_count": 343,
        "pushed_at": "2026-11-22T04:10:31Z",
        "created_at": "2025-04-14T14:31:32Z",
        "default_branch": "main",
        "topics": ["12306", "mcp", "mcp-server", "train-tickets"],
        "engines": {"node": ">=18"},
        "dependencies": {
            "@modelcontextprotocol/sdk": "^1.29.0",
            "axios": "^1.19.0",
            "commander": "^14.0.3",
            "date-fns": "^4.4.0",
            "date-fns-tz": "^3.2.0",
            "mcp-http-server": "^1.2.4",
            "zod": "^3.25.76"
        },
        "mcp_tools": tools,
        "type_definitions": types_info,
        "key_files": {
            "src/index.ts": "MCP 服务器主入口，定义所有工具",
            "src/types.ts": "TypeScript 类型定义",
            "docs/principle.md": "服务原理详解",
            "docs/architecture.md": "架构图与说明"
        },
        "installation": {
            "npx": "npx -y 12306-mcp",
            "npx_http": "npx -y 12306-mcp --port 8080",
            "docker_stdio": "docker build . -t 12306-mcp && docker run --rm -it 12306-mcp npx 12306-mcp",
            "docker_http": "docker run -p 8080:8080 -d 12306-mcp npx 12306-mcp --port 8080"
        },
        "mcp_config": {
            "command": "npx",
            "args": ["-y", "12306-mcp"]
        }
    }
    
    with open(DATA / "12306-mcp.json", "w", encoding="utf-8") as f:
        json.dump(repo_meta, f, ensure_ascii=False, indent=2)
    
    # Build tools index
    tools_index = {
        "count": len(tools),
        "tools": tools
    }
    with open(DATA / "tools.json", "w", encoding="utf-8") as f:
        json.dump(tools_index, f, ensure_ascii=False, indent=2)
    
    # Build types index
    with open(DATA / "types.json", "w", encoding="utf-8") as f:
        json.dump(types_info, f, ensure_ascii=False, indent=2)
    
    print(f"Generated: 12306-mcp.json, tools.json ({len(tools)} tools), types.json")


if __name__ == "__main__":
    main()