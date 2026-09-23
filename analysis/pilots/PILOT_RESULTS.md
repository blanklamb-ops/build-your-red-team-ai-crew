# Pilot validation results — 2026-09-03

## Test 1 — Harness structure

```bash
python3 harness/validate_setup.py
```

**Result:** PASS (`checks_run=156`)

## Test 2 — Kickoff + acceptance MVP

**Result:** PASS (local harness MVP)

## Test 3 — Live Claude Code C1 pilot (`after-action`) — VERIFIED

Operator ran Claude Code against `runs/after-action/c1/workspace`.

### Independent re-check (this session)

| Check | Result |
|-------|--------|
| CLI build from fixture | PASS (`events=10`, `linked=7`) |
| Unit tests | PASS (`14 passed`) |
| Client secret redaction | PASS (no planted secrets in client report) |
| OPSEC Detection Recommendations | PASS (≥3 bullets) |
| README authorized-use | PASS |
| Scanners archived | PASS (`../scanners/semgrep_*`, `ast_grep_*`) |
| Acceptance sheet A1–A10 / M1–M3 | All marked PASS by operator; build re-verified |

### Run metadata (from RUN_LOG)

- Condition: **c1** (single prompt, Claude Code 2.1.233)
- Model: claude-sonnet-5
- ~33 minutes wall clock; **1 intervention** (explore pause/resume)
- stop_reason: **pass**
- Note: Semgrep/ast-grep used as **CLI** (installed mid-run via pipx), not MCP — log as platform confound for scored runs

### Verdict on prompts/setup

**C1 path works.** Frozen `PROMPT.md` + `ACCEPTANCE.md` produced a working after-action tool that meets the acceptance bar.

## Ollama / C4 install

| Step | Status |
|------|--------|
| Codestral on **Windows host** Ollama | **DONE** (`codestral:latest`, digest `0898a8b286d5…`, Q4_0, 22.2B) |
| Host listen `0.0.0.0:11434` + firewall VMnet | **DONE** |
| Kali → host via VMnet8 `192.168.224.1` | **DONE** (`use_host_ollama.sh` reachable) |
| C4 venv + `crewai` 1.15.18 | **DONE** (`conditions/c4-ollama-codestral-crewai/.venv`) |
| ChatOllama smoke (`codestral` → `OK`) | **DONE** (~11s via host) |
| Local Codestral inside Kali VM | **SKIP** — OOM on ~15 GiB RAM; not used for scored runs |

### C4 client recipe (each shell)

```bash
cd "/home/kali/Desktop/research/rootcon 20"
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
source conditions/c4-ollama-codestral-crewai/.venv/bin/activate
python conditions/c4-ollama-codestral-crewai/run_pipeline.py \
  --tool after-action \
  --workspace runs/after-action/c4/workspace
```

### C4 after-action kickoff pilot (2026-09-03)

| Check | Result |
|-------|--------|
| Five role markdown artifacts | PASS (`01`–`05` under `workspace_pilot_notes_only/` / `pipeline/`) |
| Runnable implementation on disk | **FAIL** — Architect had no FileWriter; only narrated code in `04_build_notes.md` |
| Scored run? | **No** — incomplete pilot |
| Fix applied | Drop tools; `### FILE:` + `materialize_files.py` (Codestral has no tool calling) |

### C4 after-action re-run with FILE materialize (2026-09-03T13:13Z)

| Check | Result |
|-------|--------|
| Crew complete (`CREW_DONE`, EXIT:0) | PASS (~2 min wall) |
| Unassisted acceptance | **FAIL** — stubs / no testdata |
| Intervention repair | Working stdlib tool; `make build` + 4 tests PASS |
| RQ3 scored cell | **FAIL (unassisted)** — repair is intervention_cap, not model win |
| Pipeline hardening | `stub_scan.py` gate + anti-stub Architect rules |

**Next:** freeze v1.0, then remaining matrix cells (C2/C3 after-action, other tools).
