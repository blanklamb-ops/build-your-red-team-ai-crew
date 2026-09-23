# Study Protocol (FROZEN DRAFT — hash at freeze commit)

**Title:** Does multi-agent orchestration produce better operator tooling than a well-prompted single run?

**Local model lock (C4):** Ollama + **Codestral** + CrewAI, served on the
Windows hypervisor over a private VMnet segment. Record internet-isolation
state per run; do not call this air-gapped unless both host and guest egress
were disabled and verified during inference.

**Date opened:** 2026-08-12  
**Freeze status:** frozen at tag `freeze-v1.0`

---

## 1. Pre-registered research questions

| ID | Question | Primary contrast | Decision rule |
|----|----------|------------------|---------------|
| RQ1 | Does the 5-agent pipeline beat one comprehensive prompt in the same IDE? | C2 vs C1 | Compare mean rubric (dims 1–5), time-to-working, intervention count; report nulls |
| RQ2 | Does the methodology transfer from Claude Code to Codex? | C3 vs C2 | Compare rank order and per-dimension deltas across four tools |
| RQ3 | How far does the pipeline stretch a weaker local model? | C4 vs C2 (and absolute C4) | Absolute viability vs acceptance; gap to C2; when still useful |

Negative or null results are publishable outcomes.

---

## 2. Conditions

| ID | Host | Scaffolding | Model / runtime |
|----|------|-------------|-----------------|
| C1 | Claude Code | One comprehensive prompt, no multi-agent handoff | Claude (host default; record exact model string per run) |
| C2 | Claude Code | Five-agent pipeline using `agents/*.md` | Same Claude family as C1 within a tool row if possible |
| C3 | OpenAI Codex | Same five roles expressed in `AGENTS.md` + role files | Codex model string recorded per run |
| C4 | CrewAI | Same five roles as Crew agents | **Ollama `codestral`** (pin tag + digest in RUN_LOG) |

### Controlled inputs (must not vary)

- Per-tool `prompts/{tool}/PROMPT.md`
- Post-run scanner procedure: Semgrep + ast-grep CLI, with raw output archived
  (see `mcp/SHARED_MCP.md`)
- Rubric + acceptance checklists
- Stop rules and intervention budget

### Condition variables and platform confounds

- C1 vs C2 isolates scaffolding within Claude Code when the same Claude model
  family can be selected.
- C3 and C4 intentionally vary host/model as transfer and local-model tests;
  they do **not** isolate scaffolding alone.
- Serena is a coding aid, not a mandatory constant. Record whether it was
  available/used; never silently substitute another coding aid.
- Host product, model string, tool-calling support, and network topology are
  documented platform confounds.

---

## 3. Use cases (four tools)

| Tool slug | Stress on scaffolding |
|-----------|------------------------|
| `chrome-mv3-kit` | Multi-format generators, browser extension structure, many coupled artifacts |
| `gophish-ics` | Integration with existing project patterns, calendar/ICS + telemetry hooks |
| `empire-advisor` | Plugin API fidelity, operator UX, policy-ish scoring logic |
| `after-action` | Log correlation, dual audience reports (client vs internal learning) |

Prompts are research instruments: requirements + acceptance criteria. They are not a license to use outputs outside authorized engagements.

---

## 4. Agent pipeline (C2/C3/C4)

Fixed order. No skipping roles. Each role writes a named artifact before the next starts.

1. **Domain Researcher** → `01_domain_brief.md`
2. **Planner** → `02_plan.md`
3. **Ops Advisor** → `03_ops_constraints.md`
4. **Tool Architect** → implementation under `src/` (or language-appropriate root)
5. **OPSEC Reviewer** → `05_opsec_card.md` (must include Detection Recommendations)

C1 receives the same `PROMPT.md` in one shot and must still produce an OPSEC card and meet acceptance checks; it does not produce the intermediate role files unless it chooses to.

---

## 5. Run procedure

### 5.1 Preflight

1. Confirm freeze commit hash recorded in `RUN_LOG.md`.
2. Confirm Semgrep and ast-grep CLI versions; record Serena availability/use.
3. For C4: host `/api/tags` shows the pinned Codestral digest; record host and
   guest egress state as `isolated`, `private-network`, or `internet-connected`.
4. Empty output directory: `runs/{tool}/{condition}/`.

### 5.2 Execution

1. Copy `prompts/{tool}/PROMPT.md` into the host as the user task (C1) or pipeline kickoff (C2–C4).
2. Start timer (`time_start_iso`).
3. Allow the scaffold to run until stop rule.
4. Record `time_first_accept_attempt_iso` at the first acceptance attempt.
   Stop the run timer only when acceptance passes or the run is abandoned.

### 5.3 Stop rules

Stop the run when **any** is true:

- Acceptance checklist fully pass; or
- **Intervention budget** exhausted: 3 human steering messages max; or
- **Wall clock** hits 180 minutes active generation; or
- Model/host hard-fails (crash loop, auth loss) and cannot resume within 15 minutes.

Do **not** improve the global `PROMPT.md` between conditions. Per-run steering must be logged.

### 5.4 Interventions

An intervention is any human message that changes direction, pastes missing docs, or fixes errors the agent did not fix itself. Mechanical “continue” / approving a tool call is **not** an intervention.

Log each in `runs/{tool}/{condition}/interventions.csv`.

### 5.5 Artifacts to archive

```
runs/{tool}/{condition}/
  RUN_LOG.md
  interventions.csv
  transcript/          # host export or raw logs
  workspace/           # final code tree
  scanners/            # semgrep + ast-grep outputs
  pipeline/            # 01–05 artifacts when applicable
  acceptance_results.md
```

---

## 6. Evaluation

See `rubric/SCORING_PROCEDURE.md` and `rubric/dimensions.md`.

Dimensions (0–5 each, except time):

1. Correctness  
2. API fidelity  
3. OPSEC depth  
4. Code quality  
5. Completeness  
6. Time-to-working-implementation (minutes + interventions; not averaged into the 0–5 mean unless noted)

Blind scoring: prefer scoring `workspace/` with condition labels hidden when feasible.

---

## 7. Analysis plan

- Per-tool and pooled means for dims 1–5  
- Paired contrasts: C2−C1, C3−C2, C4−C2  
- Failure taxonomy tags in `analysis/comparison.csv`  
- No p-hacking: if n=4 tools, treat as structured case study with effect sizes/deltas, not overclaimed significance  

---

## 8. Ethics and disclosure

See `ethics/AUTHORIZED_USE.md`. Public tool repos must include authorized-use notice and OPSEC card Detection Recommendations. No targeting of systems without authorization.

---

## 9. Freeze checklist

- [ ] Operator reviewed four `PROMPT.md` files  
- [ ] Personas reviewed  
- [ ] Codestral Ollama tag pinned in `conditions/c4-ollama-codestral-crewai/MODEL_PIN.md`  
- [ ] Git commit `protocol: freeze v1.0` with tag `freeze-v1.0`  
- [ ] Record commit SHA in this file under **Frozen at**

**Frozen at:** `fc240352c1385ca4e356f4ea6760bb599c0dd88e`

**Prompts locked for matrix:** tag `prompts-locked-for-matrix` — see `analysis/PROMPTS_LOCKED.md` (post-freeze prompt iteration closed for scored runs; base freeze unchanged).
