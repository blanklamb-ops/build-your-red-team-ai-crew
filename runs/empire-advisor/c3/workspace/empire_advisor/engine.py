"""Deterministic, transparent advisory engine."""

from __future__ import annotations

import re
from pathlib import Path

from .config import load_knowledge_base, load_rules
from .models import Advisory, ConfigurationError, InputError, Rule, RuleHit, Suggestion

ROOT = Path(__file__).resolve().parent.parent


class Advisor:
    """Analyze text only. This class intentionally has no execution facility."""

    def __init__(
        self,
        rules: tuple[Rule, ...],
        suggestions: dict[str, Suggestion],
        max_command_length: int,
        warn_threshold: int,
        deny_threshold: int,
    ) -> None:
        dangling = sorted(
            suggestion_id
            for rule in rules
            for suggestion_id in rule.suggestion_ids
            if suggestion_id not in suggestions
        )
        if dangling:
            raise ConfigurationError(f"rules reference unknown suggestion ids: {', '.join(dangling)}")
        self._rules = rules
        self._suggestions = suggestions
        self.max_command_length = max_command_length
        self.warn_threshold = warn_threshold
        self.deny_threshold = deny_threshold

    @classmethod
    def from_paths(cls, rules_path: Path, kb_path: Path) -> "Advisor":
        rules, maximum, warn, deny = load_rules(rules_path)
        suggestions = load_knowledge_base(kb_path)
        return cls(rules, suggestions, maximum, warn, deny)

    @classmethod
    def default(cls) -> "Advisor":
        return cls.from_paths(ROOT / "rules.yaml", ROOT / "kb.yaml")

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self._rules

    def analyze(self, command: str, *, source: str = "operator") -> Advisory:
        if not isinstance(command, str):
            raise InputError("command must be a string")
        normalized = " ".join(command.strip().split())
        if not normalized:
            raise InputError("command must not be empty")
        if len(normalized) > self.max_command_length:
            raise InputError(f"command exceeds maximum length of {self.max_command_length} characters")
        if not isinstance(source, str) or not source.strip():
            raise InputError("source must be a non-empty string")

        hits: list[RuleHit] = []
        suggestion_ids: set[str] = set()
        for rule in self._rules:
            match = re.search(rule.pattern, normalized, re.IGNORECASE)
            if match is None:
                continue
            hits.append(
                RuleHit(
                    id=rule.id,
                    severity=rule.severity,
                    weight=rule.weight,
                    rationale=rule.rationale,
                    evidence=match.group(0),
                )
            )
            suggestion_ids.update(rule.suggestion_ids)

        score = min(100, sum(hit.weight for hit in hits))
        if score >= self.deny_threshold:
            state = "deny"
            summary = "Advisory deny: high-noise or dangerous patterns matched; do not submit without human review. This is not enforcement."
        elif score >= self.warn_threshold:
            state = "warn"
            summary = "Advisory warning: review matched heuristics and cited alternatives before any separate submission."
        else:
            state = "allow"
            summary = (
                "Advisory allow: no configured heuristic matched. This does not establish safety, authorization, "
                "stealth, or absence of detection."
            )
        ordered_suggestions = tuple(
            suggestion for key, suggestion in self._suggestions.items() if key in suggestion_ids
        )
        return Advisory(
            schema_version="1.0",
            command=normalized,
            source=source.strip(),
            score=score,
            state=state,
            summary=summary,
            matched_rules=tuple(hits),
            suggestions=ordered_suggestions,
            execution_performed=False,
        )
