# Build Plan — After-Action Collector

## Assumptions

- **ASSUMPTION:** Python 3.11+ standard library is the only runtime dependency.
- **ASSUMPTION:** Client output is Markdown and standalone HTML (the R4 “PDF or HTML” branch selects HTML).
- **ASSUMPTION:** Decisions are CSV; event adapters are JSONL and CSV. Default correlation is exact normalized asset plus ±10 minutes, inclusive.
- **ASSUMPTION:** Scanner executables are controlled post-run dependencies. An archive script records output or a clear unavailable status without installing tools.

## Repository layout

```text
after_action/              Python package
  __init__.py
  adapters.py              JSONL/CSV/decision ingestion and normalization
  correlate.py             explainable time/asset joins
  redact.py                configurable client-boundary redaction
  render.py                client Markdown/HTML and internal Markdown
  cli.py                   orchestration and command-line contract
config/redaction_rules.json
testdata/fixture_engagement/
  engagement.json
  events.jsonl
  events.csv
  decisions.csv
tests/test_after_action.py
scripts/archive_scanners.sh
scanner-output/            archived Semgrep and ast-grep logs
reports/                   generated fixture reports (ignored)
pipeline/                  sequential role artifacts
Makefile
README.md
OPSEC_CARD.md
ACCEPTANCE.md
ethics/AUTHORIZED_USE.md
```

## Work packages

1. **WP1 — Models and adapters** (no dependencies): define normalized records, warning collection, ISO-8601 parsing, asset normalization, JSONL and CSV event adapters, and CSV decision adapter. Preserve source and row provenance.
2. **WP2 — Correlation** (depends WP1): index by normalized asset; link every event/decision pair whose absolute UTC delta is at most the configured window. Emit sorted linked and unlinked records with match reason and delta.
3. **WP3 — Redaction and rendering** (depends WP1–WP2): load configurable rules; recursively redact client-bound strings; render executive summary, correlated timeline, findings placeholders, and Detection Recommendations to Markdown, then escaped standalone HTML. Render internal successes, failures, tool gaps, and reusable TTP references with a handling warning.
4. **WP4 — CLI and fixture** (depends WP1–WP3): validate input layout, orchestrate deterministic rendering, write outputs safely, print sanitized warnings, and construct fixtures with both event formats, at least five links, optional missing fields, and planted secrets.
5. **WP5 — Verification and documentation** (depends WP4): unit/integration tests; executable acceptance commands; README, authorized-use notice, Make targets, and scanner archive script/output.
6. **WP6 — OPSEC review** (depends WP5): inspect implementation and generated artifacts; write identical pipeline and root OPSEC cards including at least three Detection Recommendations.

## Interface contracts

```python
load_jsonl_events(path: Path, warnings: list[str]) -> list[Event]
load_csv_events(path: Path, warnings: list[str]) -> list[Event]
load_decisions(path: Path, warnings: list[str]) -> list[Decision]
parse_timestamp(value: str, source: str, warnings: list[str]) -> datetime | None
normalize_asset(value: str) -> str

correlate(events: list[Event], decisions: list[Decision], window_seconds: int) -> CorrelationResult

load_rules(path: Path) -> list[RedactionRule]
redact_text(text: str, rules: list[RedactionRule]) -> str
render_client_markdown(metadata: dict, result: CorrelationResult, rules: list[RedactionRule]) -> str
render_client_html(redacted_markdown: str) -> str
render_internal_markdown(metadata: dict, result: CorrelationResult, warnings: list[str]) -> str

run(input_dir: Path, output_dir: Path, rules_path: Path, window_minutes: float) -> RunSummary
main(argv: Sequence[str] | None = None) -> int
```

CLI: `python3 -m after_action.cli INPUT_DIR --output OUTPUT_DIR [--rules FILE] [--window-minutes N]`. Exit `0` on successful renders, `2` for invalid arguments/input, and `1` for unexpected failure. Expected optional-field issues warn on stderr but do not change success.

## Requirement trace matrix

| Requirement | Work package | Evidence |
|---|---|---|
| R1 | WP1, WP4 | JSONL + CSV fixture adapters/tests |
| R2 | WP1, WP4 | decisions CSV schema/tests |
| R3 | WP2 | window/asset unit and integration tests |
| R4 | WP3 | client `.md` and `.html` section assertions |
| R5 | WP3 | internal report section assertions |
| R6 | WP3, WP4 | configurable regex rules and negative secret assertions |
| R7 | WP4 | complete fixture and generated report target |
| R8 | WP6 | identical OPSEC cards, mishandling analysis |
| R9 | WP5 | README and ethics notice |
| R10 | WP5 | scanner archive script and two archived outputs |

## Test and acceptance plan

`make test` runs standard-library unit tests. `make fixture` regenerates reports. `make acceptance` runs executable checks without requiring scanners; `make scanners` is the controlled archive step and never installs tools.

| Acceptance | Mode | Verification |
|---|---|---|
| A1–A7 | Automated | build fixture; assert files, two adapter provenance values, ≥5 links, required sections, planted secrets absent client-side, and documented internal/client distinction |
| A8–A10 | Automated | assert OPSEC heading/bullet count, notices, and nonempty scanner archives |
| M1 | Manual | read client report for professional external tone |
| M2 | Automated + manual | assert documented defaults, inspect explanation fields |
| M3 | Automated | malformed/optional missing-field fixture completes and emits warning |

## Out of scope

Live collection/shipping, network access, operator grading, vulnerability validation, finding generation, fuzzy asset/entity resolution, PDF creation, dashboards, authentication, encryption/key management, and scanner installation or replacement are excluded.
