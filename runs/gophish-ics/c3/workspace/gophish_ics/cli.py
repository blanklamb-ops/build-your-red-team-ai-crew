"""Command-line boundary for local invitation and RSVP workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from .config import ConfigError, load_config, require_ics_enabled
from .ics import CampaignError, generate_invite, load_campaign, validate_invite
from .store import TelemetryError, campaign_report, record_response, seed_responses


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "default.yaml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gophish-ics",
        description="Offline ICS/RSVP sidecar for authorized lab use only",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="generate one local invite (never sends mail)")
    generate.add_argument("--campaign", type=Path, required=True)
    generate.add_argument("--recipient-id", required=True)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--config", type=Path, default=DEFAULT_CONFIG)

    validate = commands.add_parser("validate", help="validate an ICS file")
    validate.add_argument("file", type=Path)

    record = commands.add_parser("record", help="record a normalized RSVP observation")
    record.add_argument("--db", type=Path, required=True)
    record.add_argument("--campaign-id", required=True)
    record.add_argument("--recipient-id", required=True)
    record.add_argument("--response", required=True)
    record.add_argument("--occurred-at", required=True)

    seed = commands.add_parser("seed", help="load synthetic RSVP fixture events")
    seed.add_argument("--db", type=Path, required=True)
    seed.add_argument("--fixture", type=Path, required=True)

    report = commands.add_parser("report", help="show current RSVP counts for a campaign")
    report.add_argument("--db", type=Path, required=True)
    report.add_argument("--campaign-id", required=True)
    report.add_argument("--json", action="store_true")
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "generate":
        require_ics_enabled(load_config(args.config))
        if args.output.exists():
            raise CampaignError("output already exists; refusing to overwrite")
        campaign = load_campaign(args.campaign)
        data = generate_invite(campaign, args.recipient_id)
        try:
            with args.output.open("xb") as handle:
                handle.write(data)
        except FileExistsError as exc:
            raise CampaignError("output already exists; refusing to overwrite") from exc
        print(f"generated validated invitation at {args.output}")
        return 0
    if args.command == "validate":
        try:
            data = args.file.read_bytes()
        except OSError as exc:
            raise CampaignError("ICS file is unavailable") from exc
        errors = validate_invite(data)
        if errors:
            raise CampaignError("invalid ICS: " + "; ".join(errors))
        print("valid RFC 5545 invitation profile")
        return 0
    if args.command == "record":
        record_response(args.db, args.campaign_id, args.recipient_id, args.response, args.occurred_at)
        print("recorded RSVP response")
        return 0
    if args.command == "seed":
        count = seed_responses(args.db, args.fixture)
        print(f"seeded {count} RSVP responses")
        return 0
    if args.command == "report":
        report = campaign_report(args.db, args.campaign_id)
        if args.json:
            print(json.dumps({"campaign_id": args.campaign_id, **report}, sort_keys=True))
        else:
            print(f"Campaign: {args.campaign_id}")
            for key in ("accept", "decline", "tentative", "none", "total"):
                print(f"{key}: {report[key]}")
        return 0
    raise AssertionError("unreachable command")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return _run(args)
    except (ConfigError, CampaignError, TelemetryError, sqlite3.Error, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
