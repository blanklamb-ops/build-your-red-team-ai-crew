from pathlib import Path

from src.main import ingest_engagement, load_events_csv, load_jsonl


def ingest(file_path: str):
    """Dispatch a single file through the matching adapter (scaffold API)."""
    path = Path(file_path)
    warnings: list[str] = []
    if path.suffix == ".jsonl" or path.name.endswith(".jsonl"):
        return load_jsonl(path, warnings)
    if path.suffix == ".csv":
        return load_events_csv(path, warnings)
    raise ValueError(f"Unsupported file format: {path.suffix}")


def ingest_dir(engagement_dir: str):
    return ingest_engagement(Path(engagement_dir))
