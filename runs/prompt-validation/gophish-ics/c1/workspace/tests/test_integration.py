#!/usr/bin/env python3
"""Integration tests using fixtures."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from gophish_ics import GoPhishICS
from telemetry import RSVPStatus


@pytest.fixture
def fixtures_dir():
    """Get fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def tmp_config(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / 'config.yaml'
    config_file.write_text(f'''
ics_enabled: true
campaign:
  timezone: UTC
  default_duration_minutes: 60
database:
  path: {tmp_path / "test.db"}
''')
    return str(config_file)


def test_generate_from_json_fixture(fixtures_dir, tmp_config, tmp_path):
    """A2: Test ICS generation from fixture JSON."""
    app = GoPhishICS(tmp_config)

    campaign_file = fixtures_dir / 'campaign_basic.json'
    output_file = tmp_path / 'output.ics'

    app.generate_ics(str(campaign_file), str(output_file))

    assert output_file.exists()

    content = output_file.read_text()
    assert 'BEGIN:VCALENDAR' in content
    assert 'Security Training' in content
    # ICS library may wrap lines, normalize for checking
    content_normalized = content.replace('\r\n ', '').replace('\n ', '')
    assert 'testuser1@lab.internal' in content_normalized


def test_generate_from_yaml_fixture(fixtures_dir, tmp_config, tmp_path):
    """A2: Test ICS generation from fixture YAML."""
    app = GoPhishICS(tmp_config)

    campaign_file = fixtures_dir / 'campaign_no_end.yaml'
    output_file = tmp_path / 'output.ics'

    app.generate_ics(str(campaign_file), str(output_file))

    assert output_file.exists()

    content = output_file.read_text()
    assert 'BEGIN:VCALENDAR' in content
    assert 'Emergency Security Update' in content


def test_rsvp_tracking_with_fixtures(fixtures_dir, tmp_config):
    """A4: Test recording RSVPs from fixture data."""
    app = GoPhishICS(tmp_config)

    # Load fixture RSVP data
    rsvp_file = fixtures_dir / 'rsvp_data.json'
    with open(rsvp_file, 'r') as f:
        rsvp_data = json.load(f)

    # Record all RSVPs
    for rsvp in rsvp_data:
        app.record_rsvp(
            rsvp['campaign_id'],
            rsvp['recipient_id'],
            rsvp['recipient_email'],
            rsvp['status']
        )

    # Verify campaign stats
    stats = app.telemetry.get_campaign_stats('campaign-fixture-001')
    assert stats['ACCEPTED'] == 1
    assert stats['DECLINED'] == 1
    assert stats['TENTATIVE'] == 1


def test_campaign_report(fixtures_dir, tmp_config, capsys):
    """A5: Test that report shows aggregated RSVP counts."""
    app = GoPhishICS(tmp_config)

    # Load and record fixture data
    rsvp_file = fixtures_dir / 'rsvp_data.json'
    with open(rsvp_file, 'r') as f:
        rsvp_data = json.load(f)

    for rsvp in rsvp_data:
        app.record_rsvp(
            rsvp['campaign_id'],
            rsvp['recipient_id'],
            rsvp['recipient_email'],
            rsvp['status']
        )

    # Generate report
    app.show_report('campaign-fixture-001')

    # Capture output
    captured = capsys.readouterr()

    # Verify report contains expected data
    assert 'campaign-fixture-001' in captured.out
    assert 'Accepted:' in captured.out
    assert 'Declined:' in captured.out
    assert 'Tentative:' in captured.out
    assert 'alice@testlab.local' in captured.out
    assert 'bob@testlab.local' in captured.out
