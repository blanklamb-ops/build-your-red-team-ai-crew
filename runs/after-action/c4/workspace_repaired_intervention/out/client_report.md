# Client After-Action Report (draft)

## Executive summary

Authorized testing produced correlated operator decisions and telemetry for the engagement window. Details below are redacted for client delivery.

## Timeline

- **2026-08-01T10:06:00+00:00** · `host-a` · continue monitoring — auth flow incomplete
  - event[jsonl] session start
  - event[jsonl] observed auth redirect
  - event[csv] operator note: pivot deferred
- **2026-08-01T10:08:00+00:00** · `host-a` · document findings — enough evidence
  - event[jsonl] session start
  - event[jsonl] observed auth redirect
  - event[csv] operator note: pivot deferred
- **2026-08-01T10:22:00+00:00** · `mail-1` · hold second wave — need telemetry
  - event[jsonl] campaign send batch=1
  - event[csv] open pixel count=3
- **2026-08-01T10:30:00+00:00** · `mail-1` · close campaign path — objectives met
  - event[jsonl] campaign send batch=1
  - event[csv] open pixel count=3
- **2026-08-01T11:01:00+00:00** · `host-b` · scrub secrets before export — api_key=[REDACTED] [REDACTED_AWS_KEY]
  - event[jsonl] planted secret [REDACTED_AWS_KEY] password=[REDACTED]

## Findings placeholders

- Finding F1: _to be completed by operator_

## Detection Recommendations

- Alert on unusual automation from non-mail hosts during engagement windows.
- Monitor operator workstations for bulk auth-flow export artifacts.
- Review after-action report repositories for unredacted secrets before sharing.
