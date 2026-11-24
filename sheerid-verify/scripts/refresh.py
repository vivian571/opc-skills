#!/usr/bin/env python3
"""刷新上游镜像与自动索引。零删除：只覆盖同步，不移除本地任何文件。

用法：python3 scripts/refresh.py [--offline]

网络步骤：codeload ZIP 取源码 + GitHub API 取 star/fork/pushed_at。
失败时保留现有快照并退出非零，不写坏本地数据。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "upstream"
DATA = ROOT / "data"
ZIP_URL = "https://codeload.github.com/JenkinWoo/sheeridVerify/zip/refs/heads/main"
API_URL = "https://api.github.com/repos/JenkinWoo/sheeridVerify"
EXCLUDE = {"MIRROR-SCOPE.md"}


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "workbuddy-skill-refresh/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def sync_source():
    raw = fetch(ZIP_URL)
    with tempfile.TemporaryDirectory(prefix="sheerid-upstream-") as tmp:
        zpath = Path(tmp) / "upstream.zip"
        zpath.write_bytes(raw)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(Path(tmp) / "src")
        roots = [p for p in (Path(tmp) / "src").iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise RuntimeError("ZIP 顶层目录结构异常，未同步")
        source = roots[0]
        before = {p.relative_to(UP).as_posix() for p in UP.rglob("*") if p.is_file()}
        incoming = {p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file()}
        shutil.copytree(source, UP, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("node_modules", ".git", ".runs", "*.zip",
                                                      "*.local.json", ".env.web"))
        gone = sorted(p for p in before - incoming - EXCLUDE if not p.endswith("MIRROR-SCOPE.md"))
        print(f"源码同步：{len(incoming)} 个上游文件写入/覆盖，{len(gone)} 个上游已移除项仅报告不删除")
        for p in gone:
            print(f"  [上游已移除] {p}")
    return len(incoming), gone


def update_meta():
    try:
        meta = json.loads(fetch(API_URL, timeout=30).decode("utf-8"))
    except Exception as exc:
        print(f"元数据获取失败（保留现有值）：{exc}")
        return
    path = DATA / "repo.json"
    repo = json.loads(path.read_text(encoding="utf-8"))
    repo["stargazers_count"] = meta.get("stargazers_count", repo["stargazers_count"])
    repo["forks_count"] = meta.get("forks_count", repo["forks_count"])
    repo["pushed_at"] = meta.get("pushed_at", repo["pushed_at"])
    repo["created_at"] = meta.get("created_at", repo["created_at"])
    path.write_text(json.dumps(repo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"元数据更新：★{repo['stargazers_count']} / fork {repo['forks_count']} / pushed {repo['pushed_at']}")


def rebuild_index():
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_index.py")],
                            cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout.strip() or "(索引重建无输出)")
    if result.returncode != 0:
        print(result.stderr.strip())
        raise RuntimeError("索引重建失败")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="不联网，只从现有 upstream/ 重建索引")
    args = ap.parse_args()
    if not args.offline:
        sync_source()
    else:
        print("离线模式：跳过源码同步与元数据更新")
    # build_index 会继承 repo.json 里已有的实时字段，再写回 meta 才不会被静态快照覆盖
    rebuild_index()
    if not args.offline:
        update_meta()
    print("完成。手写数据安全文件（safety/pitfalls/diffs/verification/test-run）未改动。")


if __name__ == "__main__":
    main()
