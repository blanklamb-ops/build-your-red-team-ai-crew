 # Operational Constraints for After-Action Collector

## Runtime Environment

1. The tool should be designed to run on a Unix-based operating system (Linux or macOS).
2. The tool should not require administrative privileges to run.
3. The tool should be able to operate in a network-restricted environment.

## Secrets & Evidence Handling

1. Log files and operator decision logs should never be committed to the repository.
2. The tool should include a PII/secret redaction pass to ensure OPSEC compliance.
3. The OPSEC Reviewer must document the presence of a PII/secret redaction pass in the tool.

## Operator Workflow

1. The tool should be invoked using a command-line interface.
2. The operator should provide the paths to the log files, operator decision logs, and the output directory as arguments to the tool.

## Safety Defaults

1. The tool should include a dry-run mode that allows the operator to preview the output without making any changes.
2. The tool should include an allowlist of supported log formats and operator decision log formats.
3. The tool should prompt the operator for explicit confirmation before generating the reports.

## Degradation Modes

1. If the tool is unable to connect to the network, it should operate in offline mode and generate the reports using the locally available data.
2. If the tool encounters a partial failure during the log ingestion, correlation, or reporting processes, it should log the error and continue with the remaining tasks.

## Plan Deltas

1. The Architect must ensure that the log ingestion adapters, correlation engine, and report renderers are designed to handle the specified runtime environment assumptions.
2. The Architect must include a PII/secret redaction pass in the tool and document its presence in the OPSEC card.
3. The Architect must design the tool to operate using a command-line interface and include a dry-run mode, allowlist, and explicit confirmation mechanism.
4. The Architect must design the tool to operate in offline mode and handle partial failures gracefully.
5. The Architect must ensure that the tool's documentation includes detailed instructions on how to use the tool, including examples of the command-line interface and the expected output.