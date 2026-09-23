# Build Plan — empire-advisor

## Repository layout

```text
empire_advisor/            Python package
  __init__.py
  engine.py                deterministic scoring and suggestion join
  config.py                strict JSON-compatible YAML loading/validation
  models.py                typed advisory records
  cli.py                   offline command and fixture interface
  empire_plugin.py         plugin-shaped execute(command, **kwargs) adapter
plugin.yaml                local plugin manifest/compatibility metadata
rules.yaml                 transparent scoring rules
kb.yaml                    curated alternative templates and citations
fixtures/commands.json     synthetic offline transcripts
tests/test_advisor.py      unit/integration tests
scripts/acceptance.py      executable acceptance assertions
ACCEPTANCE.md              executable Markdown/shell entry point and checklist
scanner-output/            archived Semgrep and ast-grep run records
ethics/AUTHORIZED_USE.md   required distribution notice
README.md                  operation, design, and compatibility limits
OPSEC_CARD.md              operator and defender handoff
pipeline/                  sequential role artifacts and build notes
```

`ASSUMPTION:` “make ACCEPTANCE.md executable” means the file itself will be a shell/Markdown polyglot entry point that delegates to `scripts/acceptance.py`, in addition to the normal test command.

## Work packages

### WP1 — Data contracts and curated content

Define advisory output fields and author at least ten fixed rules with unique ID, regex, severity, weight, rationale, and suggestion IDs. Author local KB entries containing concrete, read-only alternative templates, rationale, and public citations. Add synthetic fixture transcripts. Dependencies: none.

### WP2 — Deterministic core

Implement strict loaders and validation, normalization, regex matching, additive score capped at 100, thresholds (`allow`, `warn`, `deny`), matched evidence, stable ordering, and rule-to-KB suggestion resolution. Reject malformed/duplicate/dangling data. Dependencies: WP1.

### WP3 — Interfaces and Empire shim

Implement CLI single-command and fixture modes with JSON/text renderers. Implement a plugin-shaped adapter with Empire-style metadata/options and `execute(command, **kwargs)` returning advisory JSON only. Add local `plugin.yaml`. Dependencies: WP2.

### WP4 — Tests and executable acceptance

Test loading, threshold states, expected fixture hits/citations, input determinism, CLI offline behavior, malformed data, and the invariant that no execution primitive exists. Implement A1–A10 assertions and manual-check evidence output. Make `ACCEPTANCE.md` directly executable. Dependencies: WP3.

### WP5 — Documentation and scan archives

Write README usage, schema/scoring explanation, Empire 5+/6 compatibility assumptions and shim limits, safety semantics, and authorized-use boundaries. Copy the authorized-use notice to the documented location. Run existing Semgrep and ast-grep if present; do not install or replace either. Archive commands, versions, stdout/stderr, and exit status, truthfully recording absence. Dependencies: WP3–WP4.

### WP6 — Review and handoff

Run unit and acceptance suites from a clean offline invocation, inspect final tree for secrets and unsafe execution paths, write build notes, then perform the separate OPSEC review and publish identical pipeline/root cards with at least three detection recommendations. Dependencies: WP1–WP5.

## Interface contracts

- `load_rules(path: Path) -> tuple[Rule, ...]`
- `load_knowledge_base(path: Path) -> Mapping[str, Suggestion]`
- `Advisor.from_paths(rules_path: Path, kb_path: Path) -> Advisor`
- `Advisor.analyze(command: str, *, source: str = "operator") -> Advisory`
- `Advisory.to_dict() -> dict[str, object]`
- `render_text(advisory: Advisory) -> str`
- `analyze_fixture(path: Path, advisor: Advisor) -> list[Advisory]`
- CLI: `python -m empire_advisor.cli (--command TEXT | --fixture PATH) [--format json|text]`
- Empire-shaped adapter: `Plugin.execute(command: Mapping[str, object], **kwargs: object) -> str`; requires `command["Command"]`, returns serialized advisory, and never dispatches it.

The canonical advisory object contains `schema_version`, normalized `command`, `source`, integer `score`, `state`, `summary`, ordered `matched_rules`, ordered `suggestions`, and `execution_performed: false`. Rule hits include ID, severity, weight, rationale, and matched text. Suggestions include ID, template, rationale, and citation title/URL.

## Prompt requirement traceability

| Requirement | Work package(s) | Evidence |
|---|---|---|
| R1 | WP3, WP5 | `plugin.yaml`, adapter, README limits |
| R2 | WP2, WP3 | pre-submit `analyze`/`execute`, three states |
| R3 | WP1, WP2 | `rules.yaml`, validation, deterministic engine |
| R4 | WP1, WP2 | `kb.yaml`, rule mapping, cited suggestions |
| R5 | WP3 | JSON/text CLI output |
| R6 | WP1, WP3 | fixtures and offline mode |
| R7 | WP2–WP4 | false execution flag and no dispatcher |
| R8 | WP6 | identical OPSEC cards with Detection Recommendations |
| R9 | WP5 | README and ethics notice |
| R10 | WP5 | archived scanner run records |

## Test plan

| Check | Mode | Automated evidence |
|---|---|---|
| A1 | Automated | Import adapter, load manifest, invoke `execute` |
| A2 | Automated | Fixture returns advisory and `execution_performed` is false |
| A3 | Automated | Parse/validate at least ten rules and required fields |
| A4 | Automated | Deep equality over repeated analysis |
| A5 | Automated | Assert fixture has concrete suggestion and HTTP(S) citation |
| A6 | Automated | Run fixture CLI with network disabled by design/no dependencies |
| A7 | Automated + manual | README string checks; reviewer assesses accuracy |
| A8 | Automated + manual | Heading/bullet count; reviewer assesses usefulness |
| A9 | Automated | Notice/file checks |
| A10 | Automated | Both archive files exist and describe actual run/absence |
| M1 | Manual | Inspect rendered rule evidence/rationales |
| M2 | Automated + manual | Non-empty templates and citations; inspect specificity |
| M3 | Automated | High-severity fixtures must produce warn/deny |

Run `python3 -m unittest discover -s tests -v`, then `./ACCEPTANCE.md`. The acceptance entry point must return nonzero on failed automated checks.

## Ambiguities and defaults

- `ASSUMPTION:` No live Empire instance is available; the documented shim is the primary artifact.
- `ASSUMPTION:` JSON syntax in `.yaml` files is acceptable because YAML 1.2 accepts JSON, enabling standard-library-only operation.
- `ASSUMPTION:` State thresholds are advisory labels, not command enforcement. The tool never invokes either original or alternative commands.
- `ASSUMPTION:` Scanner absence is acceptable only when archived transparently, because the pipeline forbids installation during generation.

## Out of scope

Guaranteed stealth or EDR bypass, signature-evasion packs, payload or exploit generation, obfuscation, credential capture, autonomous chaining, command execution, live C2 deployment, mutation of Empire internals, and marketplace publication are excluded.
