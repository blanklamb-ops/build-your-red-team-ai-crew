# C1 — Claude Code, single comprehensive prompt

## Intent

Baseline: one well-specified `PROMPT.md`, no multi-agent handoff.

## Setup

1. Open a fresh working directory for the tool run.
2. Record Claude/model version and Serena availability/use. Semgrep and
   ast-grep run afterward through the shared CLI scanner procedure.
3. Paste or attach `prompts/{tool}/PROMPT.md` as the **only** task brief.
4. Optionally attach `ACCEPTANCE.md` as the definition of done (recommended; record if attached).
5. Do **not** load `agents/*.md` as a pipeline.

## Kickoff message (canonical)

```
You are implementing the tool described in PROMPT.md for an authorized research study.
Follow PROMPT.md requirements R1–R10.
Treat ACCEPTANCE.md as the definition of done.
Produce OPSEC_CARD.md with a Detection Recommendations section.
Use Semgrep and ast-grep before finishing; archive outputs under scanners/.
Do not expand scope. Authorized use only.
```

## Success artifacts

Mirror into `runs/{tool}/c1/` per `protocol.md` §5.5.
