"""Empire-shaped explicit pre-submit adapter.

This is intentionally not a transparent global Empire hook. An operator UI or
workflow calls execute before separately deciding whether to submit tasking.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .engine import Advisor
from .models import InputError


class Plugin:
    """Minimal Empire-style plugin object that returns advisory JSON only."""

    name = "empire-advisor"
    author = ["Authorized Research Pipeline"]
    description = "Scores pending command text before a separate operator-controlled submission."
    options = {
        "Command": {
            "Description": "Pending command text to analyze; it will not be executed.",
            "Required": True,
            "Value": "",
        },
        "Source": {
            "Description": "Non-sensitive label for the submission source.",
            "Required": False,
            "Value": "empire-wrapper",
        },
    }

    def __init__(self, *_args: object, advisor: Advisor | None = None, **_kwargs: object) -> None:
        self._advisor = advisor or Advisor.default()

    def execute(self, command: Mapping[str, Any], **_kwargs: object) -> str:
        """Return an advisory; never send, run, or mutate the supplied command."""
        if not isinstance(command, Mapping):
            raise InputError("plugin command must be a mapping")
        text = command.get("Command")
        source = command.get("Source", "empire-wrapper")
        if not isinstance(text, str):
            raise InputError("plugin Command must be a string")
        if not isinstance(source, str):
            raise InputError("plugin Source must be a string")
        result = self._advisor.analyze(text, source=source)
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)


def advise_submission(command: str, *, source: str = "empire-wrapper") -> dict[str, Any]:
    """Convenience wrapper for an operator UI's explicit pre-submit step."""
    return Advisor.default().analyze(command, source=source).to_dict()
