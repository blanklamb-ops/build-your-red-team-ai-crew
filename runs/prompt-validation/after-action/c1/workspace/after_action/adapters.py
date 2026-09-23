"""
Log format adapters for ingesting engagement data.

Supports multiple input formats:
- JSON Lines (.jsonl)
- CSV (.csv)
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LogEvent:
    """Normalized log event from any adapter."""

    def __init__(self, timestamp: datetime, event_type: str, asset: str, details: Dict[str, Any]):
        self.timestamp = timestamp
        self.event_type = event_type
        self.asset = asset
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'asset': self.asset,
            'details': self.details
        }


class JSONLAdapter:
    """Adapter for JSON Lines format."""

    @staticmethod
    def load(file_path: Path) -> List[LogEvent]:
        """Load events from JSONL file."""
        events = []
        logger.info(f"Loading JSONL from {file_path}")

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                        # Parse timestamp
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

                        # Extract fields with fallbacks
                        event_type = data.get('event_type', data.get('event', 'unknown'))
                        asset = data.get('asset', data.get('target', data.get('host', 'unknown')))

                        # Remaining fields go to details
                        details = {k: v for k, v in data.items()
                                  if k not in ['timestamp', 'event_type', 'event', 'asset', 'target', 'host']}

                        events.append(LogEvent(timestamp, event_type, asset, details))

                    except (KeyError, ValueError, json.JSONDecodeError) as e:
                        logger.warning(f"Skipping malformed line {line_num} in {file_path}: {e}")
                        continue

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []

        logger.info(f"Loaded {len(events)} events from {file_path}")
        return events


class CSVAdapter:
    """Adapter for CSV format."""

    @staticmethod
    def load(file_path: Path) -> List[LogEvent]:
        """Load events from CSV file."""
        events = []
        logger.info(f"Loading CSV from {file_path}")

        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse timestamp (try common column names)
                        timestamp_raw = row.get('timestamp') or row.get('time') or row.get('datetime')
                        if not timestamp_raw:
                            logger.warning(f"No timestamp in row {row_num}, skipping")
                            continue

                        timestamp = datetime.fromisoformat(timestamp_raw.replace('Z', '+00:00'))

                        # Extract event type
                        event_type = row.get('event_type') or row.get('event') or row.get('action') or 'unknown'

                        # Extract asset
                        asset = row.get('asset') or row.get('target') or row.get('host') or row.get('ip') or 'unknown'

                        # Remaining fields go to details
                        details = {k: v for k, v in row.items()
                                  if k not in ['timestamp', 'time', 'datetime', 'event_type', 'event', 'action', 'asset', 'target', 'host', 'ip']}

                        events.append(LogEvent(timestamp, event_type, asset, details))

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping malformed row {row_num} in {file_path}: {e}")
                        continue

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []

        logger.info(f"Loaded {len(events)} events from {file_path}")
        return events


class DecisionLog:
    """Operator decision log entry."""

    def __init__(self, timestamp: datetime, decision: str, rationale: str, asset: str):
        self.timestamp = timestamp
        self.decision = decision
        self.rationale = rationale
        self.asset = asset

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'decision': self.decision,
            'rationale': self.rationale,
            'asset': self.asset
        }


class DecisionLogAdapter:
    """Adapter for operator decision logs (JSONL format)."""

    @staticmethod
    def load(file_path: Path) -> List[DecisionLog]:
        """Load decisions from JSONL file."""
        decisions = []
        logger.info(f"Loading decision log from {file_path}")

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                        decision = data['decision']
                        rationale = data.get('rationale', '')
                        asset = data.get('asset', data.get('related_asset', 'unknown'))

                        decisions.append(DecisionLog(timestamp, decision, rationale, asset))

                    except (KeyError, ValueError, json.JSONDecodeError) as e:
                        logger.warning(f"Skipping malformed decision {line_num} in {file_path}: {e}")
                        continue

        except FileNotFoundError:
            logger.error(f"Decision log not found: {file_path}")
            return []

        logger.info(f"Loaded {len(decisions)} decisions from {file_path}")
        return decisions


def load_all_logs(log_dir: Path) -> List[LogEvent]:
    """
    Load all logs from a directory, auto-detecting format by extension.

    Args:
        log_dir: Directory containing log files

    Returns:
        Combined list of LogEvent objects
    """
    all_events = []
    log_dir = Path(log_dir)

    if not log_dir.exists():
        logger.error(f"Log directory does not exist: {log_dir}")
        return []

    for file_path in log_dir.iterdir():
        if file_path.suffix == '.jsonl':
            all_events.extend(JSONLAdapter.load(file_path))
        elif file_path.suffix == '.csv':
            all_events.extend(CSVAdapter.load(file_path))
        else:
            logger.info(f"Skipping unsupported file type: {file_path}")

    # Sort by timestamp
    all_events.sort(key=lambda e: e.timestamp)

    logger.info(f"Total events loaded: {len(all_events)}")
    return all_events
