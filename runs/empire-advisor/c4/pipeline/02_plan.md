 # Empire-Advisor Plugin Build Plan

## Repository Layout

```
/empire-advisor
  /src
    - main.ps1
    - rules.yaml
    - knowledge_base.yaml
    - score_engine.ps1
    - suggestion_engine.ps1
  /tests
    - unit_tests.ps1
    - integration_tests.ps1
    - acceptance_tests.ps1
  /docs
    - README.md
    - USER_GUIDE.md
    - TECHNICAL_DESIGN.md
  .gitignore
  LICENSE
```

## Work Packages

1. **WP1: Set up the project structure and basic plugin functionality**
   - Create the necessary directories and files
   - Implement the basic plugin structure that matches Empire plugin conventions

2. **WP2: Implement the scoring engine**
   - Define the structure of the `rules.yaml` file (research needed)
   - Implement the scoring engine in `score_engine.ps1`

3. **WP3: Implement the suggestion engine**
   - Define the structure of the local knowledge base (research needed)
   - Implement the suggestion engine in `suggestion_engine.ps1`

4. **WP4: Integrate the scoring and suggestion engines**
   - Modify `main.ps1` to use the scoring and suggestion engines

5. **WP5: Write documentation**
   - Create a README.md file
   - Create a USER_GUIDE.md file
   - Create a TECHNICAL_DESIGN.md file

6. **WP6: Write tests**
   - Write unit tests for the scoring and suggestion engines
   - Write integration tests for the plugin as a whole
   - Write acceptance tests based on the PROMPT requirements

## Interface Contracts

- `score_engine.ps1` will have a function `ScoreCommand` that takes a command string as input and returns a score.
- `suggestion_engine.ps1` will have a function `GetSuggestions` that takes a command string and a score as input and returns a list of suggested commands.
- `main.ps1` will have a function `ProcessCommand` that takes a command string as input, calls `ScoreCommand` and `GetSuggestions`, and returns the suggestions to the operator.

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1, WP4      |
| PROMPT-2              | WP1, WP6      |
| PROMPT-3              | WP2, WP4      |
| PROMPT-4              | WP3, WP4      |
| PROMPT-5              | WP4           |

## Test Plan

- Unit tests and integration tests will be automated.
- Acceptance tests will be manual, as they will involve verifying the correctness of the suggestions made by the plugin.

## Out of Scope

- Auto-execution of suggested alternatives. This is out of scope as it goes against the requirement that the plugin should keep humans in control.
- Support for online environments. This is out of scope as the requirement is for the plugin to be compatible with offline/air-gap environments.
- The exact format of the `rules.yaml` file and the local knowledge base. These will be researched further as part of the project.

## Assumptions

- The scoring engine will be based on a set of rules that are documented in a `rules.yaml` file. This assumption is based on the requirement that the scoring engine should be transparent and deterministic.