from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from empire_advisor.cli import analyze_fixture, load_fixture, main
from empire_advisor.config import load_rules
from empire_advisor.engine import Advisor, ROOT
from empire_advisor.empire_plugin import Plugin
from empire_advisor.models import ConfigurationError, InputError


class AdvisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.advisor = Advisor.default()

    def test_policy_has_at_least_ten_complete_rules(self) -> None:
        self.assertGreaterEqual(len(self.advisor.rules), 10)
        for rule in self.advisor.rules:
            self.assertTrue(rule.id)
            self.assertTrue(rule.rationale)
            self.assertTrue(rule.pattern)
            self.assertGreater(rule.weight, 0)

    def test_fixture_expected_states_and_suggestions(self) -> None:
        expected = {
            row["id"]: row["expected_state"]
            for row in json.loads((ROOT / "fixtures/commands.json").read_text(encoding="utf-8"))["commands"]
        }
        results = dict(analyze_fixture(ROOT / "fixtures/commands.json", self.advisor))
        self.assertEqual(set(results), set(expected))
        for fixture_id, state in expected.items():
            self.assertEqual(results[fixture_id].state, state)
            self.assertFalse(results[fixture_id].execution_performed)
        suggestion = results["broad-identity"].suggestions[0]
        self.assertTrue(suggestion.template)
        self.assertTrue(suggestion.citation.url.startswith("https://"))

    def test_deterministic_byte_for_byte_json(self) -> None:
        first = json.dumps(self.advisor.analyze("  whoami.exe   /all ").to_dict(), ensure_ascii=False)
        second = json.dumps(self.advisor.analyze("  whoami.exe   /all ").to_dict(), ensure_ascii=False)
        self.assertEqual(first, second)

    def test_zero_hit_allow_includes_limitations(self) -> None:
        result = self.advisor.analyze("whoami.exe /user")
        self.assertEqual(result.state, "allow")
        self.assertEqual(result.score, 0)
        self.assertIn("does not establish safety", result.summary)

    def test_critical_patterns_deny(self) -> None:
        for command in (
            "wevtutil.exe cl System",
            "vssadmin.exe delete shadows /all",
            "Set-MpPreference -DisableRealtimeMonitoring $true",
            "reg.exe save HKLM\\SAM C:\\Lab\\sam.copy",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.advisor.analyze(command).state, "deny")

    def test_empty_and_oversized_input_rejected(self) -> None:
        with self.assertRaises(InputError):
            self.advisor.analyze("   ")
        with self.assertRaises(InputError):
            self.advisor.analyze("x" * (self.advisor.max_command_length + 1))

    def test_plugin_shim_returns_json_without_execution(self) -> None:
        result = json.loads(Plugin(advisor=self.advisor).execute({"Command": "whoami /all"}))
        self.assertEqual(result["state"], "warn")
        self.assertIs(result["execution_performed"], False)

    def test_cli_offline_fixture_mode(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(["--fixture", str(ROOT / "fixtures/commands.json"), "--format", "json"])
        self.assertEqual(status, 0)
        self.assertEqual(len(json.loads(output.getvalue())), 6)

    def test_fixture_schema_and_duplicates_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version":"2.0","commands":[]}', encoding="utf-8")
            with self.assertRaises(InputError):
                load_fixture(path)
            path.write_text(
                '{"schema_version":"1.0","commands":['
                '{"id":"same","command":"one"},{"id":"same","command":"two"}]}',
                encoding="utf-8",
            )
            with self.assertRaises(InputError):
                load_fixture(path)

    def test_invalid_regex_and_duplicate_rule_rejected(self) -> None:
        base = json.loads((ROOT / "rules.yaml").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.yaml"
            invalid = copy.deepcopy(base)
            invalid["rules"][0]["pattern"] = "("
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_rules(path)
            duplicate = copy.deepcopy(base)
            duplicate["rules"][1]["id"] = duplicate["rules"][0]["id"]
            path.write_text(json.dumps(duplicate), encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_rules(path)

    def test_dangling_suggestion_rejected(self) -> None:
        rules = json.loads((ROOT / "rules.yaml").read_text(encoding="utf-8"))
        rules["rules"][0]["suggestion_ids"] = ["not-in-kb"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.yaml"
            path.write_text(json.dumps(rules), encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                Advisor.from_paths(path, ROOT / "kb.yaml")

    def test_runtime_package_has_no_dispatch_primitives(self) -> None:
        forbidden = (
            "import subprocess",
            "from subprocess",
            "import socket",
            "from socket",
            "urllib.request",
            "requests.",
            "os.system",
            "subprocess.",
        )
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "empire_advisor").glob("*.py"))
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
