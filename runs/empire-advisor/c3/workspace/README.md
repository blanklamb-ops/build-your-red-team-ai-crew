# empire-advisor

empire-advisor is an offline, advisory-only pre-submit command scorer for authorized Empire-like labs. It evaluates command **text**, explains deterministic heuristic matches, and presents concrete alternatives from a local cited knowledge base. It never runs the original command, never runs a suggestion, and has no C2 or network client.

## Authorized use

This tool is for **authorized security testing, research, and education only**. Use it only on systems and identities you are contractually or legally authorized to test. An advisory does not establish authorization, safety, stealth, or EDR bypass. See [ethics/AUTHORIZED_USE.md](ethics/AUTHORIZED_USE.md).

## Requirements

- CPython 3.10 or later
- Linux, macOS, or Windows with a Python launcher
- No third-party packages, network, database, live Empire server, or elevated privileges

Run from the repository root. The program reads only rules.yaml, kb.yaml, and any explicitly supplied fixture. It writes no logs or telemetry.

## Quick start

Analyze a single synthetic command and render operator-oriented text:

    PYTHONDONTWRITEBYTECODE=1 python3 -m empire_advisor.cli \
      --command 'whoami.exe /all' --format text

Analyze all offline fixtures as JSON:

    PYTHONDONTWRITEBYTECODE=1 python3 -m empire_advisor.cli \
      --fixture fixtures/commands.json --format json

Run unit tests and the executable acceptance checklist:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
    ./ACCEPTANCE.md

The shell parses --command before Python sees it. A literal command may also enter shell history and terminal/CI logs. Prefer a synthetic fixture for complicated quoting, and put any real engagement output only in approved evidence storage.

## Operator workflow

1. Confirm written scope and review the versioned rules.yaml and kb.yaml policy.
2. Analyze a pending command on an engagement-controlled operator workstation.
3. Read the score, advisory state, matched evidence/rationale, and cited templates.
4. Decide as a human whether to abandon, edit, or separately submit a command through the normal authorized workflow.

There is deliberately no “continue,” forwarding, subprocess, shell, HTTP, or Empire-task call. The output field execution_performed is always false. A deny result is a strong recommendation, not technical enforcement. An allow result only means no configured pattern matched.

## Deterministic policy

rules.yaml uses JSON syntax, which is a YAML 1.2-compatible subset and can be loaded with Python’s standard json module. The fixed file order is authoritative. Each rule contains:

- id: stable unique identifier
- pattern: case-insensitive regular expression
- severity: low, medium, high, or critical
- weight: integer from 1 to 100
- rationale: operator-readable explanation
- suggestion_ids: one or more references into kb.yaml

Matching weights are added and capped at 100. The shipped thresholds are allow below 20, warn from 20 through 59, and deny at 60 or above. All matching rules are returned in file order. Suggestions are de-duplicated and returned in KB order. Command whitespace is normalized; time, host, locale, randomness, and environment do not affect results.

Configuration is validated before analysis. Missing files, malformed JSON/YAML, invalid regexes, duplicate IDs, unknown severities, invalid thresholds, and dangling KB references terminate with a nonzero status instead of falling back to empty policy. Empty commands and normalized commands longer than 4096 characters are rejected.

The score estimates relative operational noise according to this small transparent policy. It is not a probability, product signature database, or guarantee of detection/evasion.

## Local knowledge base

kb.yaml contains static, read-only alternatives with a title, operator-edited template, rationale, and public documentation citation. Angle-bracket values are placeholders and must be replaced only after scope review. The advisor does not generate payloads or fetch citations. Suggestions deliberately avoid credential access, persistence, destructive action, obfuscation, and security-control modification.

## Empire compatibility and shim limits

The supported acceptance path is an **offline shim**, not a bundled Empire plugin installation. It mirrors the documented Empire 5 and Empire 6 plugin execution shape: a Plugin class with options and execute(command, **kwargs), where command is a validated mapping. Modern Empire documents plugin execution through its v2 API and execute return values:

- [Empire REST API overview](https://github.com/BC-SECURITY/empire-docs/blob/main/restful-api/README.md)
- [Empire plugin execution documentation](https://bc-security.gitbook.io/empire-wiki/plugins/development/execution)
- [Empire hooks and filters](https://bc-security.gitbook.io/empire-wiki/plugins/development/hooks-and-filters)

Load and call the shim offline:

    from empire_advisor.empire_plugin import Plugin

    plugin = Plugin()
    advisory_json = plugin.execute({
        "Command": "whoami.exe /all",
        "Source": "operator-ui"
    })

plugin.yaml records the local registration metadata and entry point. An operator UI can call this adapter as an explicit pre-submit gate, display its JSON, then let the operator decide whether to use a separate Empire submission path.

Important limits:

- The shim has been designed against the documented Empire 5.x/6.x execute shape but has no pinned live Empire dependency and was not registered into a supplied Empire checkout.
- It is not a transparent universal hook. Empire’s documented hooks include after-tasking and result hooks, but no universal before-tasking hook. Integration therefore requires the client/operator workflow to call this adapter before submission.
- It returns a JSON string and ignores Empire context keyword arguments. It does not import Empire, mutate tasks, deny server-side API requests, or forward commands.
- Marketplace packaging, Starkiller UI changes, and live-version validation are outside this offline deliverable.

## Repository map

- empire_advisor/: immutable models, strict configuration loader, scoring engine, CLI, and adapter
- rules.yaml: 15 transparent heuristics
- kb.yaml: cited static alternatives
- fixtures/commands.json: synthetic offline transcript
- tests/: unit/integration tests including failure modes and no-dispatch checks
- scanner-output/: controlled post-build scanner run records
- pipeline/: frozen sequential research/build/review artifacts
- OPSEC_CARD.md: operator and defender handoff

## Scanner records

Generation does not install or replace static-analysis tools. The build checks for existing semgrep and ast-grep executables, runs those found, and archives exact status in scanner-output/. A not-installed status is not a clean scan; it truthfully means the corresponding scanner was unavailable. See pipeline/04_build_notes.md for reproducible commands.

## Data handling

Commands can reveal targets, identities, and intent. The CLI repeats analyzed text so the operator can verify it. Do not commit real commands, tokens, agent IDs, customer names, internal addresses, C2 transcripts, or generated evidence. The provided fixtures are synthetic. Remove Python caches and any operator-created output before publication.
