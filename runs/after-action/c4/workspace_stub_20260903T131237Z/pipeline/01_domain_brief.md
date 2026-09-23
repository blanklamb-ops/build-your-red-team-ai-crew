 # Domain Brief: After-Action Collector

## Operator Goal

The After-Action Collector is a tool designed to generate two reports: a client-facing report and an internal learning summary. The tool ingests various log formats and operator decision logs, correlates events with decisions, and produces structured reports.

## Constraints

- The tool should support ingesting at least two log formats (JSON lines and CSV) via adapters.
- The tool should have a configurable PII/secret redaction pass before client export.
- The tool should produce both reports in Markdown and PDF or HTML format.
- The tool should be offline/air-gap compatible.
- The tool should not require live log shipping from production client networks during the study.

## Prior Art

- There are no known open projects that directly align with the After-Action Collector's requirements.
- However, there are existing tools for log aggregation and correlation, such as Elasticsearch and Logstash, which could be used as a basis for the correlation engine.
- Markdown is a widely-used format for creating reports, and there are numerous tools available for rendering Markdown to PDF or HTML.

## Risks

- **Technical Failure Modes:** Incorrectly parsing log formats, failing to correlate events with decisions, or producing incorrect reports.
- **Operational Failure Modes:** Mishandling of sensitive information in the reports, leading to OPSEC failures.

## Open Questions

- The exact format of the operator decision log is not specified. Assuming a CSV format with columns for timestamp, decision, rationale, and related asset.
- The exact requirements for the PII/secret redaction pass are not specified. Assuming a configuration file with regex patterns for redaction.
- The exact format for the client-facing report is not specified. Assuming a standard format with sections for an executive summary, timeline, findings, and detection recommendations.
- The exact format for the internal learning summary is not specified. Assuming a format that highlights successes, failures, tool gaps, and reusable TTPs as references.