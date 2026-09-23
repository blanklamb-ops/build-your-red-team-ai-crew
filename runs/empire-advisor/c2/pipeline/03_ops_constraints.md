# Ops Constraints — empire-advisor

## 1. Runtime environment assumptions

### Operating system & privileges
- **Primary:** Kali Linux / Debian-based pentesting distros (Python 3.7+)
- **Secondary:** Windows with WSL2 / macOS for lab testing
- **Privileges:** User-level (no root/admin required for advisory function)
- **Empire installation:** Optional — plugin works standalone via shim if Empire absent

### Dependencies
- **Required:** Python 3.7+, PyYAML (pip-installable)
- **Optional:** Empire framework v3.x or v4.x for live plugin integration
- **Network:** None required (fully offline capable)
- **Disk:** <10 MB for plugin + knowledge base

### Lab vs. engagement environments
- **Lab:** Can test with shim + fixtures; no live C2 needed
- **Engagement:** Operator's Empire instance (team server or local)
- **Air-gap compatible:** Yes — all knowledge base files local

## 2. Secrets & evidence handling

### No secrets in this tool
- **Plugin contains:** Public scoring rules and alternative command templates only
- **No credentials stored:** Plugin does not handle target credentials, session tokens, or loot

### Evidence considerations
- **Advisory logs:** If operator saves advisory output, treat as engagement evidence
  - **MUST NOT commit to git:** Actual command submissions from real engagements
  - **Safe to commit:** Fixture commands in `tests/fixtures/` (sanitized examples only)
  
### Data to scrub before sharing
- ❌ **Never commit:** Real target commands, agent callback IPs, session IDs
- ✅ **Safe to share:** Generic rules ("shell whoami"), sanitized alternatives

### Build artifacts
- Scanner outputs (`scanner_outputs/`) are clean — no target data, safe to archive

## 3. Operator workflow

### Invocation scenarios

**Scenario 1: Live Empire integration**
1. Operator installs plugin to Empire's `plugins/` directory
2. Empire loads plugin on startup (or via `plugin load empire-advisor`)
3. Operator submits command to agent via Empire CLI/Starkiller
4. Plugin hook fires → advisory appears in console **before execution**
5. Operator reviews advisory, decides to proceed/modify/cancel
6. Original command executes unchanged (plugin is read-only)

**Scenario 2: Offline review (shim mode)**
1. Operator has list of planned commands in `tests/fixtures/commands.json`
2. Run `python plugin/shim.py` to replay commands through advisory engine
3. Review all advisories, adjust engagement plan accordingly
4. Execute refined commands in real Empire separately

**Scenario 3: Pre-engagement planning**
1. Red team reviews common commands against `rules.yaml`
2. Updates `alternatives.yaml` with target-specific safer options
3. Runs offline scoring to build low-noise command cheat sheet
4. Uses cheat sheet during engagement (advisory system not active on target network)

### When operator should NOT use this tool
- ❌ **Emergency active defense:** Scoring adds latency; don't use mid-incident response
- ❌ **Unattended automation:** Advisory requires human review; not for scripted mass tasking
- ❌ **Zero-day C2 frameworks:** Plugin targets Empire API; other C2s need adapted shim

## 4. Safety defaults

### Non-negotiable defaults (Architect must implement)

1. **Read-only operation**
   - Plugin NEVER modifies the operator's original command
   - Hook observes task, outputs advisory, allows original task to proceed
   - **Rationale:** Prevent plugin bugs from breaking operator's workflow

2. **Fail-open on errors**
   - If scoring engine crashes → log error, allow command to proceed with warning
   - If rules.yaml missing/corrupt → warn "advisory disabled", allow command
   - **Rationale:** Plugin should never block operator during time-sensitive engagement

3. **Explicit severity labeling**
   - Rules must specify severity: `low`, `medium`, `high`, `critical`
   - High/critical rules MUST include clear rationale in advisory output
   - **Rationale:** Operator needs to understand urgency without reading source code

4. **No external network calls**
   - Hardcoded: no HTTP requests, no DNS lookups, no remote KB fetching
   - **Rationale:** Prevent plugin from generating unexpected network traffic in sensitive environments

5. **Conservative scoring baseline**
   - Default baseline score: 50 (medium)
   - Rules add/subtract from baseline
   - Unknown commands default to baseline, not "safe"
   - **Rationale:** Unknown ≠ safe; operator should investigate unrecognized commands

### Configuration safety

- **rules.yaml:** Must be readable text (no binary/encrypted formats) so operator can audit scoring logic
- **alternatives.yaml:** Must cite sources (no "trust us" suggestions)
- **No auto-update mechanism:** Operator must manually review KB changes before deployment

## 5. Degradation modes

### Partial failure handling

| Failure Scenario | Behavior | Operator Visibility |
|------------------|----------|---------------------|
| rules.yaml missing | Advisory disabled; all commands allowed | Warning logged: "Advisory KB not found" |
| alternatives.yaml missing | Scoring works; suggestions empty | Advisory shows scores + rules, no suggestions section |
| Malformed rule in rules.yaml | Skip bad rule; process remaining rules | Warning logged with rule ID |
| Plugin hook fails to register | Empire runs normally without plugin | Empire startup error (document in README troubleshooting) |
| Scoring timeout (>5 sec) | Abort scoring, allow command with warning | "Advisory timeout - command allowed" |

### Offline vs. online mode

- **This tool is offline-only by design** (no "online mode" degradation)
- If operator expects plugin in live Empire but it's not loaded → no advisory appears → document how to verify plugin status in README

### Empire version mismatches

- If plugin API incompatible → shim mode is fallback
- README must document tested Empire versions (e.g., "tested on v4.x, may require shim for v3.x")

## 6. Plan deltas (required changes to WP plan)

### ✅ Approve as-is:
- WP1-WP2: Core infrastructure and KB design
- WP3: Scoring engine (determinism requirement aligns with safety)
- WP4: Suggester
- WP5: Formatter

### 🔧 Modify these work packages:

**WP6.2 (Plugin implementation) — ADD:**
- **Fail-open error handling:** Wrap scoring/suggestion calls in try/except
  - On exception: log error, output "ADVISORY UNAVAILABLE - command allowed", proceed
  - Test case: corrupt rules.yaml should not crash Empire
- **Timeout protection:** 5-second max for scoring engine
  - Rationale: Prevent regex DoS from malicious rule patterns

**WP7 (Shim) — ADD:**
- **Shim must log clearly:** Output "OFFLINE SHIM MODE" banner on startup
  - Rationale: Prevent operator confusion between shim and live Empire
- **Fixture commands must be sanitized:** Include comment in commands.json: "# SANITIZED LAB EXAMPLES ONLY"

**WP9 (Static analysis) — ADD:**
- **Scan for network calls:** ast-grep should check for `requests`, `urllib`, `socket` imports
  - If found in advisory code paths → fail build
  - Rationale: Enforce no external network requirement

**WP10 (Documentation) — ADD to README:**
- **Troubleshooting section:**
  - How to verify plugin loaded in Empire
  - How to check rules.yaml syntax with `pyyaml`
  - What to do if advisory doesn't appear
- **Engagement workflow examples:** Pre-engagement review vs. live integration modes
- **Evidence handling:** "Do not commit real engagement command logs"

### 🚨 New work package (insert before WP11):

**WP10.5: Operational smoke test**
- **Tasks:**
  - WP10.5.1: Create `smoke_test.sh` script that:
    - Loads shim mode
    - Submits 3 fixture commands (low/medium/high severity)
    - Asserts advisory output appears for each
    - Asserts commands are NOT modified
  - WP10.5.2: Document in README: "Run `./smoke_test.sh` to verify installation"
- **Rationale:** Operator needs quick confidence check before engagement

## 7. Detection-relevant artifacts (for OPSEC Reviewer)

### The OPSEC Reviewer (Stage 5) MUST document:

1. **Plugin installation artifacts:**
   - `empire/plugins/empire-advisor/` directory presence
   - Empire startup logs showing plugin registration
   - Detection opportunity: Hunt for new Empire plugins on known C2 infrastructure

2. **Advisory output leakage:**
   - If operator redirects stdout to file → advisory logs on disk
   - May contain command history revealing techniques
   - Detection: File monitoring for Empire operators saving advisory output

3. **Knowledge base as TTP fingerprint:**
   - `rules.yaml` content reveals red team's OPSEC priorities
   - `alternatives.yaml` reveals preferred quiet techniques
   - Detection: If plugin files exfiltrated, blue team can anticipate operator behavior

4. **Timing side channel:**
   - Scoring adds milliseconds before command execution
   - Unusual delay patterns may indicate advisory review
   - Low-priority detection signal, but document

5. **No network artifacts:**
   - Plugin generates ZERO network traffic (verify in WP9 scans)
   - This is a defensive strength — document clearly

## Ops constraints validation

✅ **Runtime:** Offline, user-level, cross-platform Python  
✅ **Secrets:** None handled; evidence scrubbing rules documented  
✅ **Workflow:** 3 usage scenarios defined (live/offline/planning)  
✅ **Safety:** 5 non-negotiable defaults specified  
✅ **Degradation:** 5 failure modes with explicit behaviors  
✅ **Plan deltas:** 4 WP modifications + 1 new WP for smoke test  
✅ **OPSEC handoff:** 5 artifact categories flagged for Stage 5  

**Next:** Tool Architect implements with these constraints enforced.
