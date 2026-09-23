#!/usr/bin/env python3
"""
Telemetry storage for RSVP responses in GoPhish-ICS campaigns.
"""

import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Optional
from enum import Enum


class RSVPStatus(Enum):
    """RSVP response statuses matching iCal PARTSTAT values."""
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    TENTATIVE = "TENTATIVE"
    NEEDS_ACTION = "NEEDS-ACTION"


class TelemetryStore:
    """SQLite-based storage for campaign RSVP telemetry."""

    def __init__(self, db_path: str):
        """
        Initialize telemetry store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create database schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rsvp_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_agent TEXT,
                    ip_address TEXT,
                    UNIQUE(campaign_id, recipient_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaign
                ON rsvp_responses(campaign_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipient
                ON rsvp_responses(recipient_id)
            """)

            conn.commit()

    def record_rsvp(self, campaign_id: str, recipient_id: str,
                    recipient_email: str, status: RSVPStatus,
                    user_agent: Optional[str] = None,
                    ip_address: Optional[str] = None) -> bool:
        """
        Record or update an RSVP response.

        Args:
            campaign_id: Campaign identifier
            recipient_id: Unique recipient identifier (stable across events)
            recipient_email: Recipient email address
            status: RSVP status enum value
            user_agent: Optional User-Agent header
            ip_address: Optional IP address

        Returns:
            bool: True if inserted, False if updated
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Try to insert, update if exists
            cursor = conn.execute("""
                INSERT INTO rsvp_responses
                (campaign_id, recipient_id, recipient_email, status, timestamp, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(campaign_id, recipient_id) DO UPDATE SET
                    status = excluded.status,
                    timestamp = excluded.timestamp,
                    user_agent = excluded.user_agent,
                    ip_address = excluded.ip_address
            """, (campaign_id, recipient_id, recipient_email,
                  status.value, timestamp, user_agent, ip_address))

            conn.commit()
            return cursor.rowcount == 1

    def get_campaign_rsvps(self, campaign_id: str) -> List[Dict]:
        """
        Get all RSVP responses for a campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            List of dicts with RSVP data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM rsvp_responses
                WHERE campaign_id = ?
                ORDER BY timestamp DESC
            """, (campaign_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_campaign_stats(self, campaign_id: str) -> Dict[str, int]:
        """
        Get aggregated RSVP statistics for a campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Dict with counts per status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM rsvp_responses
                WHERE campaign_id = ?
                GROUP BY status
            """, (campaign_id,))

            stats = {row[0]: row[1] for row in cursor.fetchall()}

            # Ensure all statuses are present
            for status in RSVPStatus:
                if status.value not in stats:
                    stats[status.value] = 0

            return stats

    def get_recipient_history(self, recipient_id: str) -> List[Dict]:
        """
        Get RSVP history for a specific recipient across campaigns.

        Args:
            recipient_id: Recipient identifier

        Returns:
            List of dicts with RSVP history
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM rsvp_responses
                WHERE recipient_id = ?
                ORDER BY timestamp DESC
            """, (recipient_id,))

            return [dict(row) for row in cursor.fetchall()]

    def list_campaigns(self) -> List[str]:
        """
        List all campaign IDs with recorded responses.

        Returns:
            List of campaign IDs
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT campaign_id FROM rsvp_responses
                ORDER BY campaign_id
            """)

            return [row[0] for row in cursor.fetchall()]
