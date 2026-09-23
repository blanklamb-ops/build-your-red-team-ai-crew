# Score notes — after-action / c4

Scored: 2026-09-15T14:22:10Z  
Blind protocol: workspaces inspected with condition labels visible (single operator). Dim 6 from run-metadata.

| Dim | Score | Justification |
|-----|------:|---------------|
| 1 Correctness | 1 | Generation finished in 2.91 min with incomplete tree. |
| 2 API fidelity | 1 | See notes |
| 3 OPSEC depth | 2 | Detection Recommendations present unless tagged opsec_thin |
| 4 Code quality | 1 | Tests/structure/scanners (0 Semgrep ERROR) |
| 5 Completeness | 1 | Requirement coverage vs stubs |
| 6 Time (min) | 2.91 | interventions=0 |

quality_mean=1.2  
failure_tags=accept_fail|stubbed|docs_gap  
pytest cannot collect: missing src.models; main.py uses List without import; no testdata/fixture_engagement.
