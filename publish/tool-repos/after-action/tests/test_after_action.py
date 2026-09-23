from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from after_action.adapters import Decision, Event, load_jsonl_events, parse_timestamp
from after_action.cli import run
from after_action.correlate import correlate
from after_action.redact import load_rules
from after_action.render import render_client_html, render_client_markdown

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "testdata" / "fixture_engagement"
RULES = ROOT / "config" / "redaction_rules.json"


class AfterActionTests(unittest.TestCase):
    def test_fixture_end_to_end_and_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            summary = run(FIXTURE, output, RULES, 10)
            self.assertGreaterEqual(summary.links, 5)
            self.assertEqual(summary.events, 6)
            for name in ("client_report.md", "client_report.html", "internal_learning.md"):
                self.assertTrue((output / name).is_file())
                self.assertEqual(os.stat(output / name).st_mode & 0o777, 0o600)
            client = (output / "client_report.md").read_text()
            client_html = (output / "client_report.html").read_text()
            internal = (output / "internal_learning.md").read_text()
            for secret in ("PLANTED_SECRET_CLIENT_CANARY", "lab-fixture-key-92831",
                           "analyst@example.test", "fixture.header.signature"):
                self.assertNotIn(secret, client)
                self.assertNotIn(secret, client_html)
            self.assertIn("[REDACTED", client)
            self.assertIn("PLANTED_SECRET_CLIENT_CANARY", internal)
            self.assertIn("## Executive Summary", client)
            self.assertIn("## Correlated Timeline", client)
            self.assertIn("## Detection Recommendations", client)
            self.assertIn("## Successes", internal)
            self.assertIn("## Failures", internal)
            self.assertNotIn("<script>", client_html)

    def test_boundary_link_and_no_correlation(self) -> None:
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        event = Event(base, "asset", "type", "summary", "details", "events:1")
        decision = Decision(datetime.fromtimestamp(base.timestamp() + 600, timezone.utc),
                            "decision", "reason", "asset", "outcome", "TTP-1", "decisions:1")
        self.assertEqual(len(correlate([event], [decision], 600).links), 1)
        self.assertEqual(len(correlate([event], [decision], 599).links), 0)

    def test_naive_timestamp_warns(self) -> None:
        warnings: list[str] = []
        parsed = parse_timestamp("2026-01-01T10:00:00", "fixture:1", warnings)
        self.assertEqual(parsed.tzinfo, timezone.utc)
        self.assertTrue(any("naive timestamp" in warning for warning in warnings))

    def test_malformed_jsonl_and_missing_optional_degrade(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text('{bad}\n{"timestamp":"2026-01-01T00:00:00Z","asset":"a"}\n')
            warnings: list[str] = []
            events = load_jsonl_events(path, warnings)
            self.assertEqual(len(events), 1)
            self.assertGreaterEqual(len(warnings), 4)
            self.assertFalse(any("{bad}" in warning for warning in warnings))

    def test_invalid_regex_and_window_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "rules.json"
            config.write_text(json.dumps([{"name": "bad", "pattern": "(", "replacement": "[X]"}]))
            with self.assertRaisesRegex(ValueError, "invalid pattern"):
                load_rules(config)
            with self.assertRaisesRegex(ValueError, "positive finite"):
                run(FIXTURE, Path(directory) / "output", RULES, float("nan"))

    def test_markdown_and_html_dynamic_content_are_inert(self) -> None:
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        event = Event(base, "asset|split", "type", "<script>alert(1)</script>\nnext", "x", "e:1")
        decision = Decision(base, "continue|pause", "r", "asset|split", "ok", "TTP-1", "d:1")
        result = correlate([event], [decision], 60)
        markdown = render_client_markdown({"detection_recommendations": ["Review logs"]}, result, load_rules(RULES))
        rendered = render_client_html(markdown)
        self.assertIn("\\|", markdown)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_input_output_collision_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be different"):
            run(FIXTURE, FIXTURE, RULES, 10)


if __name__ == "__main__":
    unittest.main()
