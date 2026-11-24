#!/usr/bin/env python3
"""zlib 离线索引 CLI：零网络、只读、不执行任何 Z-Library 操作。"""
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
    s = load("zlib.json")
    f = load("files.json")
    sk = load("skills.json")
    d = load("docs.json")
    info = {
        "仓库": s["repo"],
        "描述": s.get("description", "")[:60],
        "协议": s["license"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "镜像文件": len(f) if isinstance(f, list) else f.get("count", "?"),
        "技能模块": sk.get("count", "?"),
        "文档条目": len(d) if isinstance(d, dict) else "?",
        "安装方式": len(s.get("install_methods", [])),
        "CLI 命令": len(s.get("cli_commands", {})),
    }
    if args.json:
        return out(info, True)
    print("=== zlib 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_commands(args):
    s = load("zlib.json")
    cmds = s.get("cli_commands", {})
    if args.json:
        return out(cmds, True)
    print("=== CLI 命令清单 ===")
    for cmd, desc in cmds.items():
        print(f"  {cmd:<35} {desc}")
    return cmds


def cmd_skills(args):
    sk = load("skills.json")
    skills = sk.get("skills", [])
    if args.json:
        return out(skills, True)
    print(f"=== Skill 模块（共 {len(skills)} 个）===")
    for sk in skills:
        print(f"  {sk['name']:<20} {sk['description'][:60]}")
    return skills


def cmd_env(args):
    s = load("zlib.json")
    env = s.get("env_vars", {})
    if args.json:
        return out(env, True)
    print("=== 环境变量 ===")
    for k, v in env.items():
        print(f"  {k:<25} {v}")
    return env


def cmd_codes(args):
    s = load("zlib.json")
    codes = s.get("exit_codes", {})
    if args.json:
        return out(codes, True)
    print("=== 退出码 ===")
    for k, v in codes.items():
        print(f"  {k:<4} {v}")
    return codes


def cmd_skills(args):
    s = load("skills.json")
    skills = s.get("skills", [])
    if args.json:
        return out(skills, True)
    print(f"=== Skill 模块（共 {len(s.get('skills', []))} 个）===")
    for sk in s.get("skills", []):
        print(f"  {sk['name']:<20} {sk['description'][:60]}")
    return s.get("skills", [])


def cmd_keys(args):
    s = load("zlib.json")
    keys = s.get("tui_keys", {})
    if args.json:
        return out(keys, True)
    print("=== TUI 键位 ===")
    for k, v in keys.items():
        print(f"  {k:<12} {v}")
    return keys


def cmd_agents(args):
    s = load("zlib.json")
    agents = s.get("agent_setup", {})
    if args.json:
        return out(agents, True)
    print("=== Agent 集成方式 ===")
    for name, cmd in s.get("agent_setup", {}).items():
        print(f"  {name:<12} {cmd}")
    return agents


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
    ap = argparse.ArgumentParser(description="zlib 离线索引 CLI：零网络、只读、不执行任何 Z-Library 操作。")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("stats", help="仓库与索引统计")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("commands", help="CLI 命令清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_commands)

    p = sub.add_parser("skills", help="Skill 模块清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_skills)

    p = sub.add_parser("env", help="环境变量清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_env)

    p = sub.add_parser("codes", help="退出码清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_codes)

    p = sub.add_parser("keys", help="TUI 键位清单")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_keys)

    p = sub.add_parser("agents", help="Agent 集成方式")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_agents)

    p = sub.add_parser("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/zlib.py stats | commands | skills | env | codes | keys | agents | find smtp")
        return
    args.func(args)


if __name__ == "__main__":
    main()