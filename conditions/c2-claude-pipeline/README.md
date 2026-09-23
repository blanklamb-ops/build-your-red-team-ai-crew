# C2 — Claude Code, five-agent pipeline

## Intent

Same IDE as C1; scaffolding is a forced five-role pipeline using frozen personas.

## Setup

1. Fresh working directory.
2. Same post-run scanner procedure as C1; record Serena availability/use.
3. Copy `agents/*.md` into the run workspace (or reference by path).
4. Kick off with `PROMPT.md` + instruction to run roles **in order**.

## Kickoff message (canonical)

```
Run a five-stage pipeline. Do not skip stages.
Use these persona files exactly:
1) agents/01_domain_researcher.md → pipeline/01_domain_brief.md
2) agents/02_planner.md → pipeline/02_plan.md
3) agents/03_ops_advisor.md → pipeline/03_ops_constraints.md
4) agents/04_tool_architect.md → implementation + pipeline/04_build_notes.md
5) agents/05_opsec_reviewer.md → OPSEC_CARD.md + pipeline/05_opsec_card.md

User requirements: PROMPT.md
Definition of done: ACCEPTANCE.md
Post-run scanners: Semgrep and ast-grep. Record Serena availability/use.
Authorized use only. No scope expansion.
```

## Notes

- Prefer separate Claude Code subagents/tasks per role if available; if not, simulate strict stage gates in one session but still write each artifact before the next stage.
- Record in RUN_LOG whether true subagents or staged single-session was used (platform confound).
