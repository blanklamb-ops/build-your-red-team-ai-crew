# Scanner Outputs Archive

This directory contains static analysis scanner outputs for the after-action tool.

**Generated:** 2026-09-04  
**Purpose:** Security and code quality analysis per acceptance criterion A10

## Files

### semgrep_output.json
Output from Semgrep static analysis scanner.

**Command:** `semgrep --config=auto --json after_action/`

Semgrep checks for:
- Security vulnerabilities
- Code quality issues
- Best practice violations
- Common bug patterns

### ast_grep_output.txt
Output from ast-grep structural code search.

**Command:** `ast-grep --pattern 'def $FUNC($$$)' after_action/`

AST-grep performs structural pattern matching on the Abstract Syntax Tree.

## Usage

These outputs document the code quality and security posture at time of delivery.

To regenerate:
```bash
cd /path/to/workspace
semgrep --config=auto --json after_action/ > scanner_outputs/semgrep_output.json
ast-grep --pattern 'def $FUNC($$$)' after_action/ > scanner_outputs/ast_grep_output.txt
```

## Notes

Scanner outputs are archived per study protocol requirement R10/A10 for reproducibility and quality validation.
