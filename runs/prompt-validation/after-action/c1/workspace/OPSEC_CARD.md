# OPSEC Card — after-action

**Tool:** After-Action Report Generator  
**Threat model:** Report handling, data leakage, attribution

---

## What this tool does

Correlates red team / penetration testing engagement logs with operator decision records to produce:

1. **Client-facing reports** (redacted, professional tone)
2. **Internal learning summaries** (tactical detail, TTPs, lessons learned)

Input: engagement logs (JSONL/CSV) + operator decision log  
Output: Markdown reports with timeline correlation and detection guidance

---

## Detection Recommendations

Organizations can detect misuse or accidental exposure of after-action reports through the following measures:

### 1. Report Access Monitoring

**What to detect:** Unauthorized access to engagement report repositories

- Monitor file access logs for after-action report directories
- Alert on access to report files outside authorized personnel (security team, executives, legal)
- Track when reports are copied, emailed, or uploaded to cloud storage
- Flag access from unusual locations or during off-hours

**Indicators:**
- Access to paths containing `client_report.md`, `internal_learning.md`, or similar naming patterns
- File operations on directories named `after-action`, `engagement-reports`, `red-team-reports`
- Email attachments with keywords: "after-action", "penetration test results", "security assessment"

### 2. Secret Leakage in Reports

**What to detect:** Improperly redacted reports exposing credentials or PII

- Scan committed reports in version control (GitHub, GitLab) for secrets
- Use secret scanning tools (GitGuardian, TruffleHog, Semgrep) on report output directories
- Alert on API keys, passwords, private keys, or PII patterns in Markdown files
- Monitor for accidental commits of `internal_learning.md` to public repositories

**Indicators:**
- Regex patterns for API keys: `sk-[a-zA-Z0-9]{32,}`, `AKIA[0-9A-Z]{16}`
- Password patterns: `password[:=]\s*\w+`
- PII: email addresses, SSNs, credit card numbers
- Private keys: `-----BEGIN.*PRIVATE KEY-----`

### 3. Report Distribution Tracking

**What to detect:** Reports shared beyond authorized scope

- DLP (Data Loss Prevention) rules for documents containing "after-action", "penetration test", "red team engagement"
- Monitor Slack, Teams, email for report attachments
- Track cloud storage (Google Drive, Dropbox, OneDrive) uploads of report files
- Flag public paste sites (Pastebin, GitHub Gists) containing report content

**Indicators:**
- Files with "confidential", "authorized use only", "internal learning" in headers
- Markdown files with "Detection Recommendations" sections (unique to this tool format)
- Timeline entries with timestamps, decisions, and asset correlations

### 4. Tool Usage Monitoring

**What to detect:** Execution of after-action tool on unauthorized systems

- Endpoint detection for Python execution of `after_action.cli` module
- Monitor for file system creation of `after_action/` package directories
- Track installation of this tool via `pip install` or `git clone`
- Alert on execution with flags like `--logs`, `--decisions`, `--redaction-config`

**Indicators:**
- Process execution: `python -m after_action.cli`
- File creation: `.../after_action/__init__.py`, `.../after_action/cli.py`
- Network activity to repository: `github.com/.../after-action` or similar

### 5. Report Mishandling as OPSEC Failure

**Critical scenario:** Internal reports exposed to clients or public

- **Risk:** Internal learning reports contain TTPs, tool names, operational mistakes, and defensive blind spots—material that should NEVER reach client or public eyes
- **Detection:** Monitor for presence of "internal_learning.md" in client-facing email threads, shared drives, or public repositories
- **Prevention:** 
  - Enforce separation of `reports/client/` vs `reports/internal/` directories
  - Apply different access controls to internal vs. client report folders
  - Require manual review before any report distribution
  - Tag internal reports with "DO NOT SHARE EXTERNALLY" in file metadata

**Red flags:**
- Internal report uploaded to client portal
- Internal report attached to client-facing email
- Internal report committed to public repository
- Screenshots of internal reports in Slack channels visible to clients

---

## Defensive summary

**For blue teams receiving Detection Recommendations from client reports:**

The after-action report's Detection Recommendations section provides specific defensive guidance based on observed TTPs. Implement these as:

- SIEM correlation rules (time-window correlation, unusual auth patterns)
- EDR detection rules (credential access, lateral movement, process creation anomalies)
- Network monitoring alerts (unexpected SMB, RDP, PowerShell remoting)
- Behavioral analytics baselines (privilege escalation, off-hours activity)

**For organizations generating these reports:**

Treat internal learning reports as **operational security material** equivalent to engagement notes and tool configurations. A leaked internal report reveals:

- Which defensive controls you successfully evaded (helping future attackers)
- Which tools you used (enabling targeted defenses against your toolchain)
- Where you made operational mistakes (informing adversary training)
- Client blind spots you discovered (becomes their attack surface map)

**Bottom line:** Client reports are deliverables. Internal reports are operational secrets.

---

## Recommended controls

| Control | Purpose |
|---------|---------|
| Separate storage paths | Keep `client_report.md` and `internal_learning.md` in different directories with different ACLs |
| Pre-distribution review | Manual verification that redaction completed successfully before client delivery |
| Version control hygiene | Never commit unredacted reports or internal learning to repositories |
| Secret scanning CI | Run GitGuardian/Semgrep on report output directories in pre-commit hooks |
| Access logging | Monitor all access to engagement report directories |
| Retention policy | Archive old reports to cold storage; purge after engagement lifecycle |

---

## Attribution risks

This tool produces reports with a distinctive format:

- Markdown structure with specific section headers ("Detection Recommendations", "Internal Learning Summary")
- Timeline correlation format (decisions linked to events with timestamps)
- Redaction markers (`[REDACTED-API-KEY]`, `[REDACTED-PASSWORD]`)
- Detection recommendation categories (Network-Based, Host-Based, Behavioral Analytics)

An adversary who obtains multiple reports generated by this tool can:

- Attribute reports to the same operator team
- Identify the generating tool and search for its source code
- Reverse-engineer redaction rules to guess what was removed
- Map engagement methodologies across multiple clients

**Mitigation:** Customize report templates, section headers, and redaction markers for operational deployments. The fixture templates are for research and testing—not operational use without modification.
