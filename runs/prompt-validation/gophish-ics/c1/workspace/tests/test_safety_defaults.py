#!/usr/bin/env python3
"""
Tests for safety defaults (A6).
Verify that the shipped configuration has ics_enabled: false
and that generation is blocked by default.
"""

import pytest
import yaml
import sys
import os
from io import StringIO
from gophish_ics import GoPhishICS


def test_shipped_config_has_ics_disabled():
    """
    A6: Verify the checked-in configuration has ics_enabled: false.
    This test loads the ACTUAL shipped config.yaml file.
    """
    config_path = 'config.yaml'
    assert os.path.exists(config_path), "config.yaml must exist"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # The shipped default MUST be false
    assert 'ics_enabled' in config, "config.yaml must have 'ics_enabled' key"
    assert config['ics_enabled'] is False, \
        "Shipped config MUST have ics_enabled: false for safety"


def test_generation_blocked_by_default(tmp_path, monkeypatch):
    """
    A6: Verify that ICS generation is refused when disabled.
    Uses temporary override config but tests the blocking logic.
    """
    # Create test campaign file
    campaign_file = tmp_path / "test_campaign.json"
    campaign_file.write_text('''{
        "organizer": "test@example.com",
        "summary": "Test",
        "dtstart": "2024-12-15T14:00:00"
    }''')

    output_file = tmp_path / "output.ics"

    # Create config with disabled flag
    test_config = tmp_path / "test_config.yaml"
    test_config.write_text('ics_enabled: false\n')

    # Attempt generation without force flag should exit with error
    app = GoPhishICS(str(test_config))

    # Capture stderr
    old_stderr = sys.stderr
    sys.stderr = StringIO()

    with pytest.raises(SystemExit) as exc_info:
        app.generate_ics(str(campaign_file), str(output_file), force=False)

    stderr_output = sys.stderr.getvalue()
    sys.stderr = old_stderr

    # Should exit with code 1
    assert exc_info.value.code == 1

    # Should have error message about being disabled
    assert 'DISABLED' in stderr_output
    assert 'ics_enabled' in stderr_output or 'config.yaml' in stderr_output

    # File should not be created
    assert not output_file.exists()


def test_generation_with_force_flag(tmp_path):
    """
    Verify that --force flag allows generation when disabled (for testing).
    The shipped config remains unchanged.
    """
    # Create test campaign file
    campaign_file = tmp_path / "test_campaign.json"
    campaign_file.write_text('''{
        "organizer": "test@example.com",
        "summary": "Test",
        "dtstart": "2024-12-15T14:00:00"
    }''')

    output_file = tmp_path / "output.ics"

    # Create config with disabled flag
    test_config = tmp_path / "test_config.yaml"
    test_config.write_text('''
ics_enabled: false
campaign:
  timezone: UTC
  default_duration_minutes: 60
database:
  path: test.db
''')

    # With force flag, generation should succeed
    app = GoPhishICS(str(test_config))
    app.generate_ics(str(campaign_file), str(output_file), force=True)

    # File should be created
    assert output_file.exists()

    # Original config file unchanged (still disabled)
    with open(test_config, 'r') as f:
        config = yaml.safe_load(f)
    assert config['ics_enabled'] is False


def test_generation_when_enabled(tmp_path):
    """
    Verify that generation works when explicitly enabled.
    """
    # Create test campaign file
    campaign_file = tmp_path / "test_campaign.json"
    campaign_file.write_text('''{
        "organizer": "test@example.com",
        "summary": "Test",
        "dtstart": "2024-12-15T14:00:00"
    }''')

    output_file = tmp_path / "output.ics"

    # Create config with ENABLED flag (temporary for this test)
    test_config = tmp_path / "test_config.yaml"
    test_config.write_text('''
ics_enabled: true
campaign:
  timezone: UTC
  default_duration_minutes: 60
database:
  path: test.db
''')

    # Should succeed without force flag
    app = GoPhishICS(str(test_config))
    app.generate_ics(str(campaign_file), str(output_file), force=False)

    # File should be created
    assert output_file.exists()
