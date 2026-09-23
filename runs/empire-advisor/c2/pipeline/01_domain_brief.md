# Domain Brief — empire-advisor

## 1. Goal restatement

Build an **advisory plugin for Empire C2 framework** that intercepts operator command submissions, scores them against documented operational security heuristics (noisy vs. quieter tradecraft), and suggests safer alternatives from a local knowledge base — keeping the human operator in full control with no auto-execution.

**Success criteria:** An operator submitting a command like `shell whoami` sees an advisory showing a noisiness score, matched rules explaining why, and a documented alternative (e.g., using native PowerShell token queries instead), then decides whether to proceed.

## 2. Constraints

**Platform & Environment:**
- Empire C2 framework (PowerShell Empire v3/v4 or Starkiller UI assumed)
- Python 3.7+ (Empire's plugin system uses Python)
- Offline/air-gap compatible — no live exploit generation or external API calls
- Must work in lab environments where full Empire may not be available

**Technical:**
- Plugin must conform to Empire's plugin API conventions (registration, hooks)
- If Empire unavailable: provide shim layer with same contract for offline testing
- Knowledge base must be local (YAML/JSON files) with deterministic scoring
- No modification to operator's actual commands without explicit confirmation

**Operational:**
- Advisory-only system; operator retains full decision authority
- Scoring must be transparent and explainable without reading source code
- Rules must cite rationale (e.g., "process execution visible to EDR telemetry")

## 3. Prior art

**Empire Plugin Architecture:**
- Empire plugins register via `plugin.yaml` manifest with metadata and entry points
- Hooks available: `on_agent_task_create`, `on_module_run`, pre/post execution callbacks
- Reference: [BC-Security Empire docs](https://github.com/BC-SECURITY/Empire/wiki/Plugins) and existing plugins like `csharpserver`, `sample_plugin`

**Command Advisory Patterns:**
- **Mythic C2** uses `opsec` blocks in command definitions for per-command warnings
- **Cobalt Strike's Sleep API** allows aggressor scripts to intercept tasks (`beacon_task` hook)
- Format precedent: structured warnings with severity levels (info/warn/critical)

**Scoring Heuristics (Prior Research):**
- MITRE ATT&CK detection analytics often cite telemetry visibility: process creation > registry reads > WMI queries
- Red Team Field Manual (RTFM) and SpecterOps research classify commands by noisiness
- Rule format inspiration: Sigma rules (id, title, description, level)

**Alternatives Knowledge Base:**
- Similar to LOLBAS/GTFOBins pattern: technique mapping with citations
- Format: source command → target alternatives with context/prerequisites

## 4. Risks

**Technical:**
- **Empire API surface instability** — Plugin hooks may vary between Empire v3.x, v4.x, and Starkiller versions; shim may be necessary for broad compatibility
- **Command parsing ambiguity** — Distinguishing Empire module calls from raw shell commands requires understanding Empire's command grammar
- **Incomplete coverage** — Local KB can't anticipate all operator-invented command variations; scoring misses are acceptable if documented

**Operational:**
- **False confidence** — Operator may over-trust scoring and skip manual OPSEC analysis; documentation must emphasize advisory nature
- **Stale KB** — Defensive telemetry capabilities evolve; rules need maintenance but won't auto-update in offline mode
- **Determinism vs. context** — Fixed rules can't account for target-specific context (e.g., known EDR blind spots); operator must apply judgment

**Study-specific:**
- This is lab research; real engagement use requires validation against actual Empire instance and defensive telemetry

## 5. Open questions (blocking assumptions)

| Question | Assumption (for planning) | Verification needed |
|----------|---------------------------|---------------------|
| Exact Empire version available in lab? | **ASSUME:** Plugin must work offline via shim if Empire unavailable; target v4.x API conventions but provide compatibility notes | Acceptance A1/A6 tests this |
| Pre-task vs. post-task hook preference? | **ASSUME:** Pre-task hook (`on_agent_task_create` equivalent) for advisory before execution | Ops Advisor defines fail-safe defaults |
| Scoring granularity (0-10 vs. severity labels)? | **ASSUME:** Numeric 0-100 + severity labels (low/medium/high/critical) for flexibility | Acceptance A4 tests determinism |
| KB format: single file vs. directory? | **ASSUME:** `rules.yaml` for scoring logic, `alternatives.yaml` for suggestions — separate concerns | Architect implements |
| UI output: JSON vs. formatted text vs. both? | **ASSUME:** Both — JSON for automation, formatted text for operator readability | Acceptance A2 specifies "JSON/text" |

## Domain brief validation

- **Scope aligned:** Plugin + shim, scoring, suggestions, offline mode, no auto-exec ✓
- **Gaps identified:** Empire version variance (mitigated with shim), KB maintenance (doc'd in OPSEC card)
- **Prior art cited:** Empire plugin API, Mythic opsec blocks, Sigma rule format
- **Word count:** ~750 (under 800 limit)

**Next:** Planner converts this into work packages with acceptance traceability.
