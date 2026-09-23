"""
Command-line interface for after-action report generator.

Usage:
    python -m after_action.cli --logs <log_dir> --decisions <decision_file> --output <output_dir>
"""

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .adapters import load_all_logs, DecisionLogAdapter
from .correlation import CorrelationEngine
from .redaction import RedactionEngine
from .renderers import ClientReportRenderer, InternalLearningRenderer


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='After-Action Report Generator - Correlate engagement logs and decisions',
        epilog='Authorized use only. See AUTHORIZED_USE.md for ethical boundaries.'
    )

    parser.add_argument(
        '--logs',
        type=Path,
        required=True,
        help='Directory containing engagement logs (JSONL, CSV)'
    )

    parser.add_argument(
        '--decisions',
        type=Path,
        required=True,
        help='Operator decision log file (JSONL)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output directory for reports'
    )

    parser.add_argument(
        '--engagement-name',
        type=str,
        default='Security Assessment',
        help='Name of engagement for report headers'
    )

    parser.add_argument(
        '--time-window',
        type=int,
        default=5,
        help='Correlation time window in minutes (default: 5)'
    )

    parser.add_argument(
        '--redaction-config',
        type=Path,
        help='Custom redaction rules JSON file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'after-action {__version__}'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info(f"After-Action Report Generator v{__version__}")
    logger.info("=" * 60)

    # Validate inputs
    if not args.logs.exists():
        logger.error(f"Log directory not found: {args.logs}")
        sys.exit(1)

    if not args.decisions.exists():
        logger.error(f"Decision log not found: {args.decisions}")
        sys.exit(1)

    # Load data
    logger.info("Step 1: Loading logs and decisions")
    logger.info("-" * 60)

    events = load_all_logs(args.logs)
    decisions = DecisionLogAdapter.load(args.decisions)

    if not events:
        logger.warning("No events loaded. Check log directory and formats.")

    if not decisions:
        logger.error("No decisions loaded. Cannot generate reports.")
        sys.exit(1)

    logger.info(f"Loaded {len(events)} events and {len(decisions)} decisions")

    # Correlate
    logger.info("")
    logger.info("Step 2: Correlating events with decisions")
    logger.info("-" * 60)

    engine = CorrelationEngine(time_window_minutes=args.time_window)
    correlated = engine.correlate(events, decisions)
    timeline = engine.build_timeline(correlated)

    # Count linked items
    linked_count = sum(1 for item in correlated if len(item.events) > 0)
    logger.info(f"Correlated items with linked events: {linked_count}/{len(correlated)}")

    # Setup redaction
    if args.redaction_config:
        redaction = RedactionEngine.from_config_file(args.redaction_config)
    else:
        redaction = RedactionEngine()

    # Generate reports
    logger.info("")
    logger.info("Step 3: Generating reports")
    logger.info("-" * 60)

    args.output.mkdir(parents=True, exist_ok=True)

    # Client report
    client_renderer = ClientReportRenderer(redaction)
    client_output = args.output / 'client_report.md'
    redaction_stats = client_renderer.render(
        correlated,
        timeline,
        client_output,
        args.engagement_name
    )

    if redaction_stats:
        logger.info(f"Client report redaction statistics:")
        for rule, count in redaction_stats.items():
            logger.info(f"  - {rule}: {count} redaction(s)")
    else:
        logger.info("Client report: no sensitive data redacted")

    # Internal report
    internal_renderer = InternalLearningRenderer()
    internal_output = args.output / 'internal_learning.md'
    internal_renderer.render(
        correlated,
        timeline,
        internal_output,
        args.engagement_name
    )

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Report generation complete!")
    logger.info("")
    logger.info(f"Client report:   {client_output}")
    logger.info(f"Internal report: {internal_output}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Review client report - ensure appropriate tone and redaction")
    logger.info("  2. Populate findings section with specific vulnerabilities")
    logger.info("  3. Review internal report - add manual analysis and lessons learned")
    logger.info("  4. Share Detection Recommendations with defensive team")
    logger.info("")


if __name__ == '__main__':
    main()
