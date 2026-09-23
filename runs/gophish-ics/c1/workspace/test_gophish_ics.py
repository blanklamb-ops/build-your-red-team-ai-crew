#!/usr/bin/env python3
"""
Tests for GoPhish ICS Integration

Verifies:
- Safety defaults (A6)
- ICS generation (A2, A3)
- Telemetry recording (A4)
- Reporting (A5)
"""

import json
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from icalendar import Calendar

from gophish_ics import Config, ConfigError, ICSGenerator, Reporter, TelemetryStore


class TestSafetyDefaults:
    """Test A6: Configuration safety defaults."""

    def test_shipped_config_has_ics_disabled(self):
        """
        A6: The checked-in configuration has ics_enabled: false.
        This test loads the ACTUAL shipped config.yaml file.
        """
        config_path = Path(__file__).parent / "config.yaml"
        assert config_path.exists(), "Shipped config.yaml must exist"

        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        # Verify the shipped default is false
        assert config_data.get('ics_enabled') is False, \
            "Shipped config.yaml MUST have ics_enabled: false"

    def test_config_object_blocks_generation_by_default(self):
        """
        A6: Verify that Config object refuses generation when disabled.
        """
        config_path = Path(__file__).parent / "config.yaml"
        config = Config(str(config_path))

        # Should be disabled
        assert not config.is_ics_enabled()

        # Should raise error when trying to require enabled
        with pytest.raises(ConfigError) as exc_info:
            config.require_ics_enabled()

        assert "disabled" in str(exc_info.value).lower()

    def test_generator_refuses_when_disabled(self):
        """
        A6: ICS generator must refuse to generate when disabled.
        """
        # Use shipped config
        config_path = Path(__file__).parent / "config.yaml"
        config = Config(str(config_path))
        generator = ICSGenerator(config)

        campaign_data = {
            "organizer": "test@example.com",
            "summary": "Test Event",
            "dtstart": "2026-10-15T14:00:00Z",
        }

        # Generation should fail with shipped config
        with pytest.raises(ConfigError) as exc_info:
            generator.generate(campaign_data)

        assert "disabled" in str(exc_info.value).lower()


class TestICSGeneration:
    """Test A2, A3: ICS generation and validation."""

    @pytest.fixture
    def enabled_config(self):
        """Create a temporary config with ICS enabled for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'ics_enabled': True, 'ics_settings': {}}, f)
            config_path = f.name

        yield Config(config_path)

        # Cleanup
        os.unlink(config_path)

    @pytest.fixture
    def campaign_fixture(self):
        """Load campaign fixture data."""
        fixture_path = Path(__file__).parent / "testdata" / "campaign_fixture.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_generates_ics_from_fixture(self, enabled_config, campaign_fixture):
        """A2: ICS generator produces .ics from fixture JSON."""
        generator = ICSGenerator(enabled_config)

        ics_content = generator.generate(campaign_fixture)

        # Verify basic structure
        assert ics_content.startswith('BEGIN:VCALENDAR')
        assert 'BEGIN:VEVENT' in ics_content
        assert 'END:VEVENT' in ics_content
        assert 'END:VCALENDAR' in ics_content

        # Verify content
        assert 'Quarterly Planning Session' in ics_content
        assert 'hr@example.com' in ics_content

    def test_ics_validates_with_icalendar(self, enabled_config, campaign_fixture):
        """A3: ICS validates via icalendar library."""
        generator = ICSGenerator(enabled_config)
        ics_content = generator.generate(campaign_fixture)

        # Parse with icalendar library
        cal = Calendar.from_ical(ics_content)

        # Verify it parsed successfully
        assert cal is not None

        # Verify event properties
        events = cal.walk('VEVENT')
        assert len(events) == 1

        event = events[0]
        assert 'SUMMARY' in event
        assert event['SUMMARY'] == 'Quarterly Planning Session'

    def test_timezone_explicit_utc(self, enabled_config, campaign_fixture):
        """M2: Timezones in ICS are explicit (UTC format with Z suffix)."""
        generator = ICSGenerator(enabled_config)
        ics_content = generator.generate(campaign_fixture)

        # Verify UTC timestamps end with Z
        assert 'DTSTART:' in ics_content
        lines = ics_content.split('\r\n')
        dtstart_lines = [l for l in lines if l.startswith('DTSTART:')]

        assert len(dtstart_lines) > 0
        # Should be in format YYYYMMDDTHHMMSSZ
        assert dtstart_lines[0].endswith('Z') or 'TZID=' in dtstart_lines[0]

    def test_attendees_included(self, enabled_config, campaign_fixture):
        """Verify attendees are included in ICS."""
        generator = ICSGenerator(enabled_config)
        ics_content = generator.generate(campaign_fixture)

        # Check for attendees
        assert 'alice@example.com' in ics_content
        assert 'bob@example.com' in ics_content
        assert 'ATTENDEE' in ics_content
        # RSVP may be line-folded per RFC 5545
        assert 'RSVP=' in ics_content and 'TRUE' in ics_content


class TestTelemetry:
    """Test A4: Telemetry tracking."""

    @pytest.fixture
    def telemetry(self):
        """Create telemetry store with temporary database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        # Create minimal config
        config_data = {'telemetry_db': db_path, 'ics_enabled': False}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        config = Config(config_path)
        store = TelemetryStore(config)

        yield store

        # Cleanup
        os.unlink(db_path)
        os.unlink(config_path)

    @pytest.fixture
    def fixture_data(self):
        """Load RSVP fixture."""
        fixture_path = Path(__file__).parent / "testdata" / "rsvp_fixture.json"
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_records_accept_and_decline(self, telemetry):
        """A4: Telemetry store records at least accept + decline."""
        campaign_id = "test-campaign-001"

        # Create campaign and recipients
        telemetry.create_campaign(campaign_id, "Test Campaign")
        telemetry.add_recipient(campaign_id, "rec-001", "alice@example.com", "Alice")
        telemetry.add_recipient(campaign_id, "rec-002", "bob@example.com", "Bob")

        # Record responses
        telemetry.record_rsvp("rec-001", "accept")
        telemetry.record_rsvp("rec-002", "decline")

        # Verify recorded
        stats = telemetry.get_campaign_stats(campaign_id)
        assert stats['accept'] == 1
        assert stats['decline'] == 1

    def test_records_all_response_types(self, telemetry):
        """Verify all RSVP types are recorded."""
        campaign_id = "test-campaign-002"

        telemetry.create_campaign(campaign_id, "Test Campaign 2")

        recipients = [
            ("rec-101", "user1@example.com"),
            ("rec-102", "user2@example.com"),
            ("rec-103", "user3@example.com"),
            ("rec-104", "user4@example.com"),
        ]

        for rid, email in recipients:
            telemetry.add_recipient(campaign_id, rid, email)

        # Record different responses
        telemetry.record_rsvp("rec-101", "accept")
        telemetry.record_rsvp("rec-102", "decline")
        telemetry.record_rsvp("rec-103", "tentative")
        telemetry.record_rsvp("rec-104", "none")

        stats = telemetry.get_campaign_stats(campaign_id)
        assert stats['accept'] == 1
        assert stats['decline'] == 1
        assert stats['tentative'] == 1
        assert stats['none'] == 1

    def test_recipient_identity_stable(self, telemetry):
        """M1: Recipient identity keys stable across RSVP events."""
        campaign_id = "test-campaign-003"
        recipient_id = "rec-stable-001"

        telemetry.create_campaign(campaign_id, "Stability Test")
        telemetry.add_recipient(campaign_id, recipient_id, "stable@example.com")

        # Record multiple responses over time (simulating changes)
        telemetry.record_rsvp(recipient_id, "tentative")
        telemetry.record_rsvp(recipient_id, "accept")

        # Latest response should be 'accept'
        stats = telemetry.get_campaign_stats(campaign_id)
        assert stats['accept'] == 1
        assert stats['tentative'] == 0  # Overwritten by accept


class TestReporting:
    """Test A5: Campaign reporting."""

    @pytest.fixture
    def populated_telemetry(self):
        """Create telemetry store with fixture data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        config_data = {'telemetry_db': db_path, 'ics_enabled': False}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        config = Config(config_path)
        store = TelemetryStore(config)

        # Load fixture
        fixture_path = Path(__file__).parent / "testdata" / "campaign_fixture.json"
        with open(fixture_path, 'r') as f:
            campaign_data = json.load(f)

        # Populate
        campaign_id = campaign_data['campaign_id']
        store.create_campaign(campaign_id, campaign_data['campaign_name'])

        for attendee in campaign_data['attendees']:
            store.add_recipient(
                campaign_id,
                attendee['recipient_id'],
                attendee['email'],
                attendee['name']
            )

        # Load RSVP fixture
        rsvp_fixture_path = Path(__file__).parent / "testdata" / "rsvp_fixture.json"
        with open(rsvp_fixture_path, 'r') as f:
            rsvp_data = json.load(f)

        for response in rsvp_data['responses']:
            store.record_rsvp(response['recipient_id'], response['response'])

        yield store, campaign_id

        # Cleanup
        os.unlink(db_path)
        os.unlink(config_path)

    def test_report_shows_aggregated_counts(self, populated_telemetry):
        """A5: Report shows aggregated RSVP counts for a fixture campaign."""
        store, campaign_id = populated_telemetry
        reporter = Reporter(store)

        report = reporter.campaign_summary(campaign_id)

        # Verify report contains statistics
        assert campaign_id in report
        assert 'Accepted' in report
        assert 'Declined' in report
        assert 'Tentative' in report

        # Verify counts (from fixture: 1 accept, 1 decline, 1 tentative, 1 no response)
        stats = store.get_campaign_stats(campaign_id)
        assert stats['accept'] == 1
        assert stats['decline'] == 1
        assert stats['tentative'] == 1
        assert stats['no_response'] == 1  # rec-004 hasn't responded


class TestLabSafety:
    """Test A7: Lab demo uses synthetic addresses only."""

    def test_fixture_uses_synthetic_domains(self):
        """A7: Verify fixture campaign uses only synthetic addresses."""
        fixture_path = Path(__file__).parent / "testdata" / "campaign_fixture.json"
        with open(fixture_path, 'r') as f:
            campaign_data = json.load(f)

        safe_domains = ['example.com', 'test.local', 'demo.lab', 'localhost']

        organizer_domain = campaign_data['organizer'].split('@')[1]
        assert organizer_domain in safe_domains

        for attendee in campaign_data['attendees']:
            email_domain = attendee['email'].split('@')[1]
            assert email_domain in safe_domains, \
                f"Attendee {attendee['email']} uses unsafe domain"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
