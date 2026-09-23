"""Input adapters and normalized record models."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MAX_INPUT_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 100_000


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    asset: str
    event_type: str
    summary: str
    details: str
    source: str


@dataclass(frozen=True)
class Decision:
    timestamp: datetime
    decision: str
    rationale: str
    asset: str
    outcome: str
    ttp_ref: str
    source: str


def _check_file(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"required input file is missing: {path.name}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes: {path.name}")


def normalize_asset(value: str) -> str:
    return str(value or "").strip().casefold().rstrip(".")


def parse_timestamp(value: str, source: str, warnings: list[str]) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        warnings.append(f"{source}: missing required timestamp; record skipped")
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        warnings.append(f"{source}: invalid timestamp; record skipped")
        return None
    if parsed.tzinfo is None:
        warnings.append(f"{source}: naive timestamp interpreted as UTC")
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _field(row: dict[str, Any], name: str, source: str, warnings: list[str], *, required: bool = False) -> str:
    value = str(row.get(name, "") or "").strip()
    if value:
        return value
    if required:
        warnings.append(f"{source}: missing required {name}; record skipped")
        return ""
    warnings.append(f"{source}: missing optional {name}; using 'Not provided'")
    return "Not provided"


def _event_from_row(row: dict[str, Any], source: str, warnings: list[str]) -> Event | None:
    timestamp = parse_timestamp(str(row.get("timestamp", "")), source, warnings)
    asset = normalize_asset(str(row.get("asset", "")))
    if not asset:
        warnings.append(f"{source}: missing required asset; record skipped")
    if timestamp is None or not asset:
        return None
    return Event(
        timestamp=timestamp,
        asset=asset,
        event_type=_field(row, "event_type", source, warnings),
        summary=_field(row, "summary", source, warnings),
        details=_field(row, "details", source, warnings),
        source=source,
    )


def _bounded(rows: Iterable[tuple[int, dict[str, Any]]]) -> Iterable[tuple[int, dict[str, Any]]]:
    for count, pair in enumerate(rows, 1):
        if count > MAX_RECORDS:
            raise ValueError(f"input exceeds {MAX_RECORDS} records")
        yield pair


def load_jsonl_events(path: Path, warnings: list[str]) -> list[Event]:
    _check_file(path)
    events: list[Event] = []
    with path.open(encoding="utf-8") as handle:
        rows = ((line_no, line) for line_no, line in enumerate(handle, 1))
        for line_no, line in rows:
            if line_no > MAX_RECORDS:
                raise ValueError(f"input exceeds {MAX_RECORDS} records: {path.name}")
            source = f"{path.name}:{line_no}"
            if not line.strip():
                warnings.append(f"{source}: blank JSONL line skipped")
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f"{source}: malformed JSON; record skipped")
                continue
            if not isinstance(row, dict):
                warnings.append(f"{source}: JSON value is not an object; record skipped")
                continue
            event = _event_from_row(row, source, warnings)
            if event:
                events.append(event)
    return events


def load_csv_events(path: Path, warnings: list[str]) -> list[Event]:
    _check_file(path)
    events: list[Event] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV header is missing: {path.name}")
        for row_no, row in _bounded(enumerate(reader, 2)):
            event = _event_from_row(row, f"{path.name}:{row_no}", warnings)
            if event:
                events.append(event)
    return events


def load_decisions(path: Path, warnings: list[str]) -> list[Decision]:
    _check_file(path)
    decisions: list[Decision] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "decision", "rationale", "related_asset"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"decision CSV header must include {', '.join(sorted(required))}")
        for row_no, row in _bounded(enumerate(reader, 2)):
            source = f"{path.name}:{row_no}"
            timestamp = parse_timestamp(str(row.get("timestamp", "")), source, warnings)
            asset = normalize_asset(str(row.get("related_asset", "")))
            decision = _field(row, "decision", source, warnings, required=True)
            rationale = _field(row, "rationale", source, warnings, required=True)
            if not asset:
                warnings.append(f"{source}: missing required related_asset; record skipped")
            if timestamp is None or not asset or not decision or not rationale:
                continue
            decisions.append(Decision(timestamp, decision, rationale, asset,
                                      _field(row, "outcome", source, warnings),
                                      _field(row, "ttp_ref", source, warnings), source))
    return decisions
