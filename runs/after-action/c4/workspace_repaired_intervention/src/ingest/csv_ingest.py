from pathlib import Path

from src.main import load_events_csv


def ingest_csv(file_path: str):
    warnings: list[str] = []
    return load_events_csv(Path(file_path), warnings)
