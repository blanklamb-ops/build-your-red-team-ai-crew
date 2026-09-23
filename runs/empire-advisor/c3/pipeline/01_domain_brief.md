# Domain Brief — empire-advisor

## Goal restatement

Success is an operator-side, pre-execution advisor for an Empire-like lab workflow. Given a submitted command, it must deterministically return an `allow`, `warn`, or `deny` advisory, an explainable numeric score, every matching rule and rationale, and locally documented alternative command templates with citations. It must never execute the submitted command or a suggestion. The complete workflow must run offline against fixture transcripts without a live C2.

## Constraints

- **Platform and language:** Use a small Python 3 implementation with only the standard library so the acceptance path is air-gap friendly. Store deterministic rule and knowledge-base data in JSON-compatible YAML files; JSON is a valid YAML 1.2 subset and avoids a PyYAML dependency.
- **Interface:** Provide a plugin-shaped adapter plus CLI. The adapter receives a command mapping and returns serializable advisory data. The CLI supports a single command and batch fixture input, with text or JSON output.
- **Empire compatibility:** Current Empire exposes plugins through `/api/v2/plugins`, validates plugin command arguments before calling `execute(command, **kwargs)`, and permits string/boolean responses ([official API overview](https://github.com/BC-SECURITY/empire-docs/blob/main/restful-api/README.md), [official execution documentation](https://bc-security.gitbook.io/empire-wiki/plugins/development/execution)). However, the documented hook set includes `AFTER_TASKING_HOOK`, not a universal before-tasking hook ([official hooks documentation](https://bc-security.gitbook.io/empire-wiki/plugins/development/hooks-and-filters)). Therefore the deliverable must accurately claim a plugin-shaped, explicit pre-submit wrapper—not transparent interception of every Empire task.
- **Registration:** Include a local manifest and an adapter exposing Empire-style metadata/options and `execute`. Marketplace installation is outside offline acceptance; modern Empire supports registries and auto-install entries ([official plugin documentation](https://bc-security.gitbook.io/empire-wiki/plugins), [official registry](https://github.com/BC-SECURITY/Empire-Plugin-Registry)).
- **Safety:** Advisory only. `deny` means “advisor recommends not submitting,” not enforcement. No subprocess, shell, network, C2, or dynamic exploit generation paths.
- **Artifacts:** README, authorized-use notice, at least ten documented rules, local cited alternatives, fixtures, executable acceptance runner, scanner archives, and an OPSEC card with detection recommendations.

## Prior art and alignment

- BC Security Empire’s v2 REST API, introduced in Empire 5.0, defines plugin management and execution endpoints; align adapter inputs with a validated command dictionary ([official REST API documentation](https://github.com/BC-SECURITY/empire-docs/blob/main/restful-api/README.md)).
- Empire plugin `execute` functions accept `command` plus keyword context and return supported response types; expose this shape without importing Empire so offline tests work ([official execution documentation](https://bc-security.gitbook.io/empire-wiki/plugins/development/execution)).
- Empire’s marketplace registry records plugin identity, source, authors, description, and immutable version refs. A local manifest should describe analogous identity while clearly stating that it is not a marketplace registry entry ([official registry](https://github.com/BC-SECURITY/Empire-Plugin-Registry)).
- MITRE ATT&CK technique pages are suitable defensive citations for why command families may be visible. Local KB citations should point to stable public documentation, while alternative templates remain inert, operator-edited examples rather than generated payloads.

## Risks

- Operators may mistake a heuristic score for guaranteed stealth or EDR bypass. Output and documentation must state that lower noise is contextual, not undetectable.
- Regex/sub-string rules can yield false positives and negatives. Emit matched evidence and rationales; never silently suppress risky input.
- Scores may drift if ordering, environment, or timestamps affect results. Load fixed data, normalize input predictably, use additive capped scoring, and exclude time/randomness.
- A “deny” label could imply actual enforcement. Name it advisory state and keep execution out of the program entirely.
- Suggestions could become unsafe if they embed targets, credentials, encoded payloads, bypasses, or destructive actions. Keep a curated local KB of benign, read-only discovery templates and require citations.
- Upstream Empire plugin APIs can change. Pin claims to the documented API shape and state shim limits/version assumptions in README.
- Scanner tools may be absent by design. The acceptance runner must archive actual output/version when installed and a truthful “not installed” record otherwise; it must not install or replace scanners.

## Planning assumptions and open questions

**Assumption:** Acceptance evaluates the offline shim on the available Python interpreter; no live Empire checkout is present. **Assumption:** JSON-formatted `rules.yaml`/`kb.yaml` satisfies the YAML-equivalent requirement while keeping zero external dependencies. **Assumption:** Fixture commands are synthetic lab examples and are analyzed only, never run.

No question blocks planning. Live Empire validation remains an optional integration activity because no version or server is supplied.
