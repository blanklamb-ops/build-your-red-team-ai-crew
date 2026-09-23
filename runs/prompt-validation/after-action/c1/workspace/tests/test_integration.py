"""
Integration tests for after-action report generator.

Tests:
- Multi-format log loading (JSONL + CSV)
- Decision log loading
- Correlation with >= 5 linked items
- Client report generation with redaction
- Internal report generation
- Planted secret redaction
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from after_action.adapters import load_all_logs, DecisionLogAdapter
from after_action.correlation import CorrelationEngine
from after_action.redaction import RedactionEngine
from after_action.renderers import ClientReportRenderer, InternalLearningRenderer


class TestAfterActionIntegration(unittest.TestCase):
    """Integration tests using fixture engagement data."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_path = Path(__file__).parent.parent
        self.fixture_path = self.base_path / 'testdata' / 'fixture_engagement'
        self.logs_path = self.fixture_path / 'logs'
        self.decisions_path = self.fixture_path / 'decisions.jsonl'
        self.output_path = self.base_path / 'reports' / 'test'

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

    def test_load_multiple_log_formats(self):
        """Test loading both JSONL and CSV log formats."""
        events = load_all_logs(self.logs_path)

        self.assertGreater(len(events), 0, "Should load events")

        # Check we have events from both files
        # phishing.jsonl has 10 events, network.csv has 6 events
        self.assertGreaterEqual(len(events), 15, "Should load events from both JSONL and CSV")

        # Verify events have required fields
        for event in events:
            self.assertIsNotNone(event.timestamp)
            self.assertIsNotNone(event.event_type)
            self.assertIsNotNone(event.asset)
            self.assertIsInstance(event.details, dict)

        print(f"✓ Loaded {len(events)} events from multiple formats")

    def test_load_decision_log(self):
        """Test loading operator decision log."""
        decisions = DecisionLogAdapter.load(self.decisions_path)

        self.assertGreater(len(decisions), 0, "Should load decisions")
        self.assertGreaterEqual(len(decisions), 5, "Should have at least 5 decisions")

        # Verify decisions have required fields
        for decision in decisions:
            self.assertIsNotNone(decision.timestamp)
            self.assertIsNotNone(decision.decision)
            self.assertIsNotNone(decision.rationale)
            self.assertIsNotNone(decision.asset)

        print(f"✓ Loaded {len(decisions)} decisions")

    def test_correlation_produces_linked_items(self):
        """Test correlation produces >= 5 linked items."""
        events = load_all_logs(self.logs_path)
        decisions = DecisionLogAdapter.load(self.decisions_path)

        engine = CorrelationEngine(time_window_minutes=5)
        correlated = engine.correlate(events, decisions)

        # Count items with at least one linked event
        linked_count = sum(1 for item in correlated if len(item.events) > 0)

        self.assertGreaterEqual(linked_count, 5, "Should have at least 5 correlated items with linked events")
        print(f"✓ Correlation produced {linked_count} linked items (>= 5 required)")

    def test_client_report_generation(self):
        """Test client report generation with required sections."""
        events = load_all_logs(self.logs_path)
        decisions = DecisionLogAdapter.load(self.decisions_path)

        engine = CorrelationEngine(time_window_minutes=5)
        correlated = engine.correlate(events, decisions)
        timeline = engine.build_timeline(correlated)

        redaction = RedactionEngine()
        renderer = ClientReportRenderer(redaction)

        output_file = self.output_path / 'test_client_report.md'
        renderer.render(correlated, timeline, output_file, "Test Engagement")

        # Verify file was created
        self.assertTrue(output_file.exists(), "Client report should be created")

        # Read and verify content
        content = output_file.read_text()

        # Check required sections (A4)
        self.assertIn("Executive Summary", content, "Should have Executive Summary")
        self.assertIn("Timeline", content, "Should have Timeline section")
        self.assertIn("Detection Recommendations", content, "Should have Detection Recommendations")

        # Verify Detection Recommendations has multiple bullets (A8 requires >= 3)
        detection_section = content[content.find("Detection Recommendations"):]
        bullet_count = detection_section.count("- **")
        self.assertGreaterEqual(bullet_count, 3, "Should have at least 3 detection recommendations")

        print(f"✓ Client report generated with all required sections")
        print(f"  - Detection recommendations: {bullet_count} bullets")

    def test_internal_report_generation(self):
        """Test internal learning report generation."""
        events = load_all_logs(self.logs_path)
        decisions = DecisionLogAdapter.load(self.decisions_path)

        engine = CorrelationEngine(time_window_minutes=5)
        correlated = engine.correlate(events, decisions)
        timeline = engine.build_timeline(correlated)

        renderer = InternalLearningRenderer()

        output_file = self.output_path / 'test_internal_learning.md'
        renderer.render(correlated, timeline, output_file, "Test Engagement")

        # Verify file was created
        self.assertTrue(output_file.exists(), "Internal report should be created")

        # Read and verify content
        content = output_file.read_text()

        # Check required sections (A5)
        self.assertIn("What Worked (Successes)", content, "Should have Successes section")
        self.assertIn("What Failed (Failures)", content, "Should have Failures section")

        print(f"✓ Internal report generated with successes and failures sections")

    def test_planted_secret_redaction(self):
        """Test that planted secret is redacted in client report (A6)."""
        events = load_all_logs(self.logs_path)
        decisions = DecisionLogAdapter.load(self.decisions_path)

        # Verify secret exists in raw events
        secret_found = False
        for event in events:
            if 'password' in event.details:
                if 'sk-' in str(event.details['password']):
                    secret_found = True
                    print(f"✓ Found planted secret in raw event: {event.details['password']}")
                    break

        self.assertTrue(secret_found, "Planted secret should exist in test data")

        # Generate client report with redaction
        engine = CorrelationEngine(time_window_minutes=5)
        correlated = engine.correlate(events, decisions)
        timeline = engine.build_timeline(correlated)

        redaction = RedactionEngine()
        renderer = ClientReportRenderer(redaction)

        output_file = self.output_path / 'test_redaction_client_report.md'
        stats = renderer.render(correlated, timeline, output_file, "Redaction Test")

        # Verify redaction occurred
        self.assertGreater(len(stats), 0, "Should have redaction statistics")
        print(f"✓ Redaction statistics: {stats}")

        # Verify secret is NOT in client report
        content = output_file.read_text()
        self.assertNotIn("sk-1234567890abcdef1234567890abcdef", content,
                        "Planted secret should be redacted from client report")

        # Verify redaction marker is present
        self.assertIn("[REDACTED", content, "Should contain redaction markers")

        print(f"✓ Planted secret successfully redacted in client export")

    def test_internal_report_may_retain_more_detail(self):
        """Test that internal report may retain more detail than client (A7)."""
        events = load_all_logs(self.logs_path)
        decisions = DecisionLogAdapter.load(self.decisions_path)

        engine = CorrelationEngine(time_window_minutes=5)
        correlated = engine.correlate(events, decisions)
        timeline = engine.build_timeline(correlated)

        # Generate both reports
        redaction = RedactionEngine()
        client_renderer = ClientReportRenderer(redaction)
        internal_renderer = InternalLearningRenderer()

        client_output = self.output_path / 'test_comparison_client.md'
        internal_output = self.output_path / 'test_comparison_internal.md'

        client_renderer.render(correlated, timeline, client_output, "Comparison Test")
        internal_renderer.render(correlated, timeline, internal_output, "Comparison Test")

        # Read both
        client_content = client_output.read_text()
        internal_content = internal_output.read_text()

        # Internal should mention it's for operators only
        self.assertIn("operator", internal_content.lower(), "Internal report should reference operators")
        self.assertIn("internal", internal_content.lower(), "Should be marked as internal")

        # Internal should have TTP details
        self.assertIn("TTP", internal_content, "Internal should reference TTPs")

        print(f"✓ Internal report documented as retaining more technical detail")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
