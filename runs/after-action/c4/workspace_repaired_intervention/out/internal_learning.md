# Internal Learning Summary

> Not for client delivery. May retain secrets/PII — see OPSEC_CARD.md.

## Successes

- Correlation joined decisions to multi-format events on asset + time window.
- Dual adapters (JSONL + CSV) exercised on the fixture pack.

## Failures

- Manual gaps remain where asset keys were inconsistent (see warnings).

## Tool gaps

- PDF export optional; HTML provided alongside Markdown.

## Reusable notes / TTP references

- Keep decision logs with stable asset keys (`host-a`, not aliases).
- Always run redaction before client export (R6).
- Correlation: asset equality + ±30 minute window (documented in README).

## Detailed timeline (unredacted internal)

- 2026-08-01T10:06:00+00:00 | host-a | continue monitoring | auth flow incomplete
  - [jsonl] session start
  - [jsonl] observed auth redirect
  - [csv] operator note: pivot deferred
- 2026-08-01T10:08:00+00:00 | host-a | document findings | enough evidence
  - [jsonl] session start
  - [jsonl] observed auth redirect
  - [csv] operator note: pivot deferred
- 2026-08-01T10:22:00+00:00 | mail-1 | hold second wave | need telemetry
  - [jsonl] campaign send batch=1
  - [csv] open pixel count=3
- 2026-08-01T10:30:00+00:00 | mail-1 | close campaign path | objectives met
  - [jsonl] campaign send batch=1
  - [csv] open pixel count=3
- 2026-08-01T11:01:00+00:00 | host-b | scrub secrets before export | api_key=should-be-redacted AKIAIOSFODNN7EXAMPLE
  - [jsonl] planted secret AKIAIOSFODNN7EXAMPLE password=SuperSecret123