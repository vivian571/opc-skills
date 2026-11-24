#!/usr/bin/env python3
"""paper-orchestra 离线索引 CLI：零网络、只读、不执行任何 pipeline。"""
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
    s = load("paper-orchestra.json")
    f = load("files.json")
    a = load("agents.json")
    info = {
        "仓库": s["repo"],
        "描述": s.get("description", "")[:60],
        "协议": s["license"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "镜像文件": len(f) if isinstance(f, list) else f.get("count", "?"),
        "Agent 模块": a.get("count", "?"),
        "Python deps": s.get("deps_count", "?"),
        "LaTeX 模板": ", ".join(s.get("latex_templates", [])),
        "数据集状态": "暂未公开（README 声明 released separately）",
        "本包用途": "离线索引与技术架构分析，**不代跑 pipeline**",
    }
    if args.json:
        return out(info, True)
    print("=== paper-orchestra 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_pipeline(args):
    s = load("paper-orchestra.json")
    stages = s.get("pipeline_stages", [])
    if args.json:
        return out(stages, True)
    print("=== Pipeline 五阶段 ===")
    for i, st in enumerate(stages, 1):
        print(f"  {i}. [{st['stage']}] {st['desc']}")
        print(f"     文件：{st['agent_file']}")
    return stages


def cmd_cli(args):
    s = load("paper-orchestra.json")
    cli = s.get("cli_args", {})
    env = s.get("env_vars", {})
    if args.json:
        return out({"cli_args": cli, "env_vars": env}, True)
    print("=== 必填 CLI 参数 ===")
    for k, v in cli.items():
        if "必填" in v:
            print(f"  {k:<35} {v}")
    print("\n=== 可选 CLI 参数 ===")
    for k, v in cli.items():
        if "必填" not in v:
            print(f"  {k:<35} {v}")
    print("\n=== .env 环境变量 ===")
    for k, v in env.items():
        required = "必须" in v
        print(f"  {'[必填]' if required else '[可选]'} {k:<30} {v[:60]}")
    return {"cli_args": cli, "env_vars": env}


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
    ap = argparse.ArgumentParser(description="paper-orchestra 离线索引 CLI：零网络、只读、不执行任何 pipeline。")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("stats", help="仓库与索引统计")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("pipeline", help="Pipeline 五阶段详情")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_pipeline)

    p = sub.add_parser("cli", help="CLI 参数 + .env 环境变量")
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_cli)

    p = sub.add_parser("find", help="跨全部索引全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/paper_orch.py stats | pipeline | cli | find semantic")
        return
    args.func(args)


if __name__ == "__main__":
    main()