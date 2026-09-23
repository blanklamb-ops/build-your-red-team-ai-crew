# Empire Advisor

**OPSEC Advisory Plugin for PowerShell Empire**

Empire Advisor intercepts operator commands and provides real-time OPSEC scoring with documented quieter alternatives. Advisory only - never auto-executes suggestions.

## ⚠️ Authorized Use Only

This tool is for **authorized security research, red team exercises, and defensive security analysis only**. Unauthorized use against systems you don't own or have explicit permission to test is illegal and unethical.

See `AUTHORIZED_USE.md` for complete usage guidelines.

## Overview

Empire Advisor helps red team operators make informed decisions about command tradecraft by:

1. **Scoring commands** against transparent OPSEC rules (0-100 scale)
2. **Identifying detection risks** with documented rationale for each rule
3. **Suggesting quieter alternatives** from a curated knowledge base
4. **Maintaining operator control** - all suggestions are advisory only

## Features

- **Transparent Scoring**: All rules documented in `rules.yaml` with clear rationale
- **Knowledge Base**: Alternative techniques with citations (MITRE ATT&CK, LOLBAS, etc.)
- **Offline Mode**: Works without live C2 infrastructure using fixture commands
- **Deterministic**: Same command always produces identical score
- **Empire Compatible**: Plugin structure compatible with Empire 4.x+ or standalone shim mode

## Installation

### Requirements

- Python 3.7+
- PyYAML

```bash
pip install -r requirements.txt
```

### As Empire Plugin

If you have PowerShell Empire installed:

1. Copy this directory to Empire's plugin directory:
   ```bash
   cp -r empire-advisor /path/to/Empire/plugins/
   ```

2. In Empire, load the plugin:
   ```
   plugin empire-advisor
   ```

3. Commands will now be automatically scored before execution

### As Standalone Tool (Shim Mode)

Without Empire, use the standalone CLI:

```bash
python empire_advisor.py "your-command-here"
```

Example:
```bash
python empire_advisor.py "Invoke-Mimikatz -Command coffee" --json
```

## Usage

### Command Line

```bash
# Text output (human-readable)
python empire_advisor.py "Invoke-Mimikatz"

# JSON output (for automation)
python empire_advisor.py "nmap -sS 10.0.0.0/24" --json
```

### Programmatic

```python
from empire_advisor import Plugin

plugin = Plugin()
result = plugin.check_command("Get-ADUser -Filter *", output_format="json")

print(f"OPSEC Score: {result['score']}/100")
print(f"Action: {result['action']}")
print(result['advisory'])
```

## Architecture

### Components

1. **`empire_advisor.py`** - Main plugin implementation
   - `EmpireAdvisor` class: Core scoring engine
   - `Plugin` class: Empire-compatible interface
   - CLI entry point

2. **`rules.yaml`** - OPSEC scoring rules (12 rules covering major ATT&CK techniques)
   - Pattern-based detection (regex)
   - Severity levels (low, medium, high, critical)
   - Score penalties
   - Categories aligned with MITRE ATT&CK

3. **`knowledge_base.yaml`** - Alternative techniques
   - Quieter command alternatives
   - Rationale for each suggestion
   - Citations to authoritative sources

4. **`tests/`** - Comprehensive test suite
   - Acceptance criteria validation
   - Fixture-based testing
   - Determinism checks

### Scoring System

- **Score Range**: 0-100 (100 = perfect OPSEC, 0 = very noisy)
- **Calculation**: Base 100, minus penalty for each matched rule
- **Risk Levels**:
  - Critical: Score < 20 or critical severity match → **BLOCK**
  - High: Score < 40 or high severity match → **WARN**
  - Medium: Score < 70 → **WARN**
  - Low: Score ≥ 70 → **ALLOW**

### Rules Coverage

Current rules detect:

| Category | Rules | Examples |
|----------|-------|----------|
| Reconnaissance | Network scanning | nmap, portscan |
| Credential Access | Credential dumping | mimikatz, hashdump |
| Execution | PowerShell cradles, WMI | IEX DownloadString, wmic |
| Persistence | Services, registry, tasks | sc create, Run keys, schtasks |
| Defense Evasion | Known tool names | metasploit, empire |
| Discovery | AD enumeration | Get-ADUser -Filter * |
| Collection | Packet capture, keylogging | tcpdump, keylogger |
| C2 | Cleartext protocols | HTTP (non-localhost) |

## Empire Compatibility

### Empire 4.x+

This plugin follows Empire's plugin API conventions:

- Plugin class with `info` dictionary
- `onLoad()` initialization hook
- `register()` method for mainMenu integration
- Command hook interface for pre-execution checks

### Shim Mode (No Empire Required)

When Empire is not available, the plugin operates as a standalone shim:

- Same API surface
- Offline fixture testing
- No external dependencies beyond Python + PyYAML
- Full functionality preserved

**Limitations in Shim Mode**:
- No automatic command interception (must call explicitly)
- No Empire session context
- No integration with Empire's task system

## Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/test_advisor.py -v

# Run specific acceptance test
pytest tests/test_advisor.py::TestAcceptanceCriteria::test_a4_determinism -v
```

### Test Fixtures

See `tests/fixtures/commands.yaml` for example commands covering:
- Credential dumping
- Network scanning
- Lateral movement
- Persistence mechanisms
- Benign commands (should score high)

## Output Examples

### Text Format

```
======================================================================
EMPIRE ADVISOR - OPSEC ANALYSIS
======================================================================

Command: Invoke-Mimikatz -Command coffee

OPSEC Score: 10/100
Risk Level: CRITICAL
Recommended Action: BLOCK

======================================================================
MATCHED RULES (1)
======================================================================

[1] Direct Credential Dump (R002)
    Severity: CRITICAL
    Category: credential_access
    Penalty: -90 points
    Rationale: Direct credential dumping triggers AV/EDR behavioral 
               detection and LSASS access monitoring

======================================================================
QUIETER ALTERNATIVES (1)
======================================================================

[1] Use token manipulation or indirect memory reading
    Rationale: Reduces direct LSASS handle creation and mimikatz-style patterns
    Citation: Red Team Ops - Credential Access Without Direct Dumping
    Alternative commands:
      • Use process token duplication instead of direct LSASS access
      • Read memory via debugging APIs with smaller footprint

======================================================================
NOTE: This is advisory only. No commands have been executed.
======================================================================
```

### JSON Format

```json
{
  "command": "Invoke-Mimikatz -Command coffee",
  "opsec_score": 10,
  "risk_level": "critical",
  "action": "block",
  "matched_rules": [
    {
      "rule_id": "R002",
      "name": "Direct Credential Dump",
      "severity": "critical",
      "rationale": "Direct credential dumping triggers AV/EDR...",
      "score_penalty": 90,
      "category": "credential_access"
    }
  ],
  "suggestions": [...]
}
```

## Extending

### Adding New Rules

Edit `rules.yaml`:

```yaml
- id: R013
  name: "Your Rule Name"
  pattern: "(?i)(your|regex|pattern)"
  severity: high  # low, medium, high, critical
  rationale: "Why this is risky and how it's detected"
  score_penalty: 75
  category: your_category
```

### Adding Alternatives

Edit `knowledge_base.yaml`:

```yaml
- rule_id: R013
  suggestion: "Brief description of quieter approach"
  commands:
    - "Specific alternative command 1"
    - "Specific alternative command 2"
  rationale: "Why this alternative is quieter"
  citation: "Source: MITRE ATT&CK, research paper, etc."
```

## Detection Recommendations

See `OPSEC_CARD.md` for complete detection guidance.

## Limitations

1. **Pattern-based detection**: Rules use regex patterns, may have false positives/negatives
2. **No dynamic analysis**: Doesn't execute commands or analyze runtime behavior
3. **Knowledge base requires updates**: New techniques need manual addition
4. **Advisory only**: Human operator makes final decision
5. **Shim mode**: Without full Empire, some integration features unavailable

## License

Research use only. See `AUTHORIZED_USE.md`.

## Contributing

This is a research artifact for the frozen study. See project documentation for contribution guidelines.

## Support

For issues related to:
- **Empire integration**: Ensure Empire 4.x+ compatibility
- **Rule accuracy**: Submit evidence-based rule improvements
- **False positives**: Provide specific command examples

## Acknowledgments

- MITRE ATT&CK Framework for technique taxonomy
- LOLBAS Project for living-off-the-land references
- PowerShell Empire project for C2 framework

---

**Version**: 1.0.0  
**Study**: ROOTCON 20 Prompt Validation  
**Status**: Frozen implementation
