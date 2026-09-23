#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT_DIR="../scanners"
mkdir -p "$OUT_DIR"

echo "== semgrep =="
semgrep --config auto --no-git-ignore src \
    --json --output "$OUT_DIR/semgrep_after_action.json" || true
semgrep --config auto --no-git-ignore src \
    --output "$OUT_DIR/semgrep_after_action.txt" || true

echo "== ast-grep =="
AST_GREP_RULES=$(cat <<'YAML'
id: print-usage
language: Python
rule:
  pattern: print($$$ARGS)
message: print() call — confirm CLI status only.
severity: info
---
id: eval-or-exec-usage
language: Python
rule:
  any:
    - pattern: eval($$$ARGS)
    - pattern: exec($$$ARGS)
message: eval()/exec() usage detected.
severity: warning
YAML
)
ast-grep scan --inline-rules "$AST_GREP_RULES" --no-ignore vcs --no-ignore parent \
    --json src > "$OUT_DIR/ast_grep_after_action.json" || true
ast-grep scan --inline-rules "$AST_GREP_RULES" --no-ignore vcs --no-ignore parent \
    src > "$OUT_DIR/ast_grep_after_action.txt" || true

echo "Scanner output archived to $(cd "$OUT_DIR" && pwd)"
