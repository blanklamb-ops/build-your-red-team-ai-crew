"""SQLite RSVP event history and current-state reporting."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any


RESPONSES = ("accept", "decline", "tentative", "none")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_EVENT_KEYS = {"campaign_id", "recipient_id", "response", "occurred_at"}


class TelemetryError(ValueError):
    """RSVP telemetry is invalid or unsafe to persist."""


def _identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise TelemetryError(f"{field} has an invalid identifier format")
    return value


def _response(value: Any) -> str:
    if value not in RESPONSES:
        raise TelemetryError("response must be accept, decline, tentative, or none")
    return value


def _occurred_at(value: Any) -> str:
    if not isinstance(value, str):
        raise TelemetryError("occurred_at must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TelemetryError("occurred_at must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TelemetryError("occurred_at must include an explicit timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, timeout=5)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS rsvp_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            response TEXT NOT NULL CHECK(response IN ('accept','decline','tentative','none')),
            occurred_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_rsvp_events_identity
            ON rsvp_events(campaign_id, recipient_id, occurred_at, id);
        CREATE TABLE IF NOT EXISTS rsvp_current (
            campaign_id TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            response TEXT NOT NULL CHECK(response IN ('accept','decline','tentative','none')),
            occurred_at TEXT NOT NULL,
            event_id INTEGER NOT NULL REFERENCES rsvp_events(id),
            PRIMARY KEY (campaign_id, recipient_id)
        );
        """
    )


def initialize(db_path: Path) -> None:
    with _connect(db_path) as connection:
        _create_schema(connection)


def _validated_event(data: Any) -> tuple[str, str, str, str]:
    if not isinstance(data, dict) or set(data) != _EVENT_KEYS:
        raise TelemetryError("RSVP event has missing or unknown fields")
    return (
        _identifier(data["campaign_id"], "campaign_id"),
        _identifier(data["recipient_id"], "recipient_id"),
        _response(data["response"]),
        _occurred_at(data["occurred_at"]),
    )


def _insert_event(connection: sqlite3.Connection, event: tuple[str, str, str, str]) -> None:
    campaign_id, recipient_id, response, occurred_at = event
    cursor = connection.execute(
        "INSERT INTO rsvp_events(campaign_id, recipient_id, response, occurred_at) VALUES (?, ?, ?, ?)",
        event,
    )
    event_id = int(cursor.lastrowid)
    connection.execute(
        """
        INSERT INTO rsvp_current(campaign_id, recipient_id, response, occurred_at, event_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(campaign_id, recipient_id) DO UPDATE SET
            response = excluded.response,
            occurred_at = excluded.occurred_at,
            event_id = excluded.event_id
        WHERE excluded.occurred_at > rsvp_current.occurred_at
           OR (excluded.occurred_at = rsvp_current.occurred_at
               AND excluded.event_id > rsvp_current.event_id)
        """,
        (campaign_id, recipient_id, response, occurred_at, event_id),
    )


def record_response(
    db_path: Path, campaign_id: str, recipient_id: str, response: str, occurred_at: str
) -> None:
    event = _validated_event({
        "campaign_id": campaign_id,
        "recipient_id": recipient_id,
        "response": response,
        "occurred_at": occurred_at,
    })
    with _connect(db_path) as connection:
        _create_schema(connection)
        _insert_event(connection, event)


def seed_responses(db_path: Path, fixture_path: Path) -> int:
    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TelemetryError("RSVP fixture is unavailable") from exc
    except json.JSONDecodeError as exc:
        raise TelemetryError("RSVP fixture is not valid JSON") from exc
    if not isinstance(payload, list) or not payload:
        raise TelemetryError("RSVP fixture must be a non-empty list")
    events = [_validated_event(item) for item in payload]
    with _connect(db_path) as connection:
        _create_schema(connection)
        for event in events:
            _insert_event(connection, event)
    return len(events)


def campaign_report(db_path: Path, campaign_id: str) -> dict[str, int]:
    campaign_id = _identifier(campaign_id, "campaign_id")
    if not db_path.exists():
        raise TelemetryError("telemetry database is unavailable")
    with _connect(db_path) as connection:
        rows = connection.execute(
            "SELECT response, COUNT(*) FROM rsvp_current WHERE campaign_id = ? GROUP BY response",
            (campaign_id,),
        ).fetchall()
    report = {response: 0 for response in RESPONSES}
    for response, count in rows:
        report[str(response)] = int(count)
    report["total"] = sum(report.values())
    return report
