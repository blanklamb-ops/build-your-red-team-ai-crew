# Operational Constraints — gophish-ics

## Runtime environment

- Target POSIX-like lab hosts with Python 3.10+ and the standard library. Run as an unprivileged user; no daemon, privileged port, system service, or global install is needed.
- Core generation, validation, RSVP storage, report, tests, and demo must require no network access. Paths are explicit CLI arguments and must work from a clean checkout.
- GoPhish, SMTP, and calendar clients are optional handoff systems. Their absence cannot prevent local acceptance. This sidecar never sends mail.
- SQLite writes are local. Commands must create parent-independent files only at operator-selected paths; demo and tests use temporary directories and clean them automatically.
- Serena is unavailable and therefore not used. Existing scanners are invoked only in the controlled post-run step; no scanner installation or substitution is permitted.

## Secrets and evidence handling

- Never commit API keys, SMTP credentials, webhook secrets, real recipient data, production campaign exports, live hostnames, or generated operational databases.
- Checked-in data must use synthetic identities under reserved domains (for example `.test`) and documentation-only IP ranges if any addresses are needed.
- RSVP databases and generated invites are engagement evidence: store them in an access-controlled case directory, minimize retention, hash/archive as required by the engagement, and delete according to the evidence plan. They may reveal attendee addresses, event subjects, and response behavior.
- Do not print full invite bodies or recipient email addresses during routine success output. Error messages must avoid echoing secret config values or entire input payloads.
- A future GoPhish adapter must take secrets from a separately protected runtime source, never fixture/config files in this repository. This implementation does not accept or need those secrets.

## Operator workflow

1. Confirm written authorization and remain inside the lab. Review `ethics/AUTHORIZED_USE.md` and verify `config/default.yaml` remains `ics_enabled: false`.
2. Copy the fixture pattern into an engagement-local campaign file using synthetic or explicitly authorized identities. Preserve the stable GoPhish result ID as `recipient_id`.
3. For an approved test only, create a temporary configuration containing `ics_enabled: true`; pass it explicitly to `generate`. There is no environment-variable or implicit enable path.
4. Validate the resulting `.ics` locally before handing it to an approved mail pipeline. The sidecar does not perform that handoff.
5. Feed normalized RSVP observations to `record`, or load synthetic events with `seed`. Generate the campaign report from the local database.
6. Preserve evidence per engagement rules, remove the temporary enabled config, and reconfirm the shipped configuration is unchanged.

## Safety defaults

- **Fail closed:** missing, malformed, duplicate, or non-boolean `ics_enabled` configuration blocks generation. The sole shipped value is false.
- Enabling must be file-based and explicit on each generate command. No `--enable`, environment variable, auto-detection, or persistent toggle is allowed.
- There is no send command. Generation writes one specified local file and refuses to overwrite it unless an explicit overwrite control is designed and tested; the minimal implementation should simply refuse existing paths.
- Campaign and RSVP inputs are schema-validated. Reject naive times, end-before-start, control characters, unknown fields where practical, missing recipient IDs, malformed email addresses, and unsupported RSVP states.
- Fixture/demo identities must end in `.test`; production-like input is not needed for acceptance. The generator itself may support authorized addresses because integration is the goal, but the demo must enforce/check synthetic inputs.
- Database reporting is read-only; record/seed transactions either commit completely or fail without partial fixture ingestion.

## Degradation modes

- **Offline:** all core functions continue. Documentation links are informational; no runtime fetch occurs.
- **GoPhish unavailable:** generate and validate attachments from local campaign fixtures; document manual/API attachment handoff without attempting a connection.
- **Mail/calendar gateway unavailable:** retain the validated `.ics` as a local artifact; do not retry or send through an alternate route.
- **Invalid/missing configuration:** exit nonzero before reading recipient content or writing output.
- **Malformed campaign/RSVP input:** exit nonzero, identify the field category without dumping the record, and leave output/database transactions unchanged.
- **SQLite locked/unwritable/corrupt:** exit nonzero; never fall back to an untracked in-memory store. Existing evidence remains untouched.
- **Scanner unavailable:** archive the attempted command plus `NOT RUN: tool unavailable`; acceptance may verify archive presence and truthful status. Do not install a replacement.

## Detection-relevant artifacts for Role 5

- MIME/calendar indicators: `.ics` or `text/calendar`, `METHOD:REQUEST`, organizer/attendee mismatch, unusual external organizers, newly seen `UID` domains, and invitation attachments from campaign infrastructure.
- Mail/calendar gateway telemetry: attachment hashes, invite auto-processing, RSVP/iTIP reply traffic, sender authentication results, and cross-system correlation between inbound invitations and outbound replies.
- Host/application artifacts: generated `.ics` files, SQLite `rsvp_events`/current-state records, CLI process execution, enabled temporary config files, and GoPhish attachment/API audit logs.

## Non-negotiable plan deltas for the Architect

- **WP1:** configuration parsing must fail closed and reject duplicate/unknown keys; add the canonical ethics path while retaining the existing notice.
- **WP2:** validate before output, escape/fold content, normalize aware timestamps to UTC, reject end-before-start and control-character injection, and refuse overwriting an existing file at the CLI boundary.
- **WP3:** use a transaction for fixture seeding; retain immutable events and deterministically select current state by `(occurred_at, insertion id)`; enforce the four-state set in code and SQLite.
- **WP4:** provide no network/send command and no implicit enable mechanism; concise errors go to stderr with nonzero exit status.
- **WP5:** include evidence handling, explicit temporary-enable workflow, sidecar handoff boundary, and failures for unavailable GoPhish/mail/calendar/SQLite.
- **WP6:** test malformed config/input, injection, existing-output refusal, atomic seed behavior, deterministic same-time updates, synthetic demo identities, and exact shipped-config byte preservation.
- **WP7:** record scanner command, version or unavailable state, timestamp, scope, and exit/result. Do not install tools.
- **WP8:** acceptance must run unprivileged and offline, must not alter the shipped configuration, and must leave generated artifacts only in a temporary directory.
