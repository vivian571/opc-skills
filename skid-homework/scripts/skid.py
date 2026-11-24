#!/usr/bin/env python3
"""skid-homework 离线索引 CLI：零网络、只读、不执行任何 AI 调用。"""
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
    s = load("skid.json")
    f = load("files.json")
    m = load("modules.json")
    p = load("prompts.json")
    info = {
        "仓库": s["repo"],
        "描述": s.get("description", "")[:60],
        "协议": s["license"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "镜像文件": len(f) if isinstance(f, list) else f.get("count", "?"),
        "核心模块": len(m) if isinstance(m, list) else m.get("count", "?"),
        "Prompt 文件": len(p) if isinstance(p, dict) else p.get("count", "?"),
        "npm deps": s.get("dependency_count", {}).get("deps", "?"),
        "Node 要求": "≥20 (Next.js 15)",
    }
    if args.json:
        return out(info, True)
    print("=== skid-homework 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_modules(args):
    m = load("modules.json")
    mods = m if isinstance(m, list) else m.get("modules", [])
    if args.group:
        mods = [x for x in mods if args.group.lower() in x.get("group", "").lower()]
    out_data = [{"path": x["path"], "lines": x["lines"], "role": x["role"][:60]} for x in mods]
    if args.json:
        return out(out_data, True)
    print(f"=== 核心模块（共 {len(out_data)} 个）===")
    for i, x in enumerate(out_data, 1):
        print(f"  {i:2}. {x['path']:<45} {x['lines']:>4} 行  {x['role'][:60]}")
    return out_data


def cmd_prompts(args):
    p = load("prompts.json")
    if args.json:
        return out(p, True)
    print("=== AI Prompt 文件清单 ===")
    for k, v in p.items():
        print(f"  {k:<35} {v['lines']:>3} 行  {v['chars']:>5} 字  {v['preview'][:60]}")
    return p


def cmd_commands(args):
    s = load("skid.json")
    cmds = s.get("commands", [])
    shortcuts = s.get("key_shortcuts", [])
    if args.json:
        return out({"commands": cmds, "shortcuts": shortcuts}, True)
    print("=== npm/pnpm scripts ===")
    for c in cmds:
        print(f"  {c['cmd']:<35} {c['desc']}")
    print("\n=== 默认快捷键 ===")
    for k in shortcuts:
        print(f"  {k['keys']:<12} {k['action']}")
    return cmds


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
    ap = argparse.ArgumentParser(description="skid-homework 离线索引 CLI：零网络、只读、不执行任何 AI 调用。")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("stats", help="仓库与索引统计")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("modules", help="核心模块清单")
    p.add_argument("--group", default="", help="按分组过滤")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_modules)

    p = sub.add_parser("prompts", help="Prompt 文件清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_prompts)

    p = sub.add_parser("commands", help="命令清单 + 快捷键")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_commands)

    p = sub.add_parser("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/skid.py stats | modules | prompts | commands | find jsxgraph")
        return
    args.func(args)


if __name__ == "__main__":
    main()