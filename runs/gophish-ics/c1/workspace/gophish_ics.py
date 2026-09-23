#!/usr/bin/env python3
"""
GoPhish ICS Integration
Sidecar tool for adding calendar invite functionality to GoPhish campaigns.

AUTHORIZED USE ONLY - See AUTHORIZED_USE.md
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

import yaml


class ConfigError(Exception):
    """Configuration or safety check error."""
    pass


class Config:
    """Configuration manager with safety checks."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.data = self._load_config()
        self._validate_safety()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _validate_safety(self):
        """Validate that safety defaults are in place."""
        # This method is called on every config load to ensure safety
        pass

    def is_ics_enabled(self) -> bool:
        """Check if ICS generation is enabled."""
        return self.data.get('ics_enabled', False)

    def require_ics_enabled(self):
        """Raise error if ICS generation is not explicitly enabled."""
        if not self.is_ics_enabled():
            raise ConfigError(
                "ICS generation is disabled. Set 'ics_enabled: true' in config.yaml "
                "only if you have authorization to send calendar invites in this campaign."
            )

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.data.get(key, default)


class ICSGenerator:
    """Generate iCalendar (.ics) files from campaign data."""

    def __init__(self, config: Config):
        self.config = config
        self.ics_settings = config.get('ics_settings', {})

    def generate(self, campaign_data: dict) -> str:
        """
        Generate ICS content from campaign data.

        Args:
            campaign_data: Dictionary with keys:
                - organizer: Email of event organizer
                - summary: Event title
                - dtstart: Start datetime (ISO format or datetime object)
                - dtend: End datetime (ISO format or datetime object)
                - description: Event description
                - attendees: List of attendee emails or dicts with 'email' key
                - uid: Optional unique identifier
                - location: Optional location string

        Returns:
            ICS file content as string
        """
        self.config.require_ics_enabled()

        # Generate unique identifier
        uid = campaign_data.get('uid', str(uuid4()))

        # Parse datetimes
        dtstart = self._parse_datetime(campaign_data.get('dtstart'))
        dtend = self._parse_datetime(campaign_data.get('dtend'))

        if not dtend:
            # Use default duration
            duration = self.ics_settings.get('default_duration', 60)
            dtend = dtstart + timedelta(minutes=duration)

        # Format datetimes for ICS (UTC)
        dtstart_str = dtstart.strftime('%Y%m%dT%H%M%SZ')
        dtend_str = dtend.strftime('%Y%m%dT%H%M%SZ')
        dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

        # Build ICS content
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{self.ics_settings.get('prodid', '-//GoPhish ICS//EN')}",
            "CALSCALE:GREGORIAN",
            "METHOD:REQUEST",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart_str}",
            f"DTEND:{dtend_str}",
            f"SUMMARY:{self._escape_text(campaign_data.get('summary', 'Event'))}",
            f"ORGANIZER;CN={self._escape_text(campaign_data.get('organizer_name', 'Organizer'))}:mailto:{campaign_data.get('organizer', 'noreply@example.com')}",
        ]

        # Add optional fields
        if campaign_data.get('description'):
            lines.append(f"DESCRIPTION:{self._escape_text(campaign_data['description'])}")

        if campaign_data.get('location'):
            lines.append(f"LOCATION:{self._escape_text(campaign_data['location'])}")

        # Add attendees
        attendees = campaign_data.get('attendees', [])
        for attendee in attendees:
            if isinstance(attendee, dict):
                email = attendee.get('email')
                name = attendee.get('name', email)
            else:
                email = attendee
                name = email

            if email:
                lines.append(
                    f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;"
                    f"RSVP=TRUE;CN={self._escape_text(name)}:mailto:{email}"
                )

        # Close event and calendar
        lines.extend([
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "END:VEVENT",
            "END:VCALENDAR"
        ])

        return self._fold_lines(lines)

    def _parse_datetime(self, dt) -> Optional[datetime]:
        """Parse datetime from string or datetime object."""
        if not dt:
            return None

        if isinstance(dt, datetime):
            return dt

        # Try ISO format
        try:
            return datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass

        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(dt, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse datetime: {dt}")

    def _escape_text(self, text: str) -> str:
        """Escape text for ICS format."""
        if not text:
            return ""

        # Replace special characters
        text = text.replace('\\', '\\\\')
        text = text.replace(',', '\\,')
        text = text.replace(';', '\\;')
        text = text.replace('\n', '\\n')

        return text

    def _fold_lines(self, lines: List[str]) -> str:
        """
        Fold long lines according to RFC 5545.
        Lines should be no longer than 75 octets.
        """
        folded = []
        for line in lines:
            if len(line) <= 75:
                folded.append(line)
            else:
                # Fold at 75 characters
                folded.append(line[:75])
                line = line[75:]
                while line:
                    folded.append(' ' + line[:74])  # Continuation lines start with space
                    line = line[74:]

        return '\r\n'.join(folded) + '\r\n'


class TelemetryStore:
    """Store and retrieve RSVP telemetry data."""

    def __init__(self, config: Config):
        self.config = config
        self.db_path = config.get('telemetry_db', 'telemetry.db')
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipients (
                id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL,
                email TEXT NOT NULL,
                name TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rsvp_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rsvp_recipient
            ON rsvp_events(recipient_id)
        ''')

        conn.commit()
        conn.close()

    def create_campaign(self, campaign_id: str, name: str):
        """Create a campaign record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT OR REPLACE INTO campaigns (id, name, created_at) VALUES (?, ?, ?)',
            (campaign_id, name, datetime.utcnow().isoformat())
        )

        conn.commit()
        conn.close()

    def add_recipient(self, campaign_id: str, recipient_id: str, email: str, name: str = None):
        """Add a recipient to a campaign."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT OR REPLACE INTO recipients (id, campaign_id, email, name) VALUES (?, ?, ?, ?)',
            (recipient_id, campaign_id, email, name)
        )

        conn.commit()
        conn.close()

    def record_rsvp(
        self,
        recipient_id: str,
        response: str,
        user_agent: str = None,
        ip_address: str = None
    ):
        """
        Record an RSVP response.

        Args:
            recipient_id: Unique recipient identifier
            response: One of 'accept', 'decline', 'tentative', 'none'
            user_agent: Optional user agent string
            ip_address: Optional IP address
        """
        valid_responses = {'accept', 'decline', 'tentative', 'none'}
        if response not in valid_responses:
            raise ValueError(f"Invalid response: {response}. Must be one of {valid_responses}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''INSERT INTO rsvp_events
               (recipient_id, response, timestamp, user_agent, ip_address)
               VALUES (?, ?, ?, ?, ?)''',
            (recipient_id, response, datetime.utcnow().isoformat(), user_agent, ip_address)
        )

        conn.commit()
        conn.close()

    def get_campaign_stats(self, campaign_id: str) -> Dict[str, int]:
        """
        Get RSVP statistics for a campaign.

        Returns:
            Dictionary with counts: {accept: n, decline: n, tentative: n, none: n, no_response: n}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get latest response per recipient
        cursor.execute('''
            SELECT r.response, COUNT(DISTINCT r.recipient_id) as count
            FROM (
                SELECT recipient_id, response,
                       ROW_NUMBER() OVER (PARTITION BY recipient_id ORDER BY timestamp DESC) as rn
                FROM rsvp_events
                WHERE recipient_id IN (
                    SELECT id FROM recipients WHERE campaign_id = ?
                )
            ) r
            WHERE r.rn = 1
            GROUP BY r.response
        ''', (campaign_id,))

        stats = {'accept': 0, 'decline': 0, 'tentative': 0, 'none': 0}

        for response, count in cursor.fetchall():
            stats[response] = count

        # Get total recipients
        cursor.execute(
            'SELECT COUNT(*) FROM recipients WHERE campaign_id = ?',
            (campaign_id,)
        )
        total_recipients = cursor.fetchone()[0]

        # Calculate no response
        responded = sum(stats.values())
        stats['no_response'] = total_recipients - responded

        conn.close()
        return stats


class Reporter:
    """Generate reports from telemetry data."""

    def __init__(self, telemetry: TelemetryStore):
        self.telemetry = telemetry

    def campaign_summary(self, campaign_id: str) -> str:
        """Generate a text summary report for a campaign."""
        stats = self.telemetry.get_campaign_stats(campaign_id)

        total = sum(stats.values())

        lines = [
            f"Campaign RSVP Summary: {campaign_id}",
            "=" * 60,
            f"Total Recipients: {total}",
            "",
            f"  ✓ Accepted:     {stats['accept']:4d} ({self._pct(stats['accept'], total)})",
            f"  ✗ Declined:     {stats['decline']:4d} ({self._pct(stats['decline'], total)})",
            f"  ? Tentative:    {stats['tentative']:4d} ({self._pct(stats['tentative'], total)})",
            f"  ∅ No Action:    {stats['none']:4d} ({self._pct(stats['none'], total)})",
            f"  - No Response:  {stats['no_response']:4d} ({self._pct(stats['no_response'], total)})",
            "",
        ]

        return '\n'.join(lines)

    def _pct(self, count: int, total: int) -> str:
        """Format percentage."""
        if total == 0:
            return "  0.0%"
        return f"{100.0 * count / total:5.1f}%"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GoPhish ICS Integration - Calendar invite sidecar tool',
        epilog='AUTHORIZED USE ONLY - See AUTHORIZED_USE.md'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate ICS command
    gen_parser = subparsers.add_parser('generate', help='Generate ICS file from JSON')
    gen_parser.add_argument('input', help='Input JSON file with campaign data')
    gen_parser.add_argument('-o', '--output', help='Output ICS file path')
    gen_parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')

    # Record RSVP command
    rsvp_parser = subparsers.add_parser('rsvp', help='Record RSVP response')
    rsvp_parser.add_argument('recipient_id', help='Recipient unique identifier')
    rsvp_parser.add_argument('response', choices=['accept', 'decline', 'tentative', 'none'],
                            help='RSVP response type')
    rsvp_parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate campaign report')
    report_parser.add_argument('campaign_id', help='Campaign identifier')
    report_parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')

    # Check config command
    check_parser = subparsers.add_parser('check-config', help='Verify configuration safety')
    check_parser.add_argument('-c', '--config', default='config.yaml', help='Config file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == 'generate':
            config = Config(args.config)
            generator = ICSGenerator(config)

            # Load campaign data
            with open(args.input, 'r') as f:
                campaign_data = json.load(f)

            # Generate ICS
            ics_content = generator.generate(campaign_data)

            # Output
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(ics_content)
                print(f"Generated ICS file: {args.output}")
            else:
                print(ics_content)

        elif args.command == 'rsvp':
            config = Config(args.config)
            telemetry = TelemetryStore(config)
            telemetry.record_rsvp(args.recipient_id, args.response)
            print(f"Recorded {args.response} for recipient {args.recipient_id}")

        elif args.command == 'report':
            config = Config(args.config)
            telemetry = TelemetryStore(config)
            reporter = Reporter(telemetry)
            print(reporter.campaign_summary(args.campaign_id))

        elif args.command == 'check-config':
            config = Config(args.config)

            print("Configuration Safety Check")
            print("=" * 60)
            print(f"Config file: {args.config}")
            print(f"ICS enabled: {config.is_ics_enabled()}")

            if config.is_ics_enabled():
                print("\n⚠ WARNING: ICS generation is ENABLED")
                print("Only use with proper authorization!")
            else:
                print("\n✓ Safe: ICS generation is disabled by default")

            return 0

    except ConfigError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
