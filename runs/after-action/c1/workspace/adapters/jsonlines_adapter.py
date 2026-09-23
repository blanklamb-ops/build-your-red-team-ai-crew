"""JSON Lines log adapter."""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class JSONLinesAdapter:
    """Adapter for JSON Lines format logs."""

    def load(self, path: Path) -> List[Dict[str, Any]]:
        """Load and parse JSON Lines file.

        Args:
            path: Path to .jsonl file

        Returns:
            List of parsed event dictionaries
        """
        events = []

        if not path.exists():
            print(f"Warning: File not found: {path}")
            return events

        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    # Normalize timestamp
                    if 'timestamp' in event:
                        event['_timestamp'] = self._parse_timestamp(event['timestamp'])
                    events.append(event)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line {line_num} in {path.name}: {e}")
                except Exception as e:
                    print(f"Warning: Error processing line {line_num} in {path.name}: {e}")

        return events

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse timestamp string to datetime object.

        Supports ISO 8601 format and common variations.
        """
        # Try ISO format first
        for fmt in [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue

        # Fallback: try to parse with fromisoformat
        try:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except Exception:
            pass

        raise ValueError(f"Unable to parse timestamp: {ts_str}")
