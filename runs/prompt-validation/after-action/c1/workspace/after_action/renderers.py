"""
Report renderers for client-facing and internal learning documents.

Generates professional Markdown reports from correlated engagement data.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

from .correlation import CorrelatedItem
from .redaction import RedactionEngine

logger = logging.getLogger(__name__)


class ClientReportRenderer:
    """Generates client-facing professional reports."""

    def __init__(self, redaction_engine: RedactionEngine):
        self.redaction = redaction_engine

    def render(self, correlated: List[CorrelatedItem], timeline: List[Dict[str, Any]],
               output_path: Path, engagement_name: str = "Security Assessment") -> Dict[str, int]:
        """
        Render client-facing report.

        Args:
            correlated: Correlated items (decisions + events)
            timeline: Chronological timeline
            output_path: Output file path
            engagement_name: Name of engagement for report header

        Returns:
            Redaction statistics
        """
        logger.info(f"Rendering client report to {output_path}")

        # Build report content
        report = self._build_report(correlated, timeline, engagement_name)

        # Apply redaction
        redacted_report, stats = self.redaction.redact(report)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(redacted_report)

        logger.info(f"Client report written: {output_path}")
        return stats

    def _build_report(self, correlated: List[CorrelatedItem], timeline: List[Dict[str, Any]],
                      engagement_name: str) -> str:
        """Build the report content before redaction."""

        # Count total events and decisions
        total_events = sum(len(item.events) for item in correlated)
        total_decisions = len(correlated)

        # Extract date range
        if timeline:
            start_date = datetime.fromisoformat(timeline[0]['timestamp']).strftime('%Y-%m-%d')
            end_date = datetime.fromisoformat(timeline[-1]['timestamp']).strftime('%Y-%m-%d')
            date_range = f"{start_date} to {end_date}"
        else:
            date_range = "N/A"

        report_lines = [
            f"# {engagement_name} - After-Action Report",
            "",
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  ",
            f"**Engagement Period:** {date_range}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"This report summarizes the {engagement_name} conducted during the period {date_range}. ",
            f"The assessment involved {total_decisions} tactical decision points across {total_events} ",
            "technical events, providing comprehensive insight into security posture and response capabilities.",
            "",
            "### Key Highlights",
            "",
            "- Assessment methodology validated organizational defenses across multiple threat vectors",
            "- Identified security control effectiveness and areas for improvement",
            "- Documented detection and response timelines for defensive analysis",
            "- Provided actionable recommendations for security enhancement",
            "",
            "---",
            "",
            "## Engagement Timeline",
            "",
            "The following timeline correlates operator decisions with technical events, ",
            "providing a chronological view of assessment activities:",
            ""
        ]

        # Add timeline entries
        for entry in timeline:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')

            if entry['type'] == 'decision':
                report_lines.append(f"### {timestamp} - Decision: {entry['asset']}")
                report_lines.append("")
                report_lines.append(f"**Action:** {entry['content']}")
                report_lines.append("")
                if entry['event_count'] > 0:
                    report_lines.append(f"*Related events: {entry['event_count']}*")
                    report_lines.append("")
            else:  # event
                event_line = f"- **{timestamp}** - `{entry['content']}` on `{entry['asset']}`"
                # Include event details for comprehensive reporting (will be redacted)
                if 'details' in entry and entry['details']:
                    # Format details as key-value pairs
                    details_str = ', '.join(f"{k}={v}" for k, v in entry['details'].items())
                    event_line += f" ({details_str})"
                report_lines.append(event_line)

        report_lines.extend([
            "",
            "---",
            "",
            "## Findings",
            "",
            "*[This section will be populated with specific security findings, vulnerabilities, ",
            "and observations from the engagement. Each finding includes severity, description, ",
            "evidence, and remediation recommendations.]*",
            "",
            "### Finding Template",
            "",
            "**[Finding ID]** - [Finding Title]",
            "",
            "- **Severity:** [Critical/High/Medium/Low/Info]",
            "- **Affected Asset:** [Asset identifier]",
            "- **Description:** [Detailed description of the finding]",
            "- **Evidence:** [Supporting evidence and reproduction steps]",
            "- **Recommendation:** [Specific remediation steps]",
            "",
            "---",
            "",
            "## Detection Recommendations",
            "",
            "The following detection opportunities were identified during the engagement. ",
            "These recommendations help strengthen defensive monitoring capabilities:",
            "",
            "### Network-Based Detection",
            "",
            "- **Unusual authentication patterns:** Monitor for multiple failed login attempts followed by success, especially outside business hours",
            "- **Lateral movement indicators:** Alert on unexpected SMB, WinRM, or PowerShell remoting between workstations",
            "- **Data exfiltration signatures:** Track large outbound transfers to unfamiliar destinations or during off-hours",
            "",
            "### Host-Based Detection",
            "",
            "- **Credential access:** Monitor for suspicious process access to LSASS, registry hive exports, or credential dumping tools",
            "- **Persistence mechanisms:** Alert on new scheduled tasks, services, or registry run keys created outside change windows",
            "- **Defense evasion:** Detect attempts to disable logging, clear event logs, or modify security tooling",
            "",
            "### Behavioral Analytics",
            "",
            "- **Privilege escalation:** Track sudden elevation of user privileges or access to sensitive systems",
            "- **Anomalous tool usage:** Flag execution of administration tools (PSExec, WMI, PowerShell) by unusual users or systems",
            "- **Time-based anomalies:** Correlate activity patterns that deviate from established baselines",
            "",
            "---",
            "",
            "## Conclusion",
            "",
            "This assessment provided valuable insights into the organization's security posture ",
            "and defensive capabilities. The findings and recommendations outlined in this report ",
            "should be prioritized based on risk and business impact.",
            "",
            "### Next Steps",
            "",
            "1. Review and prioritize findings based on severity and business risk",
            "2. Implement recommended detection rules and monitoring enhancements",
            "3. Develop remediation plans for identified vulnerabilities",
            "4. Schedule follow-up validation testing after remediation",
            "",
            "---",
            "",
            "*This report is confidential and intended solely for the use of the organization. ",
            "Unauthorized distribution or disclosure is prohibited.*",
            ""
        ])

        return "\n".join(report_lines)


class InternalLearningRenderer:
    """Generates internal learning summaries for operator team."""

    def render(self, correlated: List[CorrelatedItem], timeline: List[Dict[str, Any]],
               output_path: Path, engagement_name: str = "Security Assessment") -> None:
        """
        Render internal learning report.

        Args:
            correlated: Correlated items (decisions + events)
            timeline: Chronological timeline
            output_path: Output file path
            engagement_name: Name of engagement
        """
        logger.info(f"Rendering internal learning report to {output_path}")

        # Build report content (no redaction for internal use)
        report = self._build_report(correlated, timeline, engagement_name)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)

        logger.info(f"Internal report written: {output_path}")

    def _build_report(self, correlated: List[CorrelatedItem], timeline: List[Dict[str, Any]],
                      engagement_name: str) -> str:
        """Build internal learning report content."""

        # Analyze decisions and events for patterns
        successes = []
        failures = []
        tool_gaps = []
        reusable_ttps = []

        for item in correlated:
            decision_lower = item.decision.decision.lower()
            rationale_lower = item.decision.rationale.lower()

            # Heuristic analysis for successes/failures
            if any(keyword in rationale_lower for keyword in ['obtained', 'successful', 'achieved', 'compromised']):
                successes.append({
                    'decision': item.decision.decision,
                    'rationale': item.decision.rationale,
                    'asset': item.decision.asset,
                    'event_count': len(item.events)
                })

            if any(keyword in rationale_lower for keyword in ['failed', 'blocked', 'denied', 'detected']):
                failures.append({
                    'decision': item.decision.decision,
                    'rationale': item.decision.rationale,
                    'asset': item.decision.asset
                })

            # Identify potential TTPs
            if any(keyword in decision_lower for keyword in ['pivot', 'escalate', 'credential', 'lateral', 'exfil']):
                reusable_ttps.append({
                    'decision': item.decision.decision,
                    'rationale': item.decision.rationale,
                    'technique': self._map_to_technique(decision_lower)
                })

        report_lines = [
            f"# {engagement_name} - Internal Learning Summary",
            "",
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  ",
            f"**For:** Red Team / Operator Review",
            "",
            "---",
            "",
            "## What Worked (Successes)",
            ""
        ]

        if successes:
            for success in successes:
                report_lines.append(f"### {success['decision']} on {success['asset']}")
                report_lines.append("")
                report_lines.append(f"**Outcome:** {success['rationale']}")
                report_lines.append("")
                report_lines.append(f"**Supporting Events:** {success['event_count']} correlated technical events")
                report_lines.append("")
                report_lines.append("**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]")
                report_lines.append("")
        else:
            report_lines.append("*No clear successes identified in automated analysis. Review timeline manually.*")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## What Failed (Failures)",
            ""
        ])

        if failures:
            for failure in failures:
                report_lines.append(f"### {failure['decision']} on {failure['asset']}")
                report_lines.append("")
                report_lines.append(f"**Outcome:** {failure['rationale']}")
                report_lines.append("")
                report_lines.append("**Root cause:** [Requires manual analysis - check for EDR detection, network controls, or operational mistakes]")
                report_lines.append("")
                report_lines.append("**Lessons learned:** [Document what defensive control stopped this and how to adapt]")
                report_lines.append("")
        else:
            report_lines.append("*No clear failures identified in automated analysis. Review timeline manually.*")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## Tool Gaps",
            "",
            "*Document tools or capabilities that would have improved efficiency or success rate:*",
            "",
            "- [ ] [Tool category] - [Specific gap identified]",
            "- [ ] [Example: More reliable credential dumping for modern EDR environments]",
            "- [ ] [Example: Better C2 channel for restrictive network egress]",
            "",
            "---",
            "",
            "## Reusable TTPs",
            "",
            "The following tactics, techniques, and procedures showed promise for future engagements:",
            ""
        ])

        if reusable_ttps:
            for ttp in reusable_ttps:
                report_lines.append(f"### {ttp['decision']}")
                report_lines.append("")
                report_lines.append(f"**Context:** {ttp['rationale']}")
                report_lines.append("")
                report_lines.append(f"**Technique Reference:** {ttp['technique']}")
                report_lines.append("")
                report_lines.append("**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]")
                report_lines.append("")
        else:
            report_lines.append("*No TTPs automatically extracted. Review timeline for manual extraction.*")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## Defensive Observations",
            "",
            "### What Defenders Did Well",
            "",
            "- [Note effective detections, quick response times, proper segmentation]",
            "- [Example: EDR caught process injection within 30 seconds]",
            "",
            "### What Defenders Missed",
            "",
            "- [Note blind spots, delayed responses, misconfigured controls]",
            "- [Example: No monitoring on legacy file shares allowed undetected exfiltration]",
            "",
            "---",
            "",
            "## Recommendations for Future Engagements",
            "",
            "1. **Preparation:**",
            "   - [Pre-engagement improvements based on this run]",
            "",
            "2. **Execution:**",
            "   - [Tactical adjustments for similar environments]",
            "",
            "3. **Tooling:**",
            "   - [Tool updates or additions to capability set]",
            "",
            "4. **Documentation:**",
            "   - [Process improvements for logging and decision tracking]",
            "",
            "---",
            "",
            "*This internal summary is for operator learning only. Do not share with clients. ",
            "For client deliverables, use the client-facing report with appropriate redaction.*",
            ""
        ])

        return "\n".join(report_lines)

    def _map_to_technique(self, decision: str) -> str:
        """Map decision keywords to technique frameworks (MITRE ATT&CK style)."""
        mappings = {
            'pivot': 'Lateral Movement',
            'lateral': 'Lateral Movement',
            'escalate': 'Privilege Escalation',
            'credential': 'Credential Access',
            'dump': 'Credential Access',
            'exfil': 'Exfiltration',
            'persist': 'Persistence',
            'recon': 'Discovery',
            'scan': 'Discovery'
        }

        for keyword, technique in mappings.items():
            if keyword in decision:
                return technique

        return 'Tactic TBD'
