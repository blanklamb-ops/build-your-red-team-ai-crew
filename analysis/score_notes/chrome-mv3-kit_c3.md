# Score notes — chrome-mv3-kit / c3

Scored: 2026-09-15T14:22:10Z  
Blind protocol: workspaces inspected with condition labels visible (single operator). Dim 6 from run-metadata.

| Dim | Score | Justification |
|-----|------:|---------------|
| 1 Correctness | 5 | Automated suites green. Dim2 4: extra MV3 permissions beyond prompt minimum. |
| 2 API fidelity | 4 | See notes |
| 3 OPSEC depth | 5 | Detection Recommendations present unless tagged opsec_thin |
| 4 Code quality | 5 | Tests/structure/scanners (0 Semgrep ERROR) |
| 5 Completeness | 5 | Requirement coverage vs stubs |
| 6 Time (min) | 18.02 | interventions=0 |

quality_mean=4.8  
failure_tags=none  
node tests/run.js: 9/9 suites PASS including regression. Extra permissions scripting/activeTab vs prompt minimum.  
**Operator manual check (2026-09-15):** C3 is the **best chrome kit**, not C1. Quality means tie at 4.8; live capture YAML was schema-valid on C3 and failed on C1 (F-2026-09-05-01).
