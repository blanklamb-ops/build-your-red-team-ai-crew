 # Empire-Advisor Build Plan

## Repository Layout

- `/src`
  - `empire_adapter.py`
  - `scoring_engine.py`
  - `suggestion_engine.py`
  - `knowledge_base.yaml`
  - `rules.yaml`
- `/tests`
  - `test_empire_adapter.py`
  - `test_scoring_engine.py`
  - `test_suggestion_engine.py`
- `/docs`
  - `README.md`
  - `INSTALLATION.md`
  - `USAGE.md`
- `.gitignore`
- `requirements.txt`
- `LICENSE`

## Work Packages

1. **WP1: Empire Adapter**
   - Implement a module that intercepts or wraps operator command submissions in the Empire interface.
   - Dependencies: None
2. **WP2: Scoring Engine**
   - Implement a module that scores commands against a heuristic related to noisy vs quieter tradecraft.
   - Dependencies: WP1
3. **WP3: Suggestion Engine**
   - Implement a module that suggests documented alternative commands from a local knowledge base.
   - Dependencies: WP1, WP2
4. **WP4: Knowledge Base**
   - Create a YAML file that includes documented alternative commands with citations.
   - Dependencies: None
5. **WP5: Rules Engine**
   - Create a YAML file that defines the scoring engine's rules.
   - Dependencies: None
6. **WP6: Documentation**
   - Create documentation for installation, usage, and contribution.
   - Dependencies: WP1-WP5

## Interface Contracts

- `empire_adapter.py`
  - `intercept_command(command: str) -> str`
- `scoring_engine.py`
  - `score_command(command: str) -> int`
- `suggestion_engine.py`
  - `suggest_alternatives(command: str) -> List[str]`

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1           |
| PROMPT-2              | WP1           |
| PROMPT-3              | WP2, WP3      |
| PROMPT-4              | WP3, WP4      |
| PROMPT-5              | WP2, WP5      |
| PROMPT-6              | WP1, WP3      |
| PROMPT-7              | WP6           |

## Test Plan

- `test_empire_adapter.py`: Manual testing
- `test_scoring_engine.py`: Automated testing
- `test_suggestion_engine.py`: Automated testing

## Out of Scope

- Autonomous EDR bypass or closed-source signature evasion packs.
- Autonomous chaining of attacks.
- Guaranteed EDR bypass or signature evasion.

## Assumptions

- The format of the scoring engine's rules will be a YAML file similar to `rules.yaml`.
- The suggestion engine's local knowledge base will be a YAML file similar to `knowledge_base.yaml`.
- The method of keeping humans in control will be manual review and approval of suggested alternatives.
- The method of archiving scanner outputs will be a log file or database.