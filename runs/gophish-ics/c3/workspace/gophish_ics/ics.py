"""Strict, dependency-free RFC 5545 invitation generation and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parseaddr
import json
from pathlib import Path
import re
from typing import Any


class CampaignError(ValueError):
    """Campaign data cannot safely produce an invitation."""


@dataclass(frozen=True)
class Person:
    name: str
    email: str
    recipient_id: str | None = None


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    organizer: Person
    summary: str
    dtstart: datetime
    dtend: datetime
    description: str
    attendees: tuple[Person, ...]


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UTC_RE = re.compile(r"^\d{8}T\d{6}Z$")
_CAMPAIGN_KEYS = {
    "campaign_id", "organizer", "summary", "dtstart", "dtend",
    "description", "attendees",
}


def _clean_text(value: Any, field: str, *, allow_newline: bool = False) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CampaignError(f"{field} must be a non-empty string")
    if any(ord(char) < 32 and char not in ("\t", "\n") for char in value):
        raise CampaignError(f"{field} contains a control character")
    if not allow_newline and any(char in value for char in "\r\n"):
        raise CampaignError(f"{field} contains a newline")
    return value


def _identifier(value: Any, field: str) -> str:
    value = _clean_text(value, field)
    if not _ID_RE.fullmatch(value):
        raise CampaignError(f"{field} has an invalid identifier format")
    return value


def _email(value: Any, field: str) -> str:
    value = _clean_text(value, field)
    parsed_name, parsed_address = parseaddr(value)
    if parsed_name or parsed_address != value or value.count("@") != 1:
        raise CampaignError(f"{field} is not a plain email address")
    local, domain = value.rsplit("@", 1)
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise CampaignError(f"{field} is not a valid campaign email address")
    return value


def _timestamp(value: Any, field: str) -> datetime:
    value = _clean_text(value, field)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CampaignError(f"{field} must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CampaignError(f"{field} must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


def _person(data: Any, field: str, *, attendee: bool) -> Person:
    if not isinstance(data, dict):
        raise CampaignError(f"{field} must be an object")
    expected = {"name", "email", "recipient_id"} if attendee else {"name", "email"}
    if set(data) != expected:
        raise CampaignError(f"{field} has missing or unknown fields")
    return Person(
        name=_clean_text(data["name"], f"{field}.name"),
        email=_email(data["email"], f"{field}.email"),
        recipient_id=_identifier(data["recipient_id"], f"{field}.recipient_id") if attendee else None,
    )


def campaign_from_dict(data: Any) -> Campaign:
    if not isinstance(data, dict) or set(data) != _CAMPAIGN_KEYS:
        raise CampaignError("campaign has missing or unknown fields")
    attendees_data = data["attendees"]
    if not isinstance(attendees_data, list) or not attendees_data:
        raise CampaignError("attendees must be a non-empty list")
    attendees = tuple(
        _person(item, f"attendees[{index}]", attendee=True)
        for index, item in enumerate(attendees_data)
    )
    ids = [item.recipient_id for item in attendees]
    if len(ids) != len(set(ids)):
        raise CampaignError("attendee recipient IDs must be unique")
    dtstart = _timestamp(data["dtstart"], "dtstart")
    dtend = _timestamp(data["dtend"], "dtend")
    if dtend <= dtstart:
        raise CampaignError("dtend must be later than dtstart")
    return Campaign(
        campaign_id=_identifier(data["campaign_id"], "campaign_id"),
        organizer=_person(data["organizer"], "organizer", attendee=False),
        summary=_clean_text(data["summary"], "summary"),
        dtstart=dtstart,
        dtend=dtend,
        description=_clean_text(data["description"], "description", allow_newline=True),
        attendees=attendees,
    )


def load_campaign(path: Path) -> Campaign:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CampaignError("campaign fixture is unavailable") from exc
    except json.JSONDecodeError as exc:
        raise CampaignError("campaign fixture is not valid JSON") from exc
    return campaign_from_dict(data)


def _escape_text(value: str) -> str:
    return (value.replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\r\n", "\\n")
            .replace("\r", "\\n").replace("\n", "\\n"))


def _quote_parameter(value: str) -> str:
    if any(char in value for char in "\r\n\""):
        raise CampaignError("calendar parameter contains an unsafe character")
    return f'"{value}"'


def _ical_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _fold_line(line: str) -> list[bytes]:
    source = line.encode("utf-8")
    folded: list[bytes] = []
    first = True
    while source:
        capacity = 75 if first else 74
        cut = min(capacity, len(source))
        while cut and cut < len(source) and source[cut] & 0xC0 == 0x80:
            cut -= 1
        if cut == 0:
            raise CampaignError("unable to fold UTF-8 content line")
        chunk, source = source[:cut], source[cut:]
        folded.append(chunk if first else b" " + chunk)
        first = False
    return folded or [b""]


def generate_invite(campaign: Campaign, recipient_id: str) -> bytes:
    recipient_id = _identifier(recipient_id, "recipient_id")
    attendee = next((item for item in campaign.attendees if item.recipient_id == recipient_id), None)
    if attendee is None:
        raise CampaignError("recipient_id is not present in the campaign")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//Authorized Research//gophish-ics 1.0//EN",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{campaign.campaign_id}-{recipient_id}@gophish-ics.test",
        f"DTSTAMP:{_ical_time(now)}",
        f"DTSTART:{_ical_time(campaign.dtstart)}",
        f"DTEND:{_ical_time(campaign.dtend)}",
        f"ORGANIZER;CN={_quote_parameter(campaign.organizer.name)}:mailto:{campaign.organizer.email}",
        (f"ATTENDEE;CN={_quote_parameter(attendee.name)};ROLE=REQ-PARTICIPANT;"
         f"PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee.email}"),
        f"SUMMARY:{_escape_text(campaign.summary)}",
        f"DESCRIPTION:{_escape_text(campaign.description)}",
        f"X-GOPHISH-CAMPAIGN-ID:{campaign.campaign_id}",
        f"X-GOPHISH-RECIPIENT-ID:{recipient_id}",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    physical = [part for line in lines for part in _fold_line(line)]
    data = b"\r\n".join(physical) + b"\r\n"
    problems = validate_invite(data)
    if problems:
        raise CampaignError("generated invitation failed validation: " + "; ".join(problems))
    return data


def validate_invite(data: bytes) -> list[str]:
    """Return structural RFC 5545 errors; an empty list means valid for this profile."""
    errors: list[str] = []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ["content is not valid UTF-8"]
    if not data.endswith(b"\r\n"):
        errors.append("content must end with CRLF")
    if b"\n" in data.replace(b"\r\n", b"") or b"\r" in data.replace(b"\r\n", b""):
        errors.append("content contains a bare line ending")
    physical = text.split("\r\n")[:-1] if text.endswith("\r\n") else text.splitlines()
    if any(len(line.encode("utf-8")) > 75 for line in physical):
        errors.append("a content line exceeds 75 octets")
    logical: list[str] = []
    for line in physical:
        if line.startswith((" ", "\t")):
            if not logical:
                errors.append("orphan folded line")
            else:
                logical[-1] += line[1:]
        else:
            logical.append(line)
    if not logical or logical[0] != "BEGIN:VCALENDAR" or logical[-1:] != ["END:VCALENDAR"]:
        errors.append("VCALENDAR envelope is invalid")
    required_prefixes = [
        "PRODID:", "VERSION:2.0", "METHOD:REQUEST", "BEGIN:VEVENT",
        "UID:", "DTSTAMP:", "DTSTART:", "DTEND:", "ORGANIZER;",
        "ATTENDEE;", "SUMMARY:", "DESCRIPTION:", "X-GOPHISH-CAMPAIGN-ID:",
        "X-GOPHISH-RECIPIENT-ID:", "END:VEVENT",
    ]
    for prefix in required_prefixes:
        if not any(line.startswith(prefix) for line in logical):
            errors.append(f"missing required {prefix.rstrip(':;')}")
    for name in ("DTSTAMP", "DTSTART", "DTEND"):
        matches = [line.split(":", 1)[1] for line in logical if line.startswith(name + ":")]
        if len(matches) != 1 or not _UTC_RE.fullmatch(matches[0]):
            errors.append(f"{name} must be a single explicit UTC date-time")
    if sum(line == "BEGIN:VEVENT" for line in logical) != 1 or sum(line == "END:VEVENT" for line in logical) != 1:
        errors.append("exactly one VEVENT is required")
    return errors
