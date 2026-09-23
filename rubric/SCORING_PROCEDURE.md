# Scoring procedure

## When to score

After each run is archived, or in a batch after all 16 — but use the same procedure.

## Blind preference

1. Copy `workspace/` to a staging path named only `{tool}-{anon_id}`.
2. Score dims 1–5 without looking at condition ID.
3. Reveal condition; fill dim 6 from RUN_LOG (cannot be blinded).
4. Enter row into `analysis/comparison.csv`.

## Per-run steps

1. Read `acceptance_results.md` (operator-filled) — if missing, execute `ACCEPTANCE.md` yourself and write results.
2. Skim README + OPSEC card.
3. Spot-check requirement IDs R1–R10.
4. Open scanner summaries.
5. Assign dims 1–5 with a one-line justification each in `analysis/score_notes/{tool}_{condition}.md`.
6. Tag failures using taxonomy in `rubric/failure_taxonomy.md`.

## Aggregation

- Primary quality score = mean(dims 1–5)
- Report dim 6 separately
- Contrasts: C2−C1, C3−C2, C4−C2 per tool and pooled mean of deltas
