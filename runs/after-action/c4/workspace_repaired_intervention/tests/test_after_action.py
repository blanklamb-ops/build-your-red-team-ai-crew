import tempfile
import unittest
from pathlib import Path

from src.main import build, correlate, ingest_engagement, redact


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "testdata" / "fixture_engagement"


class TestAfterAction(unittest.TestCase):
    def test_ingest_two_adapters(self):
        result = ingest_engagement(FIXTURE)
        sources = {e.source for e in result.events}
        self.assertIn("jsonl", sources)
        self.assertIn("csv", sources)
        self.assertGreaterEqual(len(result.decisions), 5)

    def test_correlate_links(self):
        result = ingest_engagement(FIXTURE)
        linked = correlate(result.events, result.decisions)
        with_events = sum(1 for item in linked if item["events"])
        self.assertGreaterEqual(with_events, 5)

    def test_redaction(self):
        text = "key AKIAIOSFODNN7EXAMPLE password=SuperSecret123"
        out = redact(text)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", out)
        self.assertNotIn("SuperSecret123", out)

    def test_build_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats = build(FIXTURE, Path(tmp))
            client = (Path(tmp) / "client_report.md").read_text(encoding="utf-8")
            internal = (Path(tmp) / "internal_learning.md").read_text(encoding="utf-8")
            self.assertIn("Executive summary", client)
            self.assertIn("## Timeline", client)
            self.assertIn("Detection Recommendations", client)
            self.assertIn("## Successes", internal)
            self.assertIn("## Failures", internal)
            self.assertTrue(stats["secret_redacted"])
            self.assertNotIn("AKIAIOSFODNN7EXAMPLE", client)
            # Internal may retain planted secret detail
            self.assertIn("AKIAIOSFODNN7EXAMPLE", internal)


if __name__ == "__main__":
    unittest.main()
