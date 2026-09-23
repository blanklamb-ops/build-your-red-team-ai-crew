# AGENTS.md — frozen pipeline for C3

You are running a pre-registered research pipeline. Roles are sequential. Each role must write its artifact before the next role begins. Do not skip roles. Do not expand beyond `PROMPT.md`.

## Shared rules

- Authorized security research / lab use only.
- Definition of done: `ACCEPTANCE.md`.
- Static analysis is a controlled post-run step; do not install or replace
  scanners during generation.
- Use Serena for code navigation/editing only if available; its use is recorded.
- Final tree must include `README.md` and `OPSEC_CARD.md`.

## Role 1 — Domain Researcher

Read `agents/01_domain_researcher.md`.  
Write `pipeline/01_domain_brief.md`. Stop.

## Role 2 — Planner

Read `agents/02_planner.md` and `pipeline/01_domain_brief.md`.  
Write `pipeline/02_plan.md`. Stop.

## Role 3 — Ops Advisor

Read `agents/03_ops_advisor.md`, prior pipeline files, and `PROMPT.md`.  
Write `pipeline/03_ops_constraints.md`. Stop.

## Role 4 — Tool Architect

Read `agents/04_tool_architect.md` and plan/ops artifacts.  
Implement the tool. Write `pipeline/04_build_notes.md`. Stop.

## Role 5 — OPSEC Reviewer

Read `agents/05_opsec_reviewer.md` and review the workspace.  
Write `pipeline/05_opsec_card.md` and `OPSEC_CARD.md` (same content). Stop.

## Handoff complete when

Acceptance checklist can be executed and OPSEC card includes **Detection Recommendations**.
