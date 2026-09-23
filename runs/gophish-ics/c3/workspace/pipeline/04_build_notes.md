# Build Notes — gophish-ics

## Implemented

- A standard-library Python sidecar with strict JSON campaign parsing, recipient-specific RFC 5545 generation, UTC normalization, text escaping, UTF-8-aware 75-octet folding, CRLF output, stable campaign/recipient correlation, and structural validation.
- A fail-closed single-key configuration loader. The exact shipped `config/default.yaml` is false; only an explicitly passed alternate config can enable generation.
- SQLite RSVP event history plus deterministic current state keyed by `(campaign_id, recipient_id)`, accepting `accept`, `decline`, `tentative`, and `none`. Fixture seeding validates all events before one transaction. Reports include every state and total.
- CLI commands `generate`, `validate`, `record`, `seed`, and `report`. There is no network or send path. Generation refuses to overwrite output.
- Synthetic `.test` campaign/RSVP fixtures, canonical ethics notice, sidecar architecture and offline demo documentation, 13 standard-library tests, and executable `ACCEPTANCE.md`/`scripts/acceptance.sh` entry points.

## Plan and ops conformance

- WP1–WP7 are complete. WP8 acceptance execution follows the Role 5 OPSEC artifact because A8 requires that final file.
- Serena was not available in the provided tools and was not used.
- No scanner, dependency, service, or global package was installed or replaced.
- Test/demo artifacts use temporary directories; the shipped configuration is compared byte-for-byte before and after explicit-enable tests.

## Scanner execution

Controlled run timestamp: `2026-09-04T09:57:17Z`.

- Semgrep 1.176.0: run with a temporary local three-rule Python safety profile, network version checking disabled, and writable settings/log/cache isolated under `/tmp`. It scanned all six implementation modules and reported zero findings/errors. The environment's existing ignore policy excluded test files. Full output and the initial read-only-settings degradation are archived in `scans/semgrep.txt`.
- ast-grep 0.45.3: three AST searches across implementation and tests for `eval`, `exec`, and `subprocess(..., shell=True)` returned empty match sets. Output is archived in `scans/ast-grep.txt`.

Re-run the same commands shown verbatim in those archives. The temporary Semgrep rule file is intentionally not a shipped application dependency; use the controlled scanner policy chosen for the engagement when repeating post-run analysis.

## Deviations and residual gaps

- The plan anticipated both scanner scopes including tests. Semgrep's environment ignore policy excluded the five test/package-support paths despite `--no-git-ignore`; ast-grep did scan them. This is explicitly archived rather than altering the scanner configuration during the frozen run.
- The validator implements and tests the project's narrow RFC 5545 invitation profile; it is not a general-purpose iCalendar validator or proof of every client-specific MIME behavior.
- Live GoPhish attachment upload, mail delivery, inbound iTIP parsing, and a graphical dashboard remain intentionally out of scope. The documented handoff uses GoPhish's existing attachment/results interfaces.
- No required PROMPT feature is marked `NOT IMPLEMENTED`.

## Verification at role completion

`python3 -m unittest discover -s tests -v` passes 13 tests. Final `./ACCEPTANCE.md` execution is deferred only until Role 5 creates `OPSEC_CARD.md`, as required by the sequential pipeline.
