#!/usr/bin/env bash
# 离线蒸馏（Dreaming）工作树管理脚本：
# 1. 统计全库记忆条目的真实引用频次（[ref: <id>] / referenced_ids），供升降级决策使用；
# 2. 创建隔离的 git worktree 分支供离线整理 Agent 直接编辑文件，彻底避免 LLM 手搓 .patch 行号报错；
# 3. 整理完成后一键导出真实 git diff 供人工审阅。
#
# 用法：
#   ./scripts/dream-worktree.sh start [memory目录]   # 创建隔离工作树并生成引用频次统计
#   ./scripts/dream-worktree.sh diff                # 查看离线整理产生的真实 git diff 与摘要
#   ./scripts/dream-worktree.sh clean               # 合并完成或放弃后清理临时工作树

set -euo pipefail

ACTION="${1:-help}"
MEM_DIR="${2:-templates}"
STAMP="$(date +%Y%m%d)"
NOW_ISO="$(date '+%Y-%m-%dT%H:%M:%S%z')"
BRANCH="dream/${STAMP}"
WT_DIR=".dream-worktree"

case "$ACTION" in
  start)
    if [[ -d "$WT_DIR" ]]; then
      echo "工作树 $WT_DIR 已存在。如需重建请先运行: $0 clean" >&2
      exit 1
    fi
    git worktree add -B "$BRANCH" "$WT_DIR" HEAD
    echo "==> 已创建隔离蒸馏工作树: $WT_DIR (分支: $BRANCH)"

    # 自动统计全库条目 ID 的被引用频次（排除条目自身 frontmatter 中的 id: 定义行）
    REF_REPORT="$WT_DIR/reference-stats.txt"
    {
      echo "# 记忆条目真实引用频次统计 (生成时间: $NOW_ISO)"
      if [[ -d "$WT_DIR/$MEM_DIR" ]]; then
        if command -v rg >/dev/null 2>&1; then
          rg --no-filename -v '^id:' "$WT_DIR/$MEM_DIR" 2>/dev/null \
            | rg -o '(theory|sop|asset|anom|tr)-[A-Za-z0-9_-]+' \
            | sort | uniq -c | sort -nr || true
        else
          grep -rhv '^id:' "$WT_DIR/$MEM_DIR" 2>/dev/null \
            | grep -Eo '(theory|sop|asset|anom|tr)-[A-Za-z0-9_-]+' \
            | sort | uniq -c | sort -nr || true
        fi
      fi
    } > "$REF_REPORT"
    echo "==> 已生成引用统计表: $REF_REPORT"
    echo "==> 下一步：让离线整理 Agent 在 '$WT_DIR' 目录内按 dreaming/consolidate-prompt.md 修改文件，完成后运行 '$0 diff' 审阅。"
    ;;

  diff)
    if [[ ! -d "$WT_DIR" ]]; then
      echo "错误：找不到活动的工作树 $WT_DIR" >&2
      exit 1
    fi
    if [[ -f "$WT_DIR/change-log.md" ]]; then
      echo "==================== 变更摘要 (change-log.md) ===================="
      cat "$WT_DIR/change-log.md"
      echo "=================================================================="
    fi
    git -C "$WT_DIR" status -s
    echo ""
    git -C "$WT_DIR" diff
    ;;

  clean)
    if [[ -d "$WT_DIR" ]]; then
      git worktree remove --force "$WT_DIR"
      echo "==> 已清理工作树 ${WT_DIR}（分支 ${BRANCH} 保留，按需 git merge 或 git branch -D）"
    else
      echo "无需清理：${WT_DIR} 不存在"
    fi
    ;;

  *)
    echo "用法: $0 {start|diff|clean} [memory子目录]"
    exit 1
    ;;
esac
