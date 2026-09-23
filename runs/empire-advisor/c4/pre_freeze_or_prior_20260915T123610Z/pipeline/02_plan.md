 # Empire-Advisor Build Plan

## Repository Layout

```
/empire-advisor
  /src
    /interceptor
    /scorer
    /suggester
    /tests
  /docs
  /fixtures
  rules.yaml
  README.md
```

## Work Packages

1. **WP1: Interceptor Module Development**
   - Tasks:
     - Design and implement the command interceptor module.
     - Ensure compatibility with Empire plugin conventions.
     - Document the interceptor module's interface.
2. **WP2: Scoring Engine Development**
   - Depends on: WP1
   - Tasks:
     - Define the format and structure of `rules.yaml`.
     - Implement the scoring engine.
     - Document the scoring engine's interface.
3. **WP3: Suggestion Engine Development**
   - Depends on: WP1
   - Tasks:
     - Define the source and format of the local knowledge base.
     - Implement the suggestion engine.
     - Document the suggestion engine's interface.
4. **WP4: Offline Mode Implementation**
   - Depends on: WP1-WP3
   - Tasks:
     - Define the format and location of fixture command transcripts.
     - Implement offline mode operation.
5. **WP5: Documentation and Testing**
   - Depends on: WP1-WP4
   - Tasks:
     - Write user documentation.
     - Develop a test plan.

## Interface Contracts

- **Interceptor Module:**
  - `intercept_command(command: str) -> str`
- **Scoring Engine:**
  - `score_command(command: str, rules: dict) -> float`
- **Suggestion Engine:**
  - `suggest_command(command: str, knowledge_base: dict) -> str`

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1, WP2, WP3, WP5 |
| PROMPT-2              | WP1          |
| PROMPT-3              | WP4          |
| PROMPT-4              | WP2, WP3      |
| PROMPT-5              | WP1-WP5       |

## Test Plan

- **Automated Tests:** Unit tests for interceptor module, scoring engine, and suggestion engine.
- **Manual Tests:** User acceptance testing for the entire tool.

## Out of Scope

- Autonomous chaining of attacks.
- EDR bypass or closed-source signature evasion packs.

## Assumptions

- The format of `rules.yaml` will be YAML.
- The local knowledge base for the suggestion engine will be a JSON file.
- Fixture command transcripts will be stored in the `/fixtures` directory.