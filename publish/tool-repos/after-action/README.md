# after-action

`after-action` is an offline collector that turns structured engagement events and operator decisions into a client-facing Markdown/HTML draft and a separate internal learning summary. It is intentionally conservative: correlations require an exact normalized asset key and an inclusive time window.

## Authorized use only

Use this project only for security testing, research, education, and lab activity you are legally or contractually authorized to perform. Read [the full authorized-use notice](ethics/AUTHORIZED_USE.md). Never commit real client evidence or generated engagement reports.

## Requirements

- Python 3.11 or newer
- POSIX `make` and shell for convenience targets
- No runtime packages and no network access
- Optional, controlled post-run scanners: Semgrep and ast-grep

## Quick start with synthetic data

```sh
make test
make fixture
```

The fixture writes `reports/fixture/client_report.md`, `client_report.html`, and `internal_learning.md`. It deliberately contains malformed input, a naive timestamp, and planted secrets. Warnings identify only the file and row—not the discarded value.

Run a separate authorized engagement export with an explicit output directory:

```sh
python3 -m after_action.cli /path/to/engagement \
  --output /path/to/review-output \
  --rules config/redaction_rules.json \
  --window-minutes 10
```

The input and output directories must differ. Reports are written atomically with mode `0600` where the platform supports POSIX permissions. Existing complete targets are replaced only after the new content is flushed.

## Input contract

The named files are fixed; the collector does not crawl adjacent evidence.

- `engagement.json`: JSON object with `engagement_name`, `client_name`, `period`, `executive_summary`, `findings`, `detection_recommendations`, `successes`, `failures`, and `tool_gaps`. Most fields have conservative fallback text.
- `events.jsonl`: one JSON object per line with `timestamp`, `asset`, `event_type`, `summary`, and `details`.
- `events.csv`: the same event fields as a header row and records.
- `decisions.csv`: `timestamp`, `decision`, `rationale`, `related_asset`, with optional `outcome` and `ttp_ref`.

Timestamps are ISO 8601. A missing timezone is interpreted as UTC with a warning. Timestamp and asset are required for events; timestamp, decision, rationale, and related asset are required for decisions. A malformed row is skipped with a sanitized warning, while valid rows continue. Each file is capped at 10 MiB and 100,000 records.

## Correlation rules

The default window is ±10 minutes, inclusive. Asset values are stripped, case-folded, and have a trailing dot removed. The tool performs no DNS lookup, fuzzy matching, alias inference, or network activity. It creates every event/decision pair with the same normalized asset and an absolute UTC time delta within the window. Timeline evidence includes source provenance, signed/absolute delta, and match reason; ordering is deterministic. No matches still produces valid reports.

## Redaction and handling boundary

Rules in `config/redaction_rules.json` are ordered regular expressions with fixed replacements. Safe defaults cover private-key blocks, bearer tokens, common secret key/value forms, email addresses, and the fixture canary. The entire client Markdown document is redacted in memory; client HTML is derived only from that redacted text and HTML-escaped. Neither client artifact is first written in unredacted form.

Regex redaction cannot prove anonymity. Review the client draft for engagement-specific identifiers before delivery. The internal report deliberately bypasses client redaction so it can retain learning evidence; it is marked `INTERNAL SENSITIVE — NOT CLIENT-SAFE` and must not be sent to a client.

## Acceptance and scanners

`ACCEPTANCE.md` maps the registered checks. Execute them with:

```sh
make scanners     # controlled post-run step; never installs tools
make acceptance
```

`make scanners` writes `scanner-output/semgrep.txt` and `scanner-output/ast-grep.txt`. When a scanner is absent, its archive says `NOT_AVAILABLE`; that is an honest execution record, not a clean result. `make acceptance` regenerates the fixture and executes A1–A10 plus automated fidelity checks. M1 and part of M2 remain named human review steps.

## Operator closeout workflow

Keep original exports under engagement evidence controls. Render to a dedicated review directory, inspect warnings and correlation deltas, review client content for sensitive data, and deliver only through the approved channel. Keep internal/client filenames distinct and apply the engagement retention policy to inputs, outputs, scanner logs, backups, and collaboration copies. See `OPSEC_CARD.md` for defender-oriented detection recommendations.
