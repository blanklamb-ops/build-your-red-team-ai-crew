# Results (P4 — 2026-09-15)

**Matrix:** 16 cells, locked prompts (`prompts-locked-for-matrix`).  
**Scoring:** `analysis/comparison.csv` + `analysis/score_notes/`. Dims 1–5 are 0–5; primary quality = mean of those five. Dim 6 is generation minutes (unassisted; interventions = 0).  
**Models (from each `RUN_LOG.md`):**

| Condition | Host | Model pin |
|-----------|------|-----------|
| C1, C2 | Claude Code **2.1.259** | **`claude-sonnet-4-5`** (Sonnet 4.5) |
| C3 | Codex CLI **0.147.0** | **`gpt-5.6-sol`**, `reasoning_effort=medium` |
| C4 | CrewAI **1.15.18** + Ollama (Windows host) | **`codestral:latest`**, 22.2B, Q4_0, digest `0898a8b286d56d8105587049fec69634fce83c957230fc13f0acfe03b7b11909` |

**Caveats:** scorer knew condition labels (not double-blind). Chrome **A3b** live multi-origin recorder smoke was not re-run. Serena unused (omitted from the talk). Semgrep/ast-grep were **post-run CLI** on all 16 (P4). C4 used local inference with host Ollama; the archived private-network logs do not verify egress isolation. n=4 tools: case study deltas, not significance tests.

| Tool | C1 | C2 | C3 | C4 | C2−C1 | C3−C2 | C4−C2 |
|------|---:|---:|---:|---:|------:|------:|------:|
| chrome-mv3-kit | 4.8 | 3.8 | 4.8 | 1.2 | −1.0 | +1.0 | −2.6 |
| gophish-ics | 4.6 | 4.8 | 4.8 | 1.2 | +0.2 | 0.0 | −3.6 |
| empire-advisor | 4.4 | 4.2 | 4.8 | 1.4 | −0.2 | +0.6 | −2.8 |
| after-action | 4.6 | 4.6 | 4.8 | 1.2 | 0.0 | +0.2 | −3.4 |
| **Pooled mean Δ** | | | | | **−0.25** | **+0.45** | **−3.1** |

Working implementation: C1/C3 chrome (automated; A3b N/A). **C2 chrome: unpacked recorder/UI workable; A5e/`npm test` fail** (generator parse). Non-chrome C1–C3 **yes**. All C4 **no**.

## RQ1 — Pipeline vs single prompt (C2 vs C1)

**The five-agent pipeline did not beat one comprehensive prompt in Claude Code on mean quality.** Pooled C2−C1 = **−0.25**. Three tools were a wash. Chrome C2 quality **3.8 vs C1 4.8**: the unpacked extension is **workable** (operator-confirmed; real popup + SW; unit tests PASS), but `npm test` still dies on `Illegal break` in `phishlet-generator.js`, so A5e/YAML path fails.

C2 was **slower** on every tool (chrome 25.8 vs 16.6 min; others ~+5–8 min).

**Talk answer:** In this IDE, a well-specified single prompt matched or beat the pipeline on mean quality. C2 chrome is a usable recorder with a broken generator gate — not a C4-style empty shell.

## RQ2 — Transfer to Codex (C3 vs C2)

**The same five roles in `AGENTS.md` transferred.** Pooled C3−C2 = **+0.45**, including chrome (C3 4.8 vs C2 3.8: C3 `npm test` 9/9 including A5e; C2 generator does not parse). On gophish/after-action, C3 ≈ C2 (both working). Empire C3 slightly above C2.

C3 times were between C1 and C2. Model/host is a confound (gpt-5.6-sol vs Claude Sonnet 4.5).

**Talk answer:** Methodology transfers to Codex for these four tools; Codex was not the weak condition. Chrome shows transfer can **beat a broken Claude pipeline cell**.

## RQ3 — Local Codestral stretch (C4 vs C2)

**The pipeline did not stretch Codestral into operator-ready tools.** Pooled C4−C2 = **−3.1**. All four C4 quality means are 1.2–1.4. Typical failure: `### FILE:` comments / empty function bodies / missing modules (`src.models`, no `generators/`, PowerShell one-liners).

Chrome C4 remains comment-only UI (unlike **workable C2 chrome**). Gophish C4: `GenerateICSContent` is comments. Empire C4: stub `.ps1`. After-action C4: 2.91 min, tests do not collect.

**Talk answer:** For budget / “local crew” teams, this C4 stack is **not** a substitute for Claude/Codex on these tools. That is a publishable negative.

## Failure modes worth teaching

- **F-2026-09-05-01** — C1 A5e PASS ≠ live Microsoft capture schema (`session` undefined). Fixture tests are necessary, not sufficient.
- **C2 chrome generator** — unpacked kit is workable; `phishlet-generator.js` extra `break` blocks `npm test` / A5e.
- **C4 comment-stubs** — `STUB_SCAN_OK` missed HTML/JS comment-only files (`pass` / “omitted for brevity” only).
- **Scanners** — Semgrep + ast-grep post-run CLI on all 16; Serena was not shared across runs.
- **Local topology** — C4 used Codestral through Ollama on the Windows host, with Kali over VMnet. Egress isolation was not independently verified in the archive.

## What we would change next time

- Fail C4 materialize on comment-only sources, not only `pass`.
- Require `npm test` / `go test` / pytest as a harness gate before `generated`.
- Double-blind scoring copies.
- Serena was not shared across the runs.
- Keep chrome prompt lab-safe (Evilginx 2.3.0 + overlays off + traffic stub); do not restore ClickFix/malleable C2 names that blocked C1.

## Ship list (abstract artifacts)

| Abstract item | Where |
|---------------|--------|
| Four condition configs | `conditions/` |
| Personas | `agents/` |
| Sixteen scored run records | `runs/{tool}/{c1–c4}/`; C2/C4 tracked workspace source is largely absent |
| Comparison / failure log | `analysis/comparison.csv` |
| OPSEC + Detection Recommendations | each working workspace `OPSEC_CARD.md` |
| Local tool snapshots | `publish/tool-repos/`; Chrome snapshot is C1, while C3 is the preferred demo candidate |
