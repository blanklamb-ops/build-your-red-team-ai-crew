#!/usr/bin/env python3
"""
Empire Advisor - OPSEC Advisory Plugin for PowerShell Empire

Intercepts operator commands and provides OPSEC scoring with quieter alternatives.
Advisory only - never auto-executes suggestions.

Authorized research use only.
"""

import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class RuleMatch:
    """Represents a matched OPSEC rule"""
    rule_id: str
    name: str
    severity: str
    rationale: str
    score_penalty: int
    category: str


@dataclass
class Suggestion:
    """Represents an alternative command suggestion"""
    rule_id: str
    suggestion: str
    commands: List[str]
    rationale: str
    citation: str


@dataclass
class Advisory:
    """Complete advisory response for a command"""
    command: str
    opsec_score: int  # 0-100, lower is noisier
    risk_level: str  # low, medium, high, critical
    matched_rules: List[RuleMatch]
    suggestions: List[Suggestion]
    action: str  # allow, warn, block


class EmpireAdvisor:
    """
    Empire-compatible plugin (or shim) for OPSEC command advisory.

    This implementation works as:
    1. A standalone shim for offline testing
    2. A compatible plugin structure for Empire integration
    """

    def __init__(self, rules_path: str = "rules.yaml", kb_path: str = "knowledge_base.yaml"):
        """Initialize the advisor with rules and knowledge base"""
        self.rules_path = Path(rules_path)
        self.kb_path = Path(kb_path)
        self.rules = self._load_rules()
        self.knowledge_base = self._load_kb()

    def _load_rules(self) -> List[Dict]:
        """Load OPSEC rules from YAML"""
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_path}")

        with open(self.rules_path, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('rules', [])

    def _load_kb(self) -> List[Dict]:
        """Load knowledge base alternatives from YAML"""
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {self.kb_path}")

        with open(self.kb_path, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('alternatives', [])

    def score_command(self, command: str) -> Advisory:
        """
        Score a command against OPSEC rules and provide suggestions.

        Args:
            command: The operator command to evaluate

        Returns:
            Advisory object with score, matched rules, and suggestions
        """
        matched_rules = []
        total_penalty = 0

        # Check command against all rules
        for rule in self.rules:
            pattern = rule.get('pattern', '')
            if re.search(pattern, command, re.IGNORECASE):
                matched_rules.append(RuleMatch(
                    rule_id=rule['id'],
                    name=rule['name'],
                    severity=rule['severity'],
                    rationale=rule['rationale'],
                    score_penalty=rule['score_penalty'],
                    category=rule['category']
                ))
                total_penalty += rule['score_penalty']

        # Calculate OPSEC score (100 = perfect, 0 = very noisy)
        # Cap penalties at 100 for worst case
        opsec_score = max(0, 100 - min(total_penalty, 100))

        # Determine risk level and action
        risk_level, action = self._calculate_risk_action(opsec_score, matched_rules)

        # Find suggestions for matched rules
        suggestions = self._get_suggestions([r.rule_id for r in matched_rules])

        return Advisory(
            command=command,
            opsec_score=opsec_score,
            risk_level=risk_level,
            matched_rules=matched_rules,
            suggestions=suggestions,
            action=action
        )

    def _calculate_risk_action(self, score: int, matches: List[RuleMatch]) -> Tuple[str, str]:
        """Determine risk level and recommended action based on score and severity"""
        # Check for critical severity matches
        has_critical = any(m.severity == 'critical' for m in matches)
        has_high = any(m.severity == 'high' for m in matches)

        if has_critical or score < 20:
            return "critical", "block"
        elif has_high or score < 40:
            return "high", "warn"
        elif score < 70:
            return "medium", "warn"
        else:
            return "low", "allow"

    def _get_suggestions(self, rule_ids: List[str]) -> List[Suggestion]:
        """Retrieve alternative command suggestions for matched rules"""
        suggestions = []

        for rule_id in rule_ids:
            # Find alternatives in knowledge base
            for alt in self.knowledge_base:
                if alt['rule_id'] == rule_id:
                    suggestions.append(Suggestion(
                        rule_id=rule_id,
                        suggestion=alt['suggestion'],
                        commands=alt['commands'],
                        rationale=alt['rationale'],
                        citation=alt['citation']
                    ))
                    break  # Only one suggestion per rule

        return suggestions

    def format_advisory_text(self, advisory: Advisory) -> str:
        """Format advisory as human-readable text"""
        lines = []
        lines.append("=" * 70)
        lines.append("EMPIRE ADVISOR - OPSEC ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"\nCommand: {advisory.command}")
        lines.append(f"\nOPSEC Score: {advisory.opsec_score}/100")
        lines.append(f"Risk Level: {advisory.risk_level.upper()}")
        lines.append(f"Recommended Action: {advisory.action.upper()}")

        if advisory.matched_rules:
            lines.append(f"\n{'=' * 70}")
            lines.append(f"MATCHED RULES ({len(advisory.matched_rules)})")
            lines.append("=" * 70)

            for i, rule in enumerate(advisory.matched_rules, 1):
                lines.append(f"\n[{i}] {rule.name} ({rule.rule_id})")
                lines.append(f"    Severity: {rule.severity.upper()}")
                lines.append(f"    Category: {rule.category}")
                lines.append(f"    Penalty: -{rule.score_penalty} points")
                lines.append(f"    Rationale: {rule.rationale}")

        if advisory.suggestions:
            lines.append(f"\n{'=' * 70}")
            lines.append(f"QUIETER ALTERNATIVES ({len(advisory.suggestions)})")
            lines.append("=" * 70)

            for i, sug in enumerate(advisory.suggestions, 1):
                lines.append(f"\n[{i}] {sug.suggestion}")
                lines.append(f"    Rationale: {sug.rationale}")
                lines.append(f"    Citation: {sug.citation}")
                lines.append(f"    Alternative commands:")
                for cmd in sug.commands:
                    lines.append(f"      • {cmd}")

        lines.append(f"\n{'=' * 70}")
        lines.append("NOTE: This is advisory only. No commands have been executed.")
        lines.append("=" * 70)

        return "\n".join(lines)

    def format_advisory_json(self, advisory: Advisory) -> str:
        """Format advisory as JSON"""
        # Convert dataclasses to dicts
        data = {
            'command': advisory.command,
            'opsec_score': advisory.opsec_score,
            'risk_level': advisory.risk_level,
            'action': advisory.action,
            'matched_rules': [asdict(r) for r in advisory.matched_rules],
            'suggestions': [asdict(s) for s in advisory.suggestions]
        }
        return json.dumps(data, indent=2)


# Empire Plugin Interface (Shim)
class Plugin:
    """
    Empire plugin interface shim.

    This provides the expected Empire plugin structure for compatibility.
    When full Empire is available, this integrates as a standard plugin.
    In offline mode, this serves as a standalone shim.
    """

    def __init__(self, mainMenu=None):
        """Initialize plugin with optional Empire mainMenu reference"""
        self.info = {
            'Name': 'EmpireAdvisor',
            'Author': ['Research Team'],
            'Description': 'OPSEC advisory plugin for Empire commands',
            'Software': 'Empire 4.x+',
            'Techniques': ['T1059', 'T1027'],
            'Comments': [
                'Provides pre-execution OPSEC scoring',
                'Advisory only - never auto-executes',
                'Authorized research use only'
            ]
        }
        self.mainMenu = mainMenu
        self.advisor = EmpireAdvisor()

    def onLoad(self):
        """Called when plugin is loaded by Empire"""
        print("[+] Empire Advisor plugin loaded")
        print("[*] Commands will be scored for OPSEC considerations")
        return True

    def register(self, mainMenu):
        """Register plugin hooks with Empire"""
        self.mainMenu = mainMenu
        # Hook into command execution pipeline
        # In real Empire: mainMenu.register_command_hook(self.check_command)
        return True

    def check_command(self, command: str, output_format: str = "text") -> Dict:
        """
        Main entry point for command checking.
        Called before command execution.

        Args:
            command: The command to check
            output_format: 'text' or 'json'

        Returns:
            Dict with 'advisory' and 'allow_execution' keys
        """
        advisory = self.advisor.score_command(command)

        if output_format == "json":
            output = self.advisor.format_advisory_json(advisory)
        else:
            output = self.advisor.format_advisory_text(advisory)

        return {
            'advisory': output,
            'allow_execution': advisory.action != 'block',
            'action': advisory.action,
            'score': advisory.opsec_score
        }


def main():
    """Standalone CLI entry point for testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python empire_advisor.py <command> [--json]")
        print("\nExample:")
        print('  python empire_advisor.py "Invoke-Mimikatz -Command coffee"')
        sys.exit(1)

    command = sys.argv[1]
    output_format = "json" if "--json" in sys.argv else "text"

    plugin = Plugin()
    result = plugin.check_command(command, output_format)

    print(result['advisory'])
    print(f"\nExecution {'ALLOWED' if result['allow_execution'] else 'BLOCKED'}")


if __name__ == "__main__":
    main()
