# OPSEC Card — after-action

**Tool:** After-Action Report Generator  
**Version:** 1.0.0  
**Date:** 2026-09-03  
**Classification:** INTERNAL / OPERATOR USE

## Summary

The after-action report generator correlates red team engagement logs (JSON Lines, CSV) with operator decision records to produce two outputs: a client-facing professional report (Markdown + PDF/HTML) with automated PII/secret redaction, and an internal learning summary for operator retrospectives. The tool ingests heterogeneous log formats via pluggable adapters, joins events to decisions using configurable time windows and asset key matching, applies regex-based redaction rules, and renders structured Markdown reports with placeholder sections for manual operator completion. It operates offline without network dependencies and stores all data locally on the operator's workstation.

## Operator Risks

**Report mishandling (HIGH):**
- Client report leaked with insufficient redaction exposes techniques, customer network details, or operator identities
- Internal report shared externally reveals unredacted credentials, tool capabilities, or engagement metadata
- Version control commits containing real engagement logs or reports in public/shared repositories

**Redaction bypass (MEDIUM):**
- Default rules miss context-specific secrets (project codenames, client-specific domains, alternate API key formats)
- Base64-encoded secrets in logs may pass through if not explicitly configured in redaction rules
- Over-reliance on automated redaction without manual review before client delivery

**Correlation leakage (LOW):**
- Wide time windows or verbose logging create timeline patterns that reveal operator dwell time and C2 infrastructure locations
- Asset key formats (IP addresses vs. hostnames) may fingerprint internal network topology

**Metadata exposure (LOW):**
- PDF metadata (Pandoc version, creation timestamps) reveals toolchain and engagement end date
- Correlation configuration (window size) tuned to specific engagement characteristics may be defensively profiled

## Artifacts Left Behind

**On operator workstation:**
- Generated reports in `output/` directory (Markdown, PDF, HTML)
- Per-engagement redaction configs in `config.local.yaml` (may contain client-specific patterns revealing threat model)
- Correlation engine logs with asset key and timestamp data
- Python cache files (`__pycache__/`) with bytecode metadata
- Shell history containing file paths and engagement names

**In reports (by design):**
- Client report: Correlated timeline with decision rationale (operator commentary), sanitized log excerpts, placeholder Detection Recommendations
- Internal report: Full log data, unredacted fields, operator retrospective notes, TTP references

**Network (none):**
- Tool operates entirely offline; no network calls during report generation
- Exception: PDF generation via Pandoc may trigger OS-level font/template lookups (local filesystem only)

**Filesystem metadata:**
- File creation/modification timestamps on reports reveal engagement closeout timeline
- Directory structure (`testdata/fixture_engagement/` vs. real engagement directories) distinguishes testing from production use

## Safer Operating Guidance

**Before first use:**
1. **Environment isolation:** Run in dedicated VM or encrypted volume; never on shared/corporate workstation
2. **Validate .gitignore:** Confirm `output/`, `logs_*/`, `config.local.yaml` are excluded from version control
3. **Test redaction:** Run `make reports` on fixture data and verify `sk-test...` is replaced with `[REDACTED_API_KEY]`

**Per-engagement workflow:**
1. **Stage logs in temporary directory:** Never use production C2 logs directly; copy to isolated staging area
2. **Customize redaction config:** `cp config/redaction_rules.yaml config.local.yaml` and add client-specific patterns (domains, project names)
3. **Dry-run first:** `--dry-run` validates correlation without writing reports
4. **Review internal report first:** Check correlation quality before investing time in client report completion
5. **Manual redaction check:** `grep -E 'sk-|api[_-]?key|192\.168\.|internal\.corp' output/client_report.md` before PDF generation
6. **Strip PDF metadata:** `exiftool -all= output/client_report.pdf` before delivery
7. **Secure deletion:** `shred -u output/*` after client delivery and archival

**Default safety:**
- Client report generation requires valid redaction config (hard error if missing)
- Internal report warns if content matches redaction patterns (visual reminder to operator)
- Existing reports prompt for overwrite confirmation unless `--force` flag set
- No network calls; offline-capable operation prevents log exfiltration via API

**Sequencing:**
- Always generate internal report before client report (validates correlation before manual effort)
- Complete placeholder sections in Markdown before PDF generation (Markdown is diff-able and version-controllable)
- Archive internal reports separately from client deliverables with stricter access controls

## Detection Recommendations

**For client blue teams defending against techniques documented in after-action reports:**

1. **Correlation timeline patterns:**
   - Monitor for sequences matching the engagement timeline (e.g., initial access → privilege escalation → lateral movement → exfiltration within documented time windows)
   - Alert on identical TTP combinations (same tools, same privilege escalation paths) used in the report's timeline sections
   - Detection query example (Splunk): `index=security | transaction asset_key startswith="authentication_success" endswith="data_exfiltration" maxspan=1h | where event_count >= 5`

2. **Report-referenced artifacts:**
   - Search for tools, file paths, process names, or network indicators mentioned in the "Engagement Timeline" or "Detection Recommendations" sections
   - Example: If report documents `mimikatz.exe` usage, alert on `process_name=mimikatz.exe OR parent_process=*\\mimikatz.exe OR cmdline=*sekurlsa*`
   - Cross-reference asset keys (hostnames/IPs) in the timeline with current high-value asset inventory

3. **Operator decision signatures:**
   - Extract rationale patterns from operator decision log (e.g., "cached credentials", "scheduled task persistence", "service account compromise")
   - Build behavioral analytics around decision points: authentication anomalies followed by lateral movement within correlation time windows
   - Example (Elastic): `event.category:authentication AND event.outcome:success AND user.name:*_svc | correlate by host.name within 5m with event.category:process AND process.name:(powershell.exe OR cmd.exe)`

4. **Redaction pattern reverse-engineering:**
   - If client report contains `[REDACTED_IP]` placeholders, inventory private IP ranges accessed during engagement timeframe
   - Redacted email/API key patterns indicate credential-based access; review authentication logs for service account or admin credential usage

5. **Report metadata forensics:**
   - PDF creation timestamp approximates engagement end date; review logs from that timeframe backward
   - Pandoc version in PDF metadata may indicate operator toolchain generation; cross-reference with other known red team infrastructure

6. **Report delivery channel monitoring:**
   - Track email/file transfer of PDF/Markdown files with "after-action" or "assessment" keywords
   - Alert on large Markdown files (>50KB) or PDFs with "Security Assessment" in title transferred to external domains

**Blue team implementation guidance:**
- Prioritize detections for high-confidence indicators (specific tool names, exact process paths) over generic patterns
- Combine report timeline with SIEM correlation rules to detect similar attack sequences in production
- Use Detection Recommendations section as threat hunting hypothesis generator, not authoritative detection rules (validate against environment before deployment)

## Residual Gaps

**What this review could NOT verify:**

1. **Redaction completeness at scale:**
   - Tested only on fixture data with ~15 log entries and 6 decisions
   - Real engagements with 10,000+ log lines may expose edge cases in regex performance or pattern coverage
   - Base64-encoded secrets detection is naive (checks decoded content for keywords); sophisticated encoding may bypass

2. **Correlation accuracy under real-world conditions:**
   - Fixture data uses consistent UTC timestamps and clean asset keys
   - Production logs with mixed time zones, hostname vs. IP inconsistencies, or clock drift were not tested
   - No validation of correlation behavior with >1000 log entries (potential memory/performance issues)

3. **Pandoc security:**
   - PDF generation delegates to external Pandoc binary (subprocess call)
   - No validation of Pandoc version or known vulnerabilities
   - Malicious log content (LaTeX injection via log fields) not tested for Pandoc exploitation

4. **Multi-adapter field mapping robustness:**
   - Only tested JSONLines and CSV adapters with well-formed data
   - Malformed CSV (unquoted delimiters, embedded newlines) may crash adapter
   - No testing of log files exceeding memory limits (100MB+ corpora)

5. **Operator workflow compliance:**
   - Cannot enforce secure deletion of staging files post-delivery
   - No mechanism to prevent committing `output/` or real logs to version control (relies on .gitignore + operator discipline)
   - Internal report warning for redaction patterns is passive (no hard block on sharing)

6. **Detection Recommendations quality:**
   - Recommendations are manually authored by operators (tool provides placeholders only)
   - No validation that Detection Recommendations section is populated before client delivery
   - Quality depends entirely on operator expertise; no automated TTP extraction or MITRE ATT&CK mapping

**Recommended future validation:**
- Stress test with 100,000+ log entries from diverse sources (Windows Event Logs, Sysmon, network captures)
- Red team exercise: attempt to bypass redaction with novel encoding schemes (rot13, hex, custom base-N)
- Blue team exercise: build detections from fixture engagement report and measure false positive rate in production SIEM
