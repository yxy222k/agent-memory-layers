#!/usr/bin/env bash
# Offline Dreaming worktree wrapper (delegates to scripts/aml.py).
# Usage:
#   ./scripts/dream-worktree.sh {triage|start|diff|clean|stats} [memory_dir] [--product <slug>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ACTION="${1:-start}"
MEM_DIR="."
if [[ $# -ge 2 && "${2:-}" != --* ]]; then
  MEM_DIR="$2"
  shift 2
else
  [[ $# -ge 1 ]] && shift 1
fi

PY_ARGS=("$SCRIPT_DIR/aml.py" dream "$ACTION" --repo "$MEM_DIR" "$@")

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PY_ARGS[@]}"
elif command -v py >/dev/null 2>&1; then
  exec py -3 "${PY_ARGS[@]}"
else
  exec python "${PY_ARGS[@]}"
fi
