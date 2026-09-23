 # Domain Brief: After-Action Collector

## Operator Goal

The primary goal of the After-Action Collector is to create two reports: a client-facing report and an internal learning summary. The tool should ingest at least two log formats and an operator decision log, correlate events with decisions, and render both reports in a structured and reproducible manner. The client report should be professional and non-jargony, while the internal learning summary should highlight successes, failures, tool gaps, and reusable TTPs.

## Constraints

- The tool should be able to ingest JSON lines and CSV formats.
- The tool should support adapters for additional log formats if necessary.
- The tool should support operator decision logs in a structured format.
- The tool should support correlation of events and decisions based on time window and asset key.
- The tool should support rendering of the client report in Markdown and PDF or HTML.
- The tool should support rendering of the internal learning summary in a structured format.
- The tool should support PII/secret redaction before client export.
- The tool should include a fixture engagement pack under `testdata/` to produce both reports.
- The tool should include an `OPSEC_CARD.md` to explain how report mishandling becomes an OPSEC failure.
- The tool should include a README and authorized-use notice.
- The tool should archive scanner outputs.

## Prior Art

- There are no known open projects that directly align with the requirements of the After-Action Collector.
- However, there may be existing log correlation tools or report generation tools that could be adapted to meet the requirements.

## Risks

- Technical risks include difficulties in ingesting and correlating log data, rendering reports, and redacting PII/secrets.
- Operational risks include misuse of the tool, mishandling of reports, and failure to learn from past engagements.

## Open Questions

- What is the expected format of the operator decision log?
- What is the expected format of the PII/secret redaction rules?
- How will the tool handle large volumes of log data?
- How will the tool handle real-time log shipping during the study? (This is a non-goal.)
- How will the tool support automated grading of operator skill? (This is a non-goal.)