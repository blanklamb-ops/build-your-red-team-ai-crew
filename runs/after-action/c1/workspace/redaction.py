"""PII and secret redaction for client reports."""
import re
from typing import Dict, List, Any


class Redactor:
    """Redacts sensitive information from text."""

    def __init__(self, custom_rules: List[Dict[str, str]] = None):
        """Initialize redactor with default and custom rules.

        Args:
            custom_rules: Optional list of {'pattern': regex, 'replacement': str}
        """
        self.rules = self._build_default_rules()

        if custom_rules:
            for rule in custom_rules:
                self.rules.append((
                    re.compile(rule['pattern'], re.IGNORECASE),
                    rule['replacement']
                ))

    def _build_default_rules(self) -> List[tuple]:
        """Build default redaction rules.

        Returns:
            List of (compiled_regex, replacement_string) tuples
        """
        rules = []

        # API Keys
        rules.append((
            re.compile(r'sk-proj-[A-Za-z0-9]{30,}', re.IGNORECASE),
            '[REDACTED_API_KEY]'
        ))
        rules.append((
            re.compile(r'sk-[A-Za-z0-9]{20,}', re.IGNORECASE),
            '[REDACTED_API_KEY]'
        ))
        rules.append((
            re.compile(r'ghp_[A-Za-z0-9]{36}', re.IGNORECASE),
            '[REDACTED_GITHUB_TOKEN]'
        ))
        rules.append((
            re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
            '[REDACTED_AWS_KEY]'
        ))

        # Generic secrets/tokens
        rules.append((
            re.compile(r'(secret[_-]?key|api[_-]?key|token)["\s:=]+[A-Za-z0-9+/=_-]{16,}', re.IGNORECASE),
            '[REDACTED_SECRET]'
        ))

        # Passwords
        rules.append((
            re.compile(r'password["\s:=]+[^\s"\']+', re.IGNORECASE),
            'password: [REDACTED_PASSWORD]'
        ))

        # Email addresses
        rules.append((
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            '[REDACTED_EMAIL]'
        ))

        # Private IP addresses (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
        rules.append((
            re.compile(r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            '[REDACTED_IP]'
        ))
        rules.append((
            re.compile(r'\b172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}\b'),
            '[REDACTED_IP]'
        ))
        rules.append((
            re.compile(r'\b192\.168\.\d{1,3}\.\d{1,3}\b'),
            '[REDACTED_IP]'
        ))

        # SSH private keys
        rules.append((
            re.compile(r'-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----', re.DOTALL),
            '[REDACTED_PRIVATE_KEY]'
        ))

        # Generic secret patterns
        rules.append((
            re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+', re.IGNORECASE),
            'Bearer [REDACTED_TOKEN]'
        ))

        return rules

    def redact(self, text: str) -> str:
        """Redact sensitive information from text.

        Args:
            text: Input text potentially containing sensitive data

        Returns:
            Text with sensitive information redacted
        """
        result = text

        for pattern, replacement in self.rules:
            result = pattern.sub(replacement, result)

        return result

    def redact_dict(self, data: Dict[str, Any], fields_to_redact: List[str] = None) -> Dict[str, Any]:
        """Redact sensitive fields in a dictionary.

        Args:
            data: Dictionary to redact
            fields_to_redact: List of field names to redact (defaults to common sensitive fields)

        Returns:
            Dictionary with specified fields redacted
        """
        if fields_to_redact is None:
            fields_to_redact = [
                'password', 'secret', 'token', 'api_key', 'secret_key',
                'private_key', 'credential', 'auth', 'apikey'
            ]

        result = data.copy()

        for key in result:
            # Redact specific fields by name
            if any(sensitive in key.lower() for sensitive in fields_to_redact):
                result[key] = '[REDACTED]'
            # Redact string values with pattern matching
            elif isinstance(result[key], str):
                result[key] = self.redact(result[key])
            # Recursively redact nested dicts
            elif isinstance(result[key], dict):
                result[key] = self.redact_dict(result[key], fields_to_redact)

        return result
