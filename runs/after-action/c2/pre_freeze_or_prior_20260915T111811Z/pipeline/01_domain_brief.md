# Domain Brief — after-action

**Pipeline step:** 1 / 5  
**Author role:** Domain Researcher  
**Date:** 2026-09-03

## Goal restatement

Build an after-action report generator that ingests heterogeneous engagement logs and operator decision records, correlates them on time windows and asset keys, then produces two structured outputs:

1. **Client-facing report** — professional, sanitized deliverable with executive summary, timeline, findings, and detection recommendations
2. **Internal learning summary** — operator-focused retrospective capturing successes, failures, tool gaps, and reusable TTPs

Success = fixture engagement pack renders both reports with planted secrets redacted.

## Constraints

- **Inputs:** Support ≥2 log formats (JSON lines, CSV minimum) via pluggable adapters
- **Decision log schema:** Timestamp, decision text, rationale, related asset identifier
- **Correlation method:** Time window + asset key join (parameterizable)
- **Output formats:** Client report as Markdown + (PDF or HTML); internal as Markdown
- **Redaction:** Configurable regex/rule-based PII/secret scrubbing before client export
- **Platform:** Assume CLI-friendly tooling; no live log streaming from production networks
- **Testability:** Fixture pack under `testdata/fixture_engagement/` with ≥5 correlated timeline items

## Prior art

- **MITRE ATT&CK Navigator** — standard framework for TTP mapping; many orgs expect ATT&CK IDs in reports
- **Elastic Common Schema (ECS)** — widely-adopted log field normalization; adapters should align where possible
- **RedTeam-Toolkit / PurpleSharp** — open-source engagement frameworks; common log patterns to reference
- **Pandoc** — standard Markdown→PDF renderer (assumption: available for client report generation)
- **OWASP Report Template** — established structure for finding severity, remediation sections

Existing tools (Dradis Framework, Serpico) focus on vulnerability management; few open projects address red-team engagement correlation with operator decision tracking. Gap = manual timeline assembly remains common.

## Risks

**Technical:**
- **Format drift** — Logs from different tools may lack common timestamp/asset key fields; adapter degradation handling required
- **Time zone mismatch** — Decision logs vs. system logs in different zones break correlation (mitigation: normalize to UTC)
- **Redaction bypass** — Simple regex misses base64-encoded secrets, environment variables in JSON blobs

**Operational:**
- **Report mishandling** — Client report leaked with internal commentary or insufficient redaction exposes techniques, customer data, or operator identities (OPSEC failure mode)
- **Over-redaction** — Aggressive filtering removes context needed for detection recommendations
- **Correlation noise** — Wide time windows produce false positives; narrow windows miss delayed effects

## Open questions

**Blocking planning:**
1. **Correlation time window default** — Start with ±5 minutes? (Assumption: Yes, make configurable)
2. **Asset key format** — IP, hostname, process ID? (Assumption: Support multiple via adapter-defined mapping)
3. **Detection Recommendations source** — Manual operator input, auto-generated from techniques, or both? (Assumption: Manual placeholders in fixture, documented where operators fill them)

**Non-blocking:**
- PDF vs. HTML choice for client report (either satisfies R4; defer to Planner)
- Internal report format preservation of raw logs vs. summaries (defer to Ops Advisor)

## Assumptions

- Python or Node.js CLI acceptable (not specified; assume Python for data processing ecosystem)
- Operators manually populate findings/detection recommendations in structured placeholders (tool assembles, does not generate content)
- Fixture logs are synthetic/sanitized examples, not real engagement data

---

**Words:** ~485  
**Next stage:** Planner (`02_plan.md`) can decompose into task graph with components: log adapters, correlation engine, redaction module, dual renderers, fixture pack.
