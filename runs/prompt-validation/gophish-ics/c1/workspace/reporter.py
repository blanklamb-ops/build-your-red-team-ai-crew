#!/usr/bin/env python3
"""
Reporting utilities for GoPhish-ICS campaign RSVP data.
"""

from typing import Dict, List
from telemetry import TelemetryStore, RSVPStatus


class CampaignReporter:
    """Generate reports from campaign RSVP telemetry."""

    def __init__(self, telemetry_store: TelemetryStore):
        """
        Initialize reporter.

        Args:
            telemetry_store: TelemetryStore instance
        """
        self.store = telemetry_store

    def print_campaign_report(self, campaign_id: str):
        """
        Print a formatted report for a campaign.

        Args:
            campaign_id: Campaign identifier
        """
        stats = self.store.get_campaign_stats(campaign_id)
        responses = self.store.get_campaign_rsvps(campaign_id)

        print(f"\n{'='*60}")
        print(f"Campaign RSVP Report: {campaign_id}")
        print(f"{'='*60}\n")

        # Summary statistics
        print("Summary:")
        print(f"  Total responses: {len(responses)}")
        print(f"  Accepted:       {stats.get(RSVPStatus.ACCEPTED.value, 0)}")
        print(f"  Declined:       {stats.get(RSVPStatus.DECLINED.value, 0)}")
        print(f"  Tentative:      {stats.get(RSVPStatus.TENTATIVE.value, 0)}")
        print(f"  Needs Action:   {stats.get(RSVPStatus.NEEDS_ACTION.value, 0)}")

        # Detailed responses
        if responses:
            print(f"\n{'='*60}")
            print("Detailed Responses:")
            print(f"{'='*60}\n")

            for resp in responses:
                print(f"Recipient: {resp['recipient_email']}")
                print(f"  ID:        {resp['recipient_id']}")
                print(f"  Status:    {resp['status']}")
                print(f"  Timestamp: {resp['timestamp']}")
                if resp.get('ip_address'):
                    print(f"  IP:        {resp['ip_address']}")
                if resp.get('user_agent'):
                    print(f"  UA:        {resp['user_agent'][:60]}...")
                print()

        print(f"{'='*60}\n")

    def get_summary_stats(self, campaign_id: str) -> Dict:
        """
        Get summary statistics for a campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Dict with summary data
        """
        stats = self.store.get_campaign_stats(campaign_id)
        responses = self.store.get_campaign_rsvps(campaign_id)

        return {
            'campaign_id': campaign_id,
            'total_responses': len(responses),
            'accepted': stats.get(RSVPStatus.ACCEPTED.value, 0),
            'declined': stats.get(RSVPStatus.DECLINED.value, 0),
            'tentative': stats.get(RSVPStatus.TENTATIVE.value, 0),
            'needs_action': stats.get(RSVPStatus.NEEDS_ACTION.value, 0),
        }

    def list_all_campaigns(self):
        """Print a list of all campaigns with response counts."""
        campaigns = self.store.list_campaigns()

        if not campaigns:
            print("No campaigns with RSVP data found.")
            return

        print(f"\n{'='*60}")
        print("All Campaigns")
        print(f"{'='*60}\n")

        for campaign_id in campaigns:
            stats = self.get_summary_stats(campaign_id)
            print(f"{campaign_id}:")
            print(f"  Total: {stats['total_responses']} | "
                  f"Accept: {stats['accepted']} | "
                  f"Decline: {stats['declined']} | "
                  f"Tentative: {stats['tentative']}")
            print()

        print(f"{'='*60}\n")
