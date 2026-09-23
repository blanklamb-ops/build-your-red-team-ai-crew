# Operational Constraints — after-action

**Advisor:** ops_advisor  
**Pipeline step:** 3/5  
**Date:** 2026-09-15

## Runtime environment

**Operating System:**
- Primary: Kali Linux 2024+ / Ubuntu 22.04+ (red team standard)
- Python 3.9+ with pip (no conda/pyenv assumptions)
- Offline-first: tool must function without internet after dependency install

**Privileges:**
- Runs as non-root operator user
- No special permissions required (file I/O only)
- Engagement artifacts stored in operator home directory or removable media

**Dependencies:**
- Core: Python standard library (json, csv, argparse, pathlib, re)
- Optional: `markdown`, `weasyprint` (PDF export)
- Documented fallback if weasyprint unavailable (HTML-only mode)

**Portability:**
- No hardcoded paths; use relative or CLI-specified directories
- Line endings: LF (Unix-style; engagement VMs are typically Linux)
- Encoding: UTF-8 with replacement for malformed log bytes

## Secrets & evidence handling

**High-risk data in scope:**
- Operator credentials pasted into decision rationale (careless notes)
- API keys, tokens, hashes in raw logs
- Client PII (email addresses, employee names in phishing logs)
- Internal network details (IP ranges, hostnames, AD domains)

**Mandatory protections:**
1. **No credentials in git** — `.gitignore` for `testdata/` (except checked-in fixtures), `output/`, `config/*.local.json`
2. **Redaction validation** — fixture must include planted secret; acceptance gates on redaction (A6)
3. **Config separation** — `redaction_rules.json` ships with safe defaults; operators extend with `redaction_rules.local.json` (merged at runtime, gitignored)
4. **Internal vs client split** — client report redacted; internal report retains detail (A7). README warns: "Internal report contains engagement secrets — store offline, encrypt at rest."

**Chain of custody:**
- Tool does NOT timestamp-hash logs for integrity (out of scope)
- OPSEC card must warn: operators are responsible for preserving original log files for evidence integrity; this tool is for reporting, not forensic preservation

## Operator workflow

**Typical engagement closeout:**
1. Operator collects logs from tools (Cobalt Strike, Gophish, custom scripts) into staging directory
2. Writes decision log during or immediately after engagement (JSON Lines with timestamp, decision, rationale, asset)
3. Runs tool: `python src/cli.py --engagement-dir ./engagement-2024-09-15 --output-dir ./reports`
4. Reviews generated client report, manually fills placeholders (exec summary, findings detail)
5. Applies additional redaction if automated rules missed edge cases
6. Exports final client PDF, delivers with OPSEC card

**Critical UX requirements:**
- **Dry-run mode:** `--dry-run` flag previews redaction without writing reports (operator validates rules)
- **Verbose logging:** `--verbose` shows adapter warnings, missing fields, correlation misses (helps debug incomplete logs)
- **Config validation:** Fails fast on malformed JSON, bad regex syntax (don't silently skip rules)

**Expected invocation time:** Seconds for fixture (100s of log lines), < 1 minute for real engagement (1000s of lines). No progress bar needed.

## Safety defaults

**Fail-safe behaviors:**
1. **Adapter errors:** Bad log line → warning to stderr, skip line, continue (don't abort on one malformed entry)
2. **Missing decision log:** Warning + generate reports with "No operator decisions recorded" (degraded but functional)
3. **Redaction rule errors:** Catch `re.error`, log which rule failed, skip that rule (don't leak secrets due to regex typo)
4. **Timestamp parse failures:** Log warning with line number, skip correlation for that event (degrade gracefully per M3)

**Confirmations (not required, but document in README):**
- No interactive prompts by default (batch tool)
- Operator reviews output before client handoff (human-in-loop for final redaction check)

**Dry-run implementation (WP8 delta):**
- Add `--dry-run` flag to CLI
- Run adapters → correlation → redaction
- Print redaction diff (original → redacted excerpts) to stdout
- Do NOT write report files
- Exit 0 if successful

## Degradation modes

**Offline operation:**
- No external API calls (no telemetry, no update checks)
- All dependencies installable via `pip install -r requirements.txt` (pin versions)
- Document: `pip download -r requirements.txt -d ./vendor/` for air-gapped transfer

**Partial failure scenarios:**

| Failure | Behavior | Exit Code |
|---------|----------|-----------|
| No logs found | Error, print path, exit | 1 |
| No decision log | Warn, continue, reports note "no decisions" | 0 |
| All log lines malformed | Error, "no parseable events", exit | 1 |
| Some log lines malformed | Warn per line, process valid subset | 0 |
| Redaction rules file missing | Warn, skip redaction (dangerous!), note in report header | 0 |
| PDF export fails (weasyprint not installed) | Warn, skip PDF, generate HTML + Markdown only | 0 |
| Output dir not writable | Error, fail fast | 1 |

**Missing correlation matches:**
- If 0 correlated items: warn, generate reports with timeline of all events + all decisions (un-joined)
- If < 5 correlated items (A3 threshold): warn, but still generate reports (may indicate bad time sync or asset key mismatch)

## Plan deltas (Architect must implement)

**WP2 (Adapters) changes:**
- Add `--verbose` flag support; adapters log warnings to stderr when enabled
- CSV adapter: infer timestamp field from header (configurable fallback: `timestamp`, `time`, `datetime`)

**WP5 (Redaction) changes:**
- Merge `redaction_rules.json` + `redaction_rules.local.json` if present
- Wrap regex compile in try/except, log rule name on failure

**WP6 (Client report) changes:**
- Insert header if redaction was skipped: `⚠️ WARNING: Redaction rules not applied. Review for secrets.`
- Document in README: operators must manually review client report before export

**WP8 (CLI) changes:**
- Add flags: `--dry-run`, `--verbose`, `--skip-pdf`
- Validate engagement directory structure (logs/, decisions.jsonl exist)
- Exit codes per degradation table

**WP9 (Fixtures) changes:**
- Include `redaction_rules.json` with rule matching planted secret
- Add malformed log line to one fixture (test graceful skip per M3)

**WP10 (Docs) changes:**
- README section: "Secrets Handling" — internal vs client report, gitignore, manual review requirement
- README section: "Offline Use" — pip download for air-gapped environments
- OPSEC card (stage 5) must include: evidence chain of custody warning, client report review checklist

## Detection-relevant artifacts (for OPSEC Reviewer)

The OPSEC Reviewer must document these in Detection Recommendations:

1. **Report files on disk** — `client_report.md`, `internal_report.md` in predictable output directory (forensic artifact on operator VM)
2. **Decision log format** — JSON Lines with timestamps; anomaly detection could flag rapid-fire decision entries (automated vs human-paced)
3. **Redaction patterns** — repeated `REDACTED` strings may indicate sanitization before exfil; defenders could signature on redaction artifacts
4. **Process execution** — Python interpreter running `cli.py` with engagement directory args (EDR telemetry)
5. **Network silence** — tool makes zero network calls; absence of DNS/HTTP from reporting script distinguishes from exfil-aware malware

## Non-negotiable constraints summary

For Architect checklist:

- [ ] `--dry-run` flag implemented (WP8)
- [ ] `--verbose` adapter warnings (WP2)
- [ ] Redaction rule merge + error handling (WP5)
- [ ] Internal report gitignore + README warning (WP10)
- [ ] Graceful degradation on missing decision log (WP3)
- [ ] Exit codes per degradation table (WP8)
- [ ] Fixture includes malformed log line (WP9)
- [ ] No hardcoded paths; CLI args only (WP8)
- [ ] UTF-8 encoding with replacement (WP2)
- [ ] Offline dependency documentation (WP10)

---
**Ops Advisor complete.** Architect has operational guardrails preventing credential leaks and ensuring engagement-safe defaults.
