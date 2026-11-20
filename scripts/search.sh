#!/usr/bin/env bash
# 薄封装检索脚本：强制目录白名单隔离，防止多租户场景下全库裸搜导致跨客户信息串味。
# 自动优先使用 ripgrep (rg)，若本机未安装则平滑回退至系统 grep。
#
# 用法：
#   ./scripts/search.sh "<关键词或正则>" [memory根目录]
#   ./scripts/search.sh --tenant <租户代号> "<关键词或正则>" [memory根目录]

set -euo pipefail

TENANT=""
if [[ "${1:-}" == "--tenant" ]]; then
  TENANT="${2:?错误：--tenant 需要指定租户代号}"
  shift 2
fi

QUERY="${1:?用法: search.sh [--tenant <代号>] <关键词> [memory目录]}"
MEM_DIR="${2:-./memory}"

if [[ ! -d "$MEM_DIR" ]]; then
  echo "错误：找不到记忆库目录 '$MEM_DIR'" >&2
  exit 1
fi

# 公共安全检索域（不含 tenants/* 其他租户目录）
SEARCH_PATHS=()
for sub in AGENTS.md MEMORY.md 1_theory 2_calibration 3_skills 4_anomalies transcripts; do
  [[ -e "$MEM_DIR/$sub" ]] && SEARCH_PATHS+=("$MEM_DIR/$sub")
done

# 若指定租户，仅挂载该租户分区
if [[ -n "$TENANT" ]]; then
  if [[ -d "$MEM_DIR/tenants/$TENANT" ]]; then
    SEARCH_PATHS+=("$MEM_DIR/tenants/$TENANT")
  else
    echo "警告：未找到租户分区 '$MEM_DIR/tenants/$TENANT'，仅检索全局公共层" >&2
  fi
fi

if command -v rg >/dev/null 2>&1; then
  rg --line-number --smart-case \
     --glob '!.env*' --glob '!*.local.md' \
     "$QUERY" "${SEARCH_PATHS[@]}"
else
  grep -rnEi \
     --exclude='.env*' --exclude='*.local.md' \
     "$QUERY" "${SEARCH_PATHS[@]}"
fi
