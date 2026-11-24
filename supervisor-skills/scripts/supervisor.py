#!/usr/bin/env python3
"""supervisor-skills 离线索引 CLI：零网络、只读、不调用任何模型、不写项目文件。

把 HKUSTDial/Supervisor-Skills 的 12 个科研技能 + 36 份 handbook 指南
做成可检索的离线手册。所有内容来自 upstream/ 镜像。
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UP = ROOT / "upstream"


def load(name):
    path = DATA / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def out(obj, as_json):
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return obj


def clean_desc(text, limit=160):
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text).strip()
    return t[:limit] + ("..." if len(t) > limit else "")


def cmd_stats(args):
    s = load("supervisor.json")
    sk = load("skills.json")
    hb = load("handbook.json")
    info = {
        "仓库": s["repo"],
        "作者": s["author"],
        "协议": s["license"],
        "版本": f'v{s["version"]}',
        "star/fork（核实快照）": f'{s["stargazers_count"]}/{s["forks_count"]}',
        "语言/工具链": s["language"],
        "镜像 md 文件": s["mirrored_md"],
        "科研技能": sk["count"],
        "handbook 文档": hb["count"],
        "handbook 章节": len(hb["chapters"]),
        "核心概念": len(s["core_concepts"]),
        "工作流阶段": len(s["workflow_stages"]),
    }
    if args.json:
        return out(info, True)
    print("=== supervisor-skills 技能包统计 ===")
    for k, v in info.items():
        print(f"  {k:<22} {v}")
    return info


def cmd_skills(args):
    sk = load("skills.json")["skills"]
    if args.group:
        sk = [s for s in sk if s["group"] == args.group]
    if args.json:
        if args.detail:
            return out([s for s in sk if s["name"] == args.detail] or out(sk, True), True)
        return out(sk, True)
    print(f"=== 科研技能（{len(sk)} 个）===")
    for s in sk:
        print(f"  [{s['group']}] {s['name']:<26} refs={s['reference_count']:<3} {s['description_zh'][:52]}")
    return sk


def cmd_skill(args):
    sk = load("skills.json")["skills"]
    hit = [s for s in sk if s["name"] == args.name]
    if not hit:
        print(f"未找到技能：{args.name}")
        return None
    s = hit[0]
    if args.json:
        return out(s, True)
    print(f"=== {s['name']} ===")
    print(f"路径:     {s['path']}")
    print(f"中文:     {s['description_zh']}")
    print(f"引用数:   {s['reference_count']}")
    if s["references"]:
        print("References:")
        for r in s["references"]:
            print(f"  - {r}")
    print("原始描述:")
    print("  " + clean_desc(s["description"], 400))
    return s


def cmd_handbook(args):
    hb = load("handbook.json")
    files = hb["files"]
    if args.chapter:
        files = [f for f in files if args.chapter.lower() in f["chapter"].lower()]
    if args.json:
        return out(files, True)
    print(f"=== handbook 文档（{len(files)} 份）===")
    cur = None
    for f in files:
        if f["chapter"] != cur:
            cur = f["chapter"]
            print(f"  [{cur}]")
        print(f"      {f['title']}  ({f['lines']} 行)")
    return files


def cmd_concepts(args):
    s = load("supervisor.json")
    return _emit_dict("核心概念", s["core_concepts"], args.json)


def cmd_workflow(args):
    s = load("supervisor.json")
    return _emit_dict("科研工作流阶段", s["workflow_stages"], args.json)


def cmd_safety(args):
    rules = [
        {"id": "S1", "rule": "仅离线索引", "detail": "grep/头读/索引，不调用模型、不写项目文件、不代替用户发投稿内容。"},
        {"id": "S2", "rule": "CC BY-NC-SA 4.0", "detail": "署名-非商业-相同方式共享。商业使用需单独授权；改编须同协议并注明出处。"},
        {"id": "S3", "rule": "引用必须核验", "detail": "技能强调引用经真实检索核验。离线包不提供检索能力，用户须自行在联网环境核验引用。"},
        {"id": "S4", "rule": "学术诚信", "detail": "产出是辅助建议，非代写代投。用户须对最终论文的原创性、数据真实性、署名负责。"},
        {"id": "S5", "rule": "不替代导师", "detail": "科研判断建议仅供参考，重大方向决策仍需与真实导师/同行讨论。"},
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
        {"id": "P1", "severity": "高", "pitfall": "CC BY-NC 非商业限制", "detail": "商业场景（企业内训/付费咨询/产品集成）需单独授权。"},
        {"id": "P2", "severity": "高", "pitfall": "引用幻觉风险", "detail": "paper-writer/intro-drafter/deep-research 强调引用核验，但本离线包无联网检索，引用须用户自行核实。"},
        {"id": "P3", "severity": "中", "pitfall": "技能是方法论不是模板套用", "detail": "每个 SKILL.md 有大量 when/when-not 判断，跳过直接套模板会失去门控价值。"},
        {"id": "P4", "severity": "中", "pitfall": "skills/ 与 others/ 来源不同", "detail": "others/ 是外部作者贡献由作者维护，许可与成熟度可能不同，用前看各自 LICENSE。"},
        {"id": "P5", "severity": "中", "pitfall": "英文版 SKILL.md 为主", "detail": "技能正文多为英文，中文描述是本包补的索引；实际执行须读 upstream 原文。"},
        {"id": "P6", "severity": "低", "pitfall": "Ducktor 是独立项目", "detail": "Agent 原生完全体需另装 Ducktor/DeepSeek-Ducktor，本包只含 Supervisor-Skills 本体。"},
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
    # search all mirrored markdown
    for p in sorted(UP.glob("**/*.md")):
        text = p.read_text(encoding="utf-8")
        if args.keyword.lower() in text.lower():
            for line in text.splitlines():
                if args.keyword.lower() in line.lower():
                    rel = p.relative_to(UP).as_posix()
                    hits.append({"file": rel, "line": line.strip()[:200]})
                    break  # one hit per file for readability
    if args.json:
        return out(hits[: args.limit], True)
    print(f"=== 搜索「{args.keyword}」命中 {len(hits)} 个文件，显示前 {args.limit} ===")
    for h in hits[: args.limit]:
        print(f"  [{h['file']}] {h['line'][:150]}")
    return hits


def _emit_dict(title, obj, as_json):
    if as_json:
        return out(obj, True)
    print(f"=== {title} ===")
    for k, v in obj.items():
        if isinstance(v, list):
            print(f"  {k}: {', '.join(v)}")
        else:
            print(f"  {k}: {v}")
    return obj


def main():
    ap = argparse.ArgumentParser(description="supervisor-skills 离线索引 CLI：零网络、只读、不调用模型。")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, func, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--json", action="store_true", default=False)
        p.set_defaults(func=func)
        return p

    add("stats", cmd_stats, "仓库与索引统计")
    p = add("skills", cmd_skills, "12 个科研技能清单")
    p.add_argument("--group", choices=["skills", "others"], default="", help="按来源过滤")
    p.add_argument("--detail", default="", help="显示某技能详情（JSON）")
    p = add("skill", cmd_skill, "查看单个技能详情")
    p.add_argument("name", help="技能名，如 idea-evaluator")
    p = add("handbook", cmd_handbook, "36 份 handbook 文档索引")
    p.add_argument("--chapter", default="", help="按章节过滤（如 03_Paper_Writing）")
    add("concepts", cmd_concepts, "核心概念")
    add("workflow", cmd_workflow, "科研工作流阶段与技能映射")
    add("safety", cmd_safety, "合规提示")
    add("pitfalls", cmd_pitfalls, "高频坑")
    p = sub.add_parser("find", help="跨全部镜像 markdown 全文搜索")
    p.add_argument("keyword")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--json", action="store_true", default=False)
    p.set_defaults(func=cmd_find)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        ap.print_help()
        print("\n示例：python3 scripts/supervisor.py stats | skills | skill idea-evaluator | handbook | concepts | workflow | safety | pitfalls | find evidence")
        return
    args.func(args)


if __name__ == "__main__":
    main()
