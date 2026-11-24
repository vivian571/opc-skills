#!/usr/bin/env python3
"""Mika 离线索引 CLI：零网络、只读、不执行任何 Android 操作。"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    path = DATA / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def out(obj, as_json):
    return obj if as_json else print(json.dumps(obj, ensure_ascii=False, indent=2)) or obj


def cmd_stats(args):
    s = load("mika.json")
    f = load("files.json")
    d = load("docs.json")
    info = {
        "仓库": s["repo"],
        "描述": s.get("description", "")[:60],
        "协议": s["license"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "版本": s.get("version", "?"),
        "镜像文件": len(f) if isinstance(f, list) else f.get("count", "?"),
        "文档文件": len(d) if isinstance(d, dict) else "?",
        "语言": s.get("language", "?"),
        "本机可运行": "❌ 否（需 Android 设备 + APK 安装）",
        "本包用途": "离线索引与技术架构分析，**不代部署、不连设备**",
    }
    if args.json:
        return out(info, True)
    print("=== Mika 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_quickstart(args):
    s = load("mika.json")
    steps = s.get("quick_start", [])
    if args.json:
        return out(steps, True)
    print("=== 三步快速开始 ===")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    return steps


def cmd_cli(args):
    s = load("mika.json")
    cmds = s.get("cli_commands", {})
    if args.json:
        return out(cmds, True)
    print("=== CLI 命令清单 ===")
    for cmd, desc in cmds.items():
        print(f"  {cmd:<35} {desc}")
    return cmds


def cmd_docs(args):
    d = load("docs.json")
    if args.json:
        return out(d, True)
    print("=== 关键文档 ===")
    for path, info in d.items():
        print(f"  {path:<40} {info['chars']:>5} 字  {info['lines']:>3} 行  {info['desc']}")
    return d


def cmd_find(args):
    hits = []
    for p in sorted(DATA.glob("*.json")):
        text = p.read_text(encoding="utf-8")
        if args.keyword.lower() in text.lower():
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                continue
            for line in json.dumps(obj, ensure_ascii=False, indent=2).splitlines():
                if args.keyword.lower() in line.lower():
                    hits.append({"file": p.name, "line": line.strip()})
    if args.json:
        return out(hits[: args.limit], True)
    print(f"=== 搜索「{args.keyword}」命中 {len(hits)} 行，显示前 {args.limit} ===")
    for h in hits[: args.limit]:
        print(f"  [{h['file']}] {h['line'][:160]}")
    return hits


def main():
    ap = argparse.ArgumentParser(description="Mika 离线索引 CLI：零网络、只读、不执行任何 Android 操作。")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("stats", help="仓库与索引统计")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("quickstart", help="三步快速开始")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_quickstart)

    p = sub.add_parser("cli", help="CLI 命令清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_cli)

    p = sub.add_parser("docs", help="关键文档索引")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_docs)

    p = sub.add_parser("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/mika.py stats | quickstart | cli | docs | find accessibility")
        return
    args.func(args)


if __name__ == "__main__":
    main()
