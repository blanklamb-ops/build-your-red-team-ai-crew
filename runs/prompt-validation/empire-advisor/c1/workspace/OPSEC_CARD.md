# OPSEC Card - Empire Advisor

**Tool**: Empire Advisor  
**Version**: 1.0.0  
**Purpose**: OPSEC advisory plugin for PowerShell Empire  
**Classification**: Research/Educational - Authorized Use Only

## Overview

Empire Advisor is a defensive research tool that scores red team commands for OPSEC considerations. While designed to help operators understand detection risks, the tool itself and its use patterns create detectable artifacts.

## Detection Recommendations

### 1. File System Artifacts

**Indicators**:
- Plugin files in Empire directory: `plugins/empire-advisor/`
- YAML configuration files: `rules.yaml`, `knowledge_base.yaml`
- Python cache files: `__pycache__/`, `*.pyc`
- Log files if logging enabled

**Detection Methods**:
- File integrity monitoring (FIM) on Empire installation directories
- Filesystem scanning for YAML files containing OPSEC/ATT&CK terminology
- Monitor for Python files importing `empire` modules outside standard installations

**Hunting Queries**:
```bash
# Find Empire Advisor files
find / -name "empire_advisor.py" 2>/dev/null
find / -path "*/empire/plugins/*" -name "rules.yaml" 2>/dev/null

# Check for OPSEC-related YAML configs
grep -r "opsec_score\|OPSEC" *.yaml 2>/dev/null
```

### 2. Process Execution Patterns

**Indicators**:
- Python processes loading Empire-related modules
- Command-line arguments containing "empire_advisor" or plugin names
- Python scripts with OPSEC scoring keywords in arguments

**Detection Methods**:
- EDR process monitoring for Python + Empire keyword combinations
- Command-line logging (Sysmon Event ID 1, Windows Event 4688)
- Parent-child process relationships: Empire server → Python → advisor

**Sysmon Detection**:
```xml
<RuleGroup name="Empire Advisor Detection" groupRelation="or">
  <ProcessCreate onmatch="include">
    <CommandLine condition="contains">empire_advisor</CommandLine>
    <CommandLine condition="contains all">python;rules.yaml</CommandLine>
    <Image condition="end with">empire_advisor.py</Image>
  </ProcessCreate>
</RuleGroup>
```

### 3. Network Artifacts

**Indicators** (if networked version deployed):
- Communication with Empire C2 server for command interception
- Potential external knowledge base updates via HTTP/HTTPS
- API calls to MITRE ATT&CK Navigator or similar services

**Detection Methods**:
- Network flow analysis for Empire C2 patterns
- TLS certificate inspection for Empire-related CN/SAN fields
- DNS queries for ATT&CK-related domains

**Note**: Standalone/offline mode produces NO network artifacts.

### 4. Memory Artifacts

**Indicators**:
- Python interpreter memory containing:
  - Rule patterns and rationale text
  - Command history being scored
  - Knowledge base alternatives in plaintext
  - MITRE ATT&CK technique IDs

**Detection Methods**:
- Memory scanning for OPSEC rule strings
- Process memory dumps containing Empire plugin signatures
- Volatility plugin for Python module detection

**YARA Rule Example**:
```yara
rule empire_advisor_memory {
    meta:
        description = "Detects Empire Advisor in memory"
        author = "Defensive Research"
    strings:
        $s1 = "empire_advisor" ascii wide
        $s2 = "opsec_score" ascii wide
        $s3 = "knowledge_base.yaml" ascii wide
        $s4 = "EmpireAdvisor" ascii wide
        $pattern = /R\d{3}.*rationale.*severity/ ascii
    condition:
        3 of ($s*) or $pattern
}
```

### 5. Behavioral Indicators

**Indicators**:
- Pre-command execution delays (scoring time)
- Repeated command pattern analysis without actual execution
- Filesystem reads of rules.yaml during Empire sessions
- Advisory output to operator terminal between command and execution

**Detection Methods**:
- Timing analysis of Empire task execution (delay between submit and execute)
- Behavioral analytics for command pre-processing patterns
- Monitor for advisory/scoring output in logs

### 6. Log Artifacts

**Indicators**:
- Empire server logs showing plugin load events
- Python logging output with OPSEC scores
- Advisory outputs cached or logged
- Rule match events in application logs

**Detection Methods**:
- Log aggregation and parsing for "OPSEC", "advisory", "empire_advisor"
- Correlation of scored commands with subsequent Empire tasks
- Anomaly detection for Empire plugins not in standard distribution

**Splunk Query Example**:
```spl
index=security sourcetype=python_logs 
(empire_advisor OR "OPSEC Score" OR "Matched Rules" OR "knowledge_base")
| stats count by host, user, command
| where count > 5
```

### 7. Configuration Management

**Indicators**:
- Git repositories containing Empire customizations
- Version control history of rules.yaml modifications
- Configuration management tools deploying custom Empire plugins

**Detection Methods**:
- Monitor Git repositories for Empire-related commits
- Scan for .git directories in Empire installation paths
- Check configuration management logs (Ansible, Puppet, etc.)

### 8. Testing and Development Artifacts

**Indicators**:
- pytest cache directories: `.pytest_cache/`
- Test fixtures: `tests/fixtures/commands.yaml`
- Development virtual environments with PyYAML, pytest
- Code scanning outputs: Semgrep, ast-grep results

**Detection Methods**:
- Scan for pytest artifacts in unusual locations
- Monitor for development tools on production systems
- File system scanning for fixture YAML files with attack commands

## Defensive Countermeasures

Organizations defending against red teams using this tool should:

1. **Monitor Empire Infrastructure**:
   - Deploy honeytokens in Empire server directories
   - Alert on any plugin modifications or additions
   - Baseline normal Empire behavior before exercises

2. **Command Pre-Processing Detection**:
   - Look for timing delays between command submission and execution
   - Monitor for advisory text patterns in logs/network traffic

3. **YAML Configuration Scanning**:
   - Scan for YAML files containing ATT&CK technique IDs
   - Alert on OPSEC/tradecraft terminology in configs

4. **Python Process Monitoring**:
   - Whitelist expected Python processes in Empire environment
   - Alert on new Python modules loaded in Empire context

5. **Behavioral Analytics**:
   - Baseline Empire usage patterns
   - Detect unusual command scoring or analysis behavior

## Red Team Operational Security

If using this tool in authorized engagements:

1. **Minimize Artifacts**:
   - Use in-memory execution where possible
   - Delete plugin files after use
   - Clear Python cache and logs

2. **Operational Compartmentalization**:
   - Run scoring offline on separate analysis system
   - Don't deploy plugin to production C2 infrastructure
   - Use one-time scoring sessions

3. **Anti-Forensics**:
   - Timestamp stomping on plugin files
   - Encrypt rules.yaml and knowledge_base.yaml
   - Use memory-only plugin loading if Empire supports

4. **Awareness**:
   - Understand that using an OPSEC tool creates its own OPSEC risk
   - Balance advisory benefits against detection surface
   - Consider manual analysis for most sensitive operations

## References

- MITRE ATT&CK: https://attack.mitre.org/
- Empire Documentation: https://bc-security.gitbook.io/empire-wiki/
- Sysmon Configuration: https://github.com/SwiftOnSecurity/sysmon-config
- YARA Rules: https://github.com/Yara-Rules/rules

## Disclosure

This OPSEC card is provided for defensive security research. Detection methods are based on standard forensic and security monitoring practices. Organizations should test these detections in controlled environments before production deployment.

**Last Updated**: 2026-09-04  
**Threat Model Version**: 1.0
