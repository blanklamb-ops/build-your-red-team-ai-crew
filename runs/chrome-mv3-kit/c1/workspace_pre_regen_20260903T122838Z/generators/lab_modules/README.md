# Lab modules — gated, off by default

These modules add **structural review artifacts** to a page-clone lab run.
They are for reviewing a cloned page's susceptibility to clickjacking and
file-prompt-style social-engineering pretexts on **infrastructure you are
authorized to test** (a lab environment, an intentionally vulnerable app, or
a client's explicitly in-scope staging host).

They do **not**:

- beacon anywhere
- rewrite forms to exfiltrate input
- execute automatically, download real payloads, or touch the local
  filesystem outside the run's output directory

They are disabled unless **both**:

1. `config/lab.config.json` sets `"lab_unsafe_modules": true`, **and**
2. the CLI is invoked with `--lab-unsafe`

See `../../OPSEC_CARD.md` for operator risk notes.
