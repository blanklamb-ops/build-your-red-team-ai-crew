#!/usr/bin/env python3
"""
ICS/iCal Generator for GoPhish Campaigns
Generates calendar invite payloads for authorized phishing testing.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from icalendar import Calendar, Event
import pytz


class ICSGenerator:
    """Generates ICS calendar invites from campaign data."""

    def __init__(self, config: Dict):
        """
        Initialize generator with configuration.

        Args:
            config: Configuration dict with timezone and other settings
        """
        self.config = config
        self.timezone = pytz.timezone(config.get('campaign', {}).get('timezone', 'UTC'))

    def generate(self, campaign_data: Dict) -> str:
        """
        Generate ICS content from campaign data.

        Args:
            campaign_data: Dict containing:
                - organizer: Email of organizer
                - summary: Event title/subject
                - description: Event description
                - dtstart: Start datetime (ISO format or datetime object)
                - dtend: End datetime (ISO format or datetime object)
                - attendees: List of attendee emails
                - location: Optional location
                - uid: Optional unique identifier

        Returns:
            str: ICS file content

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required = ['organizer', 'summary', 'dtstart']
        for field in required:
            if field not in campaign_data:
                raise ValueError(f"Missing required field: {field}")

        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//GoPhish-ICS//Authorized Testing Only//EN')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')

        # Create event
        event = Event()

        # Add organizer
        event.add('organizer', f"mailto:{campaign_data['organizer']}")

        # Add summary
        event.add('summary', campaign_data['summary'])

        # Add description if present
        if 'description' in campaign_data:
            event.add('description', campaign_data['description'])

        # Add location if present
        if 'location' in campaign_data:
            event.add('location', campaign_data['location'])

        # Parse and add start time with explicit timezone
        dtstart = self._parse_datetime(campaign_data['dtstart'])
        event.add('dtstart', dtstart)

        # Parse or calculate end time
        if 'dtend' in campaign_data:
            dtend = self._parse_datetime(campaign_data['dtend'])
        else:
            # Default duration from config
            duration = self.config.get('campaign', {}).get('default_duration_minutes', 60)
            dtend = dtstart + timedelta(minutes=duration)
        event.add('dtend', dtend)

        # Add UID
        if 'uid' in campaign_data:
            event.add('uid', campaign_data['uid'])
        else:
            # Generate UID from organizer and timestamp
            timestamp = dtstart.strftime('%Y%m%dT%H%M%S')
            event.add('uid', f"{timestamp}@gophish-ics")

        # Add timestamp
        event.add('dtstamp', datetime.now(pytz.UTC))

        # Add sequence
        event.add('sequence', 0)

        # Add status
        event.add('status', 'CONFIRMED')

        # Add attendees
        if 'attendees' in campaign_data:
            for attendee in campaign_data['attendees']:
                event.add('attendee', f"mailto:{attendee}", parameters={
                    'ROLE': 'REQ-PARTICIPANT',
                    'PARTSTAT': 'NEEDS-ACTION',
                    'RSVP': 'TRUE'
                })

        # Add event to calendar
        cal.add_component(event)

        return cal.to_ical().decode('utf-8')

    def _parse_datetime(self, dt_input) -> datetime:
        """
        Parse datetime input to timezone-aware datetime.

        Args:
            dt_input: ISO format string or datetime object

        Returns:
            datetime: Timezone-aware datetime object
        """
        if isinstance(dt_input, datetime):
            dt = dt_input
        elif isinstance(dt_input, str):
            # Parse ISO format
            dt = datetime.fromisoformat(dt_input.replace('Z', '+00:00'))
        else:
            raise ValueError(f"Invalid datetime format: {dt_input}")

        # Ensure timezone awareness
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)

        return dt

    def generate_to_file(self, campaign_data: Dict, output_path: str):
        """
        Generate ICS and write to file.

        Args:
            campaign_data: Campaign data dict
            output_path: Path to output .ics file
        """
        ics_content = self.generate(campaign_data)
        with open(output_path, 'w') as f:
            f.write(ics_content)
