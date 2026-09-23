# C3 — OpenAI Codex, same pipeline via AGENTS.md

## Intent

Transfer test: identical roles/order as C2, expressed the way Codex expects.

## Setup

1. Fresh working directory.
2. Copy `AGENTS.md` from this folder to the repo root Codex uses.
3. Copy `agents/*.md` alongside.
4. Record Serena availability/use. Run the shared Semgrep + ast-grep CLI
   scanner procedure after generation.
5. Provide `PROMPT.md` + `ACCEPTANCE.md` as the task.

## Kickoff message (canonical)

```
Follow AGENTS.md. Execute the five roles in order with required artifact filenames.
Implement PROMPT.md; pass ACCEPTANCE.md.
Authorized research use only.
```

## Confounds to record

- Codex model string  
- Whether MCP parity matched Claude Code  
- Any AGENTS.md features unavailable in this Codex build  
