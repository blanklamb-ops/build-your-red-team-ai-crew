from src.main import redact


def validate_data(rows):
    """Return rows unchanged; missing fields are handled at ingest with warnings."""
    return rows


def redact_data(text: str) -> str:
    return redact(text)
