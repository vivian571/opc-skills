#!/usr/bin/env python3
"""agent-skills 离线索引 CLI：零网络、只读、不执行任何 agent 流程。"""
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
    s = load("skills.json")
    f = load("files.json")
    e = load("evals.json")
    c = load("commands.json")
    phases = {}
    for sk in s.get("skills", []):
        p = sk.get("group", "其他")
        phases[p] = phases.get(p, 0) + 1
    info = {
        "仓库": s["repo"],
        "协议": s["license"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "总技能数": s.get("total_skills", len(s.get("skills", []))),
        "镜像文件": f.get("count", "?") if isinstance(f, dict) else len(f),
        "评测用例总数": sum(x["case_count"] for x in e.get("cases", [])),
        "命令文件数": len(c.get("toml", {})) + len(c.get("claude_md", {})),
        "Phase 分布": phases,
    }
    if args.json:
        return out(info, True)
    print("=== agent-skills 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_list(args):
    s = load("skills.json")
    skills = s.get("skills", [])
    if args.phase:
        skills = [sk for sk in skills if sk["group"] == args.phase]
    if args.search:
        kw = args.search.lower()
        skills = [sk for sk in skills if kw in str(sk).lower()]
    out_map = [{"name": x["name"], "group": x["group"], "overview": x["overview"][:60]} for x in skills]
    if args.json:
        return out(out_map, True)
    print(f"=== 技能清单（共 {len(out_map)} 项）===")
    for i, x in enumerate(out_map, 1):
        print(f"  {i:2}. {x['name']:<30} [{x['group']}] {x['overview'][:60]}")
    return out_map


def cmd_evals(args):
    e = load("evals.json")
    cases = e.get("cases", [])
    if args.skill:
        cases = [c for c in cases if args.skill in c.get("skill", "")]
    out_data = {"cases": cases, "count": len(cases)}
    if args.json:
        return out(out_data, True)
    print(f"=== 评测用例（共 {len(cases)} 个 skill）===")
    for c in cases:
        print(f"  {c['skill']:<32} positive={c['positive_count']} negative={c['negative_count']} case={c['case_count']}")
    return out_data


def cmd_commands(args):
    c = load("commands.json")
    toml = c.get("toml", {})
    claude = c.get("claude_md", {})
    if args.json:
        return out({"toml": toml, "claude_md": claude}, True)
    print("=== TOML 命令文件 ===")
    for k, v in toml.items():
        print(f"  {k:<15} {v[:80]}")
    print("\n=== .claude/commands 命令 ===")
    for k, v in claude.items():
        print(f"  {k:<15} {v[:80]}")
    return c


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
    ap = argparse.ArgumentParser(description="agent-skills 离线索引 CLI：零网络、只读、不执行任何 agent 流程。")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("stats", help="仓库与索引统计")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("list", help="技能清单")
    p.add_argument("--phase", default="", help="按 Phase 过滤（define/plan/build/verify/review/ship）")
    p.add_argument("--search", default="", help="关键词过滤")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("evals", help="评测用例清单")
    p.add_argument("--skill", default="", help="筛选指定 skill")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_evals)

    p = sub.add_parser("commands", help="TOML/Claude 命令文件")
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
        print("\n示例：python3 scripts/agent_skills.py stats | list --phase build | find commit")
        return
    args.func(args)


if __name__ == "__main__":
    main()
