# Feature and test-outcome comparison

This is **what the tests actually did**, not only quality-mean deltas.  
Source: `runs/*/c*/acceptance_results.md`, `analysis/comparison.csv`, score notes. Scoring 2026-09-15. Interventions = 0 on all 16.

**How to read “built / extra / missing”**

- **Built** — required by locked `PROMPT.md` / `ACCEPTANCE.md` and present enough to pass the matching A-item or test.
- **Extra** — present beyond the prompt minimum (not a penalty unless it hurts fidelity, e.g. extra Chrome permissions).
- **Missing** — required and absent, stubbed, or blocked by a defect so the test never ran.

Chrome A3b (live multi-origin recorder smoke) was **not re-run** at scoring for C1–C3; those cells are N/A, not FAIL.

---

## Best and worst (say this first)

| Rank | What | Evidence |
|------|------|----------|
| **Best condition** | **C3 Codex** (`gpt-5.6-sol`) | All four tools quality **4.8**. Tests green. Chrome 9/9 suites including A5e. |
| **Best chrome kit** | **C3** (operator manual check) | Same quality mean as C1 (**4.8**). C3: `tests/run.js` **9/9** including A5e; live capture produced schema-valid YAML (**F-2026-09-05-01**: C1 live schema FAIL). Demo and preferred publish cell: `runs/chrome-mv3-kit/c3/workspace`. |
| **Most consistent tool (C1–C3)** | **gophish-ics** and **after-action** | Every Claude/Codex cell is a working implementation; acceptance 10/10. |
| **Best gophish cell** | **C2** (Go) and **C3** (Python) at 4.8 | C1 Python sidecar also works (4.6); prompt allowed sidecar vs fork. |
| **Weakest non-C4 cell** | **chrome C2** (3.8) | Recorder/UI **works**; Evilginx generator **does not parse**. 15/22 A-items. |
| **Worst condition** | **C4 Codestral** | All four means **1.2–1.4**. No operator-ready tool. Typical: comment-only bodies, missing modules. |
| **Worst single cell** | **after-action C4** (2.91 min, 1.2) or **gophish C4** (no OPSEC card) | Tests do not collect / generator is comments. |

Do not call C2 chrome “the worst tool.” It is a usable recorder with one broken generator file. C4 is the worst **outcome**.

---

## Test outcomes (acceptance + command)

| Tool | C1 | C2 | C3 | C4 |
|------|----|----|----|----|
| chrome-mv3-kit | **20/22** · `npm test` 71/71 incl. A5e | **15/22** · unit tests PASS; `npm test` FAIL (`Illegal break`) | **20/22** · `tests/run.js` 9/9 incl. A5e | **3/22** · no real UI, no generators |
| gophish-ics | **10/10** · pytest 12 (icalendar) | **10/10** · `go test ./...` | **10/10** · pytest 13 | **2/10** · empty `GenerateICSContent` |
| empire-advisor | **10/10** · 12 tests, **shim** not live Empire | **10/10** · pytest 7; pipeline notes not in workspace | **10/10** · pytest 12 + subtests | **3/10** · stub `.ps1` / tiny `rules.yaml` |
| after-action | **10/10** · `make test` | **10/10** · `make test` (A7 documented internal vs client) | **10/10** · unittest 7 (redaction + degrade) | **2/10** · pytest cannot collect |

A3b live chrome smoke: N/A on C1–C3. Chrome C1 live-IdP residual **F-2026-09-05-01** (fixture PASS ≠ Microsoft `session` field) is a finding, not an acceptance FAIL on the study fixture.

---

## Per-tool: built / extra / missing

### chrome-mv3-kit

Prompt asked for: MV3 recorder (names only), optional host grant, form field **names**, Evilginx **2.3.0** placeholder-free YAML, lab overlays **off**, traffic **stub**, OPSEC card, one test command, A5e regression fixture.

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **Built** | Full kit: popup, SW persistence, form capture, markdown export, 2.3.0 generator, validator, traffic stub, gated overlays, OPSEC | Same **recorder/UI** as C1 (Enable / Start / Stop / Export, storage, form unit tests) | Full kit like C1; A5e green | OPSEC bullets + scanner archive only |
| **Extra** | — | Pipeline role files under `runs/.../pipeline/` | **`scripting` + `activeTab`** permissions beyond prompt minimum (fidelity 4, not 5) | — |
| **Missing** | Live A3b not re-run. Live capture finding F-2026-09-05-01 | **YAML path:** generator syntax error → A5–A5e, A11, M3/M7/M8 FAIL | Live A3b not re-run | **Almost everything:** comment-only popup/background/content; required `host_permissions` at install; no `generators/`; no `package.json`; no tests |

**Talk sentence:** Operator manual check: **C3 is the best chrome kit** (live capture schema-valid; C1 fixture tests 71/71 but live YAML failed F-2026-09-05-01). C2 built the extension and **missed the phishlet**. C4 built comments.

### gophish-ics

Prompt asked for: ICS from campaign fields, valid `.ics` / tests, RSVP telemetry, report, **`ics_enabled: false` shipped**, synthetic demo, OPSEC, sidecar **or** fork OK.

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **Built** | Python sidecar: ICS, icalendar tests, RSVP, default-off, OPSEC | **Go** sidecar: `go test` config/ics/telemetry, default-off, OPSEC | Python sidecar: pytest 13, same required path | README sketch + AUTHORIZED_USE + scanners |
| **Extra** | — | Native Go (closer to GoPhish ecosystem than C1/C3 Python) | Extra pytest vs C1 (13 vs 12) | — |
| **Missing** | Not an in-tree GoPhish plugin (allowed; fidelity 4) | Same (sidecar, not fork) | Same | **ICS body is comments**; no tests; no RSVP report; no shipped `ics_enabled: false`; **no root OPSEC_CARD.md** |

**Talk sentence:** C1–C3 all built calendar + RSVP + safety default. C2 added a Go implementation. C4 did not generate ICS.

### empire-advisor

Prompt asked for: Empire plugin **or documented shim**, pre-exec advisory, `rules.yaml`, local KB alternatives, no auto-exec, offline fixtures, OPSEC.

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **Built** | Shim + 12 tests + rules/KB + CLI advisory + OPSEC | Working advisor (pytest 7) + OPSEC; 15 rules | Plugin-shaped module, pytest 12, OPSEC | Docs/OPSEC/AUTHORIZED_USE/scanners |
| **Extra** | — | Pipeline artifacts exist but **not copied into workspace/pipeline** (tagged `pipeline_skip`) | — | — |
| **Missing** | **Not live Empire** (allowed shim). Completeness 4: some `pass` on unused paths | Live Empire not in lab (same as C1) | Live Empire not in lab | **Not a plugin:** stub `main.ps1` (~445B), `rules.yaml` (~20B), one-liner tests |

**Talk sentence:** C1–C3 built an offline advisor. None of them is a production Empire install. C4 built a PowerShell stub.

### after-action

Prompt asked for: JSONL+CSV ingest, decision log, correlation, client report, internal learning, redaction, fixture pack, OPSEC.

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **Built** | Full collector: `make test` (redaction, timeline, detections) | Full collector; client vs internal split documented | Full collector; unittest 7 including graceful degrade | Thin OPSEC card + scanners |
| **Extra** | — | Explicit A7 documentation (internal vs client) | Graceful-degrade tests called out | — |
| **Missing** | — | — | — | **No runnable CLI:** missing `src.models`, `List` import, no `testdata/fixture_engagement`; no client/internal reports |

**Talk sentence:** C1–C3 all built dual reports + redaction. C4 never collected tests.

---

## Cross-cut: what “more” vs “less” actually was

**Added more (beyond a thin pass)**

- C3 chrome: extra MV3 permissions (`scripting`, `activeTab`) — extra, slightly off prompt minimum.
- C2 gophish: Go instead of Python sidecar.
- C3 after-action / gophish: slightly thicker tests (7 unittest / 13 pytest).
- C2/C3/C4 pipelines: five role markdown artifacts (C4 still failed to materialize source).

**Missing where it hurt**

- C2 chrome generator (one syntax error blocks the scored YAML).
- All C4 implementations (comments/stubs).
- Empire: nobody shipped a live Empire hook (shim was in-prompt).
- Chrome: nobody re-ran A3b live multi-origin at P4 scoring.
- Chrome C1: live Microsoft export still has F-2026-09-05-01.

**Not missing (do not say we failed these)**

- Lab overlays / ClickFix-style modules: **required off by default**; C1–C3 gated them. That is compliance, not a missing feature.
- Malleable C2: scored as **traffic stub**, not a production profile.

---

## One slide: best / worst / tests

```
Best condition:  C3  (4.8 × 4 tools, tests green)
Best demo kit:   C3 chrome (operator manual check; live YAML valid)  +  C3 after-action (dual reports)
Most reliable:   gophish + after-action (C1–C3 all work)
Weak C1–C3 cell: chrome C2 (recorder yes, phishlet no)
Worst:           C4 (1.2–1.4, no operator tool)
```

Use this **before** the pooled Δ table so the room sees artifacts and tests, then the comparison.
