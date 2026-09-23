# PROMPT — empire-advisor

**Tool slug:** `empire-advisor`  
**Authorized use only** — see `ethics/AUTHORIZED_USE.md`.

## Operator goal

Build an **Empire-compatible plugin (or clearly documented plugin-shaped module)** that:

- intercepts or wraps operator command submissions in a lab Empire-like interface  
- scores commands against a **transparent, documented heuristic** related to noisy vs quieter tradecraft  
- suggests **documented alternative commands** from a local knowledge base (not live exploit generation)  
- keeps humans in control — advisory only; never auto-executes alternatives  

If full Empire is unavailable in the lab, ship a faithful plugin API shim + adapter so acceptance can run offline.

## Requirement IDs

| ID | Requirement |
|----|-------------|
| R1 | Plugin manifest / registration matching Empire plugin conventions **or** shim with compatibility notes |
| R2 | Command interception hook (pre-exec advisory) with allow/deny/warn states |
| R3 | Scoring engine: deterministic rules from `rules.yaml` (or equiv); each rule has id, rationale, severity |
| R4 | Suggestion engine: maps rule hits → quieter alternative templates from local KB; citations required |
| R5 | Operator UI or CLI output showing score, matched rules, suggestions |
| R6 | Offline mode with fixture command transcripts |
| R7 | No auto-execution of suggested alternatives |
| R8 | `OPSEC_CARD.md` with Detection Recommendations |
| R9 | README + authorized-use notice |
| R10 | Scanner outputs archived |

## Non-goals

- Guaranteed EDR bypass  
- Closed-source signature evasion packs  
- Autonomous attack chaining  

## Success

Passes `ACCEPTANCE.md` with fixtures; scoring is explainable and deterministic.
