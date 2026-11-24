#!/usr/bin/env python3
"""build_index.py — 从 upstream/ 重建 cli-anything 技能包的 data/ 索引。
解析 registry.json / public_registry.json + skills/ 目录，产出结构化 JSON。
零第三方依赖。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
try:
    DATA.mkdir(exist_ok=True)
except FileExistsError:
    pass


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def build_registry():
    reg = load_json(UP / "registry.json")
    clis = reg.get("clis", [])
    meta = reg.get("meta", {})
    # 归类
    by_cat = {}
    for c in clis:
        by_cat.setdefault(c.get("category", "other"), []).append(c["name"])
    return {
        "meta": meta,
        "count": len(clis),
        "categories": {k: sorted(v) for k, v in sorted(by_cat.items())},
        "clis": [
            {
                "name": c.get("name"),
                "display_name": c.get("display_name"),
                "version": c.get("version"),
                "description": c.get("description"),
                "requires": c.get("requires"),
                "category": c.get("category"),
                "install_cmd": c.get("install_cmd"),
                "entry_point": c.get("entry_point"),
                "skill_md": c.get("skill_md"),
                "homepage": c.get("homepage"),
            }
            for c in clis
        ],
    }


def build_public_registry():
    p = UP / "public_registry.json"
    if not p.exists():
        return {"count": 0, "clis": []}
    reg = load_json(p)
    clis = reg.get("clis", [])
    return {
        "count": len(clis),
        "clis": [
            {
                "name": c.get("name"),
                "display_name": c.get("display_name"),
                "description": c.get("description"),
                "install_cmd": c.get("install_cmd"),
                "category": c.get("category"),
            }
            for c in clis
        ],
    }


def build_skills():
    skills_root = UP / "skills"
    skills = []
    if skills_root.exists():
        for d in sorted(skills_root.iterdir()):
            if not d.is_dir():
                continue
            sk = d / "SKILL.md"
            desc = ""
            if sk.exists():
                text = sk.read_text(encoding="utf-8", errors="replace")
                # 抓 frontmatter description 或首个段落
                if text.startswith("---"):
                    parts = text.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].splitlines():
                            if line.strip().startswith("description:"):
                                desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                                break
                if not desc:
                    for line in text.splitlines():
                        s = line.strip()
                        if s and not s.startswith("#") and not s.startswith("---"):
                            desc = s[:160]
                            break
            skills.append({"name": d.name, "description": desc})
    return {"count": len(skills), "skills": skills}


def build_harness_index():
    """扫各软件目录下的 agent-harness，记录命令规模（有 pyproject/cli 的）"""
    harnesses = []
    for d in sorted(UP.iterdir()):
        if not d.is_dir():
            continue
        ah = d / "agent-harness"
        if not ah.exists():
            continue
        # 统计 python 文件数与是否有 CLI 入口
        py_files = list(ah.rglob("*.py"))
        has_setup = (ah / "pyproject.toml").exists() or (ah / "setup.py").exists()
        harnesses.append({
            "software": d.name,
            "harness_path": f"{d.name}/agent-harness",
            "py_files": len(py_files),
            "packaged": has_setup,
        })
    return {"count": len(harnesses), "harnesses": harnesses}


def main():
    reg = build_registry()
    pub = build_public_registry()
    skills = build_skills()
    harnesses = build_harness_index()

    (DATA / "registry.json").write_text(
        json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "public_registry.json").write_text(
        json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "skills.json").write_text(
        json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "harnesses.json").write_text(
        json.dumps(harnesses, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"registry: {reg['count']} CLIs, {len(reg['categories'])} categories")
    print(f"public_registry: {pub['count']} public CLIs")
    print(f"skills: {skills['count']} SKILL.md")
    print(f"harnesses: {harnesses['count']} agent-harness dirs")


if __name__ == "__main__":
    main()
