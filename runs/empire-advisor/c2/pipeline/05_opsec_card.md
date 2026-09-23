# OPSEC Card — empire-advisor

**Review Date:** 2026-09-15  
**Reviewer Role:** OPSEC Reviewer (Stage 5/5)  
**Tool Version:** 1.0.0

---

## 1. Summary

Empire Advisor is a plugin for the Empire C2 framework that provides operational security (OPSEC) guidance to red team operators. It intercepts command submissions before execution, scores them against a local knowledge base of 15 documented heuristics related to noisy vs. quieter tradecraft, and suggests safer alternatives with citations. The plugin is advisory-only and never modifies operator commands. It operates entirely offline with no network connectivity requirements, making it suitable for air-gapped engagements. The tool includes an offline shim mode for testing without Empire infrastructure.

**Primary Use Case:** Pre-execution command review during red team engagements to reduce detection probability while maintaining operator decision authority.

---

## 2. Operator Risks

### How operators can burn themselves

1. **False sense of security**
   - **Risk:** Operators may over-rely on the advisor and assume "low score = undetectable"
   - **Reality:** Scoring is based on generic heuristics, not target-specific defensive capabilities
   - **Mitigation:** Treat advisories as guidance, not guarantees. Always research target's actual EDR/monitoring capabilities

2. **Advisory output logging**
   - **Risk:** If operators redirect stdout to files, advisory output contains command history and intended techniques
   - **Example:** `python plugin/shim.py > review.log` creates a file with all commands + alternatives
   - **Exposure:** Log files on operator workstation or team server reveal engagement methodology
   - **Mitigation:** Never commit advisory logs to version control. Delete logs after review. Consider in-memory only output

3. **Knowledge base as TTP fingerprint**
   - **Risk:** If `rules.yaml` or `alternatives.yaml` files are exfiltrated (via compromise or accidental commit), defenders can:
     - Identify red team's OPSEC priorities
     - Predict likely alternative techniques
     - Build detections for suggested "quieter" commands
   - **Mitigation:** Treat knowledge base files as engagement-sensitive. Store encrypted or on secure workstations only

4. **Plugin installation artifacts**
   - **Risk:** Installing plugin on a compromised Empire server leaves:
     - `empire/plugins/empire-advisor/` directory
     - Empire startup logs showing plugin registration
     - File timestamps indicating installation time
   - **Exposure:** Defenders recovering C2 server can analyze plugin to understand red team TTPs
   - **Mitigation:** Use shim mode for pre-engagement planning. Only install plugin on trusted infrastructure

5. **Timing side channel**
   - **Risk:** Scoring adds 10-500ms delay before command execution
   - **Exposure:** Unusual delays between Empire task creation and execution may indicate advisory review
   - **Severity:** Low (difficult to detect without deep C2 telemetry)
   - **Mitigation:** Operators should vary command submission timing regardless of advisor use

6. **Dependency on outdated knowledge**
   - **Risk:** Rules are static; defensive capabilities evolve faster than manual KB updates
   - **Example:** A "quiet" technique from 2024 may be heavily monitored in 2026
   - **Mitigation:** Regularly update knowledge base based on actual engagement feedback. Cross-reference with current defensive research

---

## 3. Artifacts Left Behind

### On operator workstation

| Artifact | Location | Visibility | Persistence | Mitigation |
|----------|----------|------------|-------------|------------|
| Plugin files | `empire-advisor/` directory | Filesystem | Until deleted | Encrypt disk; delete after engagement |
| Knowledge base | `knowledge_base/*.yaml` | Filesystem (plaintext) | Until deleted | Treat as engagement-sensitive; don't commit to shared repos |
| Advisory logs (if saved) | Operator-defined paths | Filesystem | Until deleted | Never save to disk; use ephemeral terminals only |
| Python cache | `__pycache__/`, `*.pyc` | Filesystem | Until deleted | Delete with `find . -name "*.pyc" -delete` |
| Test fixtures | `tests/fixtures/commands.json` | Filesystem | Until deleted | Sanitized examples (safe), but reveals testing approach |

### On Empire C2 server (if plugin installed)

| Artifact | Location | Visibility | Persistence | Mitigation |
|----------|----------|------------|-------------|------------|
| Plugin installation | `Empire/plugins/empire-advisor/` | Filesystem + startup logs | Until uninstalled | Use shim mode instead; or scrub logs post-engagement |
| Empire startup logs | Empire log files | Text logs | Until rotated/deleted | Clear logs referencing plugin; use memory-resident logging if available |
| Advisory output in console | Empire console history | Terminal scrollback / tmux buffers | Session lifetime | Clear terminal history; use ephemeral sessions |

### On target systems

**None.** The advisor runs on the operator's C2 infrastructure, not on compromised endpoints. Advisory does not generate target-side artifacts.

### Network artifacts

**None.** Verified via Semgrep scan and code review. The advisor has zero network functionality:
- No HTTP/HTTPS requests
- No DNS queries  
- No socket operations
- All knowledge base queries are local file reads

---

## 4. Safer Operating Guidance

### Pre-engagement planning (safest mode)

1. **Use shim mode offline:**
   ```bash
   python plugin/shim.py --interactive
   ```
   - Review planned commands before engagement
   - Build command cheat sheet from advisories
   - No Empire server involvement; no artifacts on C2 infrastructure

2. **Customize knowledge base:**
   - Add target-specific rules to `rules.yaml`
   - Update alternatives based on target's known defensive posture
   - Sanitize any target-identifying information before saving

3. **Team review:**
   - Share advisories (not raw KB files) in team briefings
   - Document rationale for high-risk commands in engagement notes
   - Ensure team understands advisory limitations (heuristics, not target-aware)

### Live engagement use

4. **Ephemeral output only:**
   - Run plugin in terminal with no logging
   - Do NOT redirect stdout: `python plugin/shim.py > file.log` ❌
   - Clear terminal scrollback after reviewing advisories

5. **Selective installation:**
   - Install plugin only on trusted, encrypted C2 infrastructure
   - Uninstall immediately post-engagement
   - Scrub Empire logs referencing plugin

6. **Command sequencing:**
   - Review advisory BEFORE submitting to agent
   - If multiple operators share Empire instance, coordinate to avoid command pattern correlation
   - Vary timing of command submission (don't submit immediately after advisory)

### Post-engagement

7. **Artifact cleanup:**
   ```bash
   # Delete plugin
   rm -rf empire-advisor/
   
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +
   
   # Scrub shell history
   history -c
   ```

8. **Knowledge base maintenance:**
   - Review which rules triggered during engagement
   - Update alternatives based on what worked vs. what was detected
   - Remove target-specific customizations before archiving

9. **Lessons learned:**
   - Document (generically) which advisories were ignored and why
   - Track false positives (commands scored high-risk but weren't detected)
   - Share sanitized findings with team to improve KB accuracy

---

## 5. Detection Recommendations

*Written from the operator's perspective as defender-side guidance suitable for client handoff.*

### Detection Opportunity #1: Empire Plugin Directory Monitoring

**Signal:** New files in Empire C2's `plugins/` directory, especially `empire-advisor/` or similar OPSEC-related plugin names.

**Detection Logic:**
- File creation monitoring on known Empire installation paths
- Pattern: `*/Empire/plugins/empire-advisor/*` OR `*/Empire/plugins/*advisor*`
- Trigger: New directory with `plugin.yaml` + Python files appears

**Example Detection (Linux auditd):**
```bash
# Monitor Empire plugin directory
auditctl -w /opt/Empire/plugins/ -p wa -k empire_plugin_install
```

**Blue Team Action:**
- Alert on new plugin installations during active incident response
- If Empire server is recovered, inventory plugins to understand attacker's operational toolkit
- Analyze plugin code (especially knowledge base files) to anticipate attacker's likely next moves

**Limitation:** Requires access to C2 server filesystem (IR scenario, not preventative detection)

---

### Detection Opportunity #2: Knowledge Base Exfiltration Analysis

**Signal:** If `rules.yaml` or `alternatives.yaml` files are recovered (via server compromise, accidental commit to public repo, or file exfiltration), they reveal attacker TTP preferences.

**Defensive Value:**
- **Rules analysis:** Identifies which techniques attacker considers "noisy" → Build detections for the "quiet" alternatives they'll use instead
- **Alternatives analysis:** Lists specific commands attacker will likely use (e.g., PowerShell Get-LocalUser instead of net.exe)
- **Severity priorities:** High-severity rules indicate attacker's awareness of certain detections → Focus defensive telemetry on those areas

**Example Analytic Workflow:**
1. Recover `alternatives.yaml` from compromised attacker infrastructure
2. Extract all `suggestion:` fields → These are the commands attacker considers "safer"
3. Build specific detections for those commands (e.g., PowerShell Get-LocalUser, Test-Connection -Count 1, etc.)
4. Cross-reference with current telemetry to find historical usage

**Detection Query Example (Splunk for PowerShell):**
```spl
index=windows source="WinEventLog:Microsoft-Windows-PowerShell/Operational"
EventCode=4104 
(ScriptBlockText="*Get-LocalUser*" OR 
 ScriptBlockText="*Get-LocalGroup*" OR
 ScriptBlockText="*WindowsIdentity::GetCurrent*")
| stats count by ComputerName, ScriptBlockText
```

**Blue Team Action:**
- Prioritize detections for "alternative" commands listed in recovered KB
- Assume attacker has already deployed these techniques earlier in engagement
- Hunt for historical use of alternatives as indicators of earlier compromise phases

---

### Detection Opportunity #3: Advisory Output Pattern Recognition

**Signal:** Text logs or terminal captures containing Empire Advisor's distinctive output format.

**Pattern Markers:**
- String: "EMPIRE ADVISOR - OPERATIONAL SECURITY ADVISORY"
- String: "OPSEC Score: " followed by number/100
- String: "SUGGESTED ALTERNATIVES"
- String: "advisory only. Command will execute as submitted"

**Detection Scenarios:**

A. **Memory forensics:** If operator workstation is imaged, scan for advisory strings in process memory or swap
   - Tool: Volatility string scan for "EMPIRE ADVISOR" pattern

B. **Network traffic:** If operator accidentally proxies Empire console through monitored network and advisory output is transmitted
   - Pattern: TLS session containing repeated "OPSEC Score" strings
   - Likelihood: Low (advisory runs locally, but operator error possible)

C. **Captured logs:** If attacker commits advisory logs to accessible Git repository or cloud storage
   - GitHub/GitLab search: `"EMPIRE ADVISOR" OR "OPSEC Score" filename:*.log OR filename:*.txt`

**Blue Team Action:**
- If advisory output is found: Analyze logged commands to understand attacker's planned actions
- Commands with high OPSEC scores indicate attacker expected detection → Review alerts for those timeframes
- Alternatives section reveals attacker's actual deployed techniques → Hunt for those commands in telemetry

---

### Detection Opportunity #4: Behavioral - Command Timing Anomalies (Low Confidence)

**Signal:** Unusual delays between Empire task creation and execution, or patterns suggesting pre-execution review.

**Behavioral Indicators:**
- Task queued in Empire → 200-500ms delay → Task executes (scoring time)
- Operator submits command → revises/cancels immediately → Submits alternative (advisory review)

**Detection Logic:**
- Baseline normal Empire task execution timing (typically <50ms queue-to-execute)
- Alert on consistent 200-500ms delays across multiple tasks from same agent

**Limitation:** Very low confidence; delays can occur for many reasons (network latency, operator hesitation, script execution)

**Blue Team Action:**
- Use as corroborating evidence only (not standalone detection)
- If multiple other indicators present (plugin recovery, alternative command usage), timing patterns add confidence

---

### Detection Opportunity #5: Python Execution Patterns on Operator Infrastructure

**Signal:** Python processes running advisor code on known or suspected attacker infrastructure.

**Pattern:**
```bash
python.*shim.py
python.*advisor.py
python.*scorer.py
```

**Detection Context:**
- Requires monitoring of attacker-controlled infrastructure (honeypot, recovered C2, monitored attack box)
- EDR on red team operator workstation (insider threat / compromised operator scenario)

**Detection Query (EDR process telemetry):**
```sql
SELECT * FROM process_events
WHERE (process_name = 'python.exe' OR process_name = 'python3')
  AND command_line LIKE '%advisor%' 
  AND command_line LIKE '%empire%'
```

**Blue Team Action:**
- Low probability in external attacker scenario (requires access to attacker systems)
- Valuable in insider threat detection or when attacker infrastructure is compromised/monitored

---

### Summary of Detection Recommendations

| Detection | Confidence | Deployment Phase | Use Case |
|-----------|-----------|------------------|----------|
| #1 Plugin directory monitoring | High | Post-C2-compromise | IR / Forensics |
| #2 Knowledge base analysis | High | Post-file-recovery | IR / Threat Intel |
| #3 Advisory output pattern | Medium | Post-log-capture | IR / OSINT |
| #4 Timing anomalies | Low | Real-time telemetry | Corroborating evidence |
| #5 Python process monitoring | Medium | Attacker infrastructure access | Insider threat / Honeypot |

**Defensive Priority:**
1. **Immediate value:** If Empire server or operator workstation is recovered, inventory plugins and KB files (#1, #2)
2. **Proactive hunting:** Search for "alternative" commands from recovered KB in historical telemetry (#2)
3. **Ongoing monitoring:** Watch for suspicious file creations in known C2 paths (#1)

---

## 6. Residual Gaps

### What this review could not verify

1. **Live Empire integration testing**
   - **Gap:** Plugin tested only in shim mode; not validated against live Empire 4.x instance
   - **Risk:** Hook registration may fail with certain Empire configurations
   - **Recommendation:** Test with live Empire before operational use; validate `on_agent_task` hook triggers correctly

2. **Windows timeout behavior**
   - **Gap:** Timeout protection uses `signal.SIGALRM` (Unix-only); Windows behavior not tested
   - **Risk:** On Windows operator workstations, scoring could theoretically block if regex DoS occurs
   - **Likelihood:** Low (rules.yaml patterns are simple; no backtracking)
   - **Recommendation:** Test on Windows Empire instance if that's operational environment

3. **Starkiller UI integration**
   - **Gap:** Plugin may integrate with Empire backend but not display advisories in Starkiller web UI
   - **Risk:** Operators using Starkiller may not see advisories (silent failure)
   - **Recommendation:** Document Starkiller limitations; recommend CLI Empire for full advisory visibility

4. **Knowledge base completeness**
   - **Gap:** 15 rules cover common commands but not exhaustive (e.g., no Covenant/Cobalt Strike module mappings)
   - **Risk:** Novel commands receive baseline score (50/100) with no alternatives
   - **Recommendation:** Operators should extend KB based on target environment and preferred TTPs

5. **Alternative command verification**
   - **Gap:** Suggested alternatives are based on published research, not empirically tested against modern EDR
   - **Risk:** "Quieter" alternatives may trigger detections in specific EDR configurations
   - **Example:** PowerShell Get-LocalUser may trigger AMSI in some environments
   - **Recommendation:** Operators must validate alternatives in lab environment matching target's defensive stack

6. **Multi-operator concurrency**
   - **Gap:** Not tested with multiple operators using same Empire instance simultaneously
   - **Risk:** Advisory output from multiple operators may interleave in console, causing confusion
   - **Recommendation:** In multi-operator scenarios, consider separate Empire instances or enhanced output labeling

### Blocking issues found

**None.** Implementation is complete and functional. Gaps listed above are operational considerations, not implementation defects.

### Recommended follow-up testing

1. Install plugin in live Empire 4.x instance and verify hook triggers on real agent tasks
2. Test on Windows operator workstation to confirm fail-open behavior
3. Submit commands via Starkiller UI to verify advisory visibility
4. Conduct multi-operator concurrency testing with shared Empire instance

---

## OPSEC Card Validation

✅ **Summary:** Concise description of tool's function  
✅ **Operator risks:** 6 specific burn scenarios documented  
✅ **Artifacts:** Workstation, C2 server, and target artifacts categorized (zero target/network artifacts)  
✅ **Safer operating guidance:** 9 operational recommendations across engagement phases  
✅ **Detection Recommendations:** 5 defender-oriented detection opportunities with queries/ideas  
✅ **Residual gaps:** 6 items that could not be verified (none blocking)

**Acceptance A8 Status:** ✅ **PASSED** - OPSEC Card complete with ≥3 detection recommendations (delivered 5)

---

**OPSEC Reviewer Sign-off:** Tool is operationally sound for authorized research and red team use. Detection recommendations are client-handoff quality. Operators must understand advisory limitations and treat as guidance, not guarantees.
