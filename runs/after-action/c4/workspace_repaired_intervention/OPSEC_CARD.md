# OPSEC Card — after-action

## Summary

Offline closeout tool: ingests JSONL/CSV engagement events + operator decisions,
correlates on asset + time window, and writes a redacted client report plus an
unredacted internal learning summary (Markdown + HTML).

## Operator Risks

- Sharing the **internal** report externally leaks secrets/PII by design.
- Planted fixture secrets look realistic enough to confuse operators into
  treating them as live credentials.
- Overly wide correlation windows can mis-attribute decisions to unrelated events.

## Artifacts Left Behind

- `out/client_report.{md,html}`, `out/internal_learning.{md,html}`
- Local Python `__pycache__/` under `src/` / `tests/`
- No network calls, registry writes, or browser state by this tool

## Safer Operating Guidance

- Run only on synthetic fixtures or authorized engagement exports.
- Treat internal reports as controlled artifacts; client export must go through redaction.
- Delete `out/` when the engagement closes if it contains real data.

## Detection Recommendations

- Alert on after-action report directories leaving the operator network without DLP review.
- Flag commits/uploads containing `AKIA` / PEM / `password=` strings in Markdown exports.
- Monitor for bulk creation of `client_report.md` + `internal_learning.md` pairs on analyst workstations.
- Review access to engagement log shares used as ingest inputs.
- Detect unexpected Python one-off CLIs reading both decision CSVs and event JSONL in the same process tree.

## Residual Gaps

- Redaction is regex-based; novel secret formats can slip through.
- HTML export is a minimal transform, not a full document pipeline.
- No cryptographic integrity check on fixture/input logs.
