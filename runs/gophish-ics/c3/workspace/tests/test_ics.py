from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest

from gophish_ics.ics import CampaignError, campaign_from_dict, generate_invite, load_campaign, validate_invite


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "campaign.json"


class IcsTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_generates_valid_crlf_folded_utc_invite(self):
        campaign = load_campaign(FIXTURE)
        data = generate_invite(campaign, "recipient-001")
        self.assertEqual(validate_invite(data), [])
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertTrue(all(len(line) <= 75 for line in data.split(b"\r\n")[:-1]))
        text = data.decode("utf-8")
        self.assertIn("METHOD:REQUEST\r\n", text)
        self.assertIn("DTSTART:20300615T130000Z", text)
        self.assertIn("DTEND:20300615T133000Z", text)
        self.assertIn("X-GOPHISH-RECIPIENT-ID:recipient-001", text)
        self.assertRegex(text, r"DTSTAMP:\d{8}T\d{6}Z")

    def test_text_is_escaped_and_long_utf8_lines_are_folded(self):
        raw = deepcopy(self.raw)
        raw["summary"] = "Authorized, semi; slash\\ " + "é" * 80
        raw["description"] = "line one\nline two"
        data = generate_invite(campaign_from_dict(raw), "recipient-001")
        self.assertEqual(validate_invite(data), [])
        self.assertIn(b"Authorized\\, semi\\; slash\\\\", data)
        self.assertIn(b"line one\\nline two", data)

    def test_rejects_naive_time_end_before_start_and_identifier_injection(self):
        mutations = []
        naive = deepcopy(self.raw)
        naive["dtstart"] = "2030-06-15T09:00:00"
        mutations.append(naive)
        backwards = deepcopy(self.raw)
        backwards["dtend"] = "2030-06-15T08:00:00-04:00"
        mutations.append(backwards)
        injected = deepcopy(self.raw)
        injected["attendees"][0]["recipient_id"] = "safe\r\nATTENDEE:evil"
        mutations.append(injected)
        for raw in mutations:
            with self.subTest(raw=raw), self.assertRaises(CampaignError):
                campaign_from_dict(raw)

    def test_unknown_recipient_is_rejected(self):
        with self.assertRaises(CampaignError):
            generate_invite(load_campaign(FIXTURE), "recipient-999")

    def test_checked_in_demo_identities_are_synthetic(self):
        campaign = load_campaign(FIXTURE)
        addresses = [campaign.organizer.email, *(person.email for person in campaign.attendees)]
        self.assertTrue(all(address.endswith(".test") for address in addresses))


if __name__ == "__main__":
    unittest.main()
