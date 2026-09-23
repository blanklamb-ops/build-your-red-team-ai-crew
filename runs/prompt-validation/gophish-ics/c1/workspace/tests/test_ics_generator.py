#!/usr/bin/env python3
"""Tests for ICS generator."""

import pytest
import os
import tempfile
from datetime import datetime
from ics_generator import ICSGenerator


@pytest.fixture
def config():
    """Test configuration."""
    return {
        'campaign': {
            'timezone': 'UTC',
            'default_duration_minutes': 60
        }
    }


@pytest.fixture
def generator(config):
    """ICS generator instance."""
    return ICSGenerator(config)


def test_basic_generation(generator):
    """Test basic ICS generation."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test Meeting',
        'description': 'Test description',
        'dtstart': '2024-12-15T14:00:00',
        'dtend': '2024-12-15T15:00:00',
        'attendees': ['user1@example.com', 'user2@example.com']
    }

    ics_content = generator.generate(campaign_data)

    # Verify ICS structure
    assert 'BEGIN:VCALENDAR' in ics_content
    assert 'END:VCALENDAR' in ics_content
    assert 'BEGIN:VEVENT' in ics_content
    assert 'END:VEVENT' in ics_content

    # Verify content
    assert 'SUMMARY:Test Meeting' in ics_content
    assert 'ORGANIZER:mailto:test@example.com' in ics_content
    assert 'ATTENDEE;' in ics_content
    # ICS library may wrap lines, so check without line breaks
    ics_content_normalized = ics_content.replace('\r\n ', '').replace('\n ', '')
    assert 'mailto:user1@example.com' in ics_content_normalized
    assert 'METHOD:REQUEST' in ics_content


def test_timezone_explicit(generator):
    """Test that timezones are explicit in output."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test',
        'dtstart': '2024-12-15T14:00:00+00:00',
    }

    ics_content = generator.generate(campaign_data)

    # Should have DTSTART with timezone info (not naive)
    assert 'DTSTART' in ics_content
    # ICS should not have naive datetime (would be just DTSTART:20241215T140000)
    # With timezone it includes Z or TZID
    assert ('Z' in ics_content or 'TZID' in ics_content)


def test_missing_required_field(generator):
    """Test that missing required fields raise ValueError."""
    campaign_data = {
        'summary': 'Test Meeting',
        # Missing organizer
    }

    with pytest.raises(ValueError, match='Missing required field'):
        generator.generate(campaign_data)


def test_default_duration(generator):
    """Test that default duration is applied when dtend not provided."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test',
        'dtstart': '2024-12-15T14:00:00',
        # No dtend - should use default 60 minutes
    }

    ics_content = generator.generate(campaign_data)

    assert 'DTSTART' in ics_content
    assert 'DTEND' in ics_content


def test_file_output(generator):
    """Test writing ICS to file."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test',
        'dtstart': '2024-12-15T14:00:00',
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ics', delete=False) as f:
        output_path = f.name

    try:
        generator.generate_to_file(campaign_data, output_path)
        assert os.path.exists(output_path)

        with open(output_path, 'r') as f:
            content = f.read()
            assert 'BEGIN:VCALENDAR' in content
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_uid_generation(generator):
    """Test UID is included in output."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test',
        'dtstart': '2024-12-15T14:00:00',
    }

    ics_content = generator.generate(campaign_data)
    assert 'UID:' in ics_content


def test_rsvp_parameters(generator):
    """Test that attendees have RSVP=TRUE parameter."""
    campaign_data = {
        'organizer': 'test@example.com',
        'summary': 'Test',
        'dtstart': '2024-12-15T14:00:00',
        'attendees': ['user@example.com']
    }

    ics_content = generator.generate(campaign_data)
    assert 'RSVP=TRUE' in ics_content or 'RSVP:TRUE' in ics_content
