#!/usr/bin/env bash
# Scoped search wrapper (delegates to scripts/aml.py for standalone & hub modes).
# Usage:
#   ./scripts/search.sh [--product <slug>] [--tenant <code>] "<query>" [memory_dir]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PRODUCT=""
TENANT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --product) PRODUCT="${2:?--product requires a slug}"; shift 2 ;;
    --tenant)  TENANT="${2:?--tenant requires a code}"; shift 2 ;;
    *) break ;;
  esac
done

QUERY="${1:?Usage: search.sh [--product <slug>] [--tenant <code>] <query> [memory_dir]}"
MEM_DIR="${2:-.}"

PY_ARGS=("$SCRIPT_DIR/aml.py" search --repo "$MEM_DIR")
[[ -n "$PRODUCT" ]] && PY_ARGS+=(--product "$PRODUCT")
[[ -n "$TENANT" ]] && PY_ARGS+=(--tenant "$TENANT")
PY_ARGS+=("$QUERY")

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PY_ARGS[@]}"
elif command -v py >/dev/null 2>&1; then
  exec py -3 "${PY_ARGS[@]}"
else
  exec python "${PY_ARGS[@]}"
fi
