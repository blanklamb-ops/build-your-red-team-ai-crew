# OPSEC Card — `after-action`

## 1. Summary

The `after-action` tool generates post-engagement reports by correlating security testing logs with operator decisions. It produces both client-facing reports (redacted for external distribution) and internal learning reports (for operator improvement).

**Primary use case:** Structured closeout documentation for authorized penetration tests and red team engagements.

**Risk profile:** Medium — Reports contain sensitive attack methodology and may expose client vulnerabilities if mishandled.

## 2. Operator risks

### Information Disclosure

- **Incomplete redaction:** Automated redaction may miss client-specific secrets, custom identifiers, or obfuscated credentials. Always manually review client reports before distribution.

- **Report mishandling:** Client reports are confidential security documents. Unauthorized disclosure exposes vulnerability details and attack paths to potential adversaries.

- **Metadata leakage:** File metadata, timestamps, and system paths in reports may reveal operational details, tool versions, or operator identities.

### Operational Security

- **Log aggregation risk:** Consolidating logs from distributed systems creates a single high-value target. Secure the report generation environment.

- **Unencrypted storage:** Reports stored on operator workstations or file shares without encryption are vulnerable to compromise.

- **Cloud/email transmission:** Sending reports via unencrypted email or insecure cloud storage exposes sensitive assessment data in transit.

## 3. Artifacts left behind

### On Operator System

- **Generated reports:** `output/client_report.md`, `output/internal_report.md` contain full engagement details
- **Metadata files:** `output/metadata.json` includes timestamps, assessment periods, and statistics
- **Log files:** Original `testdata/` or custom log directories retain raw event and decision data
- **Python cache:** `__pycache__/` directories contain bytecode (minimal risk but identifiable)

### In Client Environment

- **None directly:** This tool processes logs offline. However, the original logs it ingests were created during the engagement and may exist on client systems if not properly cleaned up.

### In Shared Systems

- **Email attachments:** Client reports sent via email persist in mail servers and recipient inboxes
- **Cloud storage:** Reports uploaded to shared drives, Slack, or collaboration platforms create copies beyond operator control
- **Version control:** Accidentally committing reports to git repositories can expose them via history even after deletion

## 4. Safer operating guidance

### During Report Generation

1. **Isolated environment:** Run the tool on a dedicated, encrypted operator workstation—not on client systems or shared infrastructure.

2. **Verify redaction:** Always manually review `client_report.md` for client-specific secrets that automated patterns may miss:
   - Custom API endpoints and keys
   - Internal system names and identifiers
   - Proprietary technology references
   - Employee names and email addresses

3. **Validate log sources:** Ensure input logs contain only authorized engagement data. Do not mix test data with production client logs unless explicitly authorized.

4. **Test redaction rules:** Use the fixture engagement data to validate redaction patterns before processing real client logs.

### After Report Generation

1. **Encrypt reports:** Store client reports in encrypted containers (e.g., VeraCrypt, LUKS) or encrypted archives (GPG, 7-Zip with AES).

2. **Secure transmission:** Use encrypted channels for client delivery:
   - PGP/GPG-encrypted email attachments
   - Secure file transfer platforms with access controls
   - Password-protected encrypted archives (communicate password separately)

3. **Clean up artifacts:** After delivery and client acceptance:
   - Securely delete raw log files (`shred` or equivalent)
   - Archive reports according to retention policy
   - Remove temporary files and caches

4. **Access control:** Limit report access to authorized personnel only. Use role-based permissions on shared storage.

### Retention and Disposal

- **Retention policy:** Maintain reports only as long as required by contract, compliance, or legal obligations.
- **Secure deletion:** Use secure deletion tools (`shred -vfz -n 10`, BleachBit, DBAN) when disposing of reports.
- **Audit trail:** Log report generation, access, and transmission events for accountability.

## 5. Detection Recommendations

**Write from the operator's perspective as defender-side guidance suitable for a client report.**

Detecting post-engagement report generation activity is challenging because it typically occurs on the attacker's infrastructure, not the client environment. However, organizations can implement controls to detect **report mishandling** and **related log exfiltration** that feeds report generation:

### Log Exfiltration Detection

- **Unusual log access patterns:** Monitor for bulk access to security logs, authentication logs, or SIEM data by accounts not typically responsible for log analysis. Alert on log file downloads, especially during or after suspected security incidents.

- **Data staging and compression:** Detect large file compression or archiving operations (`.tar`, `.zip`, `.7z`) on log directories. Attackers often consolidate logs before exfiltration.

- **Outbound data transfers:** Monitor for large outbound data transfers from log servers or administrative workstations, especially to external IPs or cloud storage services. Correlate with authorized personnel activity.

### Report Generation Indicators (Operator Systems)

While these occur on attacker infrastructure, defensive teams conducting authorized testing should watch their own environments:

- **Python execution patterns:** Monitor for execution of custom Python scripts processing log files (process name, command-line arguments including paths to log directories).

- **File system monitoring:** Track creation of Markdown files (`.md`) or PDFs in user directories, especially with names like `client_report`, `internal_report`, or `assessment`.

- **Network artifacts:** If operators use cloud-based report generation, monitor for uploads to collaboration platforms, email services, or cloud storage that coincide with engagement completion.

### Client Delivery and Handling

- **Email security:** Organizations receiving penetration test reports should:
  - Ensure reports arrive via encrypted channels (PGP, secure portals)
  - Scan email attachments for sensitive data classification (DLP tools)
  - Restrict forwarding of security assessment reports (email rules, rights management)

- **Document access logging:** Track access to stored penetration test reports. Alert on unusual access times, unauthorized accounts, or bulk downloads.

- **Version control monitoring:** Prevent accidental exposure of reports to public or insecure git repositories. Use pre-commit hooks and secret scanning (TruffleHog, git-secrets) on repositories that might store security documentation.

### Correlation with Engagement Activity

- **Timeline correlation:** If suspicious report-like documents are detected on internal systems outside the agreed-upon engagement period, investigate for unauthorized activity or insider threats.

- **Post-engagement monitoring:** After a penetration test concludes, monitor for continued log access or data exfiltration that may indicate compromise beyond the authorized scope.

### Preventive Controls

- **Secure report delivery mechanisms:** Establish secure channels for penetration testers to deliver reports (dedicated secure portals, encrypted email with PGP keys pre-exchanged).

- **Contractual data handling clauses:** Require penetration testing vendors to document their report generation, storage, and disposal procedures. Include data retention and destruction timelines in contracts.

- **Client-side log protection:** Implement least-privilege access to security logs. Limit log export capabilities to necessary personnel and log all export operations.

## 6. Residual gaps

### Redaction Limitations

- **Context-based secrets:** Automated regex patterns cannot detect secrets that are context-dependent (e.g., a numeric ID that happens to be sensitive in the client's environment but looks generic).

- **Obfuscated data:** Base64-encoded or hex-encoded credentials may evade pattern matching if not explicitly detected.

- **Visual redaction:** The tool produces text-based redaction in Markdown. If reports are converted to PDF or screenshots are taken, redaction must be verified in the final format.

### Correlation Accuracy

- **Time synchronization:** Correlation depends on accurate timestamps across log sources. Clock skew between systems can cause events to be miscorrelated or missed entirely.

- **Asset naming inconsistencies:** Different log sources may use different identifiers for the same asset (FQDN vs. short hostname vs. IP address), potentially breaking correlation.

### Report Completeness

- **Manual findings insertion:** Client reports include a findings placeholder that must be manually populated. Operators must ensure findings are accurately transferred and appropriately de-duplicated.

- **Limited visualization:** Text-based timeline reports are harder to interpret than visual attack graphs. Consider supplementing with manual diagrams for complex engagements.

### Security of the Tool Itself

- **No integrity verification:** The tool does not cryptographically sign reports or verify input log integrity. Tampered logs could produce misleading reports.

- **Dependency supply chain:** While the tool uses only Python standard library, the Python interpreter itself is a dependency. Ensure operator systems use trusted Python distributions.

---

**Operator guidance:** Always prioritize client confidentiality. When in doubt about redaction, over-redact rather than risk disclosure. Verify client approval before distributing reports beyond agreed-upon recipients.
