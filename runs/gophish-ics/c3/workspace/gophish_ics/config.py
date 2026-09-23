"""Fail-closed loader for the intentionally tiny shipped configuration."""

from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Configuration is missing, ambiguous, or unsafe."""


class FeatureDisabledError(ConfigError):
    """ICS generation was not explicitly enabled."""


@dataclass(frozen=True)
class AppConfig:
    ics_enabled: bool


def load_config(path: Path) -> AppConfig:
    """Load only ``ics_enabled: true|false`` and reject all ambiguity."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError("configuration is unavailable") from exc

    values: dict[str, str] = {}
    for number, source_line in enumerate(raw.splitlines(), start=1):
        line = source_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(f"invalid configuration syntax on line {number}")
        key, value = (part.strip() for part in line.split(":", 1))
        if key != "ics_enabled":
            raise ConfigError(f"unknown configuration key on line {number}")
        if key in values:
            raise ConfigError("duplicate ics_enabled setting")
        if value not in {"true", "false"}:
            raise ConfigError("ics_enabled must be exactly true or false")
        values[key] = value
    if set(values) != {"ics_enabled"}:
        raise ConfigError("ics_enabled is required")
    return AppConfig(ics_enabled=values["ics_enabled"] == "true")


def require_ics_enabled(config: AppConfig) -> None:
    if not config.ics_enabled:
        raise FeatureDisabledError(
            "ICS generation is disabled; pass an explicitly enabled config for an authorized lab run"
        )
