#!/usr/bin/env python3
"""After-action report generator for security assessments.

This tool correlates engagement logs and operator decisions into:
1. Client-facing reports (professional, redacted)
2. Internal learning reports (detailed, for operator improvement)

Authorized use only — see AUTHORIZED_USE.md
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import adapters
from adapters.jsonlines_adapter import JSONLinesAdapter
from adapters.csv_adapter import CSVAdapter
from adapters.decision_adapter import DecisionAdapter

# Import core modules
from correlate import CorrelationEngine
from redaction import Redactor

# Import renderers
from renderers.client_renderer import ClientRenderer
from renderers.internal_renderer import InternalRenderer


class AfterActionTool:
    """Main after-action report generator."""

    def __init__(self, output_dir: Path = None, redaction_config: Path = None):
        """Initialize the after-action tool.

        Args:
            output_dir: Directory for output reports (default: ./output)
            redaction_config: Optional custom redaction rules file
        """
        self.output_dir = output_dir or Path("./output")
        self.output_dir.mkdir(exist_ok=True)

        # Initialize adapters
        self.jsonl_adapter = JSONLinesAdapter()
        self.csv_adapter = CSVAdapter()
        self.decision_adapter = DecisionAdapter()

        # Initialize correlation engine
        self.correlator = CorrelationEngine(
            time_window_seconds=300,  # 5 minutes
            asset_match=True
        )

        # Initialize redactor
        custom_rules = []
        if redaction_config and redaction_config.exists():
            with open(redaction_config, 'r') as f:
                config = json.load(f)
                custom_rules = config.get('additional_rules', [])

        self.redactor = Redactor(custom_rules=custom_rules)

        # Initialize renderers
        self.client_renderer = ClientRenderer()
        self.internal_renderer = InternalRenderer()

    def load_logs(self, log_dir: Path) -> tuple:
        """Load all logs from directory.

        Args:
            log_dir: Directory containing log files

        Returns:
            Tuple of (events, decisions)
        """
        events = []
        decisions = []

        if not log_dir.exists():
            print(f"Error: Log directory not found: {log_dir}")
            return events, decisions

        print(f"Loading logs from: {log_dir}")

        # Load JSON Lines event logs
        for jsonl_file in log_dir.glob("*.jsonl"):
            if "decision" in jsonl_file.name.lower():
                continue  # Skip decision logs here

            print(f"  Loading {jsonl_file.name} (JSONL)...")
            file_events = self.jsonl_adapter.load(jsonl_file)
            events.extend(file_events)
            print(f"    Loaded {len(file_events)} events")

        # Load CSV event logs
        for csv_file in log_dir.glob("*.csv"):
            print(f"  Loading {csv_file.name} (CSV)...")
            file_events = self.csv_adapter.load(csv_file)
            events.extend(file_events)
            print(f"    Loaded {len(file_events)} events")

        # Load decision logs
        for decision_file in log_dir.glob("*decision*.jsonl"):
            print(f"  Loading {decision_file.name} (Decision Log)...")
            file_decisions = self.decision_adapter.load(decision_file)
            decisions.extend(file_decisions)
            print(f"    Loaded {len(file_decisions)} decisions")

        print(f"\nTotal: {len(events)} events, {len(decisions)} decisions")

        return events, decisions

    def generate_reports(self, log_dir: Path) -> Dict[str, Any]:
        """Generate both client and internal reports.

        Args:
            log_dir: Directory containing log files

        Returns:
            Dictionary with report generation metadata
        """
        # Load logs
        events, decisions = self.load_logs(log_dir)

        if not events and not decisions:
            print("Warning: No data loaded. Cannot generate reports.")
            return {"status": "no_data"}

        # Correlate events with decisions
        print("\nCorrelating events with decisions...")
        correlated = self.correlator.correlate(events, decisions)
        print(f"  Created {len(correlated)} correlations")

        # Build unified timeline
        print("Building timeline...")
        timeline = self.correlator.build_timeline(events, decisions)
        print(f"  Timeline contains {len(timeline)} items")

        # Generate metadata
        metadata = self._build_metadata(events, decisions)

        # Generate client report (with redaction)
        print("\nGenerating client report...")
        client_report = self.client_renderer.render(timeline, correlated, metadata)
        client_report_redacted = self.redactor.redact(client_report)

        client_path = self.output_dir / "client_report.md"
        with open(client_path, 'w') as f:
            f.write(client_report_redacted)
        print(f"  Client report: {client_path}")

        # Generate internal report (no redaction for internal use)
        print("Generating internal report...")
        internal_report = self.internal_renderer.render(
            timeline, correlated, events, decisions, metadata
        )

        internal_path = self.output_dir / "internal_report.md"
        with open(internal_path, 'w') as f:
            f.write(internal_report)
        print(f"  Internal report: {internal_path}")

        # Save metadata
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        print(f"  Metadata: {metadata_path}")

        print("\n✓ Report generation complete!")

        return {
            "status": "success",
            "client_report": str(client_path),
            "internal_report": str(internal_path),
            "metadata": metadata
        }

    def _build_metadata(
        self,
        events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build report metadata.

        Args:
            events: List of events
            decisions: List of decisions

        Returns:
            Metadata dictionary
        """
        # Find assessment time range
        all_timestamps = []

        for event in events:
            if '_timestamp' in event:
                all_timestamps.append(event['_timestamp'])

        for decision in decisions:
            if '_timestamp' in decision:
                all_timestamps.append(decision['_timestamp'])

        assessment_start = min(all_timestamps) if all_timestamps else None
        assessment_end = max(all_timestamps) if all_timestamps else None

        return {
            "generated_at": datetime.now().isoformat(),
            "assessment_start": assessment_start.isoformat() if assessment_start else None,
            "assessment_end": assessment_end.isoformat() if assessment_end else None,
            "total_events": len(events),
            "total_decisions": len(decisions),
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="After-action report generator for security assessments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s testdata/fixture_engagement/
  %(prog)s logs/ -o reports/
  %(prog)s logs/ -c custom_redaction.json

Authorized use only. See AUTHORIZED_USE.md for boundaries.
        """
    )

    parser.add_argument(
        "log_dir",
        type=Path,
        help="Directory containing log files (JSONL, CSV)"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("./output"),
        help="Output directory for reports (default: ./output)"
    )

    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Custom redaction configuration file (JSON)"
    )

    args = parser.parse_args()

    # Validate log directory
    if not args.log_dir.exists():
        print(f"Error: Log directory not found: {args.log_dir}", file=sys.stderr)
        sys.exit(1)

    # Create tool instance and generate reports
    tool = AfterActionTool(
        output_dir=args.output,
        redaction_config=args.config
    )

    try:
        result = tool.generate_reports(args.log_dir)

        if result["status"] == "no_data":
            print("Error: No log data found.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating reports: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
