"""Internal learning report renderer."""
from typing import List, Dict, Any
from collections import defaultdict


class InternalRenderer:
    """Renders internal learning reports for operator teams."""

    def render(
        self,
        timeline: List[Dict[str, Any]],
        correlated: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Render internal learning report in Markdown format.

        Args:
            timeline: Unified timeline of events and decisions
            correlated: Correlated event-decision pairs
            events: All events (unfiltered)
            decisions: All operator decisions
            metadata: Report metadata

        Returns:
            Markdown-formatted internal learning report
        """
        sections = []

        sections.append(self._render_header(metadata))
        sections.append(self._render_overview(events, decisions, correlated))
        sections.append(self._render_successes(decisions, correlated))
        sections.append(self._render_failures(decisions, events))
        sections.append(self._render_tool_gaps(metadata))
        sections.append(self._render_reusable_ttps(decisions))
        sections.append(self._render_correlation_details(correlated))

        return "\n\n".join(sections)

    def _render_header(self, metadata: Dict[str, Any]) -> str:
        """Render report header."""
        return f"""# After-Action Report — Internal Learning

**Generated:** {metadata.get('generated_at', 'N/A')}
**Engagement Period:** {metadata.get('assessment_start', 'N/A')} to {metadata.get('assessment_end', 'N/A')}
**Report Type:** Internal Use Only — Contains Sensitive Technical Details

---"""

    def _render_overview(
        self,
        events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        correlated: List[Dict[str, Any]]
    ) -> str:
        """Render engagement overview."""
        total_events = len(events)
        total_decisions = len(decisions)
        successful_correlations = len([c for c in correlated if c['event'] is not None])

        # Analyze decision outcomes
        outcomes = defaultdict(int)
        for decision in decisions:
            outcome = decision.get('outcome', 'unknown')
            outcomes[outcome] += 1

        outcome_summary = ", ".join([f"{k}: {v}" for k, v in outcomes.items()])

        return f"""## Engagement Overview

**Statistics:**
- Total events logged: {total_events}
- Operator decisions: {total_decisions}
- Successful correlations: {successful_correlations}
- Decision outcomes: {outcome_summary}

**Correlation Efficiency:**
- Correlation rate: {successful_correlations / total_decisions * 100:.1f}% of decisions had matching events
- Average events per decision: {total_events / total_decisions:.1f}"""

    def _render_successes(
        self,
        decisions: List[Dict[str, Any]],
        correlated: List[Dict[str, Any]]
    ) -> str:
        """Render successes section."""
        lines = ["## Successes — What Worked\n"]

        # Find decisions with successful outcomes
        successful = [
            d for d in decisions
            if d.get('outcome') in ['success', 'completed']
        ]

        if not successful:
            lines.append("*No explicit successes recorded.*")
            return "\n".join(lines)

        lines.append("The following tactics and decisions were effective:\n")

        for decision in successful:
            timestamp = decision.get('timestamp', 'Unknown time')
            decision_text = decision.get('decision', 'Unknown decision')
            rationale = decision.get('rationale', 'No rationale provided')
            tags = decision.get('tags', [])

            lines.append(f"### {decision_text}\n")
            lines.append(f"**Time:** {timestamp}")
            lines.append(f"**Rationale:** {rationale}")

            if tags:
                lines.append(f"**Tags:** {', '.join(tags)}")

            # Find correlated events for context
            related_events = [
                c['event'] for c in correlated
                if c['decision'].get('timestamp') == timestamp and c['event'] is not None
            ]

            if related_events:
                lines.append(f"\n**Associated Events:** {len(related_events)} event(s)")
                for event in related_events[:3]:  # Show first 3
                    action = event.get('action', 'unknown')
                    lines.append(f"- {action}")

            lines.append("")  # Blank line between items

        return "\n".join(lines)

    def _render_failures(
        self,
        decisions: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> str:
        """Render failures section."""
        lines = ["## Failures and Lessons Learned\n"]

        # Find decisions with failed outcomes
        failed = [
            d for d in decisions
            if d.get('outcome') in ['failed', 'blocked', 'error']
        ]

        if not failed:
            lines.append("*No explicit failures recorded. This may indicate:*")
            lines.append("- Excellent preparation and execution")
            lines.append("- Incomplete outcome logging (process improvement needed)")
            lines.append("- Low-difficulty target environment\n")
        else:
            lines.append("The following attempts encountered obstacles:\n")

            for decision in failed:
                timestamp = decision.get('timestamp', 'Unknown time')
                decision_text = decision.get('decision', 'Unknown decision')
                rationale = decision.get('rationale', 'No rationale provided')
                outcome = decision.get('outcome', 'unknown')

                lines.append(f"### {decision_text}\n")
                lines.append(f"**Time:** {timestamp}")
                lines.append(f"**Outcome:** {outcome}")
                lines.append(f"**Context:** {rationale}\n")

        # Look for potential gaps in logging
        decisions_without_outcomes = [
            d for d in decisions
            if 'outcome' not in d or not d['outcome']
        ]

        if decisions_without_outcomes:
            lines.append(f"\n**Logging Gap:** {len(decisions_without_outcomes)} decisions lack outcome metadata.")
            lines.append("*Recommendation: Improve decision logging discipline for future engagements.*")

        return "\n".join(lines)

    def _render_tool_gaps(self, metadata: Dict[str, Any]) -> str:
        """Render tool gaps section."""
        return """## Tool Gaps and Capability Needs

*This section should be manually updated based on operator feedback.*

### Identified Gaps

- **Automated correlation:** Current time-based correlation is basic. Consider implementing ML-based behavioral correlation for complex attack chains.

- **Real-time monitoring:** After-action analysis is retrospective. Real-time operator dashboard would improve decision-making during engagements.

- **Evidence collection:** No automated screenshot or artifact collection linked to timeline events.

### Future Improvements

- Integrate with common C2 frameworks for automatic event logging
- Add support for additional log formats (Syslog, Windows Event Logs)
- Implement automated redaction validation (regression testing for new secret patterns)
- Build PDF export capability for client reports
- Add graph visualization for attack chains and lateral movement"""

    def _render_reusable_ttps(self, decisions: List[Dict[str, Any]]) -> str:
        """Render reusable TTPs section."""
        lines = ["## Reusable TTPs — Technique References\n"]

        # Group decisions by tags
        ttps_by_tag = defaultdict(list)

        for decision in decisions:
            tags = decision.get('tags', [])
            for tag in tags:
                ttps_by_tag[tag].append(decision)

        if not ttps_by_tag:
            lines.append("*No tagged techniques recorded.*\n")
            lines.append("*Recommendation: Tag decisions with technique categories for future reference.*")
            return "\n".join(lines)

        lines.append("Techniques used during this engagement, organized for reuse:\n")

        for tag, tag_decisions in sorted(ttps_by_tag.items()):
            lines.append(f"### {tag.upper()}\n")

            for decision in tag_decisions:
                decision_text = decision.get('decision', 'Unknown')
                rationale = decision.get('rationale', '')
                outcome = decision.get('outcome', 'unknown')

                lines.append(f"- **{decision_text}** ({outcome})")
                if rationale:
                    lines.append(f"  - Context: {rationale}")

            lines.append("")  # Blank line between sections

        lines.append("\n**Note:** These are framework-agnostic technique references. ")
        lines.append("Map to MITRE ATT&CK or internal TTP library as needed.")

        return "\n".join(lines)

    def _render_correlation_details(self, correlated: List[Dict[str, Any]]) -> str:
        """Render correlation analysis."""
        lines = ["## Correlation Analysis\n"]

        if not correlated:
            lines.append("*No correlated data available.*")
            return "\n".join(lines)

        lines.append("**Correlation Rules:**")
        lines.append("- Time window: ±300 seconds (5 minutes)")
        lines.append("- Asset matching: Required")
        lines.append("- Match strategy: Exact or substring match\n")

        # Analyze correlation quality
        with_events = [c for c in correlated if c['event'] is not None]
        without_events = [c for c in correlated if c['event'] is None]

        lines.append(f"**Results:**")
        lines.append(f"- Decisions with correlated events: {len(with_events)}")
        lines.append(f"- Decisions without correlated events: {len(without_events)}")

        if with_events:
            avg_time_delta = sum(c['time_delta'] for c in with_events) / len(with_events)
            lines.append(f"- Average time delta for matches: {avg_time_delta:.1f} seconds\n")

        # Show decisions without correlations for investigation
        if without_events:
            lines.append(f"\n### Uncorrelated Decisions\n")
            lines.append("The following decisions did not match any events (may indicate logging gaps):\n")

            for item in without_events[:5]:  # Show first 5
                decision = item['decision']
                decision_text = decision.get('decision', 'Unknown')
                timestamp = decision.get('timestamp', 'Unknown')
                lines.append(f"- {timestamp}: {decision_text}")

            if len(without_events) > 5:
                lines.append(f"\n*...and {len(without_events) - 5} more.*")

        return "\n".join(lines)
