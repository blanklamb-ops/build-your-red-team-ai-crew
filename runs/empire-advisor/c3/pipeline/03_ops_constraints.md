# Operational Constraints — empire-advisor

## Runtime environment assumptions

- The acceptance baseline is CPython 3.10+ on Linux, launched by an unprivileged user from the repository root. The implementation must remain portable standard-library Python and must not require root, Empire, a database, package installation, or environment variables.
- The primary environment is offline/air-gapped. Runtime network access is prohibited; citation URLs are reference metadata and are never fetched. All rules, suggestions, schemas, and fixtures are local and read-only during analysis.
- Input arrives as an explicit command string or a JSON fixture file. The tool is a pre-submit advisor: neither the CLI nor adapter is placed on an agent host, and neither is authorized to dispatch tasking.
- Paths must resolve predictably from the package/repository defaults while allowing explicit test paths. No writes occur during ordinary analysis; scanner archives are controlled build-time artifacts only.
- Locale, wall clock, host identity, randomness, and process environment must not alter an advisory. Unicode input is accepted as text; empty or oversized input must fail clearly rather than producing a misleading `allow`.

## Secrets and evidence handling

Never commit or echo real credentials, tokens, cookies, staging keys, listener profiles, agent/session IDs, customer domains, internal IP addresses, usernames, hostnames, command history, raw C2 transcripts, or engagement identifiers. Fixtures must use reserved examples such as `example.invalid`, documentation address ranges, and synthetic agent names.

The command itself is sensitive evidence. JSON/text output necessarily repeats it for operator verification, so operators must redirect output only into engagement-approved storage. The application must not create logs, telemetry, caches, histories, or reports automatically. It must not inspect arbitrary Empire logs or configuration. Scanner archives may contain repository-relative filenames but must not contain environment dumps.

Before publication, remove any operator-created outputs and rerun a secret/personal-data review. Python cache files and test byproducts are not deliverables.

## Operator workflow

1. Confirm written authorization and work from an engagement-controlled workstation, not an implant.
2. Review the versioned `rules.yaml` and `kb.yaml`; their contents are the policy being applied.
3. Analyze a pending command with the CLI, or call the adapter explicitly before the separate Empire submission step.
4. Read the advisory state, score, every matched rationale/evidence item, and cited alternatives.
5. The human decides whether to abandon, modify, or separately submit a command through Empire. Copying a suggestion requires normal engagement review; the advisor performs no confirmation or execution step.
6. Store output as engagement evidence only when required, then handle it under the engagement retention policy.

The README must demonstrate shell-safe invocation through an argument vector and through fixtures. It must warn that terminal shell parsing happens before Python receives `--command`; operators should prefer a fixture for complex quoting.

## Safety defaults

- Analysis is inherently dry-run. There is no execute, shell, subprocess, socket, HTTP, Empire client, dynamic import, `eval`, or `exec` pathway.
- `allow` means no configured heuristic matched; it does not mean safe, authorized, or undetectable. `warn` and `deny` are visible advisory states. `deny` must never be described as enforcement.
- Unknown commands are analyzed and may return `allow` with a conspicuous limitation statement. Invalid configuration, unknown severity, malformed regex, duplicate IDs, and dangling suggestion references fail closed with a nonzero error.
- High-risk/destructive patterns receive sufficient fixed weight to reach `deny`; suspicious noisy discovery patterns default to `warn`. No dangerous match may be silently ignored.
- Suggestions are static, benign/read-only templates containing no encoded payload, bypass, credential material, persistence, destructive action, or executable chaining. Each requires a title and HTTP(S) citation.
- Input has a documented maximum length to bound regex work. Patterns must avoid constructs likely to cause catastrophic backtracking.
- No allowlist is needed because the product never executes. Rule suppressions and user-defined score overrides are excluded to preserve deterministic evidence.

## Degradation modes

- **No network / no Empire:** Full CLI and fixture analysis continue normally; this is the supported baseline.
- **Empire API drift or missing Empire imports:** The standalone adapter remains importable. README must state that it is an explicit wrapper and not a transparently registered universal pre-task hook.
- **Missing or invalid rule/KB file:** Abort before advisory output, identify the file/field, and return nonzero. Never fall back to empty rules.
- **Unknown fixture schema or invalid JSON:** Reject the whole batch; do not skip records silently.
- **One command has no matches:** Return deterministic `allow`, score 0, empty match/suggestion lists, and a limitation summary.
- **Several rules map to one suggestion:** De-duplicate by suggestion ID while retaining stable KB order.
- **Scanner unavailable:** Do not install it. Archive the checked command, UTC run time, and truthful unavailable status; acceptance verifies the record, not a fabricated clean result.
- **Broken output pipe:** Exit normally according to CLI conventions without running cleanup that could affect external systems.

## Detection-relevant artifacts for OPSEC review

The reviewer must document that actual commands can appear in terminal scrollback, redirected stdout/stderr, shell history (from invocation), CI logs, and operator screen recordings. Python imports may create `__pycache__` unless bytecode writing is disabled. Tool filenames, the `empire-advisor` process command line, and access to `rules.yaml`/`kb.yaml` can be visible to host telemetry. If integrated around Empire, the separate eventual task remains visible in Empire audit/task records and endpoint/process telemetry; an advisor score does not remove those signals.

## Mandatory plan deltas for the Architect

- **WP1:** Use only synthetic fixtures and add schema/version fields plus a maximum command size.
- **WP1:** Ensure every suggestion is a concrete read-only template with citation title and HTTP(S) URL; no secrets, payloads, bypasses, or destructive syntax.
- **WP2:** Validate all data eagerly, cap scores at 100, use stable file order, de-duplicate suggestions deterministically, and fail closed on configuration errors.
- **WP2:** Add a clear limitation summary to zero-hit output and enough weight for high-risk fixtures to reach `warn` or `deny`.
- **WP3:** Keep runtime free of I/O beyond explicit local reads and stdout/stderr. The adapter may serialize only; it may not import Empire or dispatch a task.
- **WP3:** Enforce mutually exclusive command/fixture inputs, a command-length limit, and nonzero exits for invalid input/configuration.
- **WP4:** Add negative tests for empty/oversized input, malformed config, duplicate/dangling IDs, batch schema failures, and absence of execution/network primitives.
- **WP4:** Run tests with bytecode disabled where practical and verify stable byte-for-byte JSON for repeated input.
- **WP5:** Document command sensitivity, shell-history/quoting risk, `allow` limitations, supported Python baseline, Empire shim boundaries, and data-retention responsibility.
- **WP5:** Scanner records must distinguish `pass`, `findings`, `error`, and `not-installed`; never claim “clean” when a scanner did not run.
- **WP6:** Remove cache/byproduct files, inspect fixtures and archives for sensitive data, and ensure OPSEC Detection Recommendations address host command-line, file-access, Empire task/audit, and endpoint/process telemetry.
