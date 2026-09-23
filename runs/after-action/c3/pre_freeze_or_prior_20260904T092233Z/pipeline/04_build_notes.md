# Build Notes — after-action

## Delivered

- Standard-library Python 3.10+ package with bounded JSON Lines and CSV event adapters, a JSON Lines decision adapter, generic record warnings, timezone validation, and deterministic normalization.
- Inclusive configurable time-window correlation on exact normalized asset keys. The fixture produces six linked items (three from each event adapter).
- Validation-only CLI plus report build CLI with explicit paths, input symlink/output nesting rejection, fixed output names, narrow `--force`, `0700` directories, `0600` files, staged writes, and handled-failure rollback of the three-file report set.
- Ordered configurable regex redaction applied to the complete structured client context before Markdown/HTML rendering; the HTML renderer escapes dynamic content. The planted fixture email and secret are absent from both client artifacts and intentionally retained in the internal evidence report.
- Client Markdown and self-contained HTML with executive summary, correlated timeline, draft finding placeholders, Detection Recommendations, and handling note. Internal Markdown includes successes, failures, tool gaps, reusable TTP references, counts, and detailed timeline.
- Synthetic fixture pack, seven `unittest` tests, executable `ACCEPTANCE.md`, Make targets, safe configuration sample, authorized-use notice, README/operator workflow, local scanner rules, and archived scanner results.

## Verification performed

- `python3 -m compileall -q after_action tests` — passed.
- `python3 -m unittest discover -s tests -v` — 7 tests passed. Coverage includes both adapters, six links, redaction in both client formats, internal-detail retention, HTML escaping, restrictive modes, deterministic force-rerender, refusal to overwrite, nested output rejection, symlink and oversized-input rejection, inclusive/nearest correlation, and warnings that do not echo a malformed secret-bearing record.
- `make reports` — emitted `build/fixture_reports/client_report.md`, `client_report.html`, and `internal_learning.md`; machine-readable summary reported 6 events, 6 decisions, 6 linked, 0 unlinked, and 2 recoverable warnings.
- `./scripts/run_scanners.sh` — final Semgrep 1.176.0 scan completed on 7 Python targets with 0 findings and exit 0; ast-grep 0.45.3 completed with 0 findings and exit 0. Results are archived in `scanner_outputs/semgrep.txt` and `scanner_outputs/ast-grep.txt`.

## Plan and ops deltas

- Implemented the Ops Advisor's pre-architecture additions: `validate`, strict filename/path checks, size limits, generic warnings, staged set writes with rollback, machine-readable counts, and offline scanner settings.
- The initial scanner environment inherited a read-only Semgrep settings path. The wrapper now scopes Semgrep settings/cache to `scanner_outputs/`, disables metrics/version checks, uses only repository-local rules, and applies bounded timeouts. No scanner was installed or replaced.
- Scanner output paths are absolute because the scanners received explicit targets; this improves reproduction but can disclose analyst workstation directory structure if archives are shared.
- Serena was not available in the provided tool environment, so it was not used.

## Known gaps and boundaries

- Regex redaction cannot guarantee removal of contextual, encoded, split, or novel secrets/PII; manual review remains mandatory.
- Exact asset normalization does not resolve IP/FQDN/hostname aliases or clock skew. This is an explicit scope boundary to avoid misleading fuzzy joins.
- Atomic replacement and rollback cover handled process errors, but no cross-process output lock is provided; operators should not run concurrent builds into one directory.
- File permission semantics depend on the host filesystem. The tool does not encrypt, transfer, retain, or destroy evidence.
- Finding content and severity remain human-validated draft inputs. No PDF renderer, live collection, remote API, or automated operator grading is included by design.

## How to run

```sh
make validate
make reports
make test
make scan
make acceptance
```

`make acceptance` is expected to pass after Role 5 writes the identical root and pipeline OPSEC cards. Scanner reruns overwrite only the two fixed text archives and local Semgrep runtime metadata; review their exit statuses and findings before handoff.
