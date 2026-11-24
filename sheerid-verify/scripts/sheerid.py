#!/usr/bin/env python3
"""sheeridVerify 离线索引 CLI：零网络、只读、不执行任何验证流程。"""

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


def cmd_stats(args):
    repo, files, mods, tests = (load(x) for x in ("repo.json", "files.json", "modules.json", "tests.json"))
    s = tests["summary"]
    groups = {}
    for m in mods:
        groups[m["group"]] = groups.get(m["group"], 0) + 1
    info = {
        "仓库": repo["repo"], "版本": repo["version"], "协议": repo["license"],
        "star/fork（核实快照）": f'{repo["stargazers_count"]}/{repo["forks_count"]}',
        "Node 要求": repo["engines"]["node"],
        "镜像文件": len(files), "镜像体积 KB": round(sum(f["bytes"] for f in files) / 1024, 1),
        "JS 模块": len(mods), "模块分组": groups,
        "测试用例": tests["case_count"],
        "最近一次实测": f'{s["pass"]} pass / {s["fail"]} fail / {s["skipped"]} skipped（exit {s["exit"]}）',
        "测试命令": tests["command"],
    }
    if args.json:
        return out(info, True)
    print("=== sheeridVerify 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")


def cmd_tests(args):
    t = load("tests.json")
    if args.json and args.status == "all":
        return out(t, True)
    cases = [c for c in t["cases"] if args.status == "all" or c["status"] == args.status]
    if args.json:
        return out(cases, True)
    print(f"=== 测试用例（{args.status}）共 {len(cases)} / {t['case_count']} ===")
    for c in cases:
        flag = "SKIP" if c["status"] == "skip" else "PASS"
        extra = f"  ← {c['reason']}" if c.get("reason") else ""
        print(f"  [{flag}] {c['name']}{extra}")
    print(f"\n最近一次：{t['summary']}")
    print(f"Mock 说明：{t['mock']}")


def cmd_modules(args):
    mods = load("modules.json")
    if args.group:
        mods = [m for m in mods if args.group.lower() in m["group"].lower()]
    if args.json:
        return out(mods, True)
    print(f"=== 源码模块 {len(mods)} 个 ===")
    for m in mods:
        print(f"  {m['path']:<38} {m['lines']:>4} 行  [{m['group']}] {m['role']}")


def cmd_commands(args):
    c = load("commands.json")
    if args.json:
        return out(c, True)
    print("=== npm scripts ===")
    for s in c["scripts"]:
        print(f"  npm run {s['name']:<15} {s['note']}")
    print("\n=== CLI 参数 ===")
    for s in c["cli_flags"]:
        print(f"  {s['flag']:<20} {s['note']}")
    print("\n=== 退出码 ===")
    for s in c["exit_codes"]:
        print(f"  {s['code']:<4} {s['meaning']}")
    print("\n=== 环境变量 ===")
    for s in c["env_vars"]:
        print(f"  {s['name']:<26} {s['note']}")
    print("\n=== 写请求头 ===")
    for s in c["write_headers"]:
        print(f"  {s['name']:<26} {s['note']}")


def cmd_config(args):
    c = load("config.json")
    fields = c["fields"]
    if args.key:
        fields = [f for f in fields if args.key.lower() in f["key"].lower()]
    if args.json:
        return out(fields, True)
    print(f"=== 配置字段（{c['source']} → {c['target']}）===")
    for f in fields:
        print(f"  {f['key']:<36} = {json.dumps(f['example'], ensure_ascii=False)}  {f['note']}")
    print(f"\n规则：{c['rule']}")


def cmd_endpoints(args):
    e = load("endpoints.json")
    if args.json:
        return out(e, True)
    print("=== Web 工作台接口 ===")
    for x in e:
        print(f"  {x['method']:<7} {x['path']:<34} {x['note']}  [{x['auth']}]")


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


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="输出原始 JSON（可放在子命令前后）")
    ap = argparse.ArgumentParser(description="sheeridVerify 离线索引（只读，不联网、不跑验证流程）",
                                 parents=[common])
    sub = ap.add_subparsers(dest="cmd")

    def add(name, **kw):
        return sub.add_parser(name, parents=[common], **kw)

    add("stats", help="仓库与索引统计")
    p = add("tests", help="测试用例清单")
    p.add_argument("--status", choices=["all", "pass", "skip"], default="all")
    p = add("modules", help="源码模块索引")
    p.add_argument("--group", default="")
    add("commands", help="npm scripts / CLI 参数 / 环境变量")
    p = add("config", help="配置字段")
    p.add_argument("--key", default="")
    add("endpoints", help="Web API 端点")
    for name, helptext in [("safety", "合规边界"), ("pitfalls", "高频坑"),
                          ("diffs", "口径差异"), ("verification", "核实记录"),
                          ("links", "上游链接"), ("repo", "仓库元数据"),
                          ("files", "镜像文件清单")]:
        p = add(name, help=helptext)
        p.set_defaults(file=name)
    p = add("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)

    args = ap.parse_args()
    args.json = getattr(args, "json", False)
    handlers = {
        "stats": cmd_stats, "tests": cmd_tests, "modules": cmd_modules,
        "commands": cmd_commands, "config": cmd_config, "endpoints": cmd_endpoints,
        "find": cmd_find,
    }
    if not args.cmd:
        ap.print_help()
        print("\n示例：python3 scripts/sheerid.py stats | tests --status skip | find Camoufox | safety")
        return
    if args.cmd in handlers:
        handlers[args.cmd](args)
    else:
        obj = load(args.cmd + ".json")
        print(json.dumps(obj, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
