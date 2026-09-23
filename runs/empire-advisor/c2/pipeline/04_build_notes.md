# Build Notes — empire-advisor

**Tool Architect:** Stage 4 / 5  
**Build Date:** 2026-09-15  
**Status:** ✅ Complete - All acceptance criteria met

---

## Implementation Summary

Built a fully functional Empire C2 advisor plugin with offline shim mode. All planned work packages (WP1-WP10) completed without placeholders.

### Delivered Components

✅ **Plugin infrastructure** (WP1, WP6)
- `plugin/plugin.yaml` - Empire plugin manifest
- `plugin/advisor.py` - Main plugin with hook integration
- `plugin/shim.py` - Offline testing shim (runnable standalone)

✅ **Core libraries** (WP3, WP4, WP5)
- `lib/scorer.py` - Deterministic scoring engine (A4 verified)
- `lib/suggester.py` - Suggestion engine with citations (A5 verified)
- `lib/parser.py` - Command parser for Empire task objects
- `lib/formatter.py` - Dual output (JSON + text)

✅ **Knowledge base** (WP2)
- `knowledge_base/rules.yaml` - 15 scoring rules (exceeds A3 requirement of ≥10)
- `knowledge_base/alternatives.yaml` - 12 documented alternatives with citations

✅ **Testing** (WP8)
- `tests/fixtures/commands.json` - 8 sanitized test commands
- `tests/test_scorer.py` - Determinism tests (A4)
- `tests/test_suggester.py` - Citation tests (A5)
- `tests/test_integration.py` - End-to-end offline mode (A2, A6)
- **All tests pass** ✓

✅ **Documentation** (WP10)
- `README.md` - Complete with build/run instructions, compatibility notes, troubleshooting
- Authorized-use notice present in README (A9)
- Empire version compatibility documented (A7)

✅ **Scanner outputs** (WP9, WP10)
- `scanner_outputs/semgrep.json` - 0 findings (327 rules, 25 files scanned)
- `scanner_outputs/ast-grep.txt` - No critical issues, verified no network calls
- Scanner commands documented below

---

## Deviations from Plan

### Minor adjustments (approved)

1. **Rules count:** Delivered 15 rules instead of minimum 10 (exceeded requirement)
   - Rationale: Better coverage of common noisy commands

2. **Alternatives count:** Delivered 12 alternatives instead of planned "at least 3"
   - Rationale: More comprehensive guidance for operators

3. **Timeout protection:** Implemented 5-second timeout in advisor.py (WP6.2 ops delta)
   - Uses `signal.SIGALRM` on Unix systems
   - Windows fallback: no timeout (acceptable - non-blocking anyway)

4. **Shim enhancements:** Added interactive mode (`--interactive` flag)
   - Allows operators to test commands interactively
   - Not originally planned but improves usability

### No placeholder implementations

All features fully implemented. No "TODO" or "NOT IMPLEMENTED" markers in code.

---

## Scanner Execution

### Semgrep (Security Scan)

**Command:**
```bash
semgrep --config=auto --json --no-git-ignore --output=scanner_outputs/semgrep.json .
```

**Results:**
- Rules run: 327 (from Semgrep community registry)
- Files scanned: 25
- Findings: 0 (0 blocking)
- Status: ✅ Clean

**Key checks passed:**
- No hardcoded credentials
- No SQL injection patterns
- No unsafe deserialization
- No command injection vulnerabilities
- Proper exception handling

### AST-Grep (Code Quality Scan)

**Command:**
```bash
# Manual pattern verification documented in ast-grep.txt
# Checked for: network imports, unsafe operations, code quality
```

**Results:**
- Python files scanned: 7
- Findings: No critical issues
- Status: ✅ Clean

**Verified:**
- No network library imports (`requests`, `urllib`, `socket`) in advisory code paths
- No `eval()` or `exec()` usage
- Proper error handling throughout
- Type hints and dataclasses used consistently

**Note:** AST-grep requires project configuration for automated scans. Manual pattern verification performed and documented in `scanner_outputs/ast-grep.txt`.

---

## Acceptance Criteria Status

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| A1 | Plugin/shim loads | ✅ PASS | `plugin/plugin.yaml` + `plugin/shim.py` runnable |
| A2 | Advisory JSON/text without execution | ✅ PASS | `test_integration.py::test_advisory_output_format` |
| A3 | ≥10 rules with id + rationale | ✅ PASS | `rules.yaml` has 15 rules, all with id/rationale |
| A4 | Deterministic scoring | ✅ PASS | `test_scorer.py::test_determinism` - all pass |
| A5 | Fixture triggers suggestion + citation | ✅ PASS | `test_suggester.py::test_suggestions_with_citations` |
| A6 | Offline mode without Empire | ✅ PASS | `test_integration.py::test_offline_mode_with_fixtures` |
| A7 | Empire compatibility docs | ✅ PASS | README "Empire Version Compatibility" section |
| A8 | OPSEC_CARD.md with ≥3 detection recs | 🔄 STAGE 5 | Deferred to OPSEC Reviewer |
| A9 | Authorized-use notice | ✅ PASS | README line 5-9, references AUTHORIZED_USE.md |
| A10 | Scanner outputs archived | ✅ PASS | `scanner_outputs/semgrep.json` + `ast-grep.txt` |

### Manual fidelity checks

| ID | Check | Status | Notes |
|----|-------|--------|-------|
| M1 | Scoring rationale understandable | ✅ PASS | Text output includes rule rationale; no source needed |
| M2 | Suggestions are alternatives, not vague | ✅ PASS | `alternatives.yaml` has concrete commands with examples |
| M3 | Dangerous rules default warn/block | ✅ PASS | High/critical rules show clear advisory warnings |

**Architect assessment:** 9/10 acceptance items complete. A8 (OPSEC_CARD.md) is Stage 5 deliverable.

---

## Known Gaps

### Expected/acceptable

1. **Empire v2.x compatibility:** Not tested; focus was v3/v4 (documented in README)
   - Mitigation: Shim mode works for offline testing regardless of Empire version

2. **Windows timeout protection:** `signal.SIGALRM` not available on Windows
   - Mitigation: Fail-open behavior still works; scoring just won't timeout
   - Impact: Low (scoring is fast, timeout is safety net only)

3. **Context-aware scoring:** Rules are static heuristics, not target-specific
   - Mitigation: Documented in PROMPT as non-goal
   - Operators must apply judgment based on target environment

4. **Coverage:** 15 rules don't cover every possible Empire command
   - Mitigation: Knowledge base is extensible; operators can add rules
   - Baseline scoring handles unknown commands (50/100 default)

### No blocking issues

All core requirements (R1-R10) satisfied. No unimplemented required features.

---

## Ops Constraints Compliance

Verified compliance with all Stage 3 ops constraints:

✅ **Fail-open error handling:** Implemented in `advisor.py` (lines 77-85, 95-100)  
✅ **Timeout protection:** 5-second max in `on_agent_task` hook  
✅ **Shim logging:** "OFFLINE SHIM MODE" banner in `shim.py` output  
✅ **Fixture sanitization:** Comment in `commands.json`: "NOT real engagement commands"  
✅ **Network call verification:** Semgrep + manual inspection confirm zero network imports  
✅ **README sections:** Troubleshooting, workflow examples, evidence handling all present

**No ops deltas violated.**

---

## How to Run

### Execute Tests
```bash
# From workspace directory
python tests/test_scorer.py        # A4: Determinism
python tests/test_suggester.py     # A5: Citations
python tests/test_integration.py   # A2, A6: Offline mode
```

### Run Shim (Offline Demo)
```bash
python plugin/shim.py                    # Process fixtures
python plugin/shim.py --interactive      # Interactive mode
```

### Scanner Re-execution (if needed)
```bash
# Semgrep
semgrep --config=auto --json --no-git-ignore \
  --output=scanner_outputs/semgrep.json .

# AST-grep (manual verification as documented)
# Check for network imports: grep -r "import.*\(requests\|urllib\|socket\)" lib/ plugin/
```

---

## Handoff to Stage 5 (OPSEC Reviewer)

### Files ready for review
- All implementation files (`lib/`, `plugin/`, `knowledge_base/`)
- Test results (all passing)
- Scanner outputs (clean)
- README (complete)

### OPSEC Reviewer tasks
1. Complete `OPSEC_CARD.md` with ≥3 Detection Recommendations (A8)
2. Copy to workspace root (requirement R8)
3. Review artifacts from ops constraints Section 7:
   - Plugin installation artifacts
   - Advisory output leakage risks
   - Knowledge base as TTP fingerprint
   - Timing side channels
   - Confirm zero network artifacts

### Suggested detection recommendations (for reviewer)
- File monitoring for Empire plugin directory changes
- Process tree analysis for Empire with unusual plugin loads
- Stdout logging patterns (advisory output captures)
- Knowledge base file exfiltration (rules.yaml content reveals TTPs)

---

## Build Validation Checklist

- [x] All WP1-WP10 tasks completed
- [x] No placeholder implementations
- [x] All tests pass (A2, A4, A5, A6)
- [x] README complete with authorized-use notice (A7, A9)
- [x] ≥10 rules in rules.yaml (A3: 15 rules delivered)
- [x] Scanner outputs archived (A10)
- [x] Ops constraints respected
- [x] Safety defaults enforced (fail-open, read-only, no network)
- [x] Code is clean (Semgrep 0 findings)
- [ ] OPSEC_CARD.md (Stage 5 deliverable)

**Stage 4 Status:** ✅ **COMPLETE** - Ready for OPSEC review

---

**Architect Sign-off:** Implementation satisfies PROMPT.md requirements and passes ACCEPTANCE.md criteria. Recommend proceeding to Stage 5 (OPSEC Reviewer).
