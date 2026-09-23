 # Operational Constraints for After-Action Collector

## Runtime Environment

- **Operating System:** The tool should be compatible with major operating systems (Windows, Linux, macOS).
- **Privileges:** The tool should not require elevated privileges to run.
- **Network:** The tool should be offline/air-gap compatible. However, it may require internet access for certain features (e.g., report generation).

## Secrets & Evidence Handling

- **Never Commit:** The tool should not commit sensitive information to version control. This includes but is not limited to:
  - Log files
  - Decision logs
  - Redaction configuration files
  - Generated reports
- **OPSEC Reviewer Artifacts:** The OPSEC Reviewer must document the handling of sensitive information in the tool's design and operation.

## Operator Workflow

- **Invocation:** The tool should be invoked from the command line with the following arguments:
  - Log files (required)
  - Decision log (required)
  - Output format (Markdown, PDF, or HTML) (optional, default: Markdown)
- **Configuration:** The tool should use a configuration file (`redaction_config.json`) for the PII/secret redaction pass.

## Safety Defaults

- **Dry-Run:** The tool should have a dry-run mode that generates reports without modifying any data.
- **Allowlists:** The tool should have an allowlist for log formats and output formats to prevent unsupported files from being processed.
- **Explicit Confirmations:** The tool should prompt the user for confirmation before generating reports in PDF or HTML format, as these formats may contain sensitive information.

## Degradation Modes

- **Offline:** If the tool is offline, it should still be able to generate Markdown reports.
- **Partial Failure:** If the tool encounters a failure during report generation, it should still generate a Markdown report with the available data.

## Plan Deltas

- The Architect must ensure that the tool's design and implementation meet the operational constraints outlined in this document.
- The Architect must document any deviations from these constraints in the tool's design documentation.
- The Architect must ensure that the tool's documentation includes instructions for operating the tool in a secure and compliant manner.
- The Architect must ensure that the tool's source code is reviewed by the OPSEC Reviewer before release.