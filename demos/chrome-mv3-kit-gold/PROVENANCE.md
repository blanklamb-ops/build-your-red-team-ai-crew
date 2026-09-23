# PROVENANCE — chrome-mv3-kit gold / demo kit

**Status:** human-intervened gold kit for demos and operator use.  
**Not** an unassisted model PASS for C1 or C3.

## Source

- Built from prompt-validation C1 workspace archived as  
  `runs/prompt-validation/chrome-mv3-kit/archive/20260904T131634Z/`
- That archive was the last **patched** workable build before the one-shot re-test regen.

## Logged interventions included

Documented in `analysis/protocol-deviations.md`, including:

- `webRequest` `extraHeaders` so Set-Cookie names are visible under MV3
- Username exact-match + priority (`loginfmt` > `login` > …)
- Prefer credential-submission endpoints for `login.path`
- Merge `auth_tokens` by registrable domain
- `sub_filters` as YAML array; empty lists as `[]`
- Remove over-aggressive URL-parameter secret scanning

## Operator-ready example

- `examples/lab-phishlet-ready.yaml` — schema-valid scaffold from a completed lab Microsoft login capture
- Still requires operator completion of `sub_filters` and replacing `credentials.search` placeholders before live Evilginx lab use

## How to use

```bash
cd demos/chrome-mv3-kit-gold
npm install
npm test
# Load extension/ unpacked in Chromium; Enable lab access → Start → capture → export
node generators/phishlet-generator.js /path/to/session.json --output /tmp/out.yaml
node generators/validator.js /tmp/out.yaml
```

## Research framing

Use this kit for demos. Score formal C1/C3 one-shot outputs separately under `runs/` / prompt-validation archives.
