"""CSV log adapter."""
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CSVAdapter:
    """Adapter for CSV format logs."""

    def load(self, path: Path) -> List[Dict[str, Any]]:
        """Load and parse CSV file.

        Args:
            path: Path to .csv file

        Returns:
            List of parsed event dictionaries
        """
        events = []

        if not path.exists():
            print(f"Warning: File not found: {path}")
            return events

        try:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Normalize timestamp
                        if 'timestamp' in row:
                            row['_timestamp'] = self._parse_timestamp(row['timestamp'])
                        events.append(dict(row))
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num} in {path.name}: {e}")

        except Exception as e:
            print(f"Warning: Failed to read CSV file {path}: {e}")

        return events

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse timestamp string to datetime object.

        Supports common CSV timestamp formats.
        """
        # Try common formats
        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse timestamp: {ts_str}")
