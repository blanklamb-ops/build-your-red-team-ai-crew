#!/usr/bin/env python3
"""
Empire Advisor - OPSEC scoring and suggestion engine for Empire C2 commands

Authorized use only - see AUTHORIZED_USE.md
"""

import re
import json
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Rule:
    """Scoring rule for command evaluation"""
    id: str
    name: str
    pattern: str
    rationale: str
    severity: str
    category: str

    def matches(self, command: str) -> bool:
        """Check if rule pattern matches the command"""
        return bool(re.search(self.pattern, command, re.IGNORECASE))


@dataclass
class Alternative:
    """Alternative command suggestion from knowledge base"""
    rule_id: str
    suggestion: str
    kb_citation: str
    alternative_commands: List[str]


@dataclass
class AdvisoryResult:
    """Result of command evaluation"""
    command: str
    score: int
    risk_level: str
    matched_rules: List[Dict]
    suggestions: List[Dict]
    advisory_state: str  # allow, warn, block

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class EmpireAdvisor:
    """Main advisor engine for Empire command scoring and suggestions"""

    # Severity to score mapping
    SEVERITY_SCORES = {
        'critical': 100,
        'high': 75,
        'medium': 50,
        'low': 25
    }

    # Risk thresholds
    BLOCK_THRESHOLD = 100
    WARN_THRESHOLD = 50

    def __init__(self, rules_path: str = "rules.yaml", kb_path: str = "knowledge_base.yaml"):
        """Initialize advisor with rules and knowledge base"""
        self.rules = self._load_rules(rules_path)
        self.alternatives = self._load_alternatives(kb_path)

    def _load_rules(self, path: str) -> List[Rule]:
        """Load scoring rules from YAML file"""
        rules_file = Path(path)
        if not rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {path}")

        with open(rules_file, 'r') as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get('rules', []):
            rules.append(Rule(**rule_data))

        return rules

    def _load_alternatives(self, path: str) -> Dict[str, Alternative]:
        """Load alternative suggestions from YAML file"""
        kb_file = Path(path)
        if not kb_file.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {path}")

        with open(kb_file, 'r') as f:
            data = yaml.safe_load(f)

        alternatives = {}
        for alt_data in data.get('alternatives', []):
            alt = Alternative(**alt_data)
            alternatives[alt.rule_id] = alt

        return alternatives

    def evaluate_command(self, command: str) -> AdvisoryResult:
        """
        Evaluate a command and return advisory result

        Args:
            command: The operator command to evaluate

        Returns:
            AdvisoryResult with score, matched rules, and suggestions
        """
        matched_rules = []
        total_score = 0

        # Check each rule
        for rule in self.rules:
            if rule.matches(command):
                score = self.SEVERITY_SCORES.get(rule.severity, 0)
                total_score += score
                matched_rules.append({
                    'id': rule.id,
                    'name': rule.name,
                    'rationale': rule.rationale,
                    'severity': rule.severity,
                    'category': rule.category,
                    'score': score
                })

        # Determine advisory state
        if total_score >= self.BLOCK_THRESHOLD:
            advisory_state = 'block'
            risk_level = 'critical'
        elif total_score >= self.WARN_THRESHOLD:
            advisory_state = 'warn'
            risk_level = 'high'
        else:
            advisory_state = 'allow'
            risk_level = 'low' if total_score > 0 else 'minimal'

        # Gather suggestions for matched rules
        suggestions = []
        for match in matched_rules:
            rule_id = match['id']
            if rule_id in self.alternatives:
                alt = self.alternatives[rule_id]
                suggestions.append({
                    'rule_id': rule_id,
                    'suggestion': alt.suggestion,
                    'kb_citation': alt.kb_citation,
                    'alternative_commands': alt.alternative_commands
                })

        return AdvisoryResult(
            command=command,
            score=total_score,
            risk_level=risk_level,
            matched_rules=matched_rules,
            suggestions=suggestions,
            advisory_state=advisory_state
        )

    def format_advisory(self, result: AdvisoryResult) -> str:
        """Format advisory result for human-readable output"""
        lines = []
        lines.append("=" * 80)
        lines.append("EMPIRE ADVISOR - Command OPSEC Analysis")
        lines.append("=" * 80)
        lines.append(f"\nCommand: {result.command}")
        lines.append(f"Risk Score: {result.score}/100 ({result.risk_level})")
        lines.append(f"Advisory: {result.advisory_state.upper()}")

        if result.matched_rules:
            lines.append(f"\n--- Matched Rules ({len(result.matched_rules)}) ---")
            for rule in result.matched_rules:
                lines.append(f"\n[{rule['id']}] {rule['name']} ({rule['severity']})")
                lines.append(f"  Category: {rule['category']}")
                lines.append(f"  Rationale: {rule['rationale']}")
                lines.append(f"  Score: +{rule['score']}")

        if result.suggestions:
            lines.append(f"\n--- Quieter Alternatives ({len(result.suggestions)}) ---")
            for i, sug in enumerate(result.suggestions, 1):
                lines.append(f"\n{i}. {sug['suggestion']}")
                lines.append(f"   KB Citation: {sug['kb_citation']}")
                if sug['alternative_commands']:
                    lines.append(f"   Commands:")
                    for cmd in sug['alternative_commands']:
                        lines.append(f"     • {cmd}")
        else:
            lines.append("\n--- No alternative suggestions available ---")

        lines.append("\n" + "=" * 80)
        lines.append("ADVISORY ONLY - Operator approval required for execution")
        lines.append("=" * 80)

        return "\n".join(lines)


def main():
    """CLI entry point for standalone testing"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python empire_advisor.py <command>")
        print("       python empire_advisor.py --fixture <fixture_file>")
        sys.exit(1)

    advisor = EmpireAdvisor()

    if sys.argv[1] == '--fixture':
        # Fixture mode
        fixture_path = sys.argv[2]
        with open(fixture_path, 'r') as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        results = []
        for cmd in commands:
            result = advisor.evaluate_command(cmd)
            results.append(result.to_dict())
            print(advisor.format_advisory(result))
            print("\n")

        # Save JSON results
        output_path = fixture_path.replace('.txt', '_results.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_path}")
    else:
        # Single command mode
        command = ' '.join(sys.argv[1:])
        result = advisor.evaluate_command(command)
        print(advisor.format_advisory(result))
        print("\nJSON Output:")
        print(result.to_json())


if __name__ == '__main__':
    main()
