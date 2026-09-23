from pathlib import Path

from src.main import load_jsonl


def ingest_json(file_path: str):
    warnings: list[str] = []
    return load_jsonl(Path(file_path), warnings)
