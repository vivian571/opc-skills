#!/usr/bin/env python3
"""hypit 离线索引 CLI：零网络、只读、不执行任何 hypit 创作/渲染/登录操作。"""
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
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return obj
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return obj


def emit(title, obj, as_json):
    if as_json:
        return out(obj, True)
    print(f"=== {title} ===")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (list, dict)):
                print(f"  {k:<22} {len(v)} 项")
            else:
                print(f"  {k:<22} {v}")
    elif isinstance(obj, list):
        for item in obj:
            print("  " + (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)[:200]))
    return obj


def cmd_stats(args):
    s = load("hypit.json")
    f = load("files.json")
    pk = load("packages.json")
    rf = load("references.json")
    pb = load("playbooks.json")
    d = load("docs.json")
    sv = load("svml.json")
    info = {
        "仓库": s["repo"],
        "描述": s["description"][:60] + "...",
        "协议": s["license"],
        "版本": s["version"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "语言/工具链": f'{s["language"]} / node{s["node"]} / pnpm{s["pnpm"]}',
        "镜像文件": len(f),
        "子包": pk["count"],
        "reference 文档": rf["total"],
        "playbook": pb["count"],
        "文档条目": len(d),
        "SVML/SVS/SVRun": sv["counts"],
        "CLI 根命令": len(s["cli_commands"]),
    }
    if args.json:
        return out(info, True)
    print("=== hypit 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<20} {v}")
    return info


def cmd_commands(args):
    s = load("hypit.json")
    return emit("CLI 根命令清单", s["cli_commands"], args.json)


def cmd_concepts(args):
    s = load("hypit.json")
    return emit("核心概念", s["core_concepts"], args.json)


def cmd_packages(args):
    pk = load("packages.json")["packages"]
    if args.grep:
        pk = [p for p in pk if args.grep.lower() in p["name"].lower()
              or args.grep.lower() in p.get("description", "").lower()]
    if args.json:
        return out(pk, True)
    print(f"=== @hypit/* 子包（{len(pk)} 个）===")
    for p in pk:
        print(f"  {p['name']:<32} v{p['version']:<10} ts={p['src_ts_files']:<4} {p['description'][:50]}")
    return pk


def cmd_refs(args):
    rf = load("references.json")
    if args.json:
        return out(rf, True)
    print(f"=== reference 文档（共 {rf['total']} 份，按组）===")
    for g, paths in rf["groups"].items():
        print(f"  [{g}] {len(paths)} 份")
        if args.full:
            for p in paths:
                print(f"      {p}")
    return rf


def cmd_playbooks(args):
    pb = load("playbooks.json")
    if args.json:
        return out(pb, True)
    print(f"=== playbook（共 {pb['count']} 类）===")
    print(f"  -- craft（{len(pb['craft'])}）--")
    for p in pb["craft"]:
        print(f"      {p}")
    print(f"  -- formats（{len(pb['formats'])}）--")
    for p in pb["formats"]:
        print(f"      {p}")
    return pb


def cmd_svml(args):
    sv = load("svml.json")
    if args.json:
        return out(sv, True)
    print("=== SVML 三后缀 ===")
    for k, v in sv["extensions"].items():
        print(f"  .{k:<6} {v} （{sv['counts'][k]} 文件）")
    return sv


def cmd_docs(args):
    d = load("docs.json")
    if args.json:
        return out(d, True)
    print(f"=== 文档索引（{len(d)} 份）===")
    for doc in d:
        print(f"  {doc['path']:<48} {doc['title'][:40]}")
    return d


def cmd_safety(args):
    s = load("safety.json")
    if args.json:
        return out(s, True)
    return _print_rules("合规硬约束", s)


def _print_rules(title, rules):
    print(f"=== {title}（{len(rules)} 条）===")
    for r in rules:
        print(f"  [{r['id']}] {r['rule']}")
        print(f"       {r['detail']}")
    return rules


def cmd_pitfalls(args):
    p = load("pitfalls.json")
    if args.json:
        return out(p, True)
    print(f"=== 高频坑（{len(p)} 条）===")
    for x in p:
        print(f"  [{x['id']} 🔴{x['severity']}] {x['pitfall']}")
        print(f"       {x['detail']}")
    return p


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
    ap = argparse.ArgumentParser(description="hypit 离线索引 CLI：零网络、只读、不执行任何创作/渲染/登录操作。")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, func, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--json", action="store_true", default=False)
        p.set_defaults(func=func)
        return p

    add("stats", cmd_stats, "仓库与索引统计")
    add("commands", cmd_commands, "CLI 根命令清单")
    add("concepts", cmd_concepts, "核心概念")
    p = add("packages", cmd_packages, "@hypit/* 子包清单")
    p.add_argument("--grep", default="", help="按包名/描述过滤")
    p = add("refs", cmd_refs, "reference 文档索引")
    p.add_argument("--full", action="store_true", default=False, help="列出每个文件路径")
    add("playbooks", cmd_playbooks, "playbook 清单")
    add("svml", cmd_svml, "SVML/SVS/SVRun 文件清单")
    add("docs", cmd_docs, "文档索引")
    add("safety", cmd_safety, "合规硬约束")
    add("pitfalls", cmd_pitfalls, "高频坑")
    p = sub.add_parser("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/hypit.py stats | commands | concepts | packages | refs | playbooks | svml | docs | safety | pitfalls | find caption")
        return
    args.func(args)


if __name__ == "__main__":
    main()
