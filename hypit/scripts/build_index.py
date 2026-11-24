#!/usr/bin/env python3
"""从 upstream/ 镜像与源码事实重建 data/*.json 中的自动索引部分。

手写的 safety.json / pitfalls.json / diffs.json / verification.json / links.json 不被覆盖。
自动部分：hypit.json(元数据骨架) / files.json / references.json / playbooks.json /
formats.json / packages.json / docs.json / svml.json / examples_index.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
try:
    DATA.mkdir(exist_ok=True)
except (FileExistsError, OSError):
    pass


def dump(name, obj):
    (DATA / name).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  wrote {name}: {len(obj) if hasattr(obj, '__len__') else '-'}")


def rel(p):
    return p.relative_to(UP).as_posix()


def build_files():
    files = []
    for p in sorted(UP.rglob("*")):
        if p.is_file():
            files.append({"path": rel(p), "bytes": p.stat().st_size})
    dump("files.json", files)


def build_references():
    ref_root = UP / "skills/hypit/references"
    groups = {}
    for p in sorted(ref_root.rglob("*")):
        if not p.is_file():
            continue
        group = rel(p).split("/")[3] if len(rel(p).split("/")) > 3 else "other"
        groups.setdefault(group, []).append(rel(p))
    dump("references.json", {
        "total": sum(len(v) for v in groups.values()),
        "groups": groups,
    })


def build_playbooks():
    pb = UP / "skills/hypit/references/playbooks"
    craft = sorted(rel(p) for p in (pb / "craft").rglob("*.md"))
    formats = sorted(rel(p) for p in (pb / "formats").rglob("*.md"))
    dump("playbooks.json", {"craft": craft, "formats": formats,
                            "count": len(craft) + len(formats)})


def build_packages():
    pkgs = []
    for d in sorted((UP / "packages").iterdir()):
        if not d.is_dir():
            continue
        pj = d / "package.json"
        ver, desc = "", ""
        if pj.exists():
            try:
                j = json.loads(pj.read_text(encoding="utf-8"))
                ver = j.get("version", "")
                desc = j.get("description", "")
            except Exception:
                pass
        src = d / "src"
        n_ts = len(list(src.rglob("*.ts"))) if src.exists() else 0
        pkgs.append({"name": d.name, "version": ver,
                     "description": desc, "src_ts_files": n_ts})
    dump("packages.json", {"count": len(pkgs), "packages": pkgs})


def build_docs():
    docs = []
    for p in sorted((UP / "docs").rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        title = ""
        m = re.search(r'^title:\s*(.+)$', text, re.M)
        if m:
            title = m.group(1).strip().strip('"\'')
        docs.append({"path": rel(p), "title": title, "bytes": len(text.encode("utf-8"))})
    dump("docs.json", docs)


def build_svml():
    exts = {}
    for e in ("svml", "svs", "svrun"):
        exts[e] = sorted(rel(p) for p in UP.rglob(f"*.{e}"))
    dump("svml.json", {
        "extensions": {
            "svml": "Script + media + components + composition（作品主源文件）",
            "svs": "可复用 Recipe / Voice Design / direction 定义",
            "svrun": "为一次执行选择 Author Source、已有 Outputs 与目标",
        },
        "files": exts,
        "counts": {k: len(v) for k, v in exts.items()},
    })


def build_examples():
    out = []
    ex_root = UP / "examples"
    for d in sorted(ex_root.iterdir()):
        if not d.is_dir():
            continue
        readme = d / "README.md"
        head = ""
        if readme.exists():
            head = readme.read_text(encoding="utf-8")[:1200]
        out.append({"name": d.name, "has_readme": readme.exists(),
                    "files": len([p for p in d.rglob("*") if p.is_file()]),
                    "readme_head": head})
    dump("examples_index.json", out)


def build_hypit():
    pj = json.loads((UP / "package.json").read_text(encoding="utf-8"))
    commands = [
        "version", "cli", "check", "plan", "pricing", "build", "builds",
        "history", "inspect", "get", "logs", "status", "activity", "cancel",
        "result", "auth", "doctor", "studio", "run", "login", "logout",
    ]
    obj = {
        "repo": "hypit-ai/hypit",
        "description": "Clone any viral video with AI agents. Not just a script, the whole workflow: swap the face, the words, the B-roll, ship 100 variants in one command.",
        "license": "Hypit Open Source License（修改版 Apache-2.0 + 附加条件）",
        "version": pj.get("version"),
        "node": ">=22.15.0",
        "pnpm": "10.33.0",
        "typescript": "5.9.3",
        "stargazers_count": 30780,
        "forks_count": 3633,
        "created_at": "2026-07-29",
        "pushed_at": "2026-11-19",
        "language": "TypeScript",
        "install": "npx skills add hypit-ai/hypit -g",
        "bin": "hypit (bin/hypit.mjs)",
        "cli_commands": commands,
        "credential_env": [
            "各模型/服务 Provider 自带凭证（验证服务时按 Provider 文档配置，本包不记录、不生成、不存储任何密钥）",
            "HYPIT_* 多为测试/探针开关，非运行时必需（见源码 process.env.HYPIT_*）",
        ],
        "core_concepts": [
            "SVML：语义化视频编排语言，时间锚定到词（words）而非秒",
            "A-roll：承载一段表演的主画面；B-roll：辅助画面；Caption：词级字幕",
            "Component：共享布局与运动的组件；Script：以意义为主的时间组织",
            "Timeline + Canvas：唯一有限时间线与画布；Extent/Window：媒体局部域与绝对窗口",
            "Run / Build / Result / Output：一次执行、执行实例、产出结果、可复用素材",
            "Studio：可视化预览与编辑；Profile：能力路由配置",
            "Provider / Kit：模型服务连接器与模型特定提示词套件",
        ],
    }
    dump("hypit.json", obj)


if __name__ == "__main__":
    print("重建自动索引：")
    build_hypit()
    build_files()
    build_references()
    build_playbooks()
    build_packages()
    build_docs()
    build_svml()
    build_examples()
    print("完成。")
