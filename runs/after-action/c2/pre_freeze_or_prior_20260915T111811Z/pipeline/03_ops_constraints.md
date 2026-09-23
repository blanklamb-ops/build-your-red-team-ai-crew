# Ops Constraints — after-action

**Pipeline step:** 3 / 5  
**Author role:** Ops Advisor  
**Input:** `01_domain_brief.md`, `02_plan.md`, `PROMPT.md`  
**Date:** 2026-09-03

## Runtime environment

**Operator workstation:**
- OS: Linux/macOS preferred; Windows WSL2 acceptable
- Python 3.9+ with virtualenv isolation (no system package pollution)
- Pandoc for PDF generation (optional; HTML fallback if unavailable)
- Privileges: Standard user (no root/admin required)
- Network: Offline-capable (no external API calls during report generation)

**Filesystem assumptions:**
- Working directory: Temporary engagement workspace (deleted post-delivery)
- Input logs: Read-only access; never modified in place
- Output directory: Isolated from source logs (prevent accidental overwrites)
- Config files: Version-controlled defaults; per-engagement overrides in `.gitignore`d `config.local.yaml`

**Memory/scale:**
- Target: <100MB log corpus per engagement (realistic red-team engagement size)
- Fallback: Warn if input exceeds 500MB; suggest log filtering/splitting

## Secrets & evidence handling

**Never commit to version control:**
- Real engagement logs (`testdata/fixture_engagement/` is synthetic only; add `logs_*` to .gitignore)
- Operator decision logs from actual operations
- Generated reports (`output/` directory gitignored)
- Per-engagement redaction configs (`config.local.yaml`)
- Client identifiers, IP addresses, hostnames from real networks

**Evidence chain:**
- Input logs: Assume already sanitized by operator before ingestion (tool is not primary evidence store)
- Intermediate state: No temp files with unredacted data (process in-memory or clean on exit)
- Output reports: Store in encrypted volume or secure transfer staging area (document in README)

**Redaction failure = hard error:**
- If redaction rules fail to load, abort client report generation (never fallback to unredacted)
- Log warning if internal report contains patterns matching redaction rules (operator review reminder)

## Operator workflow

**Typical engagement closeout sequence:**

1. **Collect logs** from C2 infrastructure, traffic captures, tool outputs → single staging directory
2. **Author decision log** in text editor or structured form (JSONL with required fields)
3. **Configure redaction** (optional): Copy `config/redaction_rules.yaml` → `config.local.yaml`; add client-specific patterns (e.g., company name, project codenames)
4. **Run tool:**
   ```bash
   make reports  # Uses testdata for validation
   # OR for real engagement:
   python -m src.cli \
     --logs-dir /path/to/engagement/logs \
     --decisions /path/to/decisions.jsonl \
     --redaction-config config.local.yaml \
     --output-dir output
   ```
5. **Review both reports** (internal first to validate correlation quality)
6. **Manual content addition:** Edit client report Markdown to populate findings/recommendations placeholders
7. **Final redaction check:** `grep -E 'sk-|192\.168\.' output/client_report.md` (example; automate in Makefile)
8. **Generate PDF:** `make pdf` or manual Pandoc invocation
9. **Secure delivery:** Transfer via established client channel; delete staging artifacts

**Pain points addressed:**
- No live log streaming (complexity); operator collects logs manually (boring, reliable)
- Explicit redaction config (no "smart" guessing that misses edge cases)
- Markdown-first output (diff-able, version-controllable, human-editable)

## Safety defaults

**Dry-run mode:**
- CLI flag `--dry-run`: Parse logs, run correlation, show summary stats, but do not write reports
- Logs correlated item count, redaction rule matches, missing fields detected

**Confirmation prompts:**
- None required (batch tool for post-engagement use; interactive mode adds friction)
- Instead: Makefile target `make validate` runs dry-run + checks

**Allowlists:**
- Redaction: Operator can mark safe strings in `config.local.yaml` `allowlist:` section (e.g., "ACME Corp" when that's the client name in report)
- Adapters: Warn if log file extension not in `[.jsonl, .json, .csv]` (prevent accidental binary ingestion)

**Report overwrite protection:**
- If `output/client_report.md` exists and differs from expected fixture output, prompt "Overwrite existing report? [y/N]" unless `--force` flag set
- Internal report: Always overwrite (assumed iterative operator workflow)

## Degradation modes

**Missing log fields:**
- Required: `timestamp`, `asset_key` (or mappable equivalent) → Adapter raises error with helpful message
- Optional: `event_type`, `severity` → Warn, populate with "unknown", continue
- Document expected field names per adapter in README (M2 requirement)

**Correlation failures:**
- Zero correlated items: Generate reports with empty timeline + warning banner "No correlations found; check time zones and asset key format"
- Partial correlation (1-4 items when ≥5 expected): Warn but proceed (better than nothing)

**Offline / no Pandoc:**
- Graceful fallback to HTML output (CSS-styled for print)
- Log info-level message: "Pandoc not found; generating HTML instead of PDF"

**Redaction config missing:**
- Use default `config/redaction_rules.yaml`
- Warn: "Using default redaction rules; consider client-specific config"

**Decision log missing:**
- Generate reports without correlation (logs-only timeline)
- Warn prominently in both reports: "No operator decisions provided; timeline is raw log sequence"

## Plan deltas

**Concrete changes the Tool Architect must respect:**

### WP4 (Redaction module) — MUST implement:
- [ ] Load `config.local.yaml` if exists, else `config/redaction_rules.yaml`
- [ ] Hard error (exit code 1) if client report generation attempted when redaction config invalid
- [ ] Allowlist support: `allowlist: ["safe_string"]` in YAML excludes from redaction
- [ ] Log redaction summary: "Redacted N secrets across M fields"

### WP5 (Client report renderer) — MUST implement:
- [ ] Pre-render validation: Fail if unredacted data detected (configurable pattern check)
- [ ] Pandoc fallback: Try Pandoc; if unavailable, generate HTML with print-friendly CSS
- [ ] Placeholder comments in Markdown template: `<!-- TODO: Operator fill findings here -->`

### WP6 (Internal report renderer) — MUST implement:
- [ ] Warning banner if report contains strings matching redaction patterns (visual reminder)
- [ ] Retain full log context (no truncation) for operator review

### WP7 (CLI) — MUST implement:
- [ ] `--dry-run` flag: Parse + validate, log summary, no output files
- [ ] `--redaction-config <path>` flag: Override default config
- [ ] `--force` flag: Skip overwrite protection
- [ ] Exit code 0 on success, 1 on validation error, 2 on missing dependencies (Pandoc optional)

### WP8 (Fixture pack) — MUST implement:
- [ ] Include `config.local.yaml` example with client-specific pattern override
- [ ] Planted secret in decision log rationale field (tests WP4 integration)
- [ ] Timestamp variety: Different time zones in raw logs, normalized in adapter output (tests WP3 robustness)

### WP10 (README) — MUST document:
- [ ] Evidence handling best practices (encrypted storage, secure deletion post-delivery)
- [ ] Engagement workflow sequence (section above as starting point)
- [ ] "What to gitignore" section listing real engagement artifacts
- [ ] Troubleshooting: "Zero correlations" checklist (time zone, asset key mapping, window size)

### WP11 (Scanner outputs) — MUST run:
- [ ] Semgrep: Check for hardcoded secrets in code (irony detector)
- [ ] Ast-grep: Detect file write operations without explicit path validation (prevent path traversal)

## Detection-relevant artifacts

**For OPSEC Reviewer (WP9) to document:**
- Client report file metadata (modification timestamps reveal engagement end date)
- Redaction config patterns (enumeration reveals threat model: AWS keys, internal domains, etc.)
- Correlation time window size (tuned window = operator knows dwell time)
- Report template structure (fingerprints the team's methodology)
- Pandoc/Python version strings in PDF metadata (toolchain profiling)

**Mitigation notes:**
- Strip PDF metadata before delivery (`exiftool -all= client_report.pdf`)
- Randomize placeholder text in templates (avoid verbatim "TODO" strings as fingerprints)
- Store redaction configs outside repository (per-engagement secrets management)

---

**Next stage:** Tool Architect (`04_tool_architect.md`) implements WP1-WP11 respecting all constraints above, especially plan deltas checklist.
