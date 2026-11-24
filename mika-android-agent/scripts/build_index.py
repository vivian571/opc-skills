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


def build_repo():
    prev_path = DATA / "mika.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    return {
        "repo": "wangzan101/Mika",
        "url": "https://github.com/wangzan101/Mika",
        "homepage": "https://mikaphone.com",
        "name": "Mika",
        "description": prev.get("description", "An on-device AI agent for Android that operates apps and the web to get things done for you."),
        "version": "0.1.47",
        "license": "Apache-2.0",
        "author": "wangzan101",
        "language": "Kotlin / Java (Android)",
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 9099),
        "forks_count": prev.get("forks_count", 2052),
        "created_at": prev.get("created_at", "2026-10-29T14:34:07Z"),
        "pushed_at": prev.get("pushed_at", "2026-11-18T18:27:41Z"),
        "verified_at": "2026-11-19",
        "note": "star/fork/pushed_at 为 2026-11-19 GitHub API 快照。这是 Android 原生应用，非 Web/Node/Python 项目，无法在 macOS 本地运行；只能下载 APK 安装到 Android 设备。实时值以 --refresh 为准。",
        "build_requirements": prev.get("build_requirements", {}),
        "modules": prev.get("modules", []),
        "key_features": prev.get("key_features", []),
        "quick_start": prev.get("quick_start", []),
        "cli_commands": prev.get("cli_commands", {}),
        "architecture_notes": prev.get("architecture_notes", ""),
        "privacy_safety": prev.get("privacy_safety", ""),
        "deployment_options": prev.get("deployment_options", []),
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


def build_docs():
    doc_map = {
        "README.md": "项目主文档（中英双语）",
        "docs/setup-guide.en.md": "手机配对设置指南（6 步向导）",
        "docs/cli.en.md": "CLI 与 Skill 用法说明",
        "docs/computer.en.md": "计算机远程接入指南",
        "docs/dev/architecture.md": "架构文档（模块分层、TaskService、AgentLoop）",
        "docs/models.en.md": "模型 provider 列表与签名方式",
        "docs/features.en.md": "功能详细说明",
        "docs/disclaimer.en.md": "免责声明",
        ".github/CONTRIBUTING.md": "贡献指南",
    }
    out = {}
    for path, desc in doc_map.items():
        try:
            text = read(path)
            out[path] = {"desc": desc, "chars": len(text), "lines": text.count("\n")+1}
        except:
            out[path] = {"desc": desc, "chars": 0, "lines": 0}
    return out


def build_links():
    return {
        "repo": "https://github.com/wangzan101/Mika",
        "releases": "https://github.com/wangzan101/Mika/releases/latest",
        "homepage": "https://mikaphone.com",
        "setup_guide": "https://github.com/wangzan101/Mika/blob/main/docs/setup-guide.en.md",
        "cli_doc": "https://github.com/wangzan101/Mika/blob/main/docs/cli.en.md",
        "local_mirror": str(UP),
    }


def main():
    files = build_files()
    results = {
        "mika.json": build_repo(),
        "files.json": files,
        "docs.json": build_docs(),
        "links.json": build_links(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()
