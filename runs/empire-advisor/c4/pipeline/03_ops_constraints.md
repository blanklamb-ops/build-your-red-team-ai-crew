 # Empire-Advisor Operational Constraints

## Runtime Environment

1. The plugin will run on Windows operating systems.
2. The plugin will require administrative privileges to function properly.
3. The plugin will assume that it has access to a local network for command execution.
4. The plugin will assume that it has access to a local file system for reading and writing files.

## Secrets & Evidence Handling

1. The `rules.yaml` file and the local knowledge base must never be committed to the repository.
2. The plugin must handle secrets (such as passwords) securely and not log them.
3. The plugin must not store any evidence of its operation on the target system.

## Operator Workflow

1. The plugin will be invoked by the operator through the Empire framework.
2. The operator will be presented with the original command and any suggested alternatives.
3. The operator will have the final decision on which command to execute.

## Safety Defaults

1. The plugin will operate in dry-run mode by default, meaning that it will not execute any commands.
2. The plugin will have an allowlist of commands that it is allowed to suggest alternatives for.
3. The plugin will require explicit confirmation from the operator before executing any command.

## Degradation Modes

1. If the plugin is unable to access the local network, it will not be able to suggest alternatives.
2. If the plugin is unable to access the local file system, it will not be able to read the `rules.yaml` file or the local knowledge base.
3. If the plugin is unable to score a command, it will not be able to suggest alternatives.

## Plan Deltas

- The Architect must ensure that the `rules.yaml` file and the local knowledge base are not committed to the repository.
- The Architect must ensure that the plugin handles secrets securely and does not log them.
- The Architect must ensure that the plugin does not store any evidence of its operation on the target system.
- The Architect must ensure that the plugin operates in dry-run mode by default and requires explicit confirmation from the operator before executing any command.
- The Architect must ensure that the plugin has an allowlist of commands that it is allowed to suggest alternatives for.
- The Architect must ensure that the plugin is compatible with Windows operating systems and requires administrative privileges.
- The Architect must ensure that the plugin assumes access to a local network for command execution and a local file system for reading and writing files.
- The Architect must ensure that the plugin is designed to handle degradation modes gracefully.