# after-action (C4 workspace)

Correlate engagement logs + operator decisions into:

1. **Client report** (Markdown + HTML) — redacted
2. **Internal learning summary** (Markdown + HTML) — not redacted

> **Authorized use only.** See [`AUTHORIZED_USE.md`](AUTHORIZED_USE.md).
> Fixture data under `testdata/fixture_engagement/` is synthetic.

## Quick start

```bash
make build   # → out/client_report.md + out/internal_learning.md (+ .html)
make test
```

Or:

```bash
PYTHONPATH=. python3 -m src.cli build \
  --engagement testdata/fixture_engagement \
  --out out
```

## Architecture

```
adapters (JSONL + CSV) → correlate (±30m, asset) → redact (client only) → reports
```

Correlation rules: [`docs/CORRELATION.md`](docs/CORRELATION.md).

## Notes on this run

Codestral/CrewAI originally emitted scaffold stubs (`pass` / “omitted for
brevity”). The working implementation here was completed as a **logged
intervention** after the C4 pipeline — see `../interventions.csv` and
`../RUN_LOG.md`. Do not treat this tree as an unassisted model PASS for RQ3.
