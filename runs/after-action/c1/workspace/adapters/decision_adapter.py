"""Operator decision log adapter."""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class DecisionAdapter:
    """Adapter for operator decision logs (JSON Lines format)."""

    def load(self, path: Path) -> List[Dict[str, Any]]:
        """Load and parse operator decision log.

        Args:
            path: Path to decision log file (.jsonl)

        Returns:
            List of parsed decision dictionaries
        """
        decisions = []

        if not path.exists():
            print(f"Warning: Decision log not found: {path}")
            return decisions

        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    decision = json.loads(line)

                    # Validate required fields
                    required = ['timestamp', 'decision', 'rationale', 'asset']
                    missing = [field for field in required if field not in decision]

                    if missing:
                        print(f"Warning: Decision at line {line_num} missing fields: {missing}")
                        # Still include it with degraded functionality

                    # Normalize timestamp
                    if 'timestamp' in decision:
                        decision['_timestamp'] = self._parse_timestamp(decision['timestamp'])

                    decisions.append(decision)

                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse decision at line {line_num}: {e}")
                except Exception as e:
                    print(f"Warning: Error processing decision at line {line_num}: {e}")

        return decisions

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
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

        try:
            return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        except Exception:
            pass

        raise ValueError(f"Unable to parse timestamp: {ts_str}")
