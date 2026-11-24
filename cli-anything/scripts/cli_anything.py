#!/usr/bin/env python3
"""cli_anything.py — cli-anything 技能包离线索引 CLI。
12 子命令，全部支持 --json。零第三方依赖。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    p = DATA / name
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def emit(obj, as_json, title=None):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        if title:
            print(f"## {title}")
        print(json.dumps(obj, ensure_ascii=False, indent=2))


def out(obj, as_json, title=None):
    """打印或返回 obj。"""
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        if title:
            print(f"### {title}")
        print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_stats(args):
    reg = load("registry.json")
    pub = load("public_registry.json")
    sk = load("skills.json")
    hs = load("harnesses.json")
    obj = {
        "repo": "HKUDS/CLI-Anything",
        "stars": 63599,
        "license": "Apache-2.0",
        "language": "Python",
        "harness_count": reg.get("count", 0),
        "category_count": len(reg.get("categories", {})),
        "public_cli_count": pub.get("count", 0),
        "skill_count": sk.get("count", 0),
        "agent_harness_dirs": hs.get("count", 0),
    }
    if args.json:
        out(obj, True)
    else:
        print("=== cli-anything 离线索引 ===")
        for k, v in obj.items():
            print(f"  {k:20}: {v}")


def cmd_list(args):
    reg = load("registry.json")
    clis = reg.get("clis", [])
    if args.category:
        clis = [c for c in clis if c.get("category") == args.category]
    obj = {"count": len(clis), "clis": [
        {"name": c["name"], "category": c.get("category"),
         "display_name": c.get("display_name"),
         "description": (c.get("description") or "")[:100]}
        for c in clis]}
    if args.json:
        out(obj, True)
    else:
        print(f"=== {len(clis)} 个 harness" + (f"（类目 {args.category}）" if args.category else "") + " ===")
        for c in obj["clis"]:
            print(f"  {c['name']:22} [{c['category']:14}] {c['display_name']}")
        if not clis:
            print("  （无匹配）")


def cmd_show(args):
    reg = load("registry.json")
    match = next((c for c in reg.get("clis", []) if c["name"] == args.name), None)
    if not match:
        print(f"未找到 harness: {args.name}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        out(match, True)
    else:
        print(f"### {match.get('display_name')} ({match['name']})")
        for k in ["version", "category", "description", "requires",
                  "install_cmd", "entry_point", "skill_md", "homepage"]:
            v = match.get(k)
            if v:
                print(f"  {k:12}: {v}")


def cmd_categories(args):
    reg = load("registry.json")
    cats = reg.get("categories", {})
    obj = {"count": len(cats), "categories": [
        {"category": k, "count": len(v), "members": v} for k, v in cats.items()]}
    if args.json:
        out(obj, True)
    else:
        print(f"=== {len(cats)} 个类别 ===")
        for c in obj["categories"]:
            print(f"  {c['category']:20} ({c['count']:2}) {', '.join(c['members'][:6])}"
                  + (" ..." if c['count'] > 6 else ""))


def cmd_find(args):
    reg = load("registry.json")
    kw = args.keyword.lower()
    hits = []
    for c in reg.get("clis", []):
        blob = " ".join(str(c.get(k, "")) for k in
                        ["name", "display_name", "description", "category", "requires"]).lower()
        if kw in blob:
            hits.append({"name": c["name"], "category": c.get("category"),
                         "display_name": c.get("display_name"),
                         "description": (c.get("description") or "")[:120]})
    hits = hits[: args.limit]
    obj = {"keyword": args.keyword, "count": len(hits), "hits": hits}
    if args.json:
        out(obj, True)
    else:
        print(f"=== 搜「{args.keyword}」命中 {len(hits)} ===")
        for h in hits:
            print(f"  {h['name']:22} [{h['category']}] {h['display_name']}")
            print(f"    {h['description']}")
        if not hits:
            print("  （无）")


def cmd_public(args):
    pub = load("public_registry.json")
    if args.json:
        out(pub, True)
    else:
        print(f"=== {pub.get('count', 0)} 个公共 CLI ===")
        for c in pub.get("clis", []):
            print(f"  {c.get('name'):22} [{c.get('category','')}] {c.get('display_name','')}")
            if c.get("install_cmd"):
                print(f"    install: {c['install_cmd']}")


def cmd_skills(args):
    sk = load("skills.json")
    if args.json:
        out(sk, True)
    else:
        print(f"=== {sk.get('count', 0)} 份 SKILL.md ===")
        for s in sk.get("skills", []):
            print(f"  {s['name']:36} {s['description'][:80]}")


def cmd_harnesses(args):
    hs = load("harnesses.json")
    if args.json:
        out(hs, True)
    else:
        print(f"=== {hs.get('count', 0)} 个 agent-harness 目录 ===")
        for h in hs.get("harnesses", []):
            print(f"  {h['software']:22} py={h['py_files']:3} packaged={h['packaged']}")


def cmd_safety(args):
    s = load("safety.json")
    if args.json:
        out(s, True)
    else:
        print(f"### {s.get('title')}  (License: {s.get('license')})")
        for r in s.get("rules", []):
            print(f"  [{r['level'].upper():5}] {r['id']}")
            print(f"          {r['rule']}")


def cmd_pitfalls(args):
    p = load("pitfalls.json")
    if args.json:
        out(p, True)
    else:
        print(f"### {p.get('title')}")
        for x in p.get("pitfalls", []):
            print(f"  {x['id']}  {x['symptom']}")
            print(f"    因: {x['cause']}")
            print(f"    治: {x['fix']}")


def cmd_links(args):
    l = load("links.json")
    if args.json:
        out(l, True)
    else:
        print(f"### {l.get('title')}")
        for x in l.get("links", []):
            print(f"  {x['label']:28} {x['url']}")


def cmd_rebuild(args):
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_index.py")],
                       capture_output=True, text=True)
    if args.json:
        out({"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr}, True)
    else:
        print(r.stdout or r.stderr)


def main():
    ap = argparse.ArgumentParser(description="cli-anything 离线索引 CLI")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats", help="概览统计").add_argument("--json", action="store_true")
    p = sub.add_parser("list", help="列出 harness"); p.add_argument("--category"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("show", help="harness 详情"); p.add_argument("name"); p.add_argument("--json", action="store_true")
    sub.add_parser("categories", help="分类统计").add_argument("--json", action="store_true")
    p = sub.add_parser("find", help="关键词搜"); p.add_argument("keyword"); p.add_argument("--limit", type=int, default=10); p.add_argument("--json", action="store_true")
    sub.add_parser("public", help="公共 CLI").add_argument("--json", action="store_true")
    sub.add_parser("skills", help="skills 清单").add_argument("--json", action="store_true")
    sub.add_parser("harnesses", help="harness 目录").add_argument("--json", action="store_true")
    sub.add_parser("safety", help="合规硬约束").add_argument("--json", action="store_true")
    sub.add_parser("pitfalls", help="已知坑点").add_argument("--json", action="store_true")
    sub.add_parser("links", help="链接").add_argument("--json", action="store_true")
    sub.add_parser("rebuild", help="重建索引").add_argument("--json", action="store_true")

    args = ap.parse_args()
    # 统一 --json：顶层或子命令均可
    if not getattr(args, "json", False):
        args.json = False

    dispatch = {
        "stats": cmd_stats, "list": cmd_list, "show": cmd_show,
        "categories": cmd_categories, "find": cmd_find, "public": cmd_public,
        "skills": cmd_skills, "harnesses": cmd_harnesses, "safety": cmd_safety,
        "pitfalls": cmd_pitfalls, "links": cmd_links, "rebuild": cmd_rebuild,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
