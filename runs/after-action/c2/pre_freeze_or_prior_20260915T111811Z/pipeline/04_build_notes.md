# Build Notes — after-action

**Pipeline step:** 4 / 5  
**Author role:** Tool Architect  
**Date:** 2026-09-03

## Implementation Summary

Complete implementation delivered per `02_plan.md` and `03_ops_constraints.md`. All 11 work packages (WP1-WP11) implemented with no placeholder stubs. Tool successfully generates both client and internal reports from fixture engagement data with validated secret redaction.

## Deviations from Plan

### Minor Adjustments

1. **Redaction pattern syntax (WP4):**
   - **Plan:** Single-quoted regex patterns in YAML
   - **Implemented:** Double-quoted patterns with escaped backslashes
   - **Reason:** YAML parser interpreted brackets in single-quoted strings as flow collections; double-quotes with escaping resolves conflict
   - **Impact:** None (functionally equivalent, YAML spec compliant)

2. **API key pattern length (WP4):**
   - **Plan:** Pattern `{32,}` for OpenAI-style keys
   - **Implemented:** Pattern `{20,}` to match fixture planted secret (30-char suffix)
   - **Reason:** Fixture `sk-test12345678901234567890123456` is 33 total chars (30 after `sk-`), shorter than typical production keys
   - **Impact:** More permissive match catches shorter keys; acceptable for testing, may need tuning per engagement

3. **PDF generation fallback (WP5):**
   - **Plan:** Pandoc required for PDF
   - **Implemented:** Graceful fallback to HTML if Pandoc unavailable, with basic HTML generator as final fallback
   - **Reason:** Ops Advisor constraint for offline/degradation modes
   - **Impact:** Better resilience; client still receives readable output if Pandoc missing

### Enhancements Beyond Plan

1. **Base64 secret detection (WP4):**
   - Added `detect_base64_secrets()` method in Redactor class
   - Not invoked in current pipeline (future enhancement hook)
   - Addresses risk identified in domain brief

2. **Verbose logging mode (WP7):**
   - Added `--verbose` CLI flag for debug-level logging
   - Assists troubleshooting correlation issues
   - Not specified in plan but addresses M3 (graceful degradation)

## Test Results

### Automated Validation (A1, A2, A3, A6, A10)

```bash
# Dry-run validation
$ make validate
✓ Loaded 15 log entries (6 CSV + 9 JSON Lines) → A2
✓ Loaded 6 decision entries
✓ Correlation: 30 log-decision associations → A3 (exceeds minimum 5)
✓ Validation successful → A1

# Report generation
$ make reports
✓ Client report generated (output/client_report.md)
✓ Internal report generated (output/internal_report.md)
✓ Redaction applied: 5 items (1 API key, 3 IPs, 1 email)

# Secret redaction check
$ grep -i "sk-test" output/client_report.md
(no output)
$ grep "REDACTED_API_KEY" output/client_report.md
✓ Found → A6 PASS
```

### Manual Validation (A4, A5, A7, A8, A9, M1, M2)

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| A4 | Client report sections | ✓ PASS | Contains: Exec Summary, Timeline, Findings, Detection Recommendations, Conclusion |
| A5 | Internal report sections | ✓ PASS | Contains: Successes, Failures, Tool Gaps, Reusable TTPs |
| A7 | Internal retains more detail | ✓ PASS | Internal includes full log data fields; client shows excerpts only |
| A8 | OPSEC_CARD Detection Recommendations ≥3 | ✓ PASS | 6 detection recommendations documented |
| A9 | Authorized-use notice | ✓ PASS | Present in README.md + AUTHORIZED_USE.md referenced |
| M1 | Client tone professional | ✓ PASS | No jargon; uses "assessment", "engagement", "security" terminology |
| M2 | Correlation rules documented | ✓ PASS | README "Correlation Rules" section + code comments |
| M3 | Missing fields degrade gracefully | ✓ PASS | Adapters warn on optional fields; continue processing |

### Scanner Results (A10)

**Semgrep:** 22 lines output, no high-severity findings (archived to `scanner_outputs/semgrep_results.txt`)

**ast-grep:** Searched for file operations and subprocess patterns; 1 finding (Pandoc subprocess call, reviewed and deemed low risk) → `scanner_outputs/ast-grep_results.txt`

## Known Gaps

### Implementation Complete

All requirements R1-R10 and acceptance criteria A1-A10 implemented. No stub functions or placeholder code.

### Future Enhancements (Out of Scope)

1. **Automated TTP extraction:** Currently operators manually populate Detection Recommendations; future versions could parse MITRE ATT&CK IDs from logs
2. **Multi-engagement tracking:** Tool processes one engagement per run; no comparison or trend analysis across campaigns
3. **Advanced correlation:** Asset key matching is exact string match; fuzzy matching (IP → hostname resolution) could improve correlation yield
4. **Real-time log streaming:** Currently batch processing only; not required per PROMPT.md non-goals

### Operational Validation Needed

1. **Scale testing:** Fixture uses 15 logs + 6 decisions; production engagements may have 10,000+ entries (performance untested)
2. **Real engagement workflows:** Tested only on synthetic fixture data; real C2 logs, Cobalt Strike output, or network captures not validated
3. **Client acceptance:** Report tone/format validated internally; client-facing delivery not exercised

## How to Run Scanners

### Semgrep

```bash
semgrep --config auto src/ > scanner_outputs/semgrep_results.txt
```

**Patterns checked:** Auto-config includes security, correctness, and best-practice rules for Python

### ast-grep

```bash
# File operations
ast-grep --pattern 'open($PATH)' src/ > scanner_outputs/ast-grep_results.txt

# Subprocess calls
ast-grep --pattern 'subprocess.$FUNC($ARGS)' src/ >> scanner_outputs/ast-grep_results.txt
```

**Patterns checked:** File writes without path validation, subprocess calls with injection risks

## Ops Advisor Constraints Compliance

All plan deltas from `03_ops_constraints.md` implemented:

- [x] WP4: Redaction config loading with `config.local.yaml` override
- [x] WP4: Hard error if client report generated without valid redaction config
- [x] WP4: Allowlist support in YAML config
- [x] WP4: Redaction summary logging
- [x] WP5: Pre-render validation (redactor must be configured)
- [x] WP5: Pandoc fallback to HTML
- [x] WP5: Placeholder comments in Markdown templates
- [x] WP6: Warning banner if internal report contains redaction-matching patterns
- [x] WP6: Full log context retained (no truncation)
- [x] WP7: `--dry-run` flag implemented
- [x] WP7: `--redaction-config` flag implemented
- [x] WP7: `--force` flag implemented
- [x] WP7: Exit codes: 0 (success), 1 (validation error), 130 (KeyboardInterrupt)
- [x] WP8: Fixture includes `planted_secret.txt` documentation
- [x] WP8: Planted secret in decision log rationale field
- [x] WP8: Timestamp variety (UTC normalized by adapters)
- [x] WP10: Evidence handling documented in README
- [x] WP10: Engagement workflow sequence documented
- [x] WP10: "What to .gitignore" section included
- [x] WP10: Troubleshooting "Zero correlations" checklist
- [x] WP11: Semgrep and ast-grep executed and archived

## Dependencies

**Required:**
- Python 3.9+
- PyYAML (redaction config parsing)

**Optional:**
- Pandoc (PDF generation; graceful fallback if absent)

**Development:**
- Semgrep (code scanning)
- ast-grep (AST pattern matching)

## Build/Run Instructions

```bash
# Install dependencies
make install

# Validate fixture data
make validate

# Generate reports
make reports

# Clean outputs
make clean
```

**CLI usage:**
```bash
python -m src.cli \
  --logs-dir testdata/fixture_engagement/logs \
  --decisions testdata/fixture_engagement/decisions.jsonl \
  --output-dir output \
  --engagement-name "Fixture Security Assessment"
```

## Acceptance Status

| Category | Status |
|----------|--------|
| Requirements R1-R10 | ✓ ALL PASS |
| Acceptance A1-A10 | ✓ ALL PASS |
| Manual fidelity M1-M3 | ✓ ALL PASS |
| Ops constraints | ✓ ALL IMPLEMENTED |
| Scanner outputs | ✓ ARCHIVED |

**Overall:** Ready for OPSEC review (Stage 5).

---

**Next stage:** OPSEC Reviewer (`05_opsec_reviewer.md`) performs final security review and produces detection-focused OPSEC card.
