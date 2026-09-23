+# OPSEC Card — after-action

## 1. Summary

`after-action` is an offline closeout utility for authorized engagements. It reads local JSON Lines and CSV event records plus a JSON Lines operator-decision log, correlates records by an exact normalized asset key and a configurable time window, and creates redacted Markdown/HTML client drafts alongside a more detailed internal learning report. It does not collect from remote systems or transmit reports; operators remain responsible for authorization, factual review, classification, retention, and approved delivery.

## 2. Operator risks

- The input pack, decision rationales, internal report, configuration, terminal capture, and scanner archives can reveal asset identities, timelines, operator judgment, reusable techniques, coverage gaps, personal data, or credentials. The internal report is deliberately more sensitive than the client drafts.
- Pattern-based redaction can miss contextual identifiers, unfamiliar token formats, encoded or fragmented secrets, image content, and sensitive relationships between otherwise harmless fields. A successful render is not clearance to release.
- Report mishandling is itself an OPSEC failure: selecting the internal report instead of the client draft, sending to the wrong recipient, attaching it to an unapproved ticket, syncing it to a personal/cloud folder, retaining it beyond the engagement period, or publishing scanner/terminal logs can disclose client and operator information.
- Incorrect clocks, asset aliases, or an overly broad window can create plausible but false correlations. A linked decision is analytical context, not proof of causation.
- Command lines and shell history expose evidence/output paths. File names, timestamps, ownership, backups, indexing, endpoint telemetry, and deleted-file recovery may show that reporting occurred even when content is later removed.
- Opening raw CSV in spreadsheet software can activate formula-prefixed cells. Opening the HTML draft in a managed browser can add history, recent-file, cache, download, extension, or endpoint artifacts even though dynamic report text is HTML-escaped.
- Concurrent builds into one output directory are unsupported and may race. Permission guarantees can be weakened by network filesystems, inherited ACLs, backup agents, or synchronization clients.

## 3. Artifacts left behind

- **Inputs:** the explicit engagement directory and fixed names `engagement.json`, `events.jsonl`, `events.csv`, and `decisions.jsonl`; copied configuration files may contain engagement-specific redaction patterns.
- **Outputs:** `client_report.md`, `client_report.html`, and `internal_learning.md`. The default fixture workflow uses `build/fixture_reports/`. Output directories are requested as mode `0700` and files as `0600` where the filesystem honors POSIX modes.
- **Transient filesystem artifacts:** same-directory hidden files shaped like `.<report-name>.<random>.tmp` and `.<report-name>.<random>.backup` can exist briefly; handled failures clean or restore them, but abrupt power loss or process termination may leave recoverable data or metadata. Python may create `__pycache__/` bytecode.
- **Scanner artifacts:** `scanner_outputs/semgrep.txt`, `scanner_outputs/ast-grep.txt`, local Semgrep settings/cache/log metadata, scanner versions, timestamps, status, and absolute workspace paths. Findings may quote scanned source in other rule sets.
- **Host telemetry:** Python, Semgrep, ast-grep, shell, `make`, and file-operation process events; command history; terminal scrollback/capture; file create/write/rename/chmod events; audit/EDR records; recent-file lists; filesystem journal, snapshots, backups, search indexes, and deleted-file remnants.
- **Registry/network/browser/mail:** the tool creates no registry entries and initiates no network traffic. Browser artifacts arise only if a person opens the HTML report. Mail, collaboration, cloud-sync, DLP, proxy, and ticketing records arise only through operator handling or approved transfer, not tool automation.

## 4. Safer operating guidance

- Work only on an approved, access-controlled analysis host as an unprivileged account. Keep the evidence copy and output outside synced folders, shared home directories, web roots, and the source repository.
- Review the engagement's authorization, classification, approved recipients, transfer method, and retention/destruction requirements before copying evidence. Keep source evidence immutable or separately integrity-protected.
- Review the regex configuration first, then run `validate`. Resolve fatal errors and inspect warning/link counts without placing secrets on the command line. Build into a new directory outside the input tree; use `--force` only after confirming the three exact destination files.
- Compare linked and unlinked records against source evidence, clock assumptions, asset aliases, and the rules of engagement. Treat every finding and decision relationship as a draft requiring human validation.
- Search both client files for known test values and likely identifiers, then perform a contextual privacy/secret review. Keep `internal_learning.md` under evidence-level controls and never bundle it automatically with client artifacts.
- Transfer only the specifically approved client files through the engagement-approved encrypted channel, verify recipients out of band when required, and record the handoff through the approved process.
- Apply the agreed retention schedule to inputs, reports, temporary remnants, terminal capture, scanner archives, backups, and copies. Do not claim secure deletion on storage where snapshots, journaling, or wear-leveling prevent verification.

## 5. Detection Recommendations

- **Endpoint file telemetry:** alert or hunt for creation, rename, or transfer of `client_report.md`, `client_report.html`, or `internal_learning.md` outside approved assessment/evidence directories. Include actor, host, parent process, destination classification, and subsequent archive/upload/email activity; suppress only documented test windows and approved paths.
- **Process-to-file correlation:** correlate `python -m after_action` or repository `make reports` execution with the three fixed output-file creations within several minutes. Use this as a data-handling signal, then verify the account, approved engagement window, output location, and expected file permissions rather than treating execution alone as malicious.
- **Sensitive-report egress:** configure DLP/content inspection for report headings such as “Internal Learning Summary,” “Detailed Correlated Timeline,” or “Reusable TTP References,” especially when documents move to personal mail, public links, consumer cloud storage, removable media, or unapproved ticket systems. Route matches to privacy/security review; do not index full report bodies in broadly accessible alert records.
- **Permission and location drift:** monitor approved report directories for group/world-readable mode changes, permissive ACL inheritance, relocation into web roots or sync clients, and backup jobs with an unauthorized destination. Validate that client and internal artifacts have distinct handling labels and access groups.
- **Temporary and orphan cleanup:** hunt in approved work areas for hidden `.client_report.*.tmp`, `.internal_learning.*.tmp`, and `.*.backup` files that persist beyond a normal build interval. Persistence can indicate an interrupted render and should trigger controlled evidence review, not automatic deletion.
- **Tool assurance telemetry:** record nonzero exit statuses or missing archives for the controlled Semgrep/ast-grep step, unexpected scanner network attempts, and changes to redaction configuration. Baseline authorized hashes/locations where appropriate; investigate deviations as pipeline-integrity issues.
- **Handoff auditing:** reconcile approved report transfers with case/ticket identifiers, named recipients, and retention deadlines. Alert on duplicate sends, external sharing-link creation, forwarding, or access after closure while minimizing collection of the sensitive report content itself.

## 6. Residual gaps

This review used the synthetic fixture on the provided Linux workspace. It verified client-secret removal for the planted values, HTML escaping, restrictive POSIX modes, deterministic output, path/symlink safeguards, six linked fixture items, handled report-set rollback logic by inspection, and clean final Semgrep/ast-grep results. It did not validate real client data, non-POSIX filesystems or ACLs, full-disk encryption, backup/snapshot behavior, DLP/email/browser products, forced power-loss recovery, concurrent writers, or every possible regex bypass. Asset aliasing, clock-skew correction, comprehensive secret discovery, encrypted transfer, retention enforcement, and secure deletion remain outside the implemented scope. No blocking OPSEC defect was identified, but manual client-report review and environment-specific handling controls remain mandatory.

