 # Empire-Advisor Domain Brief

## Operator Goal

The goal of the Empire-Advisor tool is to build a plugin or module that intercepts or wraps operator command submissions in a lab Empire-like interface. This tool should score commands against a transparent, documented heuristic related to noisy vs quieter tradecraft, suggest documented alternative commands from a local knowledge base, and keep humans in control by never auto-executing alternatives.

## Constraints

- The tool should be compatible with the Empire platform.
- The tool should follow Empire plugin conventions or provide a shim with compatibility notes.
- The tool should operate offline in air-gap environments.
- The tool should not guarantee EDR bypass or provide closed-source signature evasion packs.
- The tool should not autonomously chain attacks.

## Prior Art

- Existing open projects that provide similar functionality include [Empire](https://github.com/EmpireProject/Empire) and [PowerShell Empire](https://github.com/EmpireProject/PowerShell-Empire).
- The format and interfaces for command scoring and suggestion engines are not explicitly mentioned in the requirements. However, similar tools may use YAML or JSON formats for rule definitions and suggestion databases.

## Risks

- **Technical Failure Modes:** Incorrect implementation of the command interception hook, scoring engine, or suggestion engine could lead to unintended consequences or false positives/negatives.
- **Operational Failure Modes:** Lack of operator training or misunderstanding of the tool's capabilities could result in misuse or inappropriate command execution.

## Open Questions

- The specific format and structure of the `rules.yaml` file for the scoring engine are not defined.
- The source and format of the local knowledge base for the suggestion engine are not specified.
- The exact mechanism for offline mode operation is not clear. It is assumed that the tool will use fixture command transcripts, but the format and location of these fixtures are not defined.