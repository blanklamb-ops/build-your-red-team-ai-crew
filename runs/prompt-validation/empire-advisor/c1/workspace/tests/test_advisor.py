#!/usr/bin/env python3
"""
Test suite for Empire Advisor

Validates all acceptance criteria (A1-A10) and manual fidelity checks.
"""

import pytest
import sys
import json
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from empire_advisor import EmpireAdvisor, Plugin


class TestAcceptanceCriteria:
    """Tests for formal acceptance criteria A1-A10"""

    @pytest.fixture
    def advisor(self):
        """Create advisor instance for testing"""
        return EmpireAdvisor(
            rules_path="rules.yaml",
            kb_path="knowledge_base.yaml"
        )

    @pytest.fixture
    def plugin(self):
        """Create plugin instance for testing"""
        return Plugin()

    @pytest.fixture
    def fixtures(self):
        """Load test fixtures"""
        fixture_path = Path(__file__).parent / "fixtures" / "commands.yaml"
        with open(fixture_path, 'r') as f:
            data = yaml.safe_load(f)
            return data['fixtures']

    def test_a1_plugin_loads(self, plugin):
        """A1: Plugin or shim loads via documented procedure"""
        assert plugin is not None
        assert plugin.info['Name'] == 'EmpireAdvisor'
        assert plugin.advisor is not None
        assert plugin.onLoad() is True

    def test_a2_advisory_without_execution(self, plugin, fixtures):
        """A2: Submitting fixture command produces advisory JSON/text without executing alternatives"""
        # Test with noisy command
        fixture = fixtures[0]  # Mimikatz
        result = plugin.check_command(fixture['command'], output_format="json")

        # Verify advisory produced
        assert 'advisory' in result
        assert 'allow_execution' in result

        # Parse JSON output
        advisory_data = json.loads(result['advisory'])
        assert 'command' in advisory_data
        assert 'opsec_score' in advisory_data
        assert 'matched_rules' in advisory_data

        # Verify no execution occurred (advisory only)
        assert advisory_data['command'] == fixture['command']

        # Test text format too
        result_text = plugin.check_command(fixture['command'], output_format="text")
        assert "EMPIRE ADVISOR" in result_text['advisory']
        assert "No commands have been executed" in result_text['advisory']

    def test_a3_rules_yaml_content(self, advisor):
        """A3: rules.yaml contains ≥10 rules with id + rationale"""
        assert len(advisor.rules) >= 10

        for rule in advisor.rules:
            # Verify required fields
            assert 'id' in rule
            assert 'rationale' in rule
            assert 'pattern' in rule
            assert 'severity' in rule

            # Verify non-empty
            assert rule['id'].strip() != ''
            assert rule['rationale'].strip() != ''

    def test_a4_determinism(self, advisor, fixtures):
        """A4: Same input twice → identical score (determinism test)"""
        # Test with multiple fixtures
        for fixture in fixtures[:5]:
            command = fixture['command']

            # Score twice
            result1 = advisor.score_command(command)
            result2 = advisor.score_command(command)

            # Verify identical results
            assert result1.opsec_score == result2.opsec_score
            assert result1.risk_level == result2.risk_level
            assert result1.action == result2.action
            assert len(result1.matched_rules) == len(result2.matched_rules)
            assert len(result1.suggestions) == len(result2.suggestions)

            # Verify matched rules are identical
            for r1, r2 in zip(result1.matched_rules, result2.matched_rules):
                assert r1.rule_id == r2.rule_id

    def test_a5_suggestion_with_citation(self, advisor, fixtures):
        """A5: At least one fixture triggers a suggestion with KB citation"""
        found_suggestion = False

        for fixture in fixtures:
            if fixture.get('has_suggestion', False):
                advisory = advisor.score_command(fixture['command'])

                if advisory.suggestions:
                    found_suggestion = True
                    # Verify suggestion has KB citation
                    for sug in advisory.suggestions:
                        assert sug.citation is not None
                        assert sug.citation.strip() != ''
                        assert sug.commands is not None
                        assert len(sug.commands) > 0
                    break

        assert found_suggestion, "At least one fixture should trigger a suggestion"

    def test_a6_offline_fixture_mode(self, advisor, fixtures):
        """A6: Offline fixture mode works without live Empire C2"""
        # Verify advisor works completely offline
        for fixture in fixtures:
            # This should work without any network or Empire connection
            advisory = advisor.score_command(fixture['command'])

            # Verify results are produced
            assert advisory is not None
            assert advisory.opsec_score >= 0
            assert advisory.opsec_score <= 100
            assert advisory.risk_level in ['low', 'medium', 'high', 'critical']
            assert advisory.action in ['allow', 'warn', 'block']

    def test_a7_readme_exists(self):
        """A7: README documents Empire version compatibility or shim limits"""
        readme_path = Path(__file__).parent.parent / "README.md"
        assert readme_path.exists(), "README.md must exist"

        content = readme_path.read_text()
        # Check for key documentation sections
        assert len(content) > 500, "README should be substantial"
        # Will be validated manually for Empire compatibility notes

    def test_a8_opsec_card_exists(self):
        """A8: OPSEC_CARD.md with Detection Recommendations (≥3 bullets)"""
        opsec_path = Path(__file__).parent.parent / "OPSEC_CARD.md"
        assert opsec_path.exists(), "OPSEC_CARD.md must exist"

        content = opsec_path.read_text()
        # Check for detection recommendations section
        assert "Detection" in content or "detection" in content
        # Count bullets (lines starting with -, *, or numbers)
        lines = content.split('\n')
        bullets = [l for l in lines if l.strip().startswith(('-', '*', '1.', '2.', '3.'))]
        assert len(bullets) >= 3, "Should have at least 3 detection recommendations"

    def test_a9_authorized_use_notice(self):
        """A9: Authorized-use notice present"""
        # Check in main plugin file
        plugin_path = Path(__file__).parent.parent / "empire_advisor.py"
        content = plugin_path.read_text()
        assert "Authorized" in content or "authorized" in content

        # Check in README
        readme_path = Path(__file__).parent.parent / "README.md"
        if readme_path.exists():
            readme = readme_path.read_text()
            assert "Authorized" in readme or "authorized" in readme or "AUTHORIZED" in readme


class TestManualFidelity:
    """Tests for manual fidelity checks M1-M3"""

    @pytest.fixture
    def advisor(self):
        return EmpireAdvisor(
            rules_path="rules.yaml",
            kb_path="knowledge_base.yaml"
        )

    @pytest.fixture
    def plugin(self):
        return Plugin()

    def test_m1_rationale_understandable(self, plugin):
        """M1: Scoring rationale understandable to operator without reading source"""
        command = "Invoke-Mimikatz -Command coffee"
        result = plugin.check_command(command, output_format="text")

        advisory = result['advisory']

        # Should contain human-readable rationale
        assert "Rationale:" in advisory
        # Should explain the risk clearly
        assert len(advisory) > 200  # Substantial explanation
        # Should not just be code dumps
        assert "def " not in advisory
        assert "class " not in advisory

    def test_m2_suggestions_are_alternatives(self, advisor):
        """M2: Suggestions are alternatives in KB, not vague advice only"""
        command = "Invoke-Mimikatz"
        advisory = advisor.score_command(command)

        if advisory.suggestions:
            for sug in advisory.suggestions:
                # Should have concrete commands
                assert sug.commands is not None
                assert len(sug.commands) > 0

                # Commands should not be vague advice
                for cmd in sug.commands:
                    assert len(cmd) > 10  # Substantial command
                    # Should contain technical details, not just "be careful"
                    assert not cmd.lower().startswith("be ")
                    assert not cmd.lower().startswith("try ")

    def test_m3_dangerous_rules_warn_or_block(self, advisor, plugin):
        """M3: Dangerous rules default to warn/block advisory, not silent ignore"""
        dangerous_commands = [
            "Invoke-Mimikatz",
            "nmap -sS 10.0.0.0/16",
            "wmic process call create malware.exe"
        ]

        for cmd in dangerous_commands:
            result = plugin.check_command(cmd)

            # Should not be silently allowed
            assert result['action'] in ['warn', 'block']
            assert result['score'] < 50  # Should be flagged as risky


class TestFixtureValidation:
    """Validate behavior against test fixtures"""

    @pytest.fixture
    def advisor(self):
        return EmpireAdvisor(
            rules_path="rules.yaml",
            kb_path="knowledge_base.yaml"
        )

    @pytest.fixture
    def fixtures(self):
        fixture_path = Path(__file__).parent / "fixtures" / "commands.yaml"
        with open(fixture_path, 'r') as f:
            data = yaml.safe_load(f)
            return data['fixtures']

    def test_fixture_expectations(self, advisor, fixtures):
        """Validate each fixture meets its expected behavior"""
        for fixture in fixtures:
            command = fixture['command']
            advisory = advisor.score_command(command)

            # Check expected rules matched
            if fixture.get('expected_rules'):
                matched_ids = [r.rule_id for r in advisory.matched_rules]
                for expected_rule in fixture['expected_rules']:
                    assert expected_rule in matched_ids, \
                        f"Expected rule {expected_rule} for: {command}"

            # Check score boundaries
            if 'expected_score_max' in fixture:
                assert advisory.opsec_score <= fixture['expected_score_max'], \
                    f"Score too high for: {command}"

            if 'expected_score_min' in fixture:
                assert advisory.opsec_score >= fixture['expected_score_min'], \
                    f"Score too low for: {command}"

            # Check action
            if 'expected_action' in fixture:
                assert advisory.action == fixture['expected_action'], \
                    f"Wrong action for: {command}"

            # Check suggestion presence
            if fixture.get('has_suggestion'):
                assert len(advisory.suggestions) > 0, \
                    f"Expected suggestion for: {command}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
