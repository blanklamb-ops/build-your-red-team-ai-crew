import re
from src.models import RedactionConfig

def redact(data: str, config: RedactionConfig) -> str:
    for pattern in config.patterns:
        data = re.sub(pattern, '[REDACTED]', data)
    return data
