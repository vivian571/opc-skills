#!/usr/bin/env bash
# 刷新上游镜像与自动索引（零删除覆盖同步）
#   sh scripts/refresh.sh           联网刷新
#   sh scripts/refresh.sh --offline 只用现有 upstream/ 重建索引
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/refresh.py "$@"
