# Failure taxonomy tags

Use one or more tags in `comparison.csv` `failure_tags` (pipe-separated).

| Tag | Meaning |
|-----|---------|
| `accept_fail` | Failed acceptance items |
| `api_mismatch` | Wrong API/manifest/plugin/ICS shape |
| `stubbed` | Required feature is placeholder |
| `opsec_thin` | OPSEC card weak or missing detections |
| `scanner_hot` | Semgrep/ast-grep critical issues |
| `timeout` | Hit wall-clock stop |
| `intervention_cap` | Hit 3-steer budget |
| `platform_mcp` | MCP parity failure |
| `model_loop` | Model thrash / non-convergence |
| `scope_creep` | Built extras, missed requirements |
| `safety_default_missing` | Unsafe defaults / missing flags |
| `docs_gap` | README/build instructions inadequate |
| `pipeline_skip` | Stage skipped or artifacts missing (C2–C4) |
| `none` | No material failure |
