#!/usr/bin/env python3
"""
GoPhish-ICS: ICS/Calendar invite integration for GoPhish campaigns
CLI interface for authorized security testing only.
"""

import argparse
import sys
import yaml
import json
from pathlib import Path

from ics_generator import ICSGenerator
from telemetry import TelemetryStore, RSVPStatus
from reporter import CampaignReporter


class GoPhishICS:
    """Main application controller."""

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize application.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.generator = ICSGenerator(self.config)
        self.telemetry = TelemetryStore(
            self.config.get('database', {}).get('path', 'telemetry.db')
        )
        self.reporter = CampaignReporter(self.telemetry)

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _check_enabled(self) -> bool:
        """
        Check if ICS generation is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get('ics_enabled', False)

    def generate_ics(self, campaign_file: str, output_file: str, force: bool = False):
        """
        Generate ICS file from campaign data.

        Args:
            campaign_file: Path to campaign JSON/YAML file
            output_file: Path to output .ics file
            force: Force generation even if disabled (for testing only)
        """
        # Safety check
        if not self._check_enabled() and not force:
            print("ERROR: ICS generation is DISABLED in config.yaml", file=sys.stderr)
            print("This is a safety default for authorized testing only.", file=sys.stderr)
            print("To enable: set 'ics_enabled: true' in config.yaml", file=sys.stderr)
            print("For testing: use --force flag", file=sys.stderr)
            sys.exit(1)

        if force and not self._check_enabled():
            print("WARNING: Using --force to override disabled state (testing only)",
                  file=sys.stderr)

        # Load campaign data
        campaign_path = Path(campaign_file)
        if campaign_path.suffix == '.json':
            with open(campaign_file, 'r') as f:
                campaign_data = json.load(f)
        elif campaign_path.suffix in ['.yaml', '.yml']:
            with open(campaign_file, 'r') as f:
                campaign_data = yaml.safe_load(f)
        else:
            print(f"ERROR: Unsupported file format: {campaign_path.suffix}",
                  file=sys.stderr)
            sys.exit(1)

        # Generate ICS
        try:
            self.generator.generate_to_file(campaign_data, output_file)
            print(f"Generated ICS file: {output_file}")
        except Exception as e:
            print(f"ERROR: Failed to generate ICS: {e}", file=sys.stderr)
            sys.exit(1)

    def record_rsvp(self, campaign_id: str, recipient_id: str,
                    recipient_email: str, status: str):
        """
        Record an RSVP response.

        Args:
            campaign_id: Campaign identifier
            recipient_id: Recipient identifier
            recipient_email: Recipient email
            status: RSVP status string
        """
        try:
            rsvp_status = RSVPStatus(status.upper())
        except ValueError:
            print(f"ERROR: Invalid status '{status}'. "
                  f"Use: ACCEPTED, DECLINED, TENTATIVE, or NEEDS-ACTION",
                  file=sys.stderr)
            sys.exit(1)

        self.telemetry.record_rsvp(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            recipient_email=recipient_email,
            status=rsvp_status
        )
        print(f"Recorded RSVP: {recipient_email} -> {status}")

    def show_report(self, campaign_id: str):
        """
        Show campaign RSVP report.

        Args:
            campaign_id: Campaign identifier
        """
        self.reporter.print_campaign_report(campaign_id)

    def list_campaigns(self):
        """List all campaigns with RSVP data."""
        self.reporter.list_all_campaigns()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='GoPhish-ICS: Calendar invite integration for authorized testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate ICS file from campaign data (requires ics_enabled: true)
  %(prog)s generate campaign.json -o invite.ics

  # Generate for testing with force flag
  %(prog)s generate campaign.json -o invite.ics --force

  # Record an RSVP response
  %(prog)s rsvp campaign-123 recipient-456 user@example.com ACCEPTED

  # Show campaign report
  %(prog)s report campaign-123

  # List all campaigns
  %(prog)s list

AUTHORIZED USE ONLY - See AUTHORIZED_USE.md
        """
    )

    parser.add_argument('--config', default='config.yaml',
                        help='Config file path (default: config.yaml)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate ICS file')
    gen_parser.add_argument('campaign_file', help='Campaign JSON/YAML file')
    gen_parser.add_argument('-o', '--output', required=True,
                            help='Output .ics file path')
    gen_parser.add_argument('--force', action='store_true',
                            help='Force generation even if disabled (testing only)')

    # RSVP command
    rsvp_parser = subparsers.add_parser('rsvp', help='Record RSVP response')
    rsvp_parser.add_argument('campaign_id', help='Campaign ID')
    rsvp_parser.add_argument('recipient_id', help='Recipient ID')
    rsvp_parser.add_argument('recipient_email', help='Recipient email')
    rsvp_parser.add_argument('status', help='RSVP status (ACCEPTED/DECLINED/TENTATIVE/NEEDS-ACTION)')

    # Report command
    report_parser = subparsers.add_parser('report', help='Show campaign report')
    report_parser.add_argument('campaign_id', help='Campaign ID')

    # List command
    list_parser = subparsers.add_parser('list', help='List all campaigns')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize application
    app = GoPhishICS(args.config)

    # Execute command
    if args.command == 'generate':
        app.generate_ics(args.campaign_file, args.output, args.force)
    elif args.command == 'rsvp':
        app.record_rsvp(args.campaign_id, args.recipient_id,
                        args.recipient_email, args.status)
    elif args.command == 'report':
        app.show_report(args.campaign_id)
    elif args.command == 'list':
        app.list_campaigns()


if __name__ == '__main__':
    main()
