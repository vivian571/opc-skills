#!/usr/bin/env python3
"""Build offline index JSON files for the supervisor-skills skill package."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
try:
    DATA.mkdir(exist_ok=True)
except FileExistsError:
    pass


def parse_frontmatter(path):
    """Return dict of YAML frontmatter (simple key: value / block scalars)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm_text = text[4:end]
    result = {}
    key = None
    for line in fm_text.splitlines():
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            result[key] = val if val else ""
        elif key and line.startswith(" ") and result.get(key) == "":
            result[key] += line.strip() + " "
        elif key and line.startswith(" ") and isinstance(result.get(key), str):
            result[key] += " " + line.strip()
    for k in result:
        result[k] = result[k].strip()
    return result, text[end + 4:]


# ---- 1. Skills index ----
skills = []
for skill_md in sorted(UP.glob("**/SKILL.md")):
    fm, body = parse_frontmatter(skill_md)
    rel = skill_md.relative_to(UP).as_posix()
    parts = rel.split("/")
    group = parts[0]  # skills / others
    skill_dir = skill_md.parent
    refs = sorted(p.name for p in (skill_dir / "references").glob("*.md")) if (skill_dir / "references").exists() else []
    # count lines as size proxy
    lines = len(body.splitlines())
    desc = fm.get("description", "")
    skills.append({
        "name": fm.get("name", skill_dir.name),
        "group": group,
        "path": rel,
        "description": desc,
        "description_zh": "",
        "references": refs,
        "reference_count": len(refs),
        "lines": lines,
    })

# Chinese one-liners per skill (curated)
zh = {
    "idea-evaluator": "Idea 五维评估（更高/更快/更强/更省/更广）+ 生命周期与能力匹配 + 范式转移探测 + 致命缺陷审计，给出审稿人式结论",
    "deep-research": "综述级文献深调：多视角检索 + 逐条引用核验 + MECE 分类综合 + 交叉对比，产出逐条回答研究问题的 survey",
    "vibe-research-workflow": "AI 辅助科研全流程：Vibe Coding / Vibe Figure / Vibe Writing 三件套实战",
    "tech-paper-template": "技术类 Full Paper 思考模板，一步步梳理论文完整逻辑链",
    "intro-drafter": "基于 Introduction Flowchart 思考模型，输入研究动机直出六段式 Intro 正文（引用经检索核验）",
    "paper-writer": "证据门控的论文正文写作：每个事实声明可溯源，引用经独立核查，绝不编造",
    "benchmark-paper-template": "Benchmark/Evaluation 类论文专用：梳理评估逻辑、gap 分析与实验设计",
    "paper-polish": "忠于原意的语言润色：改语法、去 AI 腔、把握措辞分寸，动含义处逐条标出待确认",
    "pre-submission-reviewer": "顶会审稿人视角全面审查草稿：写作 Checklist + 英语语法易错点",
    "figure-designer": "告诉 AI 你想表达什么，按动机图/总览图/实验图设计范式给专业作图建议",
    "drawio-reconstruction": "参考图/论文图/架构图/UI 截图一键重建为可编辑 .drawio + PNG 预览与视觉审计",
    "rebuttal-guidance": "条件说服模型：识别审稿人心态→匹配 rebuttal 策略，逐条生成回应指导",
}
for s in skills:
    s["description_zh"] = zh.get(s["name"], s["description"][:80])

(DATA / "skills.json").write_text(
    json.dumps({"count": len(skills), "skills": skills}, ensure_ascii=False, indent=2), encoding="utf-8"
)

# ---- 2. Handbook index ----
handbook = []
for hb in sorted(UP.glob("handbook/**/*.md")):
    rel = hb.relative_to(UP).as_posix()
    chapter = rel.split("/")[1] if "/" in rel else ""
    title = hb.stem
    lines = len(hb.read_text(encoding="utf-8").splitlines())
    handbook.append({"path": rel, "chapter": chapter, "title": title, "lines": lines})

for hb in sorted(UP.glob("handbook-en/**/*.md")):
    rel = hb.relative_to(UP).as_posix()
    chapter = rel.split("/")[1] if "/" in rel else ""
    handbook.append({"path": rel, "chapter": chapter, "title": hb.stem, "lines": len(hb.read_text(encoding="utf-8").splitlines())})

(DATA / "handbook.json").write_text(
    json.dumps({"count": len(handbook), "chapters": sorted(set(h["chapter"] for h in handbook)), "files": handbook}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# ---- 3. Repo metadata ----
meta = {
    "repo": "HKUSTDial/Supervisor-Skills",
    "name": "supervisor-skills",
    "description": "将博导十年科研经验炼化为可直接调用的 AI 技能。从 Idea 构思到论文投稿，AI 科研副导师。",
    "url": "https://github.com/HKUSTDial/Supervisor-Skills",
    "author": "骆昱宇（香港科技大学广州 助理教授）",
    "license": "CC BY-NC-SA 4.0（署名-非商业-相同方式共享）",
    "version": "2.1.0",
    "language": "Python / Markdown",
    "stargazers_count": 13160,
    "forks_count": 785,
    "created_at": "2026-04-19",
    "pushed_at": "2026-11-21",
    "default_branch": "main",
    "topics": ["ai-research", "phd-research", "research-skills", "vibe-research", "awesome"],
    "mirrored_md": len(list(UP.glob("**/*.md"))),
    "skill_count": len(skills),
    "handbook_count": len(handbook),
    "core_concepts": {
        "最后一公里问题": "科研不只是方法论缺失，更是经验、品味与判断力的综合考验",
        "Guide + Skills 双轨制": "handbook 讲道（系统理论），skills 讲器（可执行 AI 技能）",
        "五维框架": "Higher / Faster / Stronger / Cheaper / Broader — Idea 评估与构思的核心坐标系",
        "审稿人视角": "Novel Problem / Novel Method / Nice Story / Nice Presentation 四维论文质量评价",
        "证据门控": "paper-writer 的每个事实声明可溯源到材料或核验文献，绝不编造引用",
        "学科范式路由": "评估/评审技能按学科范式切换框架，不用一把尺子量所有领域",
        "条件说服模型": "rebuttal-guidance：识别审稿人心态 X → 匹配策略 Y → 生成回应",
        "Ducktor": "Agent 原生完全体，把科研判断讲给用户听，而非只点确认",
    },
    "workflow_stages": {
        "构思与调研": ["idea-evaluator", "deep-research", "vibe-research-workflow"],
        "写作": ["tech-paper-template", "intro-drafter", "paper-writer", "benchmark-paper-template"],
        "自查与润色": ["paper-polish", "pre-submission-reviewer"],
        "可视化": ["figure-designer", "drawio-reconstruction (others)"],
        "投稿后": ["rebuttal-guidance (others)"],
    },
    "related_projects": {
        "Ducktor": "Claude Code/Codex 原生插件，/duck on 全程陪伴",
        "DeepSeek-Ducktor": "DeepSeek Harness 原生插件",
        "DataMagic": "动态图表与数据故事",
        "DeepEye": "数据分析智能体，生成报告/仪表盘/数据视频",
    },
    "install_prompt": "Help me install Supervisor-Skills from https://github.com/HKUSTDial/Supervisor-Skills with Skills.",
}
(DATA / "supervisor.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"skills.json: {len(skills)} skills")
print(f"handbook.json: {len(handbook)} docs across {len(set(h['chapter'] for h in handbook))} chapters")
print(f"supervisor.json: {len(meta['core_concepts'])} concepts")
