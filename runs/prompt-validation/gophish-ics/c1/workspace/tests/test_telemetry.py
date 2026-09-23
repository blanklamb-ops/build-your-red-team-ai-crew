#!/usr/bin/env python3
"""Tests for telemetry storage."""

import pytest
import os
import tempfile
from telemetry import TelemetryStore, RSVPStatus


@pytest.fixture
def db_path():
    """Temporary database path."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def store(db_path):
    """Telemetry store instance."""
    return TelemetryStore(db_path)


def test_record_rsvp(store):
    """Test recording an RSVP."""
    result = store.record_rsvp(
        campaign_id='test-campaign',
        recipient_id='recip-001',
        recipient_email='user@example.com',
        status=RSVPStatus.ACCEPTED
    )

    assert result is True  # First insert


def test_update_rsvp(store):
    """Test updating an existing RSVP."""
    # First insert
    store.record_rsvp(
        campaign_id='test-campaign',
        recipient_id='recip-001',
        recipient_email='user@example.com',
        status=RSVPStatus.NEEDS_ACTION
    )

    # Update
    result = store.record_rsvp(
        campaign_id='test-campaign',
        recipient_id='recip-001',  # Same recipient
        recipient_email='user@example.com',
        status=RSVPStatus.ACCEPTED  # Changed status
    )

    # Check updated
    responses = store.get_campaign_rsvps('test-campaign')
    assert len(responses) == 1
    assert responses[0]['status'] == 'ACCEPTED'


def test_recipient_id_stability(store):
    """Test that recipient_id is stable across events (M1)."""
    recipient_id = 'stable-recipient-123'

    # Record first response
    store.record_rsvp(
        campaign_id='campaign-1',
        recipient_id=recipient_id,
        recipient_email='user@example.com',
        status=RSVPStatus.ACCEPTED
    )

    # Update status
    store.record_rsvp(
        campaign_id='campaign-1',
        recipient_id=recipient_id,
        recipient_email='user@example.com',
        status=RSVPStatus.DECLINED
    )

    # Should only have one record (updated)
    responses = store.get_campaign_rsvps('campaign-1')
    assert len(responses) == 1
    assert responses[0]['recipient_id'] == recipient_id
    assert responses[0]['status'] == 'DECLINED'


def test_get_campaign_stats(store):
    """Test aggregated campaign statistics."""
    campaign_id = 'test-campaign'

    # Add multiple responses
    store.record_rsvp(campaign_id, 'r1', 'u1@example.com', RSVPStatus.ACCEPTED)
    store.record_rsvp(campaign_id, 'r2', 'u2@example.com', RSVPStatus.ACCEPTED)
    store.record_rsvp(campaign_id, 'r3', 'u3@example.com', RSVPStatus.DECLINED)
    store.record_rsvp(campaign_id, 'r4', 'u4@example.com', RSVPStatus.TENTATIVE)

    stats = store.get_campaign_stats(campaign_id)

    assert stats['ACCEPTED'] == 2
    assert stats['DECLINED'] == 1
    assert stats['TENTATIVE'] == 1
    assert stats['NEEDS-ACTION'] == 0


def test_get_recipient_history(store):
    """Test getting recipient history across campaigns."""
    recipient_id = 'recip-001'

    # Add responses to multiple campaigns
    store.record_rsvp('campaign-1', recipient_id, 'user@example.com', RSVPStatus.ACCEPTED)
    store.record_rsvp('campaign-2', recipient_id, 'user@example.com', RSVPStatus.DECLINED)

    history = store.get_recipient_history(recipient_id)

    assert len(history) == 2
    campaign_ids = [h['campaign_id'] for h in history]
    assert 'campaign-1' in campaign_ids
    assert 'campaign-2' in campaign_ids


def test_list_campaigns(store):
    """Test listing all campaigns."""
    store.record_rsvp('campaign-1', 'r1', 'u1@example.com', RSVPStatus.ACCEPTED)
    store.record_rsvp('campaign-2', 'r2', 'u2@example.com', RSVPStatus.ACCEPTED)
    store.record_rsvp('campaign-1', 'r3', 'u3@example.com', RSVPStatus.DECLINED)

    campaigns = store.list_campaigns()

    assert len(campaigns) == 2
    assert 'campaign-1' in campaigns
    assert 'campaign-2' in campaigns


def test_metadata_storage(store):
    """Test that metadata (user_agent, ip) is stored."""
    store.record_rsvp(
        campaign_id='test',
        recipient_id='r1',
        recipient_email='user@example.com',
        status=RSVPStatus.ACCEPTED,
        user_agent='Test UA',
        ip_address='192.168.1.1'
    )

    responses = store.get_campaign_rsvps('test')
    assert responses[0]['user_agent'] == 'Test UA'
    assert responses[0]['ip_address'] == '192.168.1.1'
