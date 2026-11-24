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


def build_skid():
    prev_path = DATA / "skid.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    return {
        "repo": "cubewhy/skid-homework",
        "url": "https://github.com/cubewhy/skid-homework",
        "homepage": "https://skid.cubewhy.dev",
        "name": "skid-homework",
        "description": "打滑作业平台：符合人体工程学设计、AI 驱动的作业助手（Gemini / OpenAI-compatible API）",
        "version": "0.0.0",
        "license": "GPL-3.0",
        "author": "cubewhy",
        "language": "TypeScript (Next.js 15 + shadcn/ui + Tailwind)",
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 1906),
        "forks_count": prev.get("forks_count", 358),
        "created_at": prev.get("created_at", "2025-09-27T01:17:57Z"),
        "pushed_at": prev.get("pushed_at", "2026-09-14T23:24:44Z"),
        "updated_at": prev.get("updated_at", "2026-11-17T00:44:34Z"),
        "verified_at": "2026-11-17",
        "note": "star/fork/pushed_at/updated_at 为 2026-11-17 GitHub API 快照。实时值以 --refresh 为准。",
        "tech_stack": prev.get("tech_stack", {}),
        "pages": prev.get("pages", []),
        "ai_prompts": prev.get("ai_prompts", []),
        "commands": prev.get("commands", []),
        "key_shortcuts": prev.get("key_shortcuts", []),
        "dependency_count": {"deps": 68, "devDeps": 20},
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


def build_modules(files):
    module_roles = {
        "src/ai/gemini.ts": "Gemini API 客户端：@google/genai 封装，流式输出 + tool call 支持",
        "src/ai/openai.ts": "OpenAI 兼容客户端：统一请求/响应格式",
        "src/ai/prompt-manager.ts": "Prompt 管理器：从 .md 文件加载、变量替换、全局 prompt 编辑器交互",
        "src/ai/request.ts": "统一请求入口：按 provider 分发到 gemini/openai",
        "src/ai/response.ts": "统一响应解析：tool call 提取、流式分块合并",
        "src/ai/errors.ts": "AI 调用错误分类与重试策略",
        "src/ai/base-client.ts": "抽象基类：定义统一接口",
        "src/components/chat/chat-composer.tsx": "聊天输入区：文件上传/拍照/提交/快捷键",
        "src/components/chat/chat-messages.tsx": "消息列表渲染：Markdown + 代码块 + 图表",
        "src/components/chat/chat-sidebar.tsx": "侧边栏：历史记录/快捷键提示",
        "src/components/markdown/MarkdownRenderer.tsx": "Markdown 渲染入口：dompurify sanitize + 代码高亮",
        "src/components/markdown/diagram/JSXGraphDiagram.tsx": "JSXGraph 交互式几何图渲染",
        "src/components/markdown/diagram/MermaidDiagram.tsx": "Mermaid 图表渲染",
        "src/components/markdown/diagram/MathPlotDiagram.tsx": "function-plot 函数图像",
        "src/components/actions/GlobalTraitsEditor.tsx": "Ctrl+X 全局 Prompt 编辑器",
        "src/components/actions/UploadArea.tsx": "文件/拍照上传区（支持多文件/PDF/ADB）",
        "src/components/guards/RequireAiKey.tsx": "无 Key 时拦截并引导到 /init",
        "src/app/init/page.tsx": "API Key 初始化向导页面",
        "src/app/chat/page.tsx": "主聊天界面",
        "src/app/settings/page.tsx": "设置页：快捷键/主题/i18n",
        "src/app/providers.tsx": "Next.js Provider 堆栈：i18n/theme/dexie",
        "src/ai/prompts/tools/jsxgraph-tool.prompt.md": "JSXGraph 工具调用规范",
        "src/ai/prompts/tools/mermaid-tool.prompt.md": "Mermaid 工具调用规范",
        "src/ai/prompts/tools/diagram-tool.prompt.md": "通用 diagram 工具规范",
        "src/ai/prompts/solve.prompt.md": "解题流程 prompt",
        "src/ai/prompts/improve.prompt.md": "改进答案 prompt（按 / 触发）",
        "src/ai/prompts/chat.prompt.md": "对话上下文管理 prompt",
    }
    out = []
    for f in files:
        rel = f["path"]
        if not (rel.startswith("src/") and (rel.endswith(".ts") or rel.endswith(".tsx") or rel.endswith(".md"))):
            continue
        role = module_roles.get(rel, "核心模块之一")
        exports = []
        if rel.endswith(".ts") or rel.endswith(".tsx"):
            # try to extract export names
            try:
                text = read(rel)
                exports = [m.split()[1].split("(")[0] for m in text.split("export ")[1:] if m.strip()]
            except:
                pass
        out.append({
            "path": rel,
            "lines": f["lines"],
            "bytes": f["bytes"],
            "group": rel.split("/")[0],
            "role": role,
            "exports": exports[:10],
        })
    return out


def build_prompts():
    prompts = {}
    for name in ["chat.prompt.md", "solve.prompt.md", "improve.prompt.md", 
                 "tools/jsxgraph-tool.prompt.md", "tools/mermaid-tool.prompt.md", "tools/diagram-tool.prompt.md"]:
        try:
            text = read(f"src/ai/prompts/{name}")
            prompts[name] = {"chars": len(text), "lines": text.count("\n")+1, "preview": text[:200]}
        except:
            pass
    return prompts


def build_links():
    return {
        "repo": "https://github.com/cubewhy/skid-homework",
        "readme": "https://github.com/cubewhy/skid-homework#readme",
        "license": "https://github.com/cubewhy/skid-homework/blob/main/LICENSE",
        "demo": "https://skid.996every.day",
        "local_mirror": str(UP),
    }


def main():
    files = build_files()
    results = {
        "skid.json": build_skid(),
        "files.json": files,
        "modules.json": build_modules(files),
        "prompts.json": build_prompts(),
        "links.json": build_links(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()