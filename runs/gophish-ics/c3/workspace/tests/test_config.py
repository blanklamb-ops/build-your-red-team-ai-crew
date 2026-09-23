from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gophish_ics.config import ConfigError, FeatureDisabledError, load_config, require_ics_enabled


ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / "config" / "default.yaml"


class ConfigTests(unittest.TestCase):
    def test_exact_shipped_config_is_false_and_blocks_generation(self):
        before = SHIPPED.read_bytes()
        config = load_config(SHIPPED)
        self.assertFalse(config.ics_enabled)
        with self.assertRaises(FeatureDisabledError):
            require_ics_enabled(config)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "blocked.ics"
            result = subprocess.run(
                [sys.executable, "-m", "gophish_ics.cli", "generate",
                 "--campaign", str(ROOT / "fixtures" / "campaign.json"),
                 "--recipient-id", "recipient-001", "--output", str(output)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("disabled", result.stderr)
            self.assertFalse(output.exists())
        self.assertEqual(before, SHIPPED.read_bytes())

    def test_explicit_temporary_override_works_without_mutating_shipped_config(self):
        before = SHIPPED.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            enabled = temporary / "enabled.yaml"
            enabled.write_text("ics_enabled: true\n", encoding="utf-8")
            output = temporary / "invite.ics"
            result = subprocess.run(
                [sys.executable, "-m", "gophish_ics.cli", "generate",
                 "--campaign", str(ROOT / "fixtures" / "campaign.json"),
                 "--recipient-id", "recipient-001", "--output", str(output),
                 "--config", str(enabled)], cwd=ROOT, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
        self.assertEqual(before, SHIPPED.read_bytes())

    def test_config_rejects_duplicate_unknown_and_non_boolean_values(self):
        cases = (
            "ics_enabled: true\nics_enabled: false\n",
            "ics_enabled: false\nother: true\n",
            "ics_enabled: yes\n",
            "",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            for source in cases:
                path.write_text(source, encoding="utf-8")
                with self.subTest(source=source), self.assertRaises(ConfigError):
                    load_config(path)


if __name__ == "__main__":
    unittest.main()
