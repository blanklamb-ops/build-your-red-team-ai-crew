# Operational Constraints — after-action

## Runtime environment

- Run as an unprivileged user on Python 3.10+ under Linux or macOS. The supported path is local, offline execution with the Python standard library; no service, daemon, browser, database, telemetry, DNS, or outbound network traffic.
- Input and output directories must be explicit CLI paths. Do not search home directories, mounted shares, or client networks. Read only the four allowlisted fixture-style filenames and accept only `.json`, `.jsonl`, and `.csv` inputs.
- Use UTC-aware timestamps internally while retaining explicit offsets in source-derived displays. Output ordering and content must be reproducible across locale/timezone settings.
- No administrator privileges are required. Report a clear error if a path is unreadable/unwritable or if Python is too old.

## Secrets and evidence handling

- Never commit real engagement logs, credentials, access/session tokens, private keys, client PII, raw reports, custom redaction rules containing client identifiers, or scanner output containing copied client data. Repository fixtures must be synthetic and conspicuously labeled.
- Treat the entire input pack, internal report, warning stream, temporary files, configuration, and scan archives as sensitive evidence. The internal report intentionally may retain more operational detail than the client report.
- Create output directories/files with user-only permissions where the OS supports them (`0700` directories, `0600` files). Use same-directory temporary files and atomic replacement; clean temporary files on handled failure.
- Redaction is defense in depth, not a guarantee. Validate every regex before ingest/render. Apply rules to the complete structured client context before producing either Markdown or HTML. Never write an unredacted intermediate client document.
- Operators must manually review the final client report for contextual PII, encoded/split secrets, scope accuracy, and correct audience before transfer. Follow engagement-specific retention, encryption, and approved-transfer requirements.

## Operator workflow

1. On an approved analysis host, place a copied evidence pack in a restricted local directory and verify the expected four filenames/schema.
2. Review a copied configuration and redaction expressions. Run `python -m after_action validate INPUT --config CONFIG`; resolve fatal errors and inspect record warnings.
3. Run `python -m after_action build INPUT --output OUTPUT --config CONFIG`. A new or empty output directory is the default; replacing existing report files requires explicit `--force`.
4. Inspect stderr warnings, linked/unlinked counts, and both client formats. Search for known planted/engagement secrets. Compare the more detailed internal report only on the restricted host.
5. Manually approve and transfer only client artifacts through the client-approved channel. Retain or destroy working evidence according to the rules of engagement.

`validate` is the dry-run: it parses configuration and inputs, performs correlation/redaction checks, and prints counts without creating report files.

## Safety defaults

- Offline and read-only toward inputs; no recursive discovery and no implicit current/home directory.
- Reject symlink input files and an output directory nested inside the input directory, preventing accidental overwrite or recursive evidence mixing.
- Require all four named input files. Record-level malformed data and missing optional fields degrade with warnings; missing required files/fields, invalid config/regex, naive timestamps, and write failures stop safely.
- Refuse to overwrite any existing report file unless `--force` is supplied. `--force` replaces only the three fixed, allowlisted report names; it never deletes a directory or unrelated file.
- Cap individual input files and record lengths to avoid accidental resource exhaustion; report the configured limit in an actionable error.
- Escape all dynamic HTML. Treat CSV cells beginning with spreadsheet formula characters as inert text; document that raw fixtures should not be opened in spreadsheet software without import safeguards.

## Degradation modes

- **Offline:** full functionality remains available. Scanner execution records `not found` if a controlled scanner is unavailable; it does not install or substitute anything.
- **Malformed individual record:** warn with filename/line and skip it. Never include raw record content in warnings because it may contain secrets. Continue if at least one valid event and decision remain.
- **Missing optional value:** warn and substitute `Unknown` in normalized data. Missing required timestamp/asset/action or decision/rationale skips the record.
- **No eligible correlation:** retain the event as unlinked and state that no nearby decision was found; do not invent rationale.
- **Invalid redaction configuration or report write:** fail closed before client publication; remove handled temporary artifacts. Existing reports remain untouched unless a complete replacement succeeds.
- **Scanner nonzero exit:** archive output and status, flag it in build notes, and do not alter source automatically.

## Detection-relevant artifacts for OPSEC review

The reviewer must cover local evidence filenames, fixed output report names, temporary-file naming, Python process/command history, stderr/terminal capture, filesystem metadata and backups, endpoint process/file telemetry, and scanner archives. The card must explain that misaddressing, over-retaining, syncing, emailing, or ticket-uploading a report can disclose asset identities, operator reasoning, techniques, gaps, and credentials, turning closeout handling into an OPSEC failure. No tool-generated network artifact is expected.

## Non-negotiable plan deltas

- **WP1:** add `validate`; fixed input filenames; path/symlink/output-nesting checks; file/record size bounds; machine-readable final counts.
- **WP2:** warnings identify source and line but never echo record values; distinguish required from optional fields.
- **WP3:** UTC-aware, inclusive window; normalized exact asset matching; deterministic nearest/input-order tie-break; unlinked events remain visible.
- **WP4:** validate rules before ingest, redact the entire client context, and abort before any client write on redaction failure.
- **WP5:** restrictive permissions, same-directory temporary files, atomic writes, HTML escaping, three fixed output names, and narrow `--force` behavior.
- **WP6:** test symlink rejection, nested output rejection, non-overwrite, malformed-row warnings without secret reflection, size bounds, deterministic builds, and secret absence from both client files.
- **WP7:** document validation-first workflow, correlation limitations, warnings, raw-CSV spreadsheet risk, manual client approval, internal/client sensitivity, and retention/transfer responsibilities.
- **WP8:** do not install/replace scanners; archives must record absence/nonzero status as well as findings and must only scan synthetic/source repository content.
- **WP9:** include all detection-relevant artifacts and report-mishandling scenarios above.
