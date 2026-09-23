"""Strict loaders for JSON-formatted YAML policy files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .models import Citation, ConfigurationError, Rule, Suggestion

SEVERITIES = frozenset({"low", "medium", "high", "critical"})


def _read_object(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigurationError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"invalid JSON-compatible YAML in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError(f"{path}: top level must be an object")
    return raw


def _text(obj: dict[str, Any], field: str, context: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{context}.{field} must be a non-empty string")
    return value.strip()


def _unique_id(value: str, seen: set[str], context: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        raise ConfigurationError(f"{context} id must use lowercase letters, digits, and hyphens")
    if value in seen:
        raise ConfigurationError(f"duplicate id: {value}")
    seen.add(value)


def load_rules(path: Path) -> tuple[tuple[Rule, ...], int, int, int]:
    data = _read_object(path)
    if data.get("schema_version") != "1.0":
        raise ConfigurationError(f"{path}: schema_version must be '1.0'")
    max_length = data.get("max_command_length")
    thresholds = data.get("thresholds")
    rows = data.get("rules")
    if not isinstance(max_length, int) or isinstance(max_length, bool) or not 1 <= max_length <= 65536:
        raise ConfigurationError(f"{path}: max_command_length must be an integer from 1 to 65536")
    if not isinstance(thresholds, dict):
        raise ConfigurationError(f"{path}: thresholds must be an object")
    warn, deny = thresholds.get("warn"), thresholds.get("deny")
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (warn, deny)):
        raise ConfigurationError(f"{path}: warn and deny thresholds must be integers")
    if not 0 < warn < deny <= 100:
        raise ConfigurationError(f"{path}: thresholds must satisfy 0 < warn < deny <= 100")
    if not isinstance(rows, list) or not rows:
        raise ConfigurationError(f"{path}: rules must be a non-empty array")

    rules: list[Rule] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        context = f"rules[{index}]"
        if not isinstance(row, dict):
            raise ConfigurationError(f"{context} must be an object")
        rule_id = _text(row, "id", context)
        _unique_id(rule_id, seen, context)
        pattern = _text(row, "pattern", context)
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            raise ConfigurationError(f"{context}.pattern is invalid: {exc}") from exc
        severity = _text(row, "severity", context)
        if severity not in SEVERITIES:
            raise ConfigurationError(f"{context}.severity must be one of {sorted(SEVERITIES)}")
        weight = row.get("weight")
        if not isinstance(weight, int) or isinstance(weight, bool) or not 1 <= weight <= 100:
            raise ConfigurationError(f"{context}.weight must be an integer from 1 to 100")
        suggestion_ids = row.get("suggestion_ids")
        if not isinstance(suggestion_ids, list) or not suggestion_ids or any(
            not isinstance(item, str) or not item for item in suggestion_ids
        ):
            raise ConfigurationError(f"{context}.suggestion_ids must be a non-empty string array")
        rules.append(
            Rule(
                id=rule_id,
                pattern=pattern,
                severity=severity,
                weight=weight,
                rationale=_text(row, "rationale", context),
                suggestion_ids=tuple(suggestion_ids),
            )
        )
    return tuple(rules), max_length, warn, deny


def load_knowledge_base(path: Path) -> dict[str, Suggestion]:
    data = _read_object(path)
    if data.get("schema_version") != "1.0":
        raise ConfigurationError(f"{path}: schema_version must be '1.0'")
    rows = data.get("suggestions")
    if not isinstance(rows, list) or not rows:
        raise ConfigurationError(f"{path}: suggestions must be a non-empty array")
    suggestions: dict[str, Suggestion] = {}
    seen: set[str] = set()
    for index, row in enumerate(rows):
        context = f"suggestions[{index}]"
        if not isinstance(row, dict):
            raise ConfigurationError(f"{context} must be an object")
        suggestion_id = _text(row, "id", context)
        _unique_id(suggestion_id, seen, context)
        citation = row.get("citation")
        if not isinstance(citation, dict):
            raise ConfigurationError(f"{context}.citation must be an object")
        url = _text(citation, "url", f"{context}.citation")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigurationError(f"{context}.citation.url must be an HTTP(S) URL")
        suggestions[suggestion_id] = Suggestion(
            id=suggestion_id,
            title=_text(row, "title", context),
            template=_text(row, "template", context),
            rationale=_text(row, "rationale", context),
            citation=Citation(title=_text(citation, "title", f"{context}.citation"), url=url),
        )
    return suggestions
