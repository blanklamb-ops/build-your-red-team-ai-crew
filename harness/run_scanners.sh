#!/usr/bin/env bash
# Identical post-run scanner procedure for every condition.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="${1:?usage: $0 <tool> <condition> [run-base]}"
COND="${2:?usage: $0 <tool> <condition> [run-base]}"
BASE="${3:-$ROOT/runs/$TOOL/$COND}"
WS="$BASE/workspace"
OUT="$BASE/scanners"
mkdir -p "$OUT" "$ROOT/.tools/semgrep-config" "$ROOT/.tools/semgrep-cache"

export XDG_CONFIG_HOME="$ROOT/.tools/semgrep-config"
export XDG_CACHE_HOME="$ROOT/.tools/semgrep-cache"
export SEMGREP_SETTINGS_FILE="$OUT/.semgrep-settings.yml"

semgrep --config "$ROOT/harness/semgrep-study.yml" --no-git-ignore \
  --exclude node_modules --exclude venv --exclude .venv --exclude __pycache__ \
  --json --output "$OUT/semgrep.json" "$WS" \
  >"$OUT/semgrep.stdout.txt" 2>"$OUT/semgrep.stderr.txt"
SEMGREP_RC=$?

AST_RULES='
id: dynamic-exec
language: Python
rule:
  any:
    - pattern: eval($$$ARGS)
    - pattern: exec($$$ARGS)
message: Dynamic code execution requires review.
severity: error
---
id: todo-pass
language: Python
rule:
  all:
    - pattern: |
        def $F($$$ARGS):
          $$$BODY
    - has:
        pattern: pass
message: Function contains pass; review for a required stub.
severity: warning
'

ast-grep scan --inline-rules "$AST_RULES" --no-ignore vcs --no-ignore parent \
  --globs '!**/node_modules/**' --globs '!**/venv/**' --globs '!**/.venv/**' \
  --json "$WS" >"$OUT/ast-grep.json" 2>"$OUT/ast-grep.stderr.txt"
AST_RC=$?
ast-grep scan --inline-rules "$AST_RULES" --no-ignore vcs --no-ignore parent \
  --globs '!**/node_modules/**' --globs '!**/venv/**' --globs '!**/.venv/**' \
  "$WS" >"$OUT/ast-grep.txt" 2>>"$OUT/ast-grep.stderr.txt"

printf 'semgrep_exit=%s\nast_grep_exit=%s\n' "$SEMGREP_RC" "$AST_RC" \
  >"$OUT/scanner-status.txt"

if [[ $SEMGREP_RC -ne 0 || $AST_RC -gt 1 ]]; then
  echo "scanner execution incomplete; inspect $OUT" >&2
  exit 1
fi
echo "scanner artifacts: $OUT"
