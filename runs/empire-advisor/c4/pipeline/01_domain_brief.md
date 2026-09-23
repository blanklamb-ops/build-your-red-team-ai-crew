 # Empire-Advisor Domain Brief

## Operator Goal Restatement

The goal is to create an Empire-compatible plugin that intercepts operator command submissions, scores them against a transparent, documented heuristic related to noisy vs quieter tradecraft, suggests documented alternative commands from a local knowledge base, and keeps humans in control by never auto-executing alternatives.

## Constraints

- The plugin must match Empire plugin conventions or provide a shim with compatibility notes.
- The solution must be compatible with offline/air-gap environments.
- The scoring engine should use deterministic rules from a `rules.yaml` file.
- The suggestion engine should map rule hits to quieter alternative templates from a local knowledge base with citations.
- The plugin should not auto-execute suggested alternatives.

## Prior Art

- There are no known open projects that directly match the requirements.
- However, there are existing tools and formats that could be aligned with, such as:
  - [Empire](https://github.com/EmpireProject/Empire), an open-source post-exploitation framework.
  - [MITRE ATT&CK](https://attack.mitre.org/), a knowledge base of adversary tactics and techniques.

## Risks

- **Technical Failure Modes:** Incorrect implementation of the scoring engine or suggestion engine could lead to incorrect advice being given to operators.
- **Operational Failure Modes:** If the plugin is not user-friendly, operators may find it difficult to use, which could lead to mistakes being made.

## Open Questions

- **Assumption:** The scoring engine will be based on a set of rules that are documented in a `rules.yaml` file. This assumption is based on the requirement that the scoring engine should be transparent and deterministic.
- **Unknown:** The exact format of the `rules.yaml` file is not known. This will need to be researched further.
- **Unknown:** The exact format of the local knowledge base is not known. This will need to be researched further.