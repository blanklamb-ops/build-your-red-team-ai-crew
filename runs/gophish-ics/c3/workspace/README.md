# gophish-ics

`gophish-ics` is an offline Python sidecar for authorized GoPhish-style calendar-invite exercises. It generates one RFC 5545 `.ics` attachment for a stable campaign recipient ID, validates the result, records normalized RSVP telemetry in SQLite, and reports per-campaign counts. It never sends mail or connects to GoPhish.

> **Authorized use only.** Use this project only for systems and identities you own or have explicit written authorization to test. Do not target real external victims or use it to bypass mail/calendar security. Read [the full notice](ethics/AUTHORIZED_USE.md).

## Architecture and integration approach

This repository chooses a **sidecar**, not a GoPhish fork. The boundary stays small and version-independent:

```text
synthetic campaign JSON                 normalized RSVP observation
          |                                      |
          v                                      v
  config safety gate -> ICS generator     RSVP CLI -> SQLite event history
          |                 |                         |
          |          local .ics attachment            v
          |                 |                  per-campaign report
          v                 v
   shipped false      approved operator handoff
                      to GoPhish template attachment
                      (outside this harness)
```

For a future authorized deployment, map each GoPhish campaign result ID unchanged to `recipient_id`. Generate the recipient-specific bytes, validate them, then use GoPhish’s documented template attachment model (`name`, MIME `type`, base64 `content`) or an approved mail integration to attach them. Normalize observed calendar replies to the four CLI states and preserve that same result ID. This project deliberately implements neither API credentials nor the network handoff. GoPhish’s documented [template attachment model](https://github.com/gophish/python-api-documentation/blob/master/templates.md), [campaign results](https://docs.getgophish.com/api-documentation/campaigns), and [signed webhooks](https://docs.getgophish.com/user-guide/documentation/webhooks) are the integration seams.

## Requirements

- Python 3.10 or newer on a POSIX-like lab host
- No third-party Python packages, root privileges, services, or network access

Run commands from the repository root. There is no install step:

```sh
python3 -m gophish_ics.cli --help
python3 -m unittest discover -s tests -v
./ACCEPTANCE.md
```

## Safe local lab demo

All checked-in identities use the reserved `.test` domain. The shipped [configuration](config/default.yaml) is `ics_enabled: false`, so this command must fail closed and write nothing:

```sh
demo_dir=$(mktemp -d)
python3 -m gophish_ics.cli generate \
  --campaign fixtures/campaign.json \
  --recipient-id recipient-001 \
  --output "$demo_dir/blocked.ics"
```

For an authorized lab run, make a temporary, explicit override; do not edit the shipped configuration:

```sh
printf 'ics_enabled: true\n' > "$demo_dir/enabled.yaml"
python3 -m gophish_ics.cli generate \
  --campaign fixtures/campaign.json \
  --recipient-id recipient-001 \
  --output "$demo_dir/invite.ics" \
  --config "$demo_dir/enabled.yaml"
python3 -m gophish_ics.cli validate "$demo_dir/invite.ics"

python3 -m gophish_ics.cli seed \
  --db "$demo_dir/rsvps.sqlite3" \
  --fixture fixtures/rsvps.json
python3 -m gophish_ics.cli report \
  --db "$demo_dir/rsvps.sqlite3" \
  --campaign-id lab-campaign-001
```

Expected counts are one each for `accept`, `decline`, `tentative`, and `none`, with total four. Remove the temporary directory when evidence retention permits:

```sh
rm -rf -- "$demo_dir"
```

To record a single normalized observation instead of seeding fixtures:

```sh
python3 -m gophish_ics.cli record \
  --db /path/to/case/rsvps.sqlite3 \
  --campaign-id lab-campaign-001 \
  --recipient-id recipient-001 \
  --response accept \
  --occurred-at 2030-06-01T14:00:00Z
```

Response state is current per `(campaign_id, recipient_id)`, while every observation remains in `rsvp_events`. Later timestamps win; for equal timestamps, later insertion wins deterministically. Email is never an identity key.

## Calendar profile and validation

The generator consumes organizer, summary, description, explicit-offset `dtstart`/`dtend`, and attendee fields from JSON. It emits UTF-8, CRLF line endings, 75-octet folding, escaped text, UTC `DTSTAMP`/`DTSTART`/`DTEND`, `METHOD:REQUEST`, a stable `UID`, and recipient correlation properties. Each output is structurally validated before it is written. `validate` and the automated tests are the documented linter path for CI; they check this intentionally narrow RFC 5545 profile.

The generator writes a single attendee per recipient-specific invite to avoid disclosing other addresses. Output files are created exclusively and never overwritten.

## Failure and degradation behavior

- Missing, malformed, duplicate, unknown, non-boolean, or false config fails before campaign data is read or output is written.
- Naive/invalid timestamps, end-before-start, unknown fields, duplicate recipient IDs, unsafe identifiers, malformed addresses, and unknown RSVP states fail with a nonzero status.
- Existing output is preserved. SQLite lock, permission, or corruption errors fail visibly; there is no in-memory fallback.
- Without GoPhish, generation/validation/reporting still work from fixtures. Without SMTP or a calendar gateway, keep the validated attachment locally; this sidecar neither retries nor finds an alternate delivery route.
- Without a calendar client, CI validation is the compatibility evidence. This is not a full iMIP delivery or inbound iTIP parser.
- Without Semgrep or ast-grep, the scanner archive records `NOT RUN: tool unavailable`; scanners are not installed or replaced during this pipeline.

Generated `.ics` files and SQLite databases can contain campaign content, attendee addresses, and response behavior. Treat them as engagement evidence: use an access-controlled case directory, avoid committing them, and follow the agreed retention and disposal plan.

See [OPSEC_CARD.md](OPSEC_CARD.md) for defender-facing artifacts, safer operation, and Detection Recommendations.
