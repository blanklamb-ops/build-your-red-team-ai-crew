# Operational Constraints — After-Action Collector

## Runtime environment

- Target Python 3.11+ on Linux/macOS with no elevated privileges. The tool must use the standard library, local files, and no network access.
- Treat the working directory as untrusted. Resolve input/output paths explicitly; do not discover or ingest arbitrary neighboring files.
- Read only the named fixture schema files (`engagement.json`, `events.jsonl`, `events.csv`, `decisions.csv`). Reject an input/output directory collision.
- Use UTC for comparison and rendering. Accept timezone-aware ISO 8601; interpret naive timestamps as UTC only with a source/row warning.
- Output is a new or existing operator-selected directory. Individual report writes must use a same-directory temporary file followed by atomic replacement, with restrictive `0600` report permissions where supported.

## Secrets and evidence handling

- Never commit real client logs, credentials, API keys, tokens, cookies, private keys, personal email addresses, or generated real-engagement reports. Fixtures must be synthetic and conspicuously labeled.
- Treat source files and the internal report as sensitive evidence. Internal output intentionally may retain more detail; it must never be assumed sanitized or client-safe.
- The redaction boundary is before construction/persistence of **both** client Markdown and HTML. Do not create an unredacted temporary client artifact. Use configured rules plus safe defaults for bearer tokens, common key/value secrets, private-key blocks, email addresses, and the fixture canary.
- Validation/warning text may include filenames and row numbers but must not echo record values. Exceptions shown to users must avoid dumping input payloads.
- Do not claim that regex redaction guarantees anonymity. Operators must review the draft before delivery and apply their engagement evidence-retention policy.

## Operator workflow

1. Place exported, offline evidence in a dedicated engagement directory following the documented schema; keep originals under the engagement evidence controls.
2. Review `engagement.json`, the selected correlation window, and `config/redaction_rules.json`.
3. Render to a dedicated output directory with `python3 -m after_action.cli …` or use `make fixture` for synthetic verification.
4. Review stderr warnings and both reports. Confirm correlation deltas and false/missed associations. Never send the internal report to a client.
5. Search client outputs for engagement-specific sensitive indicators, then transfer only through the approved client channel.
6. Run `make scanners` only in the controlled post-run environment; archive its honest output. Run `make acceptance` for handoff.

## Safety defaults

- The collector is read-only with respect to evidence; no dry-run is needed because its only mutation is report creation. Require explicit `--output` for direct CLI use. Refuse input and output resolving to the same directory.
- Default to a conservative, inclusive ±10-minute window and exact case-folded, trailing-dot-trimmed asset identity. No fuzzy matching, DNS, address resolution, or inferred aliases.
- Reject non-positive/non-finite windows, missing required files, invalid config, invalid regexes, and output paths that are files. Continue past malformed individual records with sanitized warnings; fail if no valid events or decisions remain.
- Keep correlation explainable: each link includes asset match, configured window, signed/absolute delta, event provenance, and decision provenance. Sort deterministically.
- Escape all dynamic values for HTML and neutralize dynamic Markdown table delimiters/newlines. Keep generated HTML free of scripts and remote resources.
- Redaction replacements are fixed labels, not captured secret material. Apply rules iteratively in declared order to every dynamic client string, including metadata and recommendation text.

## Degradation modes

- **Offline:** Normal operation is unchanged; there are no remote dependencies.
- **One malformed row:** Skip it, issue a filename/row warning, and render remaining valid data.
- **Missing optional field:** Substitute “Not provided,” warn, and retain the record when timestamp and asset are usable.
- **Invalid timestamp or missing asset:** Retain only as an unlinked internal record when safely representable; never fabricate a correlation. If normalization cannot form a valid record, skip with a warning.
- **No correlations:** Render valid reports stating no links were found; this is not a crash. Acceptance fixtures separately require five links.
- **Render/write failure:** Return nonzero, leave no partial target file, and preserve prior complete reports through atomic replacement.
- **Scanner unavailable:** Do not install or substitute it. Archive a nonempty status file with UTC timestamp, command, and `NOT_AVAILABLE`; acceptance verifies archival, not a false clean result.

## Plan deltas the Architect must respect

- **WP1:** Add sanitized structured warnings; strict required-key handling; UTC normalization; provenance; bounded input file sizes/record counts documented as operator safeguards.
- **WP2:** Preserve unlinked records and emit signed plus absolute deltas; deterministic tie/order behavior; no fuzzy identity.
- **WP3:** Redact structured dynamic content before either client renderer; HTML-escape after redaction; sanitize Markdown layout; include an explicit “draft/review required” label.
- **WP4:** Require `--output`; refuse resolved input/output equality; atomic `0600` writes; fixture includes a canary, email, bearer token, key/value secret, malformed row, and optional missing field without printing their values in warnings.
- **WP5:** Add tests for no-correlation, boundary-time, naive-time, malformed row, invalid regex/window, HTML injection, Markdown layout, secret absence from both client formats, and atomic write behavior. Scanner archives must distinguish executed results from absence.
- **WP6:** Document report names/locations, console warning traces, output timestamps/permissions, scanner commands/logs, and evidence-access patterns as detection-relevant artifacts. Explain how misaddressed email, shared-drive permissions, internal/client report confusion, retained temp files, or unmanaged copies become OPSEC failures. Provide Detection Recommendations for monitoring report creation, access/transfer, and secret-pattern findings.
