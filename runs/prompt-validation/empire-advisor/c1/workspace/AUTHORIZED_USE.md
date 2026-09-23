# Authorized use

This methodology compares AI coding scaffolds. Reference tools and prompts exist for **authorized security testing, research, and education** only.

## Required boundaries

- Use outputs only on systems and identities you are contractually or legally authorized to test.
- Do not use generated phishing, credential-capture, C2, or evasion materials against unauthorized targets.
- When publishing tool repos, include this notice and an OPSEC card with Detection Recommendations (defender/client handoff).
- Strip client secrets, real victim data, and engagement identifiers before any public archive.

## Researcher obligations

- Prefer lab / intentionally vulnerable / owned infrastructure for acceptance testing.
- Document authorization scope in private run notes (not required in the public methodology dump).
- If a run produces clearly harmful dual-use instructions beyond the prompt scope, quarantine that artifact and note it in the failure log.
