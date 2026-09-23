# Acceptance results — after-action / c4

## Scoring note (important)

| Layer | Result |
|-------|--------|
| **Unassisted C4 model output** (Codestral/CrewAI) | **FAIL** — scaffold stubs only |
| **After logged intervention** (agent completed stubs) | **PASS** (functional A1–A10) |

RQ3 talk slide should cite the **unassisted FAIL**. The repaired tree shows the scaffold *can* be completed, but that completion is **not** a C4 model win.

---

### Unassisted model (pre-repair)

| ID | Result | Notes |
|----|--------|-------|
| A1–A7, A10 | **FAIL** | `pass` / “omitted for brevity”; no testdata |
| A8 | **PASS** | OPSEC_CARD Detection Recommendations present |
| A9 | **PASS*** | AUTHORIZED_USE.md present in workspace |

### After intervention repair (2026-09-03)

| ID | Result | Notes |
|----|--------|-------|
| A1 | **PASS** | `make build` → `out/client_report.md` + HTML |
| A2 | **PASS** | JSONL + CSV adapters on fixtures |
| A3 | **PASS** | `linked_items=5` |
| A4 | **PASS** | exec summary, timeline, Detection Recommendations |
| A5 | **PASS** | Successes + Failures in internal report |
| A6 | **PASS** | Planted AWS key / password redacted in client export |
| A7 | **PASS** | Internal retains planted secret detail |
| A8 | **PASS** | Updated OPSEC_CARD ≥3 Detection bullets |
| A9 | **PASS** | README + AUTHORIZED_USE.md |
| A10 | **PASS*** | ast-grep archived; Semgrep JSON archived (engine OOM on auto ruleset — env limit) |

## Manual fidelity (post-repair)

| ID | Result | Notes |
|----|--------|-------|
| M1 | **PASS** | Client tone appropriate |
| M2 | **PASS** | `docs/CORRELATION.md` (±30m, asset key) |
| M3 | **PASS** | Bad rows → warnings, not hard abort |

**Working implementation?** yes — **after intervention only**

**Verify:**
```bash
cd runs/after-action/c4/workspace && make build && make test
```
