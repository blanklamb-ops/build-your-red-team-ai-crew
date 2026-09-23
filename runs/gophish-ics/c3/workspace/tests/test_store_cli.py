import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from gophish_ics.store import TelemetryError, campaign_report, record_response, seed_responses


ROOT = Path(__file__).resolve().parents[1]
RSVPS = ROOT / "fixtures" / "rsvps.json"


class StoreTests(unittest.TestCase):
    def test_seed_records_all_states_and_report_aggregates_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "telemetry.sqlite3"
            self.assertEqual(seed_responses(db, RSVPS), 4)
            self.assertEqual(
                campaign_report(db, "lab-campaign-001"),
                {"accept": 1, "decline": 1, "tentative": 1, "none": 1, "total": 4},
            )
            with sqlite3.connect(db) as connection:
                identities = connection.execute(
                    "SELECT campaign_id, recipient_id FROM rsvp_events ORDER BY id"
                ).fetchall()
            self.assertEqual(identities[0], ("lab-campaign-001", "recipient-001"))
            self.assertEqual(len(set(identities)), 4)

    def test_event_history_and_deterministic_current_state(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "telemetry.sqlite3"
            when = "2030-06-01T14:00:00Z"
            record_response(db, "campaign-1", "recipient-1", "accept", when)
            record_response(db, "campaign-1", "recipient-1", "decline", when)
            record_response(db, "campaign-1", "recipient-1", "tentative", "2030-05-01T00:00:00Z")
            report = campaign_report(db, "campaign-1")
            self.assertEqual(report["decline"], 1)
            self.assertEqual(report["total"], 1)
            with sqlite3.connect(db) as connection:
                count = connection.execute("SELECT COUNT(*) FROM rsvp_events").fetchone()[0]
            self.assertEqual(count, 3)

    def test_malformed_seed_is_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            db = temporary / "telemetry.sqlite3"
            record_response(db, "campaign-1", "recipient-1", "accept", "2030-01-01T00:00:00Z")
            fixture = temporary / "bad.json"
            fixture.write_text(json.dumps([
                {"campaign_id": "campaign-1", "recipient_id": "recipient-2", "response": "decline", "occurred_at": "2030-01-01T00:00:00Z"},
                {"campaign_id": "campaign-1", "recipient_id": "recipient-3", "response": "invalid", "occurred_at": "2030-01-01T00:00:00Z"},
            ]), encoding="utf-8")
            with self.assertRaises(TelemetryError):
                seed_responses(db, fixture)
            self.assertEqual(campaign_report(db, "campaign-1")["total"], 1)

    def test_cli_seed_and_json_report(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "telemetry.sqlite3"
            seed = subprocess.run(
                [sys.executable, "-m", "gophish_ics.cli", "seed", "--db", str(db),
                 "--fixture", str(RSVPS)], cwd=ROOT, text=True, capture_output=True,
                check=False,
            )
            self.assertEqual(seed.returncode, 0, seed.stderr)
            result = subprocess.run(
                [sys.executable, "-m", "gophish_ics.cli", "report", "--db", str(db),
                 "--campaign-id", "lab-campaign-001", "--json"], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["accept"], 1)
            self.assertEqual(report["decline"], 1)
            self.assertEqual(report["total"], 4)

    def test_generate_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            enabled = temporary / "enabled.yaml"
            enabled.write_text("ics_enabled: true\n", encoding="utf-8")
            output = temporary / "invite.ics"
            output.write_text("preserve me", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "gophish_ics.cli", "generate",
                 "--campaign", str(ROOT / "fixtures" / "campaign.json"),
                 "--recipient-id", "recipient-001", "--output", str(output),
                 "--config", str(enabled)], cwd=ROOT, text=True, capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserve me")


if __name__ == "__main__":
    unittest.main()
