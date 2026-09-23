# Build Notes — empire-advisor

## Implemented result

The Role 4 build implements the frozen plan and operational constraints as a Python 3.10+ standard-library package. The CLI and Empire-shaped adapter analyze text only. They expose deterministic scores, allow/warn/deny advisory states, ordered rule evidence, and de-duplicated local KB suggestions with citations. The output always reports execution_performed as false.

The policy includes 15 validated rules and 13 curated, concrete, read-only suggestion templates. Six synthetic fixture transcripts exercise allow, warn, and deny paths offline. Invalid configuration, empty/oversized commands, malformed fixtures, duplicate IDs, bad regexes, and dangling KB links fail explicitly.

## Plan conformance

- WP1: rules.yaml, kb.yaml, and versioned synthetic fixtures are complete.
- WP2: additive capped scoring, fixed thresholds, stable ordering, normalization, eager validation, and deterministic de-duplication are implemented.
- WP3: text/JSON CLI and explicit Plugin.execute(command, **kwargs) shim are implemented with plugin.yaml registration metadata.
- WP4: 12 unit/integration tests and a directly executable ACCEPTANCE.md entry point are implemented.
- WP5: README and ethics/AUTHORIZED_USE.md document use, scoring, evidence sensitivity, and Empire 5.x/6.x shim limits. Scanner output is archived.
- WP6 implementation checks are complete; the independently sequenced Role 5 OPSEC review remains the next pipeline action.

## Safety properties verified

- Runtime package contains no subprocess, shell, socket, HTTP client, dynamic code execution, Empire import, or task-forwarding path.
- Suggestions are static local records and are never executed.
- Network-free fixtures work without Empire or third-party dependencies.
- An allow state carries an explicit limitation; deny is described as advice rather than enforcement.
- Runtime analysis writes no file, cache, telemetry, or log through application code.

## Verification performed

Unit/integration command:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

Result: 12 tests passed.

Semgrep command:

    SEMGREP_SETTINGS_FILE=/tmp/empire-advisor-semgrep-settings.yml \
    SEMGREP_LOG_FILE=/tmp/empire-advisor-semgrep.log \
    SEMGREP_SEND_METRICS=off \
    semgrep scan --config scanners/semgrep.yml --disable-version-check \
    --metrics=off --no-git-ignore empire_advisor scripts tests

Result: Semgrep 1.176.0 scanned 7 targets with 3 local rules and reported 0 findings. The no-git-ignore option was necessary because this generated tree was untracked. The first bare invocation encountered a read-only home configuration path; the recorded successful invocation used explicit temporary paths. No installation or replacement occurred.

ast-grep command:

    ast-grep scan --rule scanners/ast-grep.yml empire_advisor scripts tests

Result: ast-grep 0.45.3 exited 0 with no findings. Full records are in scanner-output/semgrep.txt and scanner-output/ast-grep.txt.

## Deviations from the plan

- The source plan named separate config.py, engine.py, models.py, CLI, and adapter files; this layout was followed.
- ACCEPTANCE.md is a shell/Markdown polyglot as assumed. It preserves the checklist and delegates to scripts/acceptance.py with bytecode generation disabled.
- Static scanner rules were added under scanners/ so the controlled checks are reproducible without downloading community rule packs.

## Known gaps

No required Role 4 feature is unimplemented. Live registration into an actual Empire checkout is intentionally unverified because none was supplied; the README accurately scopes the explicit offline shim. Marketplace publishing and a transparent global pre-task hook remain out of scope. The mandatory Role 5 OPSEC artifact is not authored here to preserve role separation.
