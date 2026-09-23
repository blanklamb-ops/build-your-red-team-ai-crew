 # Empire-Advisor Operational Constraints

## Runtime Environment

1. The tool should be compatible with the Empire platform, which primarily runs on Windows.
2. The tool should operate with the necessary privileges to intercept and modify operator commands.
3. The tool should be able to operate in a network environment with limited outbound connections for air-gap environments.

## Secrets & Evidence Handling

1. The `rules.yaml` file should never be committed to the repository. It should be securely stored and managed separately.
2. The local knowledge base for the suggestion engine should never contain sensitive or classified information.
3. Fixture command transcripts should not contain sensitive or classified information.
4. The OPSEC Reviewer must document the presence and handling of these artifacts.

## Operator Workflow

1. The tool should be invoked by the operator through the Empire platform.
2. The operator should be aware of the tool's capabilities and limitations.
3. The tool should not automatically execute commands without operator confirmation.

## Safety Defaults

1. The tool should operate in a dry-run mode by default, allowing the operator to preview the effects of commands without execution.
2. The tool should have an allowlist of commands that it can intercept and modify.
3. The tool should require explicit operator confirmation for any command that scores above a certain threshold.

## Degradation Modes

1. In offline mode, the tool should fall back to using fixture command transcripts for scoring and suggestion.
2. In the event of a failure in the interceptor module, scoring engine, or suggestion engine, the tool should log the error and continue operating with the available functionality.

## Plan Deltas

1. The Architect must ensure that the `rules.yaml` file is not committed to the repository.
2. The Architect must design the tool to handle the secure storage and management of the `rules.yaml` file.
3. The Architect must define the format and structure of the `rules.yaml` file and document it in the user documentation.
4. The Architect must ensure that the local knowledge base for the suggestion engine does not contain sensitive information.
5. The Architect must define the source and format of the local knowledge base for the suggestion engine and document it in the user documentation.
6. The Architect must ensure that fixture command transcripts do not contain sensitive information.
7. The Architect must define the format and location of fixture command transcripts and document it in the user documentation.
8. The Architect must design the tool to handle offline mode operation using fixture command transcripts.
9. The Architect must design the tool to log errors in the interceptor module, scoring engine, and suggestion engine.
10. The Architect must design the tool to continue operating with available functionality in the event of a failure in the interceptor module, scoring engine, or suggestion engine.