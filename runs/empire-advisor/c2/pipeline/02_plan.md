# Build Plan — empire-advisor

## 1. Repository layout

```
empire-advisor/
├── plugin/
│   ├── plugin.yaml              # Empire plugin manifest
│   ├── advisor.py               # Main plugin entry point
│   └── shim.py                  # Offline Empire API shim (if needed)
├── lib/
│   ├── scorer.py                # Scoring engine
│   ├── suggester.py             # Suggestion engine
│   ├── parser.py                # Command parser
│   └── formatter.py             # Output formatter (JSON + text)
├── knowledge_base/
│   ├── rules.yaml               # Scoring rules (id, pattern, rationale, severity)
│   └── alternatives.yaml        # Command alternatives with citations
├── tests/
│   ├── fixtures/
│   │   └── commands.json        # Test command fixtures
│   ├── test_scorer.py           # Determinism tests (A4)
│   ├── test_suggester.py        # Suggestion + citation tests (A5)
│   └── test_integration.py      # End-to-end offline tests (A2, A6)
├── scanner_outputs/
│   ├── semgrep.json             # Semgrep scan results (A10)
│   └── ast-grep.txt             # ast-grep scan results (A10)
├── README.md                    # Build/run instructions (A7, A9)
├── OPSEC_CARD.md                # Detection recommendations (A8)
└── requirements.txt             # Python dependencies
```

## 2. Work packages

### WP1: Core infrastructure
**Dependencies:** None  
**Tasks:**
- WP1.1: Create repository skeleton
- WP1.2: Write `requirements.txt` (PyYAML, minimal deps)
- WP1.3: Create README skeleton with authorized-use notice (R9)

### WP2: Knowledge base foundation
**Dependencies:** WP1  
**Tasks:**
- WP2.1: Design `rules.yaml` schema (id, pattern, rationale, severity, score_delta)
- WP2.2: Populate ≥10 rules covering common noisy commands (R3, A3)
  - Examples: `shell whoami`, `shell ipconfig`, `shell net user`, raw PowerShell vs. modules
- WP2.3: Design `alternatives.yaml` schema (rule_id, suggestion, citation)
- WP2.4: Populate alternatives for at least 3 rules (R4, A5)

### WP3: Scoring engine
**Dependencies:** WP2  
**Tasks:**
- WP3.1: Implement `scorer.py` loading rules.yaml
- WP3.2: Implement command matching logic (regex/substring patterns)
- WP3.3: Implement score calculation (base + rule deltas → 0-100 scale)
- WP3.4: Add determinism guarantee (no randomness, no timestamps in score) (A4)
- WP3.5: Write unit tests for determinism (same input → same output)

### WP4: Suggestion engine
**Dependencies:** WP3  
**Tasks:**
- WP4.1: Implement `suggester.py` loading alternatives.yaml
- WP4.2: Map matched rules → suggestions with citations (R4)
- WP4.3: Handle cases where no alternative exists (return empty suggestions)
- WP4.4: Unit test for citation presence (A5)

### WP5: Output formatter
**Dependencies:** WP3, WP4  
**Tasks:**
- WP5.1: Implement `formatter.py` with dual output modes
- WP5.2: JSON output with fields: {command, score, matched_rules, suggestions}
- WP5.3: Text output: human-readable with rule rationales and suggestions (R5)
- WP5.4: Ensure both formats contain identical data

### WP6: Empire plugin integration
**Dependencies:** WP3, WP4, WP5  
**Tasks:**
- WP6.1: Write `plugin.yaml` manifest (R1)
  - Name: empire-advisor
  - Author, version, description
  - Hooks: `on_agent_task_create` (or equivalent pre-exec hook)
- WP6.2: Implement `advisor.py` plugin class
  - Hook registration
  - Command interception: read task → score → suggest → output advisory (R2)
  - No command modification (R7)
- WP6.3: Document compatibility assumptions in README (A7)

### WP7: Offline shim (if Empire unavailable)
**Dependencies:** WP6  
**Tasks:**
- WP7.1: Implement `shim.py` with minimal Empire API mock
  - Fake `MainMenu`, `Task`, `Agent` classes
  - Replay fixture commands from `tests/fixtures/commands.json`
- WP7.2: Adapter layer so `advisor.py` works with shim or real Empire
- WP7.3: Document shim limitations in README (R1, A7)

### WP8: Testing
**Dependencies:** WP3-WP7  
**Tasks:**
- WP8.1: Create `tests/fixtures/commands.json` with ≥5 test commands
- WP8.2: Write `test_scorer.py` (determinism: A4)
- WP8.3: Write `test_suggester.py` (citation presence: A5)
- WP8.4: Write `test_integration.py` (offline mode end-to-end: A2, A6)
- WP8.5: Document how to run tests in README

### WP9: Static analysis
**Dependencies:** WP6, WP7 (full implementation done)  
**Tasks:**
- WP9.1: Run Semgrep with security ruleset
- WP9.2: Run ast-grep for Python best practices
- WP9.3: Archive outputs to `scanner_outputs/` (R10, A10)
- WP9.4: Document scanner commands in `pipeline/04_build_notes.md`

### WP10: Documentation
**Dependencies:** All prior WPs  
**Tasks:**
- WP10.1: Complete README with build/run/test instructions (A7)
- WP10.2: Add Empire version compatibility notes (A7)
- WP10.3: Verify authorized-use notice present (A9)
- WP10.4: Create OPSEC_CARD.md skeleton (deferred to WP11/stage 5)

### WP11: OPSEC review
**Dependencies:** WP10  
**Tasks:**
- Stage 5 deliverable; planned but executed by OPSEC Reviewer persona
- Output: final OPSEC_CARD.md (R8, A8)

## 3. Interface contracts

### scorer.py
```python
def load_rules(rules_path: str) -> List[Rule]:
    """Load scoring rules from YAML. Returns list of Rule objects."""

def score_command(command: str, rules: List[Rule]) -> ScoringResult:
    """
    Returns: ScoringResult(
        score: int,  # 0-100
        matched_rules: List[RuleMatch]  # id, rationale, severity
    )
    Deterministic: same command → same score.
    """
```

### suggester.py
```python
def load_alternatives(alt_path: str) -> Dict[str, Alternative]:
    """Load alternatives KB, keyed by rule_id."""

def suggest_alternatives(matched_rules: List[RuleMatch], kb: Dict) -> List[Suggestion]:
    """
    Returns: List[Suggestion(alternative_command, citation, context)]
    Empty list if no alternatives available.
    """
```

### formatter.py
```python
def format_json(result: AdvisoryResult) -> str:
    """JSON output with all fields."""

def format_text(result: AdvisoryResult) -> str:
    """Human-readable advisory with rationales and suggestions."""
```

### advisor.py (plugin)
```python
class EmpireAdvisor:
    def on_task_create(self, task: Task) -> None:
        """
        Hook: intercept task creation.
        - Parse command from task
        - Score via scorer
        - Suggest via suggester
        - Format and print advisory (JSON + text)
        - Allow task to proceed unchanged (R7)
        """
```

### shim.py (if needed)
```python
class FakeEmpire:
    """Minimal Empire API mock for offline testing."""
    def load_fixture_commands(self, fixture_path: str) -> List[Task]:
        """Load commands from JSON for replay."""
```

## 4. Requirement trace matrix

| Requirement ID | Description | Work Packages | Acceptance IDs |
|----------------|-------------|---------------|----------------|
| R1 | Plugin manifest / shim | WP6.1, WP7.1-WP7.3 | A1, A7 |
| R2 | Command interception hook | WP6.2 | A2 |
| R3 | Scoring engine (rules.yaml) | WP2.1-WP2.2, WP3 | A3, A4 |
| R4 | Suggestion engine + KB | WP2.3-WP2.4, WP4 | A5 |
| R5 | Operator UI/CLI output | WP5 | A2 |
| R6 | Offline fixture mode | WP7, WP8.4 | A6 |
| R7 | No auto-execution | WP6.2 (design constraint) | A2 (test verifies) |
| R8 | OPSEC_CARD.md | WP11 | A8 |
| R9 | README + auth notice | WP1.3, WP10 | A9 |
| R10 | Scanner outputs | WP9 | A10 |

## 5. Test plan

### Automated tests (via pytest)
| Acceptance ID | Test File | Description |
|---------------|-----------|-------------|
| A4 | test_scorer.py | Run same command twice, assert identical score |
| A5 | test_suggester.py | Load fixtures, assert ≥1 suggestion has citation |
| A2 | test_integration.py | Submit fixture command, verify advisory output with no command modification |
| A6 | test_integration.py | Run in offline mode (shim), verify output |

### Manual verification
| Acceptance ID | Check | How |
|---------------|-------|-----|
| A1 | Plugin loads | README instructions + manual load attempt OR shim demo |
| A3 | ≥10 rules in rules.yaml | `grep '^- id:' knowledge_base/rules.yaml | wc -l` |
| A7 | Empire compatibility docs | README inspection |
| A8 | OPSEC_CARD.md with ≥3 detection recommendations | File inspection |
| A9 | Authorized-use notice | README inspection |
| A10 | Scanner outputs archived | `ls scanner_outputs/` |

### Manual fidelity checks (M1-M3)
- **M1:** Scoring rationale understandable — Test: read advisory output without source; rationale should be clear
- **M2:** Suggestions are alternatives, not vague advice — Test: verify alternatives.yaml has concrete commands
- **M3:** Dangerous rules default warn/block — Test: high-severity rules should have clear advisory warnings

## 6. Out of scope

### Explicitly excluded from this build:
- ❌ **Live exploit generation** — All alternatives are pre-documented in local KB
- ❌ **Auto-execution of suggestions** — Operator must manually choose alternatives (R7)
- ❌ **Real-time EDR telemetry analysis** — Scoring is heuristic-based, not detection-verified
- ❌ **Multi-agent attack chaining** — Single command analysis only
- ❌ **Guaranteed bypass techniques** — Advisory system, not evasion guarantee
- ❌ **Cloud/API-based knowledge updates** — Offline-only knowledge base
- ❌ **GUI for Empire/Starkiller** — CLI/text output only (plugin hooks into backend)
- ❌ **Command modification/rewriting** — Advisory only; operator retains control

### Acceptable gaps (to document in build notes):
- Empire v2.x backward compatibility (focus on v3/v4)
- Coverage of every possible Empire module (sample coverage with extensible KB)
- Context-aware scoring (e.g., target-specific EDR configurations)

## Plan validation

✅ **Repository layout:** 4 main directories, clear separation of concerns  
✅ **Work packages:** 11 WPs with explicit dependencies  
✅ **Interface contracts:** 4 core modules with function signatures  
✅ **Trace matrix:** All 10 requirements mapped to WPs and acceptance IDs  
✅ **Test plan:** 6 automated tests, 6 manual checks, 3 fidelity checks  
✅ **Out of scope:** 8 explicit exclusions matching PROMPT non-goals  

**Next:** Ops Advisor injects operational constraints before architecture hardens.
