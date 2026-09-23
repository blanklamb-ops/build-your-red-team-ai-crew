# C1 prompt validation 

**Purpose:** Confirm the four tool prompts produce usable C1 outputs **before** the formal 16-cell matrix.

**Status:** Prompts **LOCKED** for matrix — see `analysis/PROMPTS_LOCKED.md` (tag `prompts-locked-for-matrix`).

**Not a formal matrix cell.** Artifacts live under `runs/prompt-validation/{tool}/c1/`. Do not score these against C2–C4 yet.

## Status snapshot (2026-09-05)

| Tool | C1 validation | Notes for reviewers |
|------|---------------|---------------------|
| `chrome-mv3-kit` | **C1+C3 regen PASS (placeholder-free); locked** | C1 17.59 min; C3 18.02 min; both `generated`. Tests PASS (A5e). Live residual: **F-2026-09-05-01** (C1 live schema fail / C3 live schema pass). |
| `after-action` | **PASS** (automated) | Prompt hash matches; prior build/tests OK |
| `gophish-ics` | **PASS** (automated) | Prompt hash matches; `ics_enabled: false` default enforced after revision |
| `empire-advisor` | **PASS** (automated) | Prompt hash matches; prior pytest OK |

## Where to look

```
prompts/{tool}/PROMPT.md          # LOCKED — do not edit without new lock
prompts/{tool}/ACCEPTANCE.md
analysis/PROMPTS_LOCKED.md        # matrix lock + verify commands
analysis/FINDINGS.md              # live-capture residuals
analysis/protocol-deviations.md
runs/prompt-validation/{tool}/c1/
```

### chrome-mv3-kit quick check

```bash
cd "runs/prompt-validation/chrome-mv3-kit/c1/workspace"
npm install
npm test
node generators/phishlet-generator.js /path/to/session.json \
  --output /tmp/out.yaml --schema schemas/phishlet-schema-2.3.0.json
```

## Known residual issues (chrome)

1. A5e does not fully cover CLI flag UX — verify `--output` / positional after each regen.
2. Fixture PASS ≠ gold live-IdP kit. Score unassisted output; use `demos/chrome-mv3-kit-gold/` for demos only.
3. **F-2026-09-05-01:** live C1 capture can fail Evilginx 2.3.0 schema (`session` undefined); C3 live capture validates. Accepted under lock — do not reopen prompts for this.

## Review ask (closed)

The prompts were locked for the scored matrix on 2026-09-05.
