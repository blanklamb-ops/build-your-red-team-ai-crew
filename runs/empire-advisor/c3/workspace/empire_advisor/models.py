"""Immutable data contracts used by the advisor."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class AdvisorError(ValueError):
    """Base class for expected, operator-actionable failures."""


class ConfigurationError(AdvisorError):
    """Raised when a local rule or knowledge-base file is invalid."""


class InputError(AdvisorError):
    """Raised when a command or fixture is invalid."""


@dataclass(frozen=True)
class Citation:
    title: str
    url: str


@dataclass(frozen=True)
class Suggestion:
    id: str
    title: str
    template: str
    rationale: str
    citation: Citation


@dataclass(frozen=True)
class Rule:
    id: str
    pattern: str
    severity: str
    weight: int
    rationale: str
    suggestion_ids: tuple[str, ...]


@dataclass(frozen=True)
class RuleHit:
    id: str
    severity: str
    weight: int
    rationale: str
    evidence: str


@dataclass(frozen=True)
class Advisory:
    schema_version: str
    command: str
    source: str
    score: int
    state: str
    summary: str
    matched_rules: tuple[RuleHit, ...]
    suggestions: tuple[Suggestion, ...]
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable object with stable field ordering."""
        return asdict(self)
