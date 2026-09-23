"""Thin package wrappers around src.main (kept for Codestral scaffold paths)."""

from src.main import (
    correlate,
    ingest_engagement,
    load_decisions_csv,
    load_events_csv,
    load_jsonl,
    redact,
    render_client_md,
    render_internal_md,
)

__all__ = [
    "correlate",
    "ingest_engagement",
    "load_decisions_csv",
    "load_events_csv",
    "load_jsonl",
    "redact",
    "render_client_md",
    "render_internal_md",
]
