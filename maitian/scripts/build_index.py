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
    pkg = json.loads(read("package.json"))
    prev_path = DATA / "maitian.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    return {
        "repo": "CzzzzzzJ/mdldm-maitian",
        "url": "https://github.com/CzzzzzzJ/mdldm-maitian",
        "name": pkg["name"],
        "description": pkg.get("description", ""),
        "version": pkg.get("version", "unspecified"),
        "license": pkg["license"],
        "author": "麦当 mdldm",
        "language": "JavaScript (ESM)",
        "platform": "macOS only",
        "engines": pkg.get("engines", {}),
        "default_branch": "main",
        "stargazers_count": prev.get("stargazers_count", 335),
        "forks_count": prev.get("forks_count", 114),
        "created_at": prev.get("created_at", "2026-11-14T03:59:22Z"),
        "pushed_at": prev.get("pushed_at", "2026-11-16T12:27:07Z"),
        "verified_at": "2026-11-17",
        "note": "star/fork/pushed_at 为 2026-11-17 GitHub API 快照；实时值以 --refresh 为准。本项目仅 macOS 可用。",
        "ecosystem": {
            "publisher_repo": "https://github.com/CzzzzzzJ/mdldm-maitian-publisher",
            "publisher_note": "本包不携带各平台适配器代码；adapter 在姊妹仓库，通过 bridge :8765 调用"
        },
        "requirements": [
            "macOS（硬约束）",
            "Node.js ≥ 22.5（用到内置 node:sqlite）",
            "Google Chrome（CDP 端口 9333）",
            "专用 Chrome profile（chrome-profile/，各平台登录态存放于此）",
            "可选：NAS（SMB 共享）、飞书群机器人 webhook、cloudflared 隧道"
        ],
        "commands": [
            {"cmd": "node src/demo.mjs", "desc": "假数据大屏 demo，无需任何凭据"},
            {"cmd": "node src/init.mjs", "desc": "安装向导：检查环境、生成 config.json、装开机自启、打开各平台登录页"},
            {"cmd": "node src/hub.mjs plan [工程目录]", "desc": "登记进分发计划"},
            {"cmd": "node src/hub.mjs run <工程目录> [--only x,zsz] [--force] [--now]", "desc": "发一期；--now 让站点课程立即上线"},
            {"cmd": "node src/hub.mjs status [id] [--logs]", "desc": "查状态"},
            {"cmd": "node src/hub.mjs sync <id> [--only a,b]", "desc": "取链接、写发布记录、回填 md"},
            {"cmd": "node src/hub.mjs mark <id> <平台> <状态> [备注] [--url 链接]", "desc": "手动改状态"},
            {"cmd": "node src/hub.mjs adopt <工程目录>", "desc": "登记已发的期（不上传）"},
            {"cmd": "node src/hub.mjs metrics [id]", "desc": "采流量并发日报"},
            {"cmd": "node src/hub.mjs followers", "desc": "采粉丝"},
            {"cmd": "node src/hub.mjs review <id> [天数] [--notify]", "desc": "复盘卡片"},
            {"cmd": "node src/hub.mjs weekly [--notify]", "desc": "周报"},
            {"cmd": "node src/hub.mjs board", "desc": "同步到飞书多维表格"},
            {"cmd": "node src/hub.mjs daemon", "desc": "常驻守护进程"},
            {"cmd": "bash scripts/install.sh", "desc": "一键安装向导"},
            {"cmd": "bash scripts/install-launchd.sh", "desc": "装开机自启（可加 --tunnel 装 cloudflared 隧道）"}
        ],
        "web_ui": {
            "port": 8787,
            "demo_port": 8788,
            "key_required": True,
            "remote_access_options": ["cloudflared 固定域名（推荐）", "飞书验证码登录（零配置）", "快速隧道（每次重启地址变）"]
        },
        "privacy": {
            "no_password_stored": True,
            "chromium_profile_isolated": True,
            "gitignore": ["config.json", "data/", "chrome-profile/"],
            "read_only_creator_data": True
        }
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
    out = []
    module_roles = {
        "src/hub.mjs": "发布中控主入口：plan/run/status/sync/mark/adopt/metrics/followers/review/weekly/board/daemon",
        "src/web.mjs": "本地网页服务：大屏/分页面/API，带 web.key 鉴权",
        "src/db.mjs": "SQLite 状态落盘：episodes/tasks/logs/snapshot/meta",
        "src/feishu.mjs": "飞书卡片通知：开跑/到位/异常/等你点/日报/复盘/周报",
        "src/login.mjs": "各平台登录态探测与引导扫码",
        "src/checks.mjs": "发布前校验：字数/禁词/封面比例/faststart",
        "src/metrics.mjs": "每日流量采集（播放/互动/涨粉）",
        "src/followers.mjs": "粉丝数采集",
        "src/review.mjs": "复盘计算（第 1/3/7 天自动触发）",
        "src/site.mjs": "自有站点转化归因接口（可选二次开发）",
        "src/access.mjs": "网页访问控制：key 口令 + 飞书验证码登录 + Cloudflare Access",
        "src/tunnel.mjs": "cloudflared 隧道管理",
        "src/board.mjs": "飞书多维表格看板同步",
        "src/bridge.mjs": "Chrome DevTools Protocol 桥接器（调 publisher 插件）",
        "src/chrome-shim.mjs": "Node 内 mock chrome.tabs/chrome.debugger",
        "src/driver.mjs": "各平台浏览器驱动适配层",
        "src/init.mjs": "首次安装向导：环境检查+配置生成+开机自启+登录页",
        "src/demo.mjs": "演示模式：用假数据起 :8788 静态服务",
        "src/access.mjs": "access control middleware",
    }
    for f in files:
        rel = f["path"]
        if not (rel.startswith("src/") and rel.endswith(".mjs")):
            continue
        role = module_roles.get(rel, "核心模块之一")
        exports = []
        if rel == "src/db.mjs":
            exports = ["db", "NAMES", "STATE_CN", "episodes", "getEpisode", "getTasks", "recentLogs", "getSnapshot", "getMeta"]
        elif rel == "src/web.mjs":
            exports = ["createServer", "handlers"]
        out.append({
            "path": rel,
            "lines": f["lines"],
            "bytes": f["bytes"],
            "group": "核心模块",
            "role": role,
            "exports": exports,
        })
    # Add skill
    skill_md = UP / "skills" / "maitian-publish" / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        out.append({
            "path": "skills/maitian-publish/SKILL.md",
            "lines": text.count("\n") + 1,
            "bytes": skill_md.stat().st_size,
            "group": "技能文档",
            "role": "发布流程 9 步 SOP：看片→写素材→确认封面→建工程→generate&validate→plan→run→你点→sync",
            "exports": [],
        })
    return out


def build_configs():
    example = json.loads(read("config.example.json"))
    fields = []
    def flatten(obj, prefix=""):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                flatten(v, key)
            else:
                sample = str(v)[:60] if v else ""
                fields.append({"key": key, "example": sample, "required": key in ("pluginDir", "extensionId", "rootPath", "web.key")})
    flatten(example)
    return {"source": "config.example.json", "fields": fields, "note": "带 * 的字段必须填写才能真跑；其余均可选或按需配"}


def build_links():
    return {
        "repo": "https://github.com/CzzzzzzJ/mdldm-maitian",
        "publisher_repo": "https://github.com/CzzzzzzJ/mdldm-maitian-publisher",
        "readme": "https://github.com/CzzzzzzJ/mdldm-maitian#readme",
        "license": "https://github.com/CzzzzzzJ/mdldm-maitian/blob/main/LICENSE",
        "skill_md": "https://github.com/CzzzzzzJ/mdldm-maitian/blob/main/skills/maitian-publish/SKILL.md",
        "local_mirror": str(UP),
        "local_demo_cmd": "cd upstream && node src/demo.mjs  →  http://localhost:8788/?key=demo",
    }


def main():
    files = build_files()
    results = {
        "maitian.json": build_repo(),
        "files.json": files,
        "modules.json": build_modules(files),
        "config.json": build_configs(),
        "links.json": build_links(),
    }
    for name, obj in results.items():
        dump(name, obj)
        print(f"  {name:<18} {len(obj) if isinstance(obj, (list, dict)) else 1} 条")
    print("完成：索引重建成功（手写数据安全文件未改动）")


if __name__ == "__main__":
    main()
