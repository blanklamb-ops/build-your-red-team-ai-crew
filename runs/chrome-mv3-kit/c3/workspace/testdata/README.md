# Study-owned chrome regression fixture

`regression-mixed-capture.json` is a **synthetic** mixed-host capture used as A5e.

It encodes the defects that passed unit tests but failed real-capture usefulness:

- OAuth authorize + savestate + silent-signin **and** a real credential POST
- savestate `form_fields` (no password) plus a password form (`loginfmt` hidden + `passwd`)
- API / admin / monitor / storage / CDN / edge / copilot / telemetry hosts mixed in
- a long hex CDN label that naive PSL parsing turns into junk
- recorder-faithful fields only (`url`, `set_cookie_names`; no `origin`, no `cookieNames`)

Harness copies this folder into each chrome workspace as `study-fixtures/`. Generators must ship the JSON unchanged under `testdata/` and assert A5e against it.

`phishlet-schema-2.3.0.json` is the **study reference** Evilginx 2.3.0 schema (wiki-aligned). Generators should copy or re-emit an equivalent schema under `schemas/` and validate exports against it (`min_ver: "2.3.0"`, map `credentials`, object `sub_filters`, no top-level `name`). Scored YAML must also be **placeholder-free** (real `credentials.search`, hostname-rewrite `sub_filters`).

Do not replace hosts with live IdP hostnames. Do not add secrets.
