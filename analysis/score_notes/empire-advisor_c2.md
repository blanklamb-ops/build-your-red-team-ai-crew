# Score notes — empire-advisor / c2

Scored: 2026-09-15T14:22:10Z  
Blind protocol: workspaces inspected with condition labels visible (single operator). Dim 6 from run-metadata.

| Dim | Score | Justification |
|-----|------:|---------------|
| 1 Correctness | 4 | Tests pass; pipeline copied to run archive not workspace (harness copies c2 pipeline). |
| 2 API fidelity | 4 | See notes |
| 3 OPSEC depth | 5 | Detection Recommendations present unless tagged opsec_thin |
| 4 Code quality | 4 | Tests/structure/scanners (0 Semgrep ERROR) |
| 5 Completeness | 4 | Requirement coverage vs stubs |
| 6 Time (min) | 16.06 | interventions=0 |

quality_mean=4.2  
failure_tags=pipeline_skip  
pytest 7 passed. Pipeline artifacts in runs/.../pipeline but not workspace/pipeline.
