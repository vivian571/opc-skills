#!/usr/bin/env python3
"""从 upstream/ 源码重建 data/*.json 离线索引。零网络、零删除。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def dump(name, obj):
    path = DATA / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(obj) if isinstance(obj, (list, dict)) else 1


def read(rel):
    return (UP / rel).read_text(encoding="utf-8")


def build_repo():
    prev_path = DATA / "paper-orchestra.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    reqs = read("requirements.txt").strip().splitlines()
    return {
        "repo": "google-research/paper-orchestra",
        "url": "https://github.com/google-research/paper-orchestra",
        "homepage": "https://yiwen-song.github.io/paper_orchestra/",
        "name": "paper-orchestra",
        "description": "Google Research 多智能体框架：自动将研究笔记与实验日志转成投稿级 LaTeX 论文（含文献综述 + 图表生成）",
        "license": "Apache-2.0",
        "author": "Yiwen Song, Yale Song, Tomas Pfister, Jinsung Yoon @ Google Cloud AI Research",
        "language": "Python 3.11",
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 3500),
        "forks_count": prev.get("forks_count", 453),
        "created_at": prev.get("created_at", "2026-05-01T18:07:52Z"),
        "pushed_at": prev.get("pushed_at", "2026-11-15T18:08:08Z"),
        "verified_at": "2026-11-18",
        "note": "star/fork/pushed_at 为 2026-11-18 GitHub API 快照。数据集未包含在仓库中。实时值以 --refresh 为准。",
        "pipeline_stages": prev.get("pipeline_stages", []),
        "llm_providers": prev.get("llm_providers", {}),
        "latex_templates": prev.get("latex_templates", []),
        "cli_args": prev.get("cli_args", {}),
        "env_vars": prev.get("env_vars", {}),
        "autoraters": prev.get("autoraters", []),
        "frontend_demo": prev.get("frontend_demo", ""),
        "data_note": prev.get("data_note", ""),
        "python_deps": reqs,
        "deps_count": len(reqs),
    }


def build_files():
    out = []
    for p in sorted(UP.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(UP))
        text = None
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            pass
        out.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "lines": text.count("\n") + 1 if text is not None else 0,
            "kind": "text" if text is not None else "binary",
            "group": rel.split("/")[0],
        })
    return out


def build_agents(files):
    agent_roles = {
        "methods/agents/outline_agent.py": "大纲生成：idea.md + experimental_log.md → 论文结构",
        "methods/agents/literature_review_agent.py": "文献综述：Semantic Scholar 检索 + LLM 筛选 + 综述段落写作",
        "methods/agents/section_writing_agent.py": "章节撰写：按大纲逐节生成正文内容",
        "methods/agents/content_refinement_agent.py": "内容润色：整体一致性检查与格式统一",
        "methods/agents/plotting_agent.py": "图表生成：从代码自动生成配图（可选）",
    }
    prompts = {}
    prompts_dir = UP / "methods" / "prompts"
    if prompts_dir.exists():
        for p in sorted(prompts_dir.rglob("*.py")):
            prompts[str(p.relative_to(UP))] = "prompt 函数定义"
    out = []
    for f in files:
        rel = f["path"]
        if rel in agent_roles:
            out.append({"path": rel, "lines": f["lines"], "role": agent_roles[rel]})
    for rel, desc in prompts.items():
        out.append({"path": rel, "role": desc, "lines": 0})
    return {"agents": out, "count": len(out)}


def build_links():
    return {
        "repo": "https://github.com/google-research/paper-orchestra",
        "readme": "https://github.com/google-research/paper-orchestra#readme",
        "license": "https://github.com/google-research/paper-orchestra/blob/main/LICENSE",
        "homepage": "https://yiwen-song.github.io/paper_orchestra/",
        "arxiv": "https://arxiv.org/abs/2604.05018",
        "local_mirror": str(UP),
        "local_cli_example": "python upstream/paper_writing_cli.py --raw_materials_dir <dir> --latex_template_dir upstream/templates/cvpr2025",
    }


def main():
    files = build_files()
    results = {
        "paper-orchestra.json": build_repo(),
        "files.json": files,
        "agents.json": build_agents(files),
        "links.json": build_links(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<26} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()