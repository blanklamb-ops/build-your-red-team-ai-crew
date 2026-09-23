"""Event-decision correlation engine."""
from typing import List, Dict, Any, Optional
from datetime import timedelta


class CorrelationEngine:
    """Correlates events with operator decisions based on time and asset matching."""

    def __init__(self, time_window_seconds: int = 300, asset_match: bool = True):
        """Initialize correlation engine.

        Args:
            time_window_seconds: Time window for correlation (±seconds from decision)
            asset_match: Require asset identifiers to match
        """
        self.time_window_seconds = time_window_seconds
        self.asset_match = asset_match

    def correlate(
        self,
        events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Correlate events with decisions.

        Args:
            events: List of event dictionaries (must have _timestamp)
            decisions: List of decision dictionaries (must have _timestamp)

        Returns:
            List of correlated items with both event and decision data
        """
        correlated = []

        # Create sorted copies for efficient matching
        sorted_events = sorted(
            [e for e in events if '_timestamp' in e],
            key=lambda x: x['_timestamp']
        )

        sorted_decisions = sorted(
            [d for d in decisions if '_timestamp' in d],
            key=lambda x: x['_timestamp']
        )

        # For each decision, find matching events
        for decision in sorted_decisions:
            decision_time = decision['_timestamp']
            decision_asset = decision.get('asset', '')

            # Find events within time window
            matching_events = []

            for event in sorted_events:
                event_time = event['_timestamp']
                time_diff = abs((event_time - decision_time).total_seconds())

                if time_diff <= self.time_window_seconds:
                    # Check asset matching if required
                    if self.asset_match:
                        event_asset = event.get('asset', '')
                        if self._assets_match(event_asset, decision_asset):
                            matching_events.append(event)
                    else:
                        matching_events.append(event)

            # Create correlated entries
            if matching_events:
                for event in matching_events:
                    correlated.append({
                        'decision': decision,
                        'event': event,
                        'time_delta': abs((event['_timestamp'] - decision_time).total_seconds()),
                    })
            else:
                # Include decision even without matching events
                correlated.append({
                    'decision': decision,
                    'event': None,
                    'time_delta': 0,
                })

        return correlated

    def _assets_match(self, asset1: str, asset2: str) -> bool:
        """Check if two asset identifiers match.

        Args:
            asset1: First asset identifier
            asset2: Second asset identifier

        Returns:
            True if assets match (exact or substring match)
        """
        if not asset1 or not asset2:
            return False

        # Special case: "all" matches everything
        if asset1 == "all" or asset2 == "all":
            return True

        # Exact match
        if asset1 == asset2:
            return True

        # Substring match (either direction)
        if asset1 in asset2 or asset2 in asset1:
            return True

        return False

    def build_timeline(
        self,
        events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build a unified timeline of events and decisions.

        Args:
            events: List of event dictionaries
            decisions: List of decision dictionaries

        Returns:
            Sorted list of timeline items (events and decisions merged)
        """
        timeline = []

        # Add events to timeline
        for event in events:
            if '_timestamp' in event:
                timeline.append({
                    'timestamp': event['_timestamp'],
                    'type': 'event',
                    'data': event,
                })

        # Add decisions to timeline
        for decision in decisions:
            if '_timestamp' in decision:
                timeline.append({
                    'timestamp': decision['_timestamp'],
                    'type': 'decision',
                    'data': decision,
                })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])

        return timeline
