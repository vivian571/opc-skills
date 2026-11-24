#!/usr/bin/env python3
"""从 upstream/ 源码与 data/test-run.json 重建 data/*.json 离线索引。

零网络、零删除：只覆盖写入自己生成的 JSON，不改动手写数据文件
（safety.json / pitfalls.json / diffs.json / verification.json / test-run.json）。
"""

import json
import re
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


MODULE_ROLES = {
    "src/index.js": "包入口，导出核心模块",
    "src/cli.js": "命令行入口：--config/--submit/--status/--file/--url/--help 与退出码",
    "src/core/config.js": "读取并校验 JSON 配置，禁止注释与尾随逗号",
    "src/core/errors.js": "AutomationError / requireValue 参数断言",
    "src/core/http.js": "fetch 封装、重试与限速处理",
    "src/core/logger.js": "按 verificationId 隔离的异步日志",
    "src/core/network.js": "代理 dispatcher 与直连切换",
    "src/core/proxy.js": "HTTP/SOCKS5 代理解析、proxy-chain 本地转发",
    "src/core/runner.js": "任务锁、浏览器生命周期与提交流程编排",
    "src/core/status-query.js": "状态查询入口",
    "src/core/storage.js": "运行产物与结果持久化",
    "src/core/workflow.js": "按 currentStep 分流：只读查询 / 浏览器 / 材料",
    "src/apps/registry.js": "应用适配器注册表",
    "src/apps/sheerid/index.js": "SheerID 应用主流程与步骤状态机",
    "src/apps/sheerid/client.js": "rest/v2 verification 接口封装",
    "src/apps/sheerid/status.js": "状态查询与响应解析",
    "src/apps/sheerid/page-state.js": "页面当前步骤识别",
    "src/apps/sheerid/selectors.js": "页面选择器常量",
    "src/apps/sheerid/labels.js": "界面文案与错误标签映射",
    "src/apps/sheerid/organization.js": "学校检索与精确匹配",
    "src/apps/sheerid/document.js": "材料原始字节读取与上传",
    "src/apps/sheerid/document-workflow.js": "docUpload 轮询、复审、丢失响应补偿",
    "src/apps/sheerid/human-verification.js": "交互式真人验证提示（由用户本人完成）",
    "src/browser/session.js": "Camoufox 会话启动与关闭",
    "src/browser/form.js": "表单填写、学校搜索与提交动作",
    "src/browser/interaction.js": "打字/点击的拟人延时",
    "src/web/server.js": "本机 Web 工作台 HTTP 服务、鉴权与 CSP",
    "src/web/jobs.js": "任务队列、并发上限、停止/恢复/删除",
    "src/web/public/app.js": "前端页面逻辑与 SSE 式轮询",
    "scripts/process.js": "ESM 主模块判定与致命错误输出",
    "scripts/install-browser.js": "Camoufox 下载（Windows 解压补丁）",
}


def build_repo():
    pkg = json.loads(read("package.json"))
    prev_path = DATA / "repo.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    return {
        "repo": "JenkinWoo/sheeridVerify",
        "url": "https://github.com/JenkinWoo/sheeridVerify",
        "name": pkg["name"],
        "version": pkg["version"],
        "license": pkg["license"],
        "type": pkg["type"],
        "engines": pkg["engines"],
        "dependencies": pkg["dependencies"],
        "language": "JavaScript (ESM)",
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 3199),
        "forks_count": prev.get("forks_count", 1516),
        "created_at": prev.get("created_at", "2026-11-06T09:28:09Z"),
        "pushed_at": prev.get("pushed_at", "2026-11-06T09:54:37Z"),
        "verified_at": "2026-11-15",
        "note": "star/fork/日期为 2026-11-15 通过 GitHub API 核实的快照，实时值以 --refresh 为准",
    }


def build_files():
    out = []
    for p in sorted(UP.rglob("*")):
        if not p.is_file() or p.name == "MIRROR-SCOPE.md":
            continue
        rel = p.relative_to(UP).as_posix()
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
    out = []
    for f in files:
        rel = f["path"]
        if not (rel.startswith("src/") or rel.startswith("scripts/")) or not rel.endswith(".js"):
            continue
        if rel.startswith("src/web/public/"):
            group = "Web 前端"
        elif rel.startswith("src/web/"):
            group = "Web 工作台"
        elif rel.startswith("src/apps/"):
            group = "SheerID 适配"
        elif rel.startswith("src/browser/"):
            group = "浏览器交互"
        elif rel.startswith("src/core/"):
            group = "核心框架"
        elif rel.startswith("scripts/"):
            group = "辅助脚本"
        else:
            group = "入口"
        out.append({
            "path": rel,
            "lines": f["lines"],
            "bytes": f["bytes"],
            "group": group,
            "role": MODULE_ROLES.get(rel, "见上游源码"),
            "exports": re.findall(r"^export (?:async )?(?:function|const|class)\s+(\w+)",
                                  read(rel), re.M),
        })
    return out


def build_commands():
    pkg = json.loads(read("package.json"))
    notes = {
        "test": "node --experimental-test-module-mocks --test；本地 mock，不访问真实验证接口",
        "start": "按状态分流的命令行入口（默认只填表、不提交）",
        "web": "启动本机 Web 工作台，默认 http://127.0.0.1:8787",
        "status": "只读查询状态，不开浏览器、不改远端状态",
        "submit": "按当前步骤提交（浏览器或材料接口）",
        "browser:install": "下载 Camoufox；未安装时 8 个浏览器用例会跳过",
    }
    scripts = [{"name": k, "command": v, "note": notes.get(k, "")} for k, v in pkg["scripts"].items()]
    cli_flags = [
        {"flag": "--config <path>", "note": "指定 JSON 配置，默认 config/sheerid.local.json"},
        {"flag": "--submit", "note": "按当前步骤提交；会改变远端状态，仅限授权测试"},
        {"flag": "--status", "note": "只读查询，不开浏览器、不上传"},
        {"flag": "--file <path>", "note": "本地 PNG/JPEG/PDF，覆盖配置的材料来源"},
        {"flag": "--url <url>", "note": "HTTP/HTTPS 材料地址，覆盖配置的材料来源"},
        {"flag": "--help", "note": "输出 CLI 帮助"},
    ]
    exit_codes = [
        {"code": 0, "meaning": "filled / verified / manual"},
        {"code": 1, "meaning": "failed / rejected"},
        {"code": 2, "meaning": "需要后续动作（document_required / pending 等）"},
        {"code": 3, "meaning": "submission_unknown，提交结果不确定"},
        {"code": 130, "meaning": "被 SIGINT/SIGTERM 中断"},
    ]
    env_vars = [
        {"name": "ONE_WEB_PASSWORD", "note": "Web 访问密码；公网部署必须改掉默认值 JenkinWoo"},
        {"name": "ONE_WEB_HOST", "note": "监听地址，默认 127.0.0.1；0.0.0.0 需同时配 HTTPS 公网地址"},
        {"name": "ONE_WEB_PUBLIC_ORIGIN", "note": "公网 HTTPS 源站地址，用于来源校验"},
        {"name": "AUTOMATION_URL", "note": "覆盖 CLI 配置里的验证链接（不覆盖网页输入）"},
        {"name": "AUTOMATION_PROXY", "note": "覆盖 CLI 代理（HTTP/HTTPS/SOCKS5 或 direct）"},
    ]
    headers = [
        {"name": "X-Web-Password", "note": "访问密码，换取会话"},
        {"name": "Cookie: one-session", "note": "HttpOnly + SameSite=Strict 会话"},
        {"name": "X-Local-Token", "note": "所有非 GET 写请求必须携带，防 CSRF"},
    ]
    return {"scripts": scripts, "cli_flags": cli_flags, "exit_codes": exit_codes,
            "env_vars": env_vars, "write_headers": headers,
            "cli_usage": "npm start -- [--config <path>] [--submit | --status] [--file <path> | --url <url>]"}


ENDPOINTS = [
    {"method": "GET", "path": "/", "note": "工作台首页 index.html", "auth": "密码或会话"},
    {"method": "GET", "path": "/app.js | /style.css", "note": "静态资源", "auth": "密码或会话"},
    {"method": "GET", "path": "/api/session", "note": "校验密码、下发 one-session Cookie 与 X-Local-Token", "auth": "X-Web-Password"},
    {"method": "GET", "path": "/api/jobs", "note": "列出全部任务", "auth": "密码或会话"},
    {"method": "POST", "path": "/api/jobs", "note": "创建任务（202）；仅接受 application/json，body ≤ 64 KB", "auth": "密码或会话 + X-Local-Token"},
    {"method": "GET", "path": "/api/jobs/:id?after=N", "note": "增量读取任务日志", "auth": "密码或会话"},
    {"method": "POST", "path": "/api/jobs/:id/cancel", "note": "停止任务", "auth": "密码或会话 + X-Local-Token"},
    {"method": "POST", "path": "/api/jobs/:id/resume", "note": "把已停止任务重新排到队尾", "auth": "密码或会话 + X-Local-Token"},
    {"method": "DELETE", "path": "/api/jobs/:id", "note": "删除已结束任务；运行中的任务返回 409", "auth": "密码或会话 + X-Local-Token"},
]


CONFIG_NOTES = {
    "web.concurrency": "并发上限，正整数，默认 1；启动时与入队时读取",
    "app": "应用适配器名，当前仅有 sheerid",
    "proxy": "代理；Web 模式留空强制直连，不使用环境代理",
    "browser.headless": "是否无头；示例为 false，本机需可用桌面",
    "browser.locale": "浏览器语言，示例 en-US",
    "browser.keepOpen": "提交后是否保留浏览器，示例 true",
    "browser.autoFill": "自动填表；false 时改为手动填写",
    "document.path": "本地材料路径；与 document.url 二选一，不可同时填",
    "document.url": "材料下载地址；与 document.path 二选一",
    "timeouts.apiMs": "接口超时，默认 20000 ms",
    "timeouts.actionMs": "页面动作超时，默认 15000 ms",
    "timeouts.navigationMs": "导航超时，默认 60000 ms",
    "timeouts.readyMs": "页面就绪超时，默认 120000 ms",
    "timeouts.humanMs": "真人验证等待，默认 180000 ms",
    "timeouts.resultMs": "结果等待，默认 45000 ms",
    "interaction.keyDelayMs": "按键延时区间 40–120 ms",
    "interaction.fieldDelayMs": "字段间延时区间 500–1200 ms",
    "interaction.submitDelayMs": "提交前延时区间 1000–2000 ms",
    "artifactsDir": "运行产物目录，默认 .runs，必须保持私有",
    "data.country": "国家；示例为空，需自行填授权范围内的值",
    "data.organization.name": "学校名称",
    "data.organization.optionText": "下拉选项文本",
    "data.organization.emailDomain": "邮箱后缀，示例 example.edu",
    "selectors": "自定义页面选择器覆盖，默认空对象",
}


def flatten(obj, prefix=""):
    out = []
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.extend(flatten(v, key))
        else:
            out.append((key, v))
    return out


def build_config():
    raw = json.loads(read("config/sheerid.example.json"))
    fields = [{"key": k, "example": v, "note": CONFIG_NOTES.get(k, "")}
              for k, v in flatten(raw)]
    return {"source": "config/sheerid.example.json",
            "target": "config/sheerid.local.json",
            "rule": "必须是标准 JSON，不支持 // 注释与尾随逗号；document.path 与 document.url 只能填一个",
            "fields": fields}


def build_tests():
    run = json.loads((DATA / "test-run.json").read_text(encoding="utf-8"))
    cases = run["cases"]
    by_file = {}
    for f in sorted((UP / "tests").glob("*.test.js")):
        text = f.read_text(encoding="utf-8")
        by_file[f.name] = [c["name"] for c in cases if c["name"][:24] in text or c["name"] in text]
    return {
        "command": run["command"],
        "test_files": [p.name for p in sorted((UP / "tests").glob("*.test.js"))],
        "fixture": "tests/fixtures/web-config.js",
        "mock": "node:test 的 t.mock.method(globalThis, 'fetch') 全量替换网络请求；URL 均为 aaaa…/example.com 占位符",
        "runs": run["runs"],
        "summary": run["runs"][-1],
        "case_count": len(cases),
        "cases": cases,
        "by_file": by_file,
    }


def build_links():
    return {
        "repo": "https://github.com/JenkinWoo/sheeridVerify",
        "readme": "https://github.com/JenkinWoo/sheeridVerify#readme",
        "disclaimer": "https://github.com/JenkinWoo/sheeridVerify/blob/main/DISCLAIMER.md",
        "security": "https://github.com/JenkinWoo/sheeridVerify/blob/main/SECURITY.md",
        "contributing": "https://github.com/JenkinWoo/sheeridVerify/blob/main/CONTRIBUTING.md",
        "ci": "https://github.com/JenkinWoo/sheeridVerify/actions/workflows/ci.yml",
        "issues": "https://github.com/JenkinWoo/sheeridVerify/issues",
        "local_mirror": str(UP),
        "local_checkout": "{{WORKSPACE}}/_work/sheeridVerify",
    }


def main():
    files = build_files()
    results = {
        "repo.json": build_repo(),
        "files.json": files,
        "modules.json": build_modules(files),
        "commands.json": build_commands(),
        "endpoints.json": ENDPOINTS,
        "config.json": build_config(),
        "tests.json": build_tests(),
        "links.json": build_links(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()
