# Scanner Outputs

Security scanner results for gophish-ics tool (A10 requirement).

## Files

- `semgrep.json` - Semgrep static analysis results
- `ast-grep.json` - AST-grep pattern matching results

## Run Information

- **Date**: 2026-09-04
- **Semgrep Version**: Community rules (1074 rules, 290 applicable to Python)
- **Files Scanned**: 9 Python files (main modules + tests)
- **Findings**: 0 blocking issues

## Summary

Both scanners completed successfully with no security findings. The codebase follows secure coding practices:

- No SQL injection patterns (parameterized queries used)
- No command injection (no shell=True usage)
- Input validation on required fields
- Safe file operations
- No hardcoded credentials or secrets

## Re-running Scanners

```bash
# Semgrep
semgrep --config=auto --json --no-git-ignore -o semgrep.json *.py tests/*.py

# AST-grep
ast-grep scan --json *.py tests/*.py > ast-grep.json
```
