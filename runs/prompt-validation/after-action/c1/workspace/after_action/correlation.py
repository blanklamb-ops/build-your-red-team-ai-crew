"""
Correlation engine for joining events and decisions.

Correlates based on:
- Time window (configurable, default ±5 minutes)
- Asset key matching
"""

from datetime import timedelta
from typing import List, Dict, Any, Tuple
import logging

from .adapters import LogEvent, DecisionLog

logger = logging.getLogger(__name__)


class CorrelatedItem:
    """A decision correlated with related events."""

    def __init__(self, decision: DecisionLog, events: List[LogEvent]):
        self.decision = decision
        self.events = events

    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision.to_dict(),
            'related_events': [e.to_dict() for e in self.events]
        }


class CorrelationEngine:
    """Correlates events with operator decisions."""

    def __init__(self, time_window_minutes: int = 5):
        """
        Initialize correlation engine.

        Args:
            time_window_minutes: Time window for correlation (±N minutes)
        """
        self.time_window = timedelta(minutes=time_window_minutes)
        logger.info(f"Correlation engine initialized with ±{time_window_minutes}min window")

    def correlate(self, events: List[LogEvent], decisions: List[DecisionLog]) -> List[CorrelatedItem]:
        """
        Correlate decisions with events based on time window and asset matching.

        Args:
            events: List of log events
            decisions: List of operator decisions

        Returns:
            List of correlated items (decisions with related events)
        """
        logger.info(f"Correlating {len(decisions)} decisions with {len(events)} events")
        correlated = []

        for decision in decisions:
            related_events = []

            # Find events within time window
            for event in events:
                time_diff = abs(event.timestamp - decision.timestamp)

                if time_diff <= self.time_window:
                    # Check asset match
                    if self._assets_match(event.asset, decision.asset):
                        related_events.append(event)
                    # Also include events that mention the asset in details
                    elif self._asset_in_details(decision.asset, event.details):
                        related_events.append(event)

            # Sort related events by timestamp
            related_events.sort(key=lambda e: e.timestamp)

            correlated.append(CorrelatedItem(decision, related_events))
            logger.debug(f"Decision '{decision.decision}' matched with {len(related_events)} events")

        logger.info(f"Correlation complete: {len(correlated)} items")
        return correlated

    def _assets_match(self, asset1: str, asset2: str) -> bool:
        """
        Check if two asset identifiers match.

        Handles:
        - Exact matches (case-insensitive)
        - Partial matches (substring)
        - 'unknown' never matches
        """
        if asset1 == 'unknown' or asset2 == 'unknown':
            return False

        asset1_lower = asset1.lower()
        asset2_lower = asset2.lower()

        # Exact match
        if asset1_lower == asset2_lower:
            return True

        # Substring match (handles IPs in hostnames, etc.)
        if asset1_lower in asset2_lower or asset2_lower in asset1_lower:
            return True

        return False

    def _asset_in_details(self, asset: str, details: Dict[str, Any]) -> bool:
        """Check if asset appears in event details."""
        if asset == 'unknown':
            return False

        asset_lower = asset.lower()

        for value in details.values():
            if isinstance(value, str) and asset_lower in value.lower():
                return True

        return False

    def build_timeline(self, correlated: List[CorrelatedItem]) -> List[Dict[str, Any]]:
        """
        Build a chronological timeline from correlated items.

        Returns:
            Timeline entries sorted by timestamp
        """
        timeline = []

        for item in correlated:
            timeline.append({
                'timestamp': item.decision.timestamp.isoformat(),
                'type': 'decision',
                'content': f"{item.decision.decision}: {item.decision.rationale}",
                'asset': item.decision.asset,
                'event_count': len(item.events)
            })

            for event in item.events:
                timeline.append({
                    'timestamp': event.timestamp.isoformat(),
                    'type': 'event',
                    'content': f"{event.event_type}",
                    'asset': event.asset,
                    'details': event.details
                })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])

        logger.info(f"Built timeline with {len(timeline)} entries")
        return timeline
