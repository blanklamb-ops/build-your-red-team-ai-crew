# Acceptance results — empire-advisor / c1

Independent verification 2026-09-03.

| ID | Result | Notes |
|----|--------|-------|
| A1 | **PASS** | Plugin + shim present; offline CLI via `PYTHONPATH=. python3 -m empire_advisor.cli` (documented in README) |
| A2 | **PASS** | `score "procdump…"` returns advisory JSON; `auto_executed: false`; does not execute alternatives |
| A3 | **PASS** | `rules.yaml` has **13** rules with id + rationale (≥10) |
| A4 | **PASS** | 23 pytest tests PASS including determinism; repeated score output stable |
| A5 | **PASS** | Score/demo include suggestions with KB ids + citations (e.g. `KB-CREDDUMP-01`) |
| A6 | **PASS** | `demo` runs fixture transcripts without live Empire |
| A7 | **PASS** | README documents shim / offline usage |
| A8 | **PASS** | OPSEC Detection Recommendations ≥7 bullets |
| A9 | **PASS** | Authorized-use in README + `AUTHORIZED_USE.md` |
| A10 | **PASS** | Scanners archived under `../scanners/` |

## Manual fidelity

| ID | Result | Notes |
|----|--------|-------|
| M1 | **PASS** | Text/JSON explanations readable without reading source |
| M2 | **PASS** | Suggestions map to KB templates with citations |
| M3 | **PASS** | High-risk rules use block/deny advisory (e.g. LSASS dump) |

**Working implementation?** yes  
**Tests:** 23 passed  

**Note:** Invoke as `PYTHONPATH=. python3 -m empire_advisor.cli …` from workspace (no `__main__.py` at package root for bare `python -m empire_advisor`).
