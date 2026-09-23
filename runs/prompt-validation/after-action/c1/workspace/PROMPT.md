# PROMPT — after-action

**Tool slug:** `after-action`  
**Authorized use only** — see `ethics/AUTHORIZED_USE.md`.

## Operator goal

Build an after-action collector that correlates engagement logs and operator decisions into:

1. a **client-facing report** draft (professional, non-jargony where possible)  
2. an **internal learning summary** (what worked, what failed, reuse notes)  

This is the boring-but-critical closeout tool. Prefer structured inputs and reproducible renders.

## Requirement IDs

| ID | Requirement |
|----|-------------|
| R1 | Ingest at least two log formats (e.g. JSON lines + CSV) via adapters |
| R2 | Ingest operator decision log (timestamp, decision, rationale, related asset) |
| R3 | Correlation engine joins events↔decisions on time window + asset key |
| R4 | Client report renderer (Markdown + PDF **or** HTML) with exec summary, timeline, findings placeholders, Detection Recommendations section |
| R5 | Internal learning renderer: successes, failures, tool gaps, reusable TTPs as references (framework-agnostic IDs ok) |
| R6 | PII/secret redaction pass (regex/rules configurable) before client export |
| R7 | Fixture engagement pack under `testdata/` producing both reports |
| R8 | `OPSEC_CARD.md` (include how report mishandling becomes an OPSEC failure) |
| R9 | README + authorized-use notice |
| R10 | Scanner outputs archived |

## Non-goals

- Live log shipping from production client networks during the study  
- Fully automated grading of operator skill  

## Success

Fixture pack renders both reports; redaction removes planted secrets.
