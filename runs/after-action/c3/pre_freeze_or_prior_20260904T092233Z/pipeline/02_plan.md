# Build Plan — after-action

## Assumptions and repository layout

**ASSUMPTION:** Python 3.10+ standard library only; Markdown and self-contained HTML are the two client formats. **ASSUMPTION:** an engagement directory has `events.jsonl`, `events.csv`, `decisions.jsonl`, and `engagement.json`; optional narrative fields absent from metadata render as `Not provided`. **ASSUMPTION:** the default inclusive join window is ±10 minutes, exact on a case-folded/trimmed asset key; nearest decision wins with input order as a deterministic tie-break.

```text
after_action/             package: models, adapters, correlation, redaction, renderers, CLI
  __init__.py
  __main__.py
  models.py
  adapters.py
  correlate.py
  redact.py
  render.py
config/default.json       safe correlation and redaction defaults
testdata/fixture_engagement/
  engagement.json
  events.jsonl
  events.csv
  decisions.jsonl
tests/test_after_action.py
scripts/run_scanners.sh
scanner_outputs/          archived Semgrep and ast-grep status/output
ethics/AUTHORIZED_USE.md
Makefile
README.md
OPSEC_CARD.md
pipeline/01…05_*.md
```

## Work packages

- **WP1 — contracts and CLI skeleton** (no dependencies): dataclasses, timestamp/asset normalization, warnings, configuration loader, `python -m after_action build INPUT --output OUTPUT --config CONFIG`.
- **WP2 — ingestion adapters** (WP1): JSONL and CSV event adapters plus JSONL decision adapter; skip malformed records with stderr warnings, but fail on absent/unreadable required files.
- **WP3 — correlation** (WP1, WP2): stable event ordering and nearest eligible decision join using the configured inclusive time window and normalized asset.
- **WP4 — redaction** (WP1): ordered configurable regex rules recursively applied to every client-facing string; validate regex at startup and fail closed before any client file is written.
- **WP5 — report rendering** (WP3, WP4): client Markdown and escaped self-contained HTML; internal Markdown with successes, failures, tool gaps, and reusable TTP references. Write through temporary files with restrictive permissions and atomic replacement.
- **WP6 — fixtures and automated checks** (WP2–WP5): mixed adapters, at least five linked events, malformed/missing optional-field cases, planted secret, deterministic output, HTML escaping, and client leakage assertions.
- **WP7 — operator documentation and ethics** (WP5): README, safe workflow, schema, correlation rules, warnings, internal/client sensitivity difference, authorized-use notice, Make targets.
- **WP8 — controlled scans and archive** (WP6): run installed Semgrep and ast-grep without installation; archive stdout/stderr, version, command, timestamp, and exit status, including an explicit unavailable record if absent.
- **WP9 — OPSEC review** (WP7, WP8): final review and identical root/pipeline cards with all required sections and at least three detection recommendations.

## Interface contracts

```python
def load_jsonl_events(path: Path, warn: WarningSink) -> list[Event]: ...
def load_csv_events(path: Path, warn: WarningSink) -> list[Event]: ...
def load_decisions(path: Path, warn: WarningSink) -> list[Decision]: ...
def parse_timestamp(value: str) -> datetime: ...
def normalize_asset(value: str) -> str: ...
def correlate(events: list[Event], decisions: list[Decision], window: timedelta) -> list[TimelineItem]: ...
def compile_rules(config: dict) -> list[RedactionRule]: ...
def redact(value: str, rules: list[RedactionRule]) -> str: ...
def render_client_markdown(context: ReportContext, rules: list[RedactionRule]) -> str: ...
def render_client_html(redacted_context: ReportContext) -> str: ...
def render_internal_markdown(context: ReportContext) -> str: ...
def build(input_dir: Path, output_dir: Path, config_path: Path) -> BuildResult: ...
```

Normalized `Event` fields: timestamp, asset, action, outcome, detail, source, source index. `Decision`: timestamp, asset, decision, rationale, source index. `TimelineItem`: event plus optional decision and signed delta seconds. Renderers receive structured context and return complete text; only the client path accepts redacted data. CLI exits nonzero on configuration/required-file/write failure and zero when record-level warnings were recoverable.

## Requirement trace matrix

| Requirement | Work package(s) | Evidence |
|---|---|---|
| R1 | WP2, WP6 | JSONL/CSV adapters and fixture assertions |
| R2 | WP2, WP6 | decision schema and ingestion tests |
| R3 | WP3, WP6 | window/asset join tests, ≥5 links |
| R4 | WP5, WP6 | client `.md` + `.html` required sections |
| R5 | WP5, WP6 | internal required sections and TTP refs |
| R6 | WP4, WP6 | configurable regex and planted-secret assertion |
| R7 | WP6 | fixture engagement and smoke build |
| R8 | WP9 | identical OPSEC cards, mishandling risk |
| R9 | WP7 | README and ethics notice |
| R10 | WP8 | archived scanner records |

## Test plan

Automated `unittest` checks cover A1–A7: fixture build, both adapter labels, ≥5 linked items, required report headings, internal sections/detail distinction, secret absence, HTML escaping, deterministic rerender, correlation boundaries, invalid timestamps, and warning behavior. A shell/Make smoke target performs the operator-facing build. A8–A10 are checked automatically for required files/text and archived scan records; scanner findings themselves are reviewed manually. M1 is manual editorial review. M2 is automated heading/content presence plus README review. M3 is automated with fixture malformed/missing fields plus manual warning inspection.

## Out of scope

No live collection or shipping, remote APIs, databases, dashboards, authentication, client-network access, automated operator scoring, fuzzy asset identity resolution, secret discovery guarantees, PDF generation, finding severity adjudication, or scanner installation/replacement. Finding entries remain explicit report-drafting prompts populated from engagement metadata, not automated security conclusions.
