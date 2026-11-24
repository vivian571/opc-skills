#!/usr/bin/env python3
"""从 upstream/ 源码与 data/*.json 重建离线索引。零网络、零删除。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def dump(name, obj):
    path = DATA / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(obj) if isinstance(obj, list) else 1


def read(rel):
    return (UP / rel).read_text(encoding="utf-8")


def build_skills():
    skill_map = {
        "interview-me": ("定义", "通过一次一个问题提取用户真正想要的东西，而非他们嘴上说的要求"),
        "idea-refine": ("定义", "把模糊的想法结构化发散后再收敛，输出可执行的概念"),
        "spec-driven-development": ("定义", "写 PRD/spec 之前先明确范围和验收标准"),
        "planning-and-task-breakdown": ("规划", "把一个复杂任务拆解成有序、原子、可并行的子任务清单"),
        "incremental-implementation": ("构建", "每次只改一个文件/一个小功能，做完一个测一个再推进"),
        "test-driven-development": ("构建", "先写失败测试，再写最小实现，最后回归全套测试"),
        "context-engineering": ("构建", "启动会话前整理上下文预算：决定给 agent 看什么、什么时候看"),
        "source-driven-development": ("构建", "每个框架相关决策都要对照官方文档，不靠记忆手写"),
        "doubt-driven-development": ("构建", "对非平凡决策做对抗式评审——假设要推翻它"),
        "frontend-ui-engineering": ("构建", "生产级 UI：响应式、无障碍、符合设计系统，拒绝 AI 审美"),
        "api-and-interface-design": ("构建", "对外暴露的接口（API、模块边界、组件 props）要有稳定的契约"),
        "browser-testing-with-devtools": ("验证", "通过 Chrome DevTools MCP 在真实浏览器里检查 DOM/网络/性能/控制台错误"),
        "debugging-and-error-recovery": ("验证", "系统性根因分析：先复现、隔离变量、找最小复现路径，最后修 bug"),
        "code-review-and-quality": ("评审", "五个维度的代码审查：正确性、可读性、架构、安全、性能"),
        "code-simplification": ("评审", "在不改变行为的前提下降低复杂度，优先改善可读性与可维护性"),
        "security-and-hardening": ("评审", "OWASP Top Ten 防护：输入处理、认证、数据加密、第三方集成加固"),
        "performance-optimization": ("评审", "先测量再优化：识别实际瓶颈，避免过早优化引入复杂度"),
        "git-workflow-and-versioning": ("发布", "原子化提交、语义化版本、PR 描述规范、changelog 生成"),
        "ci-cd-and-automation": ("发布", "质量门禁自动化：lint/type-check/test/build 全流程 CI"),
        "deprecation-and-migration": ("发布", "新旧系统共存过渡：expand-contract 模式避免停机"),
        "documentation-and-adrs": ("发布", "记录架构决策 ADR；检测文档与代码漂移"),
        "observability-and-instrumentation": ("发布", "让线上行为可观测：日志、指标、追踪、告警"),
        "shipping-and-launch": ("发布", "上线前的 checklist：监控、灰度、回滚策略"),
        "using-agent-skills": ("元技能", "发现并调度哪个 skill 适用当前任务"),
    }
    out = []
    for p in sorted(UP.rglob("SKILL.md")):
        if not p.name == "SKILL.md":
            continue
        name = str(p.relative_to(UP)).replace("SKILL.md", "").replace("/", "-").lower()
        # normalize
        name = name.strip("-")
        parts = name.split("-")
        # The SKILL.md frontmatter contains `name:` field
        text = p.read_text(encoding="utf-8")
        header = next((l for l in text.splitlines() if l.startswith("---")), "")
        if not header:
            continue
        lines = text.splitlines()[1:]  # skip ---
        fname = None
        desc = ""
        for line in lines:
            if line.startswith("name:"):
                fname = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip('"')
                break
        group, overview = skill_map.get(fname, ("未知", desc[:60]))
        out.append({
            "name": fname or name,
            "group": group,
            "overview": overview,
            "path": f"skills/{fname}/SKILL.md" if fname else f"skills/{name}/SKILL.md",
        })
    return {"skills": out, "count": len(out)}


def build_evals():
    cases_dir = UP / "evals" / "cases"
    out = []
    if cases_dir.exists():
        for f in sorted(cases_dir.glob("*.json")):
            try:
                c = json.loads(f.read_text(encoding="utf-8"))
                trigger = c.get("trigger", {})
                pos = trigger.get("positive", [])
                neg = trigger.get("negative", [])
                out.append({
                    "skill": c.get("skill_name"),
                    "positive_count": len(pos),
                    "negative_count": len(neg),
                    "case_count": len(c.get("evals", [])),
                })
            except Exception:
                pass
    return {"cases": out, "count": len(out)}


def build_commands():
    cmds = {}
    src = UP / "commands"
    if src.exists():
        for f in sorted(src.glob("*.toml")):
            name = f.stem
            text = f.read_text(encoding="utf-8")
            prompt = ""
            for line in text.splitlines():
                if "prompt" in line.lower() and "=" in line:
                    prompt = line.split("=", 1)[1].strip().strip('"').replace("\\n", " ").strip()
                    break
            cmds[name] = prompt[:100]
    claude_cmds = {}
    claude_src = UP / ".claude" / "commands"
    if claude_src.exists():
        for f in sorted(claude_src.rglob("*.md")):
            name = f.stem
            text = f.read_text(encoding="utf-8")
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")][:5]
            claude_cmds[name] = " | ".join(lines)[:100]
    return {"toml": cmds, "claude_md": claude_cmds}


def build_links():
    return {
        "repo": "https://github.com/addyosmani/agent-skills",
        "readme": "https://github.com/addyosmani/agent-skills#readme",
        "homepage": "https://skills.addy.ie",
        "contributing": "https://github.com/addyosmani/agent-skills/blob/main/CONTRIBUTING.md",
        "local_mirror": str(UP),
    }


def build_files():
    files = []
    for p in sorted(UP.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(UP))
        text = None
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            pass
        files.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "lines": text.count("\n") + 1 if text is not None else 0,
            "kind": "text" if text is not None else "binary",
            "group": rel.split("/")[0],
        })
    return files


def main():
    results = {
        "skills.json": build_skills(),
        "evals.json": build_evals(),
        "commands.json": build_commands(),
        "links.json": build_links(),
        "files.json": build_files(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()
