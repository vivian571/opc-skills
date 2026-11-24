#!/usr/bin/env python3
"""t3code 离线索引 CLI：零网络、只读、不执行任何 t3server/agent 连接操作。"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # ~/.workbuddy/skills/t3code/
DATA = ROOT / "data"
UPSTREAM = ROOT / "upstream"


def load(name):
    path = DATA / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def out(obj, as_json):
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return obj


def emit(title, obj, as_json):
    if as_json:
        return out(obj, True)
    print(f"=== {title} ===")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (list, dict)):
                print(f"  {k:<20} {len(v) if isinstance(v, list) else 'dict'} 项")
            else:
                print(f"  {k:<20} {v}")
    elif isinstance(obj, list):
        for item in obj:
            print("  " + (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)[:180]))
    return obj


def cmd_stats(args):
    s = load("t3code.json")
    info = {
        "仓库": s["repo"],
        "描述": s["description"][:70] + "...",
        "协议": s["license"],
        "版本": s["version"],
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "语言/工具链": f'{s["language"]} / pnpm monorepo',
        "镜像文件(本包)": len(list((ROOT / "upstream").glob("*.md"))),
        "apps": len(s.get("apps", [])),
        "core_concepts": len(s.get("core_concepts", {})),
        "supported_providers": len(s.get("supported_providers", {})),
        "cli_commands": len(s.get("cli_commands", {})),
    }
    if args.json:
        return out(info, True)
    print("=== t3code 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<20} {v}")
    return info


def cmd_commands(args):
    s = load("t3code.json")
    return emit("CLI 命令清单", s.get("cli_commands", {}), args.json)


def cmd_providers(args):
    s = load("t3code.json")
    return emit("支持的所有 Agent Provider", s.get("supported_providers", {}), args.json)


def cmd_concepts(args):
    s = load("t3code.json")
    return emit("核心概念", s.get("core_concepts", {}), args.json)


def cmd_architecture(args):
    s = load("t3code.json")
    return emit("架构", s.get("architecture", {}), args.json)


def cmd_safety(args):
    rules = [
        {"id": "S1", "rule": "只做离线索引", "detail": "grep/头读/索引，不启动 t3 server、不连 agent、不登录。"},
        {"id": "S2", "rule": "凭证不在本包内", "detail": "t3code 用系统 keychain 或 1Password Connect；本包不记录密钥。"},
        {"id": "S3", "rule": "MIT 无附加条件", "detail": "商业使用/再分发/修改均自由，无需额外授权。"},
        {"id": "S4", "rule": "ACP 兼容性自负", "detail": "需确认所用 agent 版本与 t3code version 兼容。"},
        {"id": "S5", "rule": "隐私边界", "detail": "thread 内容经 server 转发给 agent，公共环境勿跑敏感项目。"},
    ]
    if args.json:
        return out(rules, True)
    print(f"=== 合规提示（{len(rules)} 条）===")
    for r in rules:
        print(f"  [{r['id']}] {r['rule']}")
        print(f"       {r['detail']}")
    return rules


def cmd_pitfalls(args):
    pitfalls = [
        {"id": "P1", "severity": "高", "pitfall": "Skill 与可执行是两条独立通道", "detail": "装 Skill ≠ 能 connect agent"},
        {"id": "P2", "severity": "高", "pitfall": "t3 server 需 agent 已登录", "detail": "它不调凭证，用你自己的 claude/codex auth"},
        {"id": "P3", "severity": "中", "pitfall": "Thread 重启丢失历史", "detail": "每个 thread 是独立会话，不是持久终端"},
        {"id": "P4", "severity": "中", "pitfall": "Worktree 需 git ≥ 2.25", "detail": "老系统 worktree 命令不生效"},
        {"id": "P5", "severity": "中", "pitfall": "Mobile app 需同网/Tailscale", "detail": "手机连不到 server IP 就无法远程审批"},
        {"id": "P6", "severity": "中", "pitfall": "Provider 升级可能破坏 ACP", "detail": "升级前查 release notes 和 provider 最低要求"},
        {"id": "P7", "severity": "低", "pitfall": "SnapShots 不持久化代码变更", "detail": "只是可视快照，commit 才是真实状态保存"},
    ]
    if args.json:
        return out(pitfalls, True)
    print(f"=== 高频坑（{len(pitfalls)} 条）===")
    for x in pitfalls:
        mark = "🔴" if x["severity"] == "高" else ("🟡" if x["severity"] == "中" else "⚪")
        print(f"  [{x['id']} {mark}{x['severity']}] {x['pitfall']}")
        print(f"       {x['detail']}")
    return pitfalls


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
    # Also search upstream docs
    for p in sorted(UPSTREAM.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if args.keyword.lower() in text.lower():
            lines_found = [l.strip() for l in text.splitlines() if args.keyword.lower() in l.lower()]
            for line in lines_found[:5]:  # cap per-file hits
                hits.append({"file": "upstream/" + p.name, "line": line[:200]})
    if args.json:
        return out(hits[: args.limit], True)
    print(f"=== 搜索「{args.keyword}」命中 {len(hits)} 行，显示前 {args.limit} ===")
    for h in hits[: args.limit]:
        print(f"  [{h['file']}] {h['line'][:180]}")
    return hits


def main():
    ap = argparse.ArgumentParser(description="t3code 离线索引 CLI：零网络、只读、不执行任何连接操作。")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, func, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--json", action="store_true", default=False)
        p.set_defaults(func=func)
        return p

    add("stats", cmd_stats, "仓库与索引统计")
    add("commands", cmd_commands, "CLI 命令清单")
    add("providers", cmd_providers, "支持的 Agent Provider 列表")
    add("concepts", cmd_concepts, "核心概念")
    add("architecture", cmd_architecture, "架构组件说明")
    add("safety", cmd_safety, "合规提示")
    add("pitfalls", cmd_pitfalls, "高频坑")
    p = sub.add_parser("find", help="跨全部索引全文搜索（含 upstream/ 文档）")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/t3code.py stats | commands | providers | concepts | architecture | safety | pitfalls | find <关键词>")
        return
    args.func(args)


if __name__ == "__main__":
    main()
