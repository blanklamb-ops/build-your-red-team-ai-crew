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

- Existing open projects that provide similar functionality include:
  - [Empire](https://github.com/EmpireProject/Empire) - A post-exploitation agent used for penetration testing and red teaming.
  - [PowerShell Empire](https://github.com/EmpireProject/PowerTools/tree/master/PSEmpire) - A PowerShell version of Empire.
- The format for the scoring engine's rules is not specified, but it should be a YAML file similar to `rules.yaml`.
- The suggestion engine's local knowledge base is not specified, but it should include documented alternative commands with citations.

## Risks

- Technical failure modes include:
  - Incompatibility with the Empire platform.
  - Incorrect implementation of the command interception hook.
  - Inaccurate or insufficient scoring engine rules.
  - Insufficient or incorrect suggestions in the local knowledge base.
- Operational failure modes include:
  - Misuse of the tool by operators.
  - False positives or negatives in the scoring engine.
  - Inadequate operator training on using the suggested alternatives.

## Open Questions

- The format of the scoring engine's rules is not specified.
- The source of the suggestion engine's local knowledge base is not specified.
- The exact method of keeping humans in control is not specified. Assuming manual review and approval of suggested alternatives.
- The exact method of archiving scanner outputs is not specified. Assuming a log file or database.