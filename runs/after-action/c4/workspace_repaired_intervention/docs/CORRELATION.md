# Correlation rules

- **Asset key:** case-insensitive string equality on the `asset` field after trim.
- **Time window:** symmetric ±30 minutes (override with `--window-minutes`).
- **Join direction:** each decision is matched to nearby events; a decision with
  zero nearby events still appears on the timeline (unlinked).
- **Degrade:** malformed ingest rows are skipped with warnings (internal report).
