#!/usr/bin/env bash
set -euo pipefail
ROOT="/home/kali/Desktop/research/rootcon 20"
LOG="$ROOT/analysis/pilots/c3_matrix_rerun.log"
cd "$ROOT"
echo "C3 sequential start $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
for tool in chrome-mv3-kit gophish-ics empire-advisor after-action; do
  echo "===== START $tool/c3 $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >>"$LOG"
  set +e
  python3 "$ROOT/harness/run_scored_condition.py" "$tool" c3 --timeout-minutes 180 >>"$LOG" 2>&1
  rc=$?
  set -e
  echo "===== END $tool/c3 rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ) =====" >>"$LOG"
  if [ "$rc" -ne 0 ]; then
    echo "STOPPING after failure on $tool" >>"$LOG"
    exit "$rc"
  fi
done
echo "C3 sequential complete $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
