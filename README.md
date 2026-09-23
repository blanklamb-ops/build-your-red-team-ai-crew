# Build Your Red Team AI Crew: One Prompt vs Five Agents

Research artifacts for a 16-cell comparison of one comprehensive coding prompt with five-role workflows across four tool-building tasks. This repository preserves the study method, selected run records, scored outputs, and documented failures. The scores describe these runs; they are not a deployment-readiness rating.

## Conditions and tasks

| ID | Workflow | Recorded stack |
| --- | --- | --- |
| C1 | One comprehensive prompt | Claude Code 2.1.259, Sonnet 4.5 |
| C2 | Five roles in one session | Claude Code 2.1.259, Sonnet 4.5 |
| C3 | Five roles through `AGENTS.md` | Codex CLI 0.147.0, gpt-5.6-sol, medium |
| C4 | Five sequential CrewAI roles | CrewAI 1.15.18, Ollama Codestral 22.2B Q4_0 |

The four tasks were `chrome-mv3-kit`, `gophish-ics`, `empire-advisor`, and `after-action`. See [`protocol.md`](protocol.md) for the procedure, [`prompts/`](prompts/) for the locked task specifications and acceptance criteria, [`agents/`](agents/) for the roles, and [`conditions/`](conditions/) for the workflow configurations. Semgrep and ast-grep were run after generation; Serena was not shared across the runs.

## Results

| Condition | Mean recorded quality / 5 | End-to-end result |
| --- | ---: | --- |
| C1 | 4.60 | Four task implementations passed recorded local tests; Chrome live capture still needed review. |
| C2 | 4.35 | Three tasks passed recorded local tests; the Chrome recorder worked but its required generator could not parse. |
| C3 | 4.80 | Four task implementations passed recorded local tests; Chrome capture used heuristic credential keys. |
| C4 | 1.25 | No complete working implementation in this configuration. |

C2 took 29.38 more recorded generation minutes than C1 across the four tasks. C3 transferred the workflow to Codex, but the platform and model also changed. The local Codestral result has no local single-prompt baseline. These are four selected outputs per condition, scored by one unblinded rater; generation time excludes prompt preparation and human review. See [`analysis/comparison.csv`](analysis/comparison.csv), [`analysis/results.md`](analysis/results.md), and [`analysis/score_notes/`](analysis/score_notes/) for the rating trail. The Chrome C2 rating should be read alongside its broken generator, as the rubric anchor and recorded score are in tension.

## What is in this repository

- [`runs/`](runs/) contains the recorded logs, acceptance results, scanner outputs, pipeline documents, and tracked source where available. **The tracked C2 and C4 workspace trees are largely absent.** This is not a complete archive of raw source for all sixteen cells.
- [`analysis/protocol-deviations.md`](analysis/protocol-deviations.md) records deviations and earlier iterations. Historical notes there document what changed during the study; the scored matrix is the source for final ratings.
- [`publish/tool-repos/`](publish/tool-repos/) contains local tool snapshots. Its Chrome snapshot is **C1**, while the talk selects **C3** as a preferred demo candidate. These are study artifacts within this one repository; no separate tool repositories are planned.
- [`ethics/`](ethics/) describes the authorized-use boundary. Fixture checks and offline demonstrations do not establish live deployment readiness.

The C4 run used local model inference, with Ollama on a Windows host and a Kali guest on a private network. The archived logs do not establish verified egress isolation. Live GoPhish delivery and RSVP ingestion were not demonstrated.

## Reproduce and review

Start with [`protocol.md`](protocol.md), use the condition README under [`conditions/`](conditions/), and compare a task's `PROMPT.md` and `ACCEPTANCE.md` against its run record. Review the relevant [`OPSEC_CARD.md`](publish/tool-repos/) and detection recommendations before using a tool snapshot. Tests and scores answer different questions: inspect both the acceptance record and the implementation.

This is the one public study archive for the methodology and available tool artifacts. No separate tool repositories are planned. The included snapshots are not reviewed operational builds.
