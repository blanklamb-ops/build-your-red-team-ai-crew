# OPSEC Card — `empire-advisor`

## 1. Summary

**Empire Advisor** is an OPSEC scoring engine that evaluates PowerShell Empire C2 commands against detection heuristics and suggests quieter tradecraft alternatives. The tool operates in advisory mode — it scores commands pre-execution but never auto-executes alternatives, keeping operators in control. Designed for authorized security testing, research, and red team training environments.

**Primary artifacts**: `rules.yaml` (scoring logic), `knowledge_base.yaml` (alternative suggestions), command evaluation logs (JSON output).

## 2. Operator Risks

### Detection Surfaces

1. **Command Interception Telemetry**
   - PowerShell script block logging (Event ID 4104) may capture advisor evaluation logic if loaded in PowerShell session
   - Empire plugin directory reads generate filesystem access logs (Sysmon Event ID 11)
   - YAML file parsing operations visible in process memory/module loads

2. **Behavioral Indicators**
   - Advisory tool usage implies red team/penetration testing activity
   - Presence of `rules.yaml` with signature patterns indicates offensive security tooling
   - Knowledge base of evasion techniques matches threat intelligence indicators

3. **False Confidence**
   - Advisor suggestions reduce but do not eliminate detection risk
   - KB alternatives may be outdated against current EDR/SIEM capabilities
   - Over-reliance on tool recommendations without environment-specific validation

### Operational Risks

- **Dwell time**: Manual review of advisories increases command execution latency (opportunity for defender detection)
- **Training dependency**: Operators unfamiliar with suggested alternatives may misuse commands
- **Logging artifacts**: JSON output files with command history create forensic evidence trail

## 3. Artifacts Left Behind

### Filesystem Artifacts

- **Plugin files**: `empire-advisor/` directory in Empire plugins path
  - `rules.yaml`, `knowledge_base.yaml` (offensive capability indicators)
  - `empire_advisor.py`, `empire_plugin.py` (Python modules)
  - `testdata/fixture_commands.txt` (example attack commands)

- **Output files**:
  - `testdata/*_results.json` (command evaluation history with scores, matched rules, suggestions)
  - Log files if Empire logging configured to capture plugin output

### Memory Artifacts

- Python process memory containing:
  - Full rule set with detection evasion patterns
  - Knowledge base of alternative attack techniques
  - Recent command evaluations and scores

- Empire process memory:
  - Loaded plugin metadata and advisory results

### Network Artifacts

- **None in default configuration** (fully offline operation)
- If operators follow suggested download alternatives (BITS, SMB), those generate respective network telemetry

### Execution Artifacts

- **Process creation events**: Python interpreter launching `empire_advisor.py` (if run standalone)
- **Empire plugin loads**: Plugin registration events in Empire console logs
- **PowerShell script blocks**: If advisor logic integrated into PowerShell Empire agents (AMSI/ETW visibility)

## 4. Safer Operating Guidance

### Pre-Engagement

1. **Validate knowledge base alternatives in isolated lab environment** matching target defender capabilities
2. **Review rules.yaml patterns** against known target EDR signatures (may need custom rule additions)
3. **Test advisor in offline shim mode** before loading into live Empire C2 infrastructure
4. **Establish secure artifact cleanup procedures** for JSON output and log files

### During Engagement

1. **Use advisor on operator workstation**, not on implants/beacons (keep tool off target network)
2. **Disable JSON logging** for production operations (use display-only advisory mode)
3. **Manually validate each suggestion** against target environment reconnaissance before execution
4. **Consider timing**: Advisory review process should not create suspicious command execution delays

### Post-Engagement

1. **Securely delete all JSON output files** from operator workstation
2. **Remove plugin from Empire directory** if engagement-specific customization was performed
3. **Strip command history** from Python REPL and shell history files
4. **Document used alternatives** in private engagement notes (not in artifacts leaving operator control)

### Operational Best Practices

- **Combine with proper C2 infrastructure**: Advisory tool does not replace proper domain fronting, jitter, sleep timing
- **Layer evasion techniques**: Use multiple quieter alternatives in sequence, not single replacement
- **Monitor defender response**: If suggested alternatives trigger alerts, fall back to manual tradecraft
- **Keep knowledge base current**: EDR vendors update detection logic — validate alternatives quarterly

## 5. Detection Recommendations

**From the operator's perspective, as guidance suitable for client/defender handoff:**

- **Hunt for Empire Advisor plugin artifacts**: Search Windows filesystems for `rules.yaml` containing regex patterns for `mimikatz`, `Invoke-Mimikatz`, `SharpHound`, or other offensive tool names combined with fields like `severity`, `rationale`, `category`. File presence indicates red team tooling on host.

- **Monitor for YAML parsing libraries in unusual process trees**: Detect PyYAML module loads (`import yaml`) in Python processes spawned from non-standard paths or launched by users without legitimate DevOps/scripting responsibilities. Cross-reference with processes reading files containing offensive security keywords.

- **Correlate sequential alternative technique execution**: Advisor suggests specific quiet alternatives (BITS transfer instead of WebClient, DCOM instead of WMI process creation, PowerShell LDAP instead of net.exe). Behavioral analytics should flag sequential use of "quieter" variants following noisy attempts, especially with timing gaps consistent with manual review.

- **Detect JSON output files with offensive security command history**: Hunt for JSON files containing keys like `matched_rules`, `advisory_state`, `alternative_commands` combined with values referencing PowerShell Empire modules (`usemodule powershell/credentials/*`), MITRE ATT&CK techniques, or evasion rationales. These files indicate post-operation forensic evidence.

- **Alert on BITS jobs, DCOM lateral movement, and WMI event consumers in environments where baseline is low**: The knowledge base suggests these as "quieter" alternatives. While legitimate uses exist, sudden adoption following blocked/alerted PowerShell download cradles or PsExec attempts may indicate adversary adaptation guided by OPSEC tooling.

- **Flag processes accessing both offensive security knowledge bases and live credential material**: Memory analysis should detect Python processes with loaded YAML containing `credential_access`, `lateral_movement` categories accessing LSASS memory, registry hives, or network authentication APIs. This indicates active advisory-guided attack execution.

## 6. Residual Gaps

### Unaddressed Attack Surfaces

1. **No obfuscation of advisor tool itself**: Plugin files are cleartext Python/YAML (defenders can trivially signature the tool)
2. **Static rule patterns**: Regex-based detection doesn't account for semantic variations or polymorphic payloads
3. **Knowledge base currency**: Alternatives may be outdated against latest EDR behavioral detection (no auto-update mechanism)
4. **No target environment profiling**: Advisor doesn't adapt suggestions to specific defender capabilities (assumes generic enterprise)

### Defender Advantages

1. **Tool presence is high-confidence indicator**: Finding Empire Advisor artifacts = confirmed red team/attacker infrastructure
2. **JSON logs create forensic timeline**: Detailed command evaluation history aids incident reconstruction
3. **Suggested alternatives are documented**: Defenders can pre-signature KB alternatives before attackers use them
4. **Advisory delays increase detection window**: Manual review latency gives SIEM/SOC time to correlate precursor events

### Limitations of Quieter Alternatives

- **"Quieter" ≠ "Undetectable"**: All suggested alternatives generate some telemetry (BITS jobs, DCOM network traffic, PowerShell LDAP queries)
- **Behavioral analytics bypass**: Modern EDR uses ML models on execution chains — single command replacement may not evade sequence-based detection
- **Assumes static defenses**: Defenders continuously update signatures — yesterday's quiet alternative is today's high-fidelity alert

### Operator Awareness

- This tool provides **comparative risk assessment** (noisy vs quieter), not **detection probability guarantees**
- Validate all suggestions in lab with target-equivalent defensive stack before field use
- Combine advisor guidance with human tradecraft expertise and environment-specific reconnaissance
- Remember: The best OPSEC is not needing the command at all (prefer passive collection, living-off-the-land, minimal footprint)

---

**Defense-in-Depth Recommendation**: Even "quieter" alternatives leave artifacts. Defenders should implement:
- Comprehensive PowerShell logging (script block + module + transcription)
- Sysmon with BITS, WMI, and DCOM event coverage
- Behavioral analytics on rare/anomalous WMI event consumers and DCOM activations
- Network inspection of BITS traffic to non-Windows Update destinations
- Filesystem monitoring for offensive security tool artifacts (rules.yaml, SharpHound, Mimikatz variants)

The presence of Empire Advisor indicates **active threat actor operational security practices** — treat as high-confidence compromise indicator requiring immediate response.
