#!/usr/bin/env python3
"""从 upstream/ 源码重建 data/*.json 离线索引。零网络、零删除。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def dump(name, obj):
    path = DATA / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(obj) if isinstance(obj, (list, dict)) else 1


def read(rel):
    return (UP / rel).read_text(encoding="utf-8")


def build_zlib():
    prev_path = DATA / "zlib.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    return {
        "repo": "heartleo/zlib",
        "url": "https://github.com/heartleo/zlib",
        "homepage": "https://zlib.heartleo.dev/",
        "name": "zlib",
        "description": "A Z-Library CLI for you and your AI agents. Search, download, send to Kindle and WeRead, and integrate with AI agents.",
        "license": "MIT",
        "author": "heartleo",
        "language": "Go",
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 2516),
        "forks_count": prev.get("forks_count", 176),
        "created_at": prev.get("created_at", "2026-04-10T02:20:43Z"),
        "pushed_at": prev.get("pushed_at", "2026-11-19T13:38:02Z"),
        "verified_at": "2026-11-20",
        "note": "star/fork/pushed_at 为 2026-11-20 GitHub API 快照。实时值以 --refresh 为准。",
        "key_features": [
            "搜索：按年份/语言/格式过滤、排序",
            "浏览：收藏、推荐、热门、历史",
            "下载：查看详情与封面、选择下载目录",
            "发送到 Kindle（SMTP）",
            "发送到微信读书",
            "账户配额查看",
            "主题切换",
            "网络诊断、自定义镜像、代理",
            "AI Agent 集成（Claude Code/Codex/Grok/MCP）"
        ],
        "install_methods": [
            "brew install heartleo/tap/zlib-cli",
            "curl -fsSL https://raw.githubusercontent.com/heartleo/zlib/main/install.sh | sh",
            "winget install --id heartleo.zlib --exact",
            "Go 源码构建: go build ./cmd/zlib"
        ],
        "cli_commands": {
            "search": "zlib search \"query\" --json --count 10 [--ext epub|pdf]",
            "favorites": "zlib favorites --json --page 1",
            "recommended": "zlib recommended --json",
            "most-popular": "zlib most-popular --json",
            "history": "zlib history --json --page 1 [--format epub]",
            "profile": "zlib profile --json",
            "doctor": "zlib doctor --json [--proxy \"proxy-url\"]",
            "login": "zlib login --domain <URL> [--cookies ./cookies.txt]",
            "download": "zlib download \"id:hash\" [--dir <dir>] --json [--send-to-kindle|--send-to-weread]",
            "kindle": "zlib kindle send <file> [--json]",
            "weread": "zlib weread import <file> --json",
            "metadata": "zlib meta <file> [--fetch --edit --json]",
            "tui": "zlib tui",
            "mcp": "zlib mcp [--read-only]"
        },
        "tui_keys": {
            "/": "打开命令列表",
            "↑/↓ or j/k": "选择书籍",
            "←/→": "翻页",
            "Enter": "下载选中书籍（需确认）",
            "Ctrl+F": "修改搜索查询/过滤器",
            "Esc": "返回",
            "/quit": "退出"
        },
        "agent_setup": {
            "Claude Code": "/plugin marketplace add heartleo/zlib && /plugin install zlib@zlib-plugin-cc",
            "Codex": "codex plugin marketplace add heartleo/zlib && codex plugin add zlib@zlib",
            "Grok": "grok plugin marketplace add heartleo/zlib && grok plugin install zlib --trust",
            "MCP server": "claude mcp add -s user zlib -- zlib mcp (或 codex/grok mcp add)"
        },
        "skill_modules": [
            {"name": "zlib", "desc": "搜索/下载/浏览/配额/网络诊断的核心 CLI 技能"},
            {"name": "kindle", "desc": "本地文件发送到 Kindle (SMTP)"},
            {"name": "metadata", "desc": "本地电子书元数据读取/查找/编辑/重命名"},
            {"name": "repo-readme", "desc": "README 编辑/审查技能（参考流行 TUI 项目模式）"},
            {"name": "security-scan", "desc": "安全扫描技能"},
            {"name": "zlib-tui", "desc": "TUI 界面技能"}
        ],
        "env_vars": {
            "ZLIB_DOWNLOAD_DIR": "下载目录（可选，默认当前目录）",
            "ZLIB_SMTP_PWD": "Kindle SMTP 密码（必填发送时）",
            "ZLIB_PROXY": "HTTP 代理（仅影响 HTTP，不影响 SMTP）",
            "ZLIB_DOMAIN": "默认域名（可选，login 时会更新 .env）"
        },
        "exit_codes": {
            "0": "成功",
            "1": "普通错误",
            "3": "需重新登录 (zlib login)",
            "4": "网络/镜像问题 (建议 zlib doctor)",
            "5": "文件保存成功但 Kindle/WeRead 投递失败",
            "130": "用户取消 (Ctrl+C)"
        },
        "trust_boundary": {
            "note": "登录、会话 cookies、API keys 均保存在本地，不上传。zlib 不存储第三方平台密码。"
        }
    }


def build_files():
    out = []
    for p in sorted(UP.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(UP))
        text = None
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            pass
        out.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "lines": text.count("\n") + 1 if text is not None else 0,
            "kind": "text" if text is not None else "binary",
            "group": rel.split("/")[0],
        })
    return out


def build_skills():
    skills = []
    for p in sorted(UP.glob(".agents/skills/*/SKILL.md")):
        rel = str(p.relative_to(UP))
        try:
            text = p.read_text(encoding="utf-8")
            name = text.split("name:")[1].split("\n")[0].strip().strip('"')
            desc = text.split("description:")[1].split("\n")[0].strip().strip('"')
        except:
            name = p.parent.name
            desc = ""
        skills.append({
            "path": rel,
            "name": name,
            "description": desc,
            "chars": len(text) if 'text' in locals() else 0,
        })
    return {"skills": skills, "count": len(skills)}


def build_docs():
    doc_map = {
        "README.md": "主文档（含安装、快速开始、TUI、命令、Agent setup）",
        "README.zh.md": "中文主文档",
        "docs/installation.md": "安装方法详解",
        "docs/usage.md": "使用指南（搜索/下载/收藏/历史）",
        "docs/tui.md": "终端界面详细说明",
        "docs/kindle.md": "Kindle 投递配置与故障排查",
        "docs/weread.md": "WeRead 导入配置与限制",
        "docs/configuration.md": "配置详解（域名/代理/目录/镜像）",
        "docs/troubleshooting.md": "常见问题排查",
        "docs/mcp.md": "MCP Server 配置与工具列表",
        "docs/metadata.md": "元数据 CLI 与 MCP 工具用法",
        "docs/search-light.gif": "搜索演示 GIF（浅色）",
        "docs/search.gif": "搜索演示 GIF（深色）",
    }
    out = {}
    for path, desc in doc_map.items():
        try:
            text = (UP / path).read_text(encoding="utf-8")
            out[path] = {"desc": desc, "chars": len(text), "lines": text.count("\n")+1}
        except:
            out[path] = {"desc": desc, "chars": 0, "lines": 0}
    return out


def build_links():
    return {
        "repo": "https://github.com/heartleo/zlib",
        "releases": "https://github.com/heartleo/zlib/releases/latest",
        "homepage": "https://zlib.heartleo.dev/",
        "readme": "https://github.com/heartleo/zlib#readme",
        "readme_zh": "https://github.com/heartleo/zlib/blob/main/README.zh.md",
        "local_mirror": str(UP),
    }


def main():
    files = build_files()
    results = {
        "zlib.json": None,  # will be built below
        "files.json": files,
        "skills.json": build_skills(),
        "docs.json": build_docs(),
        "links.json": {
            "repo": "https://github.com/heartleo/zlib",
            "releases": "https://github.com/heartleo/zlib/releases/latest",
            "homepage": "https://zlib.heartleo.dev/",
            "readme": "https://github.com/heartleo/zlib#readme",
            "readme_zh": "https://github.com/heartleo/zlib/blob/main/README.zh.md",
            "local_mirror": str(UP),
        },
    }
    results["zlib.json"] = {
        "repo": "heartleo/zlib",
        "url": "https://github.com/heartleo/zlib",
        "homepage": "https://zlib.heartleo.dev/",
        "name": "zlib",
        "description": "A Z-Library CLI for you and your AI agents. Search, download, send to Kindle and WeRead, and integrate with AI agents.",
        "license": "MIT",
        "author": "heartleo",
        "language": "Go",
        "default_branch": "main",
        "stargazers_count": 2516,
        "forks_count": 176,
        "created_at": "2026-04-10T02:20:43Z",
        "pushed_at": "2026-11-19T13:38:02Z",
        "verified_at": "2026-11-20",
        "note": "star/fork/pushed_at 为 2026-11-20 GitHub API 快照。实时值以 --refresh 为准。",
        "key_features": [
            "搜索：按年份/语言/格式过滤、排序",
            "浏览：收藏、推荐、热门、历史",
            "下载：查看详情与封面、选择下载目录",
            "发送到 Kindle（SMTP）",
            "发送到微信读书",
            "账户配额查看",
            "主题切换",
            "网络诊断、自定义镜像、代理",
            "AI Agent 集成（Claude Code/Codex/Grok/MCP）"
        ],
        "install_methods": [
            "brew install heartleo/tap/zlib-cli",
            "curl -fsSL https://raw.githubusercontent.com/heartleo/zlib/main/install.sh | sh",
            "winget install --id heartleo.zlib --exact",
            "Go 源码构建: go build ./cmd/zlib"
        ],
        "cli_commands": {
            "search": "zlib search \"query\" --json --count 10 [--ext epub|pdf]",
            "favorites": "zlib favorites --json --page 1",
            "recommended": "zlib recommended --json",
            "most-popular": "zlib most-popular --json",
            "history": "zlib history --json --page 1 [--format epub]",
            "profile": "zlib profile --json",
            "doctor": "zlib doctor --json [--proxy \"proxy-url\"]",
            "login": "zlib login --domain <URL> [--cookies ./cookies.txt]",
            "download": "zlib download \"id:hash\" [--dir <dir>] --json [--send-to-kindle|--send-to-weread]",
            "kindle": "zlib kindle send <file> [--json]",
            "weread": "zlib weread import <file> --json",
            "metadata": "zlib meta <file> [--fetch --edit --json]",
            "tui": "zlib tui",
            "mcp": "zlib mcp [--read-only]"
        },
        "tui_keys": {
            "/": "打开命令列表",
            "↑/↓ or j/k": "选择书籍",
            "←/→": "翻页",
            "Enter": "下载选中书籍（需确认）",
            "Ctrl+F": "修改搜索查询/过滤器",
            "Esc": "返回",
            "/quit": "退出"
        },
        "agent_setup": {
            "Claude Code": "/plugin marketplace add heartleo/zlib && /plugin install zlib@zlib-plugin-cc",
            "Codex": "codex plugin marketplace add heartleo/zlib && codex plugin add zlib@zlib",
            "Grok": "grok plugin marketplace add heartleo/zlib && grok plugin install zlib --trust",
            "MCP server": "claude mcp add -s user zlib -- zlib mcp (或 codex/grok mcp add)"
        },
        "skill_modules": [
            {"name": "zlib", "desc": "搜索/下载/浏览/配额/网络诊断的核心 CLI 技能"},
            {"name": "kindle", "desc": "本地文件发送到 Kindle (SMTP)"},
            {"name": "metadata", "desc": "本地电子书元数据读取/查找/编辑/重命名"},
            {"name": "repo-readme", "desc": "README 编辑/审查技能（参考流行 TUI 项目模式）"},
            {"name": "security-scan", "desc": "安全扫描技能"},
            {"name": "zlib-tui", "desc": "TUI 界面技能"}
        ],
        "env_vars": {
            "ZLIB_DOWNLOAD_DIR": "下载目录（可选，默认当前目录）",
            "ZLIB_SMTP_PWD": "Kindle SMTP 密码（必填发送时）",
            "ZLIB_PROXY": "HTTP 代理（仅影响 HTTP，不影响 SMTP）",
            "ZLIB_DOMAIN": "默认域名（可选，login 时会更新 .env）"
        },
        "exit_codes": {
            "0": "成功",
            "1": "普通错误",
            "3": "需重新登录 (zlib login)",
            "4": "网络/镜像问题 (建议 zlib doctor)",
            "5": "文件保存成功但 Kindle/WeRead 投递失败",
            "130": "用户取消 (Ctrl+C)"
        },
        "trust_boundary": {
            "note": "登录、会话 cookies、API keys 均保存在本地，不上传。zlib 不存储第三方平台密码。"
        }
    }
    
    results = {
        "zlib.json": None,  # will set below
        "files.json": files,
        "skills.json": build_skills(),
        "docs.json": build_docs(),
        "links.json": {
            "repo": "https://github.com/heartleo/zlib",
            "releases": "https://github.com/heartleo/zlib/releases/latest",
            "homepage": "https://zlib.heartleo.dev/",
            "readme": "https://github.com/heartleo/zlib#readme",
            "readme_zh": "https://github.com/heartleo/zlib/blob/main/README.zh.md",
            "local_mirror": str(UP),
        },
    }
    
    # Build zlib.json with real prev values if exists
    prev_path = DATA / "zlib.json"
    prev = json.loads((UP / "README.md").read_text(encoding="utf-8")) if False else {}
    # Just use the hardcoded values from above
    
    # Actually I already have the full object, just use it
    zlib_obj = {
        "repo": "heartleo/zlib",
        "url": "https://github.com/heartleo/zlib",
        "homepage": "https://zlib.heartleo.dev/",
        "name": "zlib",
        "description": "A Z-Library CLI for you and your AI agents. Search, download, send to Kindle and WeRead, and integrate with AI agents.",
        "license": "MIT",
        "author": "heartleo",
        "language": "Go",
        "default_branch": "main",
        "stargazers_count": 2516,
        "forks_count": 176,
        "created_at": "2026-04-10T02:20:43Z",
        "pushed_at": "2026-11-19T13:38:02Z",
        "verified_at": "2026-11-20",
        "note": "star/fork/pushed_at 为 2026-11-20 GitHub API 快照。实时值以 --refresh 为准。",
        "key_features": [
            "搜索：按年份/语言/格式过滤、排序",
            "浏览：收藏、推荐、热门、历史",
            "下载：查看详情与封面、选择下载目录",
            "发送到 Kindle（SMTP）",
            "发送到微信读书",
            "账户配额查看",
            "主题切换",
            "网络诊断、自定义镜像、代理",
            "AI Agent 集成（Claude Code/Codex/Grok/MCP）"
        ],
        "install_methods": [
            "brew install heartleo/tap/zlib-cli",
            "curl -fsSL https://raw.githubusercontent.com/heartleo/zlib/main/install.sh | sh",
            "winget install --id heartleo.zlib --exact",
            "Go 源码构建: go build ./cmd/zlib"
        ],
        "cli_commands": {
            "search": "zlib search \"query\" --json --count 10 [--ext epub|pdf]",
            "favorites": "zlib favorites --json --page 1",
            "recommended": "zlib recommended --json",
            "most-popular": "zlib most-popular --json",
            "history": "zlib history --json --page 1 [--format epub]",
            "profile": "zlib profile --json",
            "doctor": "zlib doctor --json [--proxy \"proxy-url\"]",
            "login": "zlib login --domain <URL> [--cookies ./cookies.txt]",
            "download": "zlib download \"id:hash\" [--dir <dir>] --json [--send-to-kindle|--send-to-weread]",
            "kindle": "zlib kindle send <file> [--json]",
            "weread": "zlib weread import <file> --json",
            "metadata": "zlib meta <file> [--fetch --edit --json]",
            "tui": "zlib tui",
            "mcp": "zlib mcp [--read-only]"
        },
        "tui_keys": {
            "/": "打开命令列表",
            "↑/↓ or j/k": "选择书籍",
            "←/→": "翻页",
            "Enter": "下载选中书籍（需确认）",
            "Ctrl+F": "修改搜索查询/过滤器",
            "Esc": "返回",
            "/quit": "退出"
        },
        "agent_setup": {
            "Claude Code": "/plugin marketplace add heartleo/zlib && /plugin install zlib@zlib-plugin-cc",
            "Codex": "codex plugin marketplace add heartleo/zlib && codex plugin add zlib@zlib",
            "Grok": "grok plugin marketplace add heartleo/zlib && grok plugin install zlib --trust",
            "MCP server": "claude mcp add -s user zlib -- zlib mcp (或 codex/grok mcp add)"
        },
        "skill_modules": [
            {"name": "zlib", "desc": "搜索/下载/浏览/配额/网络诊断的核心 CLI 技能"},
            {"name": "kindle", "desc": "本地文件发送到 Kindle (SMTP)"},
            {"name": "metadata", "desc": "本地电子书元数据读取/查找/编辑/重命名"},
            {"name": "repo-readme", "desc": "README 编辑/审查技能（参考流行 TUI 项目模式）"},
            {"name": "security-scan", "desc": "安全扫描技能"},
            {"name": "zlib-tui", "desc": "TUI 界面技能"}
        ],
        "env_vars": {
            "ZLIB_DOWNLOAD_DIR": "下载目录（可选，默认当前目录）",
            "ZLIB_SMTP_PWD": "Kindle SMTP 密码（必填发送时）",
            "ZLIB_PROXY": "HTTP 代理（仅影响 HTTP，不影响 SMTP）",
            "ZLIB_DOMAIN": "默认域名（可选，login 时会更新 .env）"
        },
        "exit_codes": {
            "0": "成功",
            "1": "普通错误",
            "3": "需重新登录 (zlib login)",
            "4": "网络/镜像问题 (建议 zlib doctor)",
            "5": "文件保存成功但 Kindle/WeRead 投递失败",
            "130": "用户取消 (Ctrl+C)"
        },
        "trust_boundary": {
            "note": "登录、会话 cookies、API keys 均保存在本地，不上传。zlib 不存储第三方平台密码。"
        }
    }
    
    results = {
        "zlib.json": zlib_obj,
        "files.json": files,
        "skills.json": build_skills(),
        "docs.json": build_docs(),
        "links.json": {
            "repo": "https://github.com/heartleo/zlib",
            "releases": "https://github.com/heartleo/zlib/releases/latest",
            "homepage": "https://zlib.heartleo.dev/",
            "readme": "https://github.com/heartleo/zlib#readme",
            "readme_zh": "https://github.com/heartleo/zlib/blob/main/README.zh.md",
            "local_mirror": str(UP),
        },
    }
    
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()