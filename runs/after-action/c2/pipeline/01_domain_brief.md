# Domain Brief — after-action

**Tool slug:** `after-action`  
**Research date:** 2026-09-15  
**Researcher:** domain_researcher

## Goal restatement

Build an after-action report generator that transforms raw engagement artifacts (logs, operator notes) into two distinct deliverables:

1. **Client-facing report** — professional, accessible writeup with executive summary, timeline, findings placeholders, and detection recommendations suitable for handoff
2. **Internal learning summary** — candid operator debrief documenting successes, failures, tool gaps, and reusable TTPs for team knowledge retention

Success means reproducible report generation from structured inputs with automated PII/secret redaction before client export.

## Constraints

**Platform/Language:**
- ASSUMPTION: Python 3.9+ (ubiquitous on Kali/engagement VMs, strong ecosystem for log parsing)
- Must run offline (engagement networks often lack internet; no cloud dependencies)
- PDF rendering requires headless solution (wkhtmltopdf, weasyprint, or Markdown→HTML→PDF)

**Input formats:**
- Minimum two log adapters: JSON Lines (common for tool outputs) and CSV (spreadsheet exports)
- Operator decision log: structured format with timestamp, decision, rationale, asset correlation key
- ASSUMPTION: UTC timestamps; correlation relies on synchronized clocks

**Output formats:**
- Client report: Markdown primary + PDF or HTML export
- Internal report: Markdown acceptable (team tooling assumption)

**Data handling:**
- Redaction pass before client export (regex/rule-based)
- ASSUMPTION: secrets appear as plaintext in logs (base64/encoded variants out of scope)

## Prior art

**Report generation:**
- **Plextrac / Pwndoc** — web-based engagement reporting platforms; overkill for post-engagement batch processing
- **Dradis Framework** — collaborative reporting; requires server infrastructure
- **Ghostwriter** — Django-based; too heavy for single-operator closeout workflow

**Log correlation:**
- **Splunk / ELK** — enterprise SIEM; assumes live aggregation, not post-engagement batch
- **Timesketch** — forensic timeline tool; closer match but requires PostgreSQL/Elasticsearch

**Format alignment:**
- JSON Lines: one JSON object per line, newline-delimited (e.g., `{"timestamp": "...", "event": "..."}`)
- CSV: RFC 4180 compliant with header row
- Markdown: CommonMark spec for client report portability

**Gap justification:**
- Existing platforms assume persistent infrastructure or web UIs. This tool targets single-operator, offline, batch processing with zero setup beyond Python dependencies.

## Risks

**Technical:**
1. **Timestamp ambiguity** — mixed timezones or missing TZ info breaks correlation; mitigation: enforce UTC or explicit TZ field
2. **Schema variability** — real logs have inconsistent field names; adapter layer must handle missing/optional fields gracefully (ACCEPTANCE M3)
3. **PDF rendering fragility** — HTML→PDF tools are finicky with CSS/images; fallback to styled HTML output acceptable
4. **Redaction false negatives** — regex misses obfuscated secrets; OPSEC card must warn operators to manual review

**Operational:**
1. **Report mishandling** — client report with insufficient redaction leaks engagement details; OPSEC card critical
2. **Incomplete decision log** — operator forgets to log key decisions during engagement; tool can't invent context
3. **Fixture validity** — synthetic test data doesn't expose edge cases in real log formats

## Open questions

1. **Correlation window size** — default time window for join (±5 min? ±1 hour?)  
   **ASSUMPTION:** Configurable, default ±10 minutes

2. **Asset key format** — IP? hostname? FQDN? mixed?  
   **ASSUMPTION:** Treat as opaque string; exact match only (operator responsibility to normalize)

3. **Decision log schema** — JSON? YAML? structured CSV?  
   **ASSUMPTION:** JSON Lines matching log format pattern (consistency over bike-shedding)

4. **Client report tone** — "professional" ranges from SANS-style technical to management-friendly executive brief  
   **ASSUMPTION:** Mid-technical (assumes IT/security reader, minimal jargon, explain TTPs in context)

5. **Scanner integration** — Semgrep/ast-grep run manually or via Makefile?  
   **ASSUMPTION:** Documented Make targets; acceptance requires archived outputs (R10)

## Deliverable

This brief provides sufficient grounding for a Planner to decompose work packages without re-researching log formats, correlation algorithms, or reporting platform choices. Next stage must define module boundaries and requirement traceability.

---
**Word count:** ~680
