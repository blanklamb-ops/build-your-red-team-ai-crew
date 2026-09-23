"""Configurable regex redaction for client-bound content."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RedactionRule:
    name: str
    pattern: re.Pattern[str]
    replacement: str


def load_rules(path: Path) -> list[RedactionRule]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load redaction configuration: {path.name}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError("redaction configuration must be a nonempty JSON list")
    rules: list[RedactionRule] = []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict) or not all(key in item for key in ("name", "pattern", "replacement")):
            raise ValueError(f"redaction rule {index} is incomplete")
        replacement = str(item["replacement"])
        if "\\" in replacement or "$" in replacement:
            raise ValueError(f"redaction rule {index} replacement must be a fixed label")
        try:
            compiled = re.compile(str(item["pattern"]), re.IGNORECASE | re.MULTILINE)
        except re.error as exc:
            raise ValueError(f"redaction rule {index} has an invalid pattern") from exc
        rules.append(RedactionRule(str(item["name"]), compiled, replacement))
    return rules


def redact_text(text: str, rules: list[RedactionRule]) -> str:
    redacted = text
    for rule in rules:
        redacted = rule.pattern.sub(lambda _match, label=rule.replacement: label, redacted)
    return redacted
