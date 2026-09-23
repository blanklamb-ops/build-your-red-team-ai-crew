"""
PII and secret redaction for client-facing reports.

Configurable regex-based rules to sanitize sensitive data before export.
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class RedactionRule:
    """A single redaction rule with pattern and replacement."""

    def __init__(self, name: str, pattern: str, replacement: str = "[REDACTED]"):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.replacement = replacement

    def apply(self, text: str) -> Tuple[str, int]:
        """
        Apply redaction rule to text.

        Returns:
            Tuple of (redacted_text, match_count)
        """
        result, count = self.pattern.subn(self.replacement, text)
        return result, count


class RedactionEngine:
    """Applies redaction rules to sanitize sensitive data."""

    DEFAULT_RULES = [
        # API keys and tokens
        {
            "name": "openai_api_key",
            "regex": r"sk-[a-zA-Z0-9]{32,}",
            "replacement": "[REDACTED-API-KEY]"
        },
        {
            "name": "generic_api_key",
            "regex": r"(?i)api[_-]?key[\"']?\s*[:=]\s*[\"']?([a-zA-Z0-9_\-]{16,})",
            "replacement": "api_key=[REDACTED-API-KEY]"
        },
        # Passwords
        {
            "name": "password",
            "regex": r"(?i)password[\"']?\s*[:=]\s*[\"']?([^\s\"']{6,})",
            "replacement": "password=[REDACTED-PASSWORD]"
        },
        # AWS keys
        {
            "name": "aws_access_key",
            "regex": r"AKIA[0-9A-Z]{16}",
            "replacement": "[REDACTED-AWS-KEY]"
        },
        # Private keys
        {
            "name": "private_key",
            "regex": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----[\s\S]*?-----END (RSA |EC )?PRIVATE KEY-----",
            "replacement": "[REDACTED-PRIVATE-KEY]"
        },
        # Email addresses
        {
            "name": "email",
            "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "replacement": "[REDACTED-EMAIL]"
        },
        # JWT tokens
        {
            "name": "jwt",
            "regex": r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
            "replacement": "[REDACTED-JWT]"
        },
        # IP addresses (optional - may want to keep some)
        # Commented out by default as IPs are often needed in security reports
        # {
        #     "name": "ipv4",
        #     "regex": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        #     "replacement": "[REDACTED-IP]"
        # },
        # Social Security Numbers (US)
        {
            "name": "ssn",
            "regex": r"\b\d{3}-\d{2}-\d{4}\b",
            "replacement": "[REDACTED-SSN]"
        },
        # Credit card numbers
        {
            "name": "credit_card",
            "regex": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "replacement": "[REDACTED-CC]"
        }
    ]

    def __init__(self, rules: List[Dict[str, str]] = None):
        """
        Initialize redaction engine.

        Args:
            rules: List of rule dictionaries with 'name', 'regex', 'replacement'
                  If None, uses DEFAULT_RULES
        """
        if rules is None:
            rules = self.DEFAULT_RULES

        self.rules = [
            RedactionRule(r['name'], r['regex'], r.get('replacement', '[REDACTED]'))
            for r in rules
        ]

        logger.info(f"Redaction engine initialized with {len(self.rules)} rules")

    @classmethod
    def from_config_file(cls, config_path: Path):
        """Load redaction rules from JSON config file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                rules = config.get('patterns', cls.DEFAULT_RULES)
                logger.info(f"Loaded redaction config from {config_path}")
                return cls(rules)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}, using defaults")
            return cls()

    def redact(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Apply all redaction rules to text.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, stats_dict)
            stats_dict maps rule name to number of matches
        """
        stats = {}
        result = text

        for rule in self.rules:
            result, count = rule.apply(result)
            if count > 0:
                stats[rule.name] = count
                logger.debug(f"Rule '{rule.name}' matched {count} time(s)")

        total_redactions = sum(stats.values())
        if total_redactions > 0:
            logger.info(f"Total redactions: {total_redactions}")

        return result, stats

    def redact_dict(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """
        Recursively redact all string values in a dictionary.

        Args:
            data: Dictionary to redact

        Returns:
            Tuple of (redacted_dict, stats_dict)
        """
        result = {}
        total_stats = {}

        for key, value in data.items():
            if isinstance(value, str):
                redacted_value, stats = self.redact(value)
                result[key] = redacted_value
                # Merge stats
                for rule_name, count in stats.items():
                    total_stats[rule_name] = total_stats.get(rule_name, 0) + count

            elif isinstance(value, dict):
                redacted_dict, stats = self.redact_dict(value)
                result[key] = redacted_dict
                # Merge stats
                for rule_name, count in stats.items():
                    total_stats[rule_name] = total_stats.get(rule_name, 0) + count

            elif isinstance(value, list):
                redacted_list = []
                for item in value:
                    if isinstance(item, str):
                        redacted_item, stats = self.redact(item)
                        redacted_list.append(redacted_item)
                        for rule_name, count in stats.items():
                            total_stats[rule_name] = total_stats.get(rule_name, 0) + count
                    elif isinstance(item, dict):
                        redacted_item, stats = self.redact_dict(item)
                        redacted_list.append(redacted_item)
                        for rule_name, count in stats.items():
                            total_stats[rule_name] = total_stats.get(rule_name, 0) + count
                    else:
                        redacted_list.append(item)
                result[key] = redacted_list

            else:
                result[key] = value

        return result, total_stats
