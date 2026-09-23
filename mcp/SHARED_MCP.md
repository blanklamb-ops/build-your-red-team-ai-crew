# Shared analysis and coding-aid tools

Every scored run receives the same post-run static-analysis procedure. Scanner
execution is outside the model interaction, so differences in host MCP support
cannot change generation quality. Record versions in each `RUN_LOG.md`.

| Tool | Study role |
|------|------------|
| **Semgrep CLI** | Mandatory post-run SAST; archive JSON, text, and stderr |
| **ast-grep CLI** | Mandatory post-run structural scan; archive JSON, text, and stderr |
| **Serena** | Optional coding aid; availability and use are recorded as a platform confound |

## Rules

1. Use the same scanner commands/rules after every run, whether the host exposes
   those tools through MCP.
2. Do not add extra coding aids that materially change generation quality
   mid-study.
3. Read-only documentation tools are discouraged during scored runs; log any use.
4. If a scanner cannot run, archive stderr and tag `platform_mcp`; do not report
   the scan as clean.
5. Archive raw scanner output even when clean.

## Version capture template

```
semgrep_cli:
ast_grep_cli:
serena_available:
serena_used:
host_version: 
```
