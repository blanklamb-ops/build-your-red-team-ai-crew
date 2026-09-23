from pathlib import Path

from src.main import load_decisions_csv


def load_decision_log(file_path: str):
    warnings: list[str] = []
    return load_decisions_csv(Path(file_path), warnings)
