"""Client-facing report renderer."""
from typing import List, Dict, Any
from datetime import datetime


class ClientRenderer:
    """Renders professional client-facing reports."""

    def render(
        self,
        timeline: List[Dict[str, Any]],
        correlated: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Render client report in Markdown format.

        Args:
            timeline: Unified timeline of events and decisions
            correlated: Correlated event-decision pairs
            metadata: Report metadata (generation time, etc.)

        Returns:
            Markdown-formatted client report
        """
        sections = []

        sections.append(self._render_header(metadata))
        sections.append(self._render_executive_summary(timeline, correlated))
        sections.append(self._render_timeline(timeline))
        sections.append(self._render_findings_placeholder())
        sections.append(self._render_detection_recommendations())
        sections.append(self._render_footer())

        return "\n\n".join(sections)

    def _render_header(self, metadata: Dict[str, Any]) -> str:
        """Render report header."""
        return f"""# Security Assessment Report

**Report Generated:** {metadata.get('generated_at', 'N/A')}
**Assessment Period:** {metadata.get('assessment_start', 'N/A')} to {metadata.get('assessment_end', 'N/A')}

---"""

    def _render_executive_summary(
        self,
        timeline: List[Dict[str, Any]],
        correlated: List[Dict[str, Any]]
    ) -> str:
        """Render executive summary section."""
        total_events = len([t for t in timeline if t['type'] == 'event'])
        total_decisions = len([t for t in timeline if t['type'] == 'decision'])
        successful_correlations = len([c for c in correlated if c['event'] is not None])

        return f"""## Executive Summary

This report summarizes the findings from the authorized security assessment conducted during the specified period. The testing team identified vulnerabilities and assessed the security posture of the target environment.

**Assessment Scope:**
- Total activities logged: {total_events} events
- Operator decisions recorded: {total_decisions}
- Successful attack chains: {successful_correlations} correlated sequences

**Key Objectives:**
- Identify exploitable vulnerabilities in the external perimeter
- Assess lateral movement capabilities within the network
- Evaluate detection and response capabilities
- Provide actionable remediation guidance

The assessment was conducted in accordance with the agreed-upon scope and rules of engagement. All activities were authorized and performed by qualified security professionals."""

    def _render_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Render engagement timeline."""
        lines = ["## Assessment Timeline\n"]

        if not timeline:
            lines.append("*No timeline data available.*")
            return "\n".join(lines)

        lines.append("The following timeline shows key activities during the assessment:\n")

        for item in timeline:
            timestamp = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            data = item['data']

            if item['type'] == 'decision':
                decision = data.get('decision', 'Unknown decision')
                lines.append(f"**{timestamp}** — {decision}")

            elif item['type'] == 'event':
                action = data.get('action', 'Unknown action')
                asset = data.get('asset', 'Unknown asset')
                details = data.get('details', '')

                # Format event with context
                if details:
                    lines.append(f"- {timestamp} — {action} on {asset}: {details}")
                else:
                    lines.append(f"- {timestamp} — {action} on {asset}")

        return "\n".join(lines)

    def _render_findings_placeholder(self) -> str:
        """Render findings section placeholder."""
        return """## Findings

The following vulnerabilities and security issues were identified during the assessment:

### Critical Findings

*[Findings to be inserted here based on operator analysis]*

### High-Risk Findings

*[Findings to be inserted here based on operator analysis]*

### Medium-Risk Findings

*[Findings to be inserted here based on operator analysis]*

### Informational Findings

*[Findings to be inserted here based on operator analysis]*"""

    def _render_detection_recommendations(self) -> str:
        """Render detection recommendations section."""
        return """## Detection Recommendations

To improve detection capabilities and identify similar attack patterns in the future, we recommend implementing the following monitoring and detection strategies:

### Network-Level Detection

- **Port Scanning Detection:** Monitor for rapid connection attempts across multiple ports from single source IPs. Baseline normal scanning patterns and alert on anomalies.

- **Exploitation Attempts:** Log and analyze HTTP requests with suspicious patterns, including path traversal attempts, unusual user agents, and malformed requests.

- **Lateral Movement:** Alert on unusual SSH/RDP connections between internal hosts, especially from systems that don't typically initiate such connections.

### Host-Level Detection

- **Process Monitoring:** Track unusual process creation, especially command shells spawned by web services or other non-interactive processes.

- **File Integrity:** Monitor critical system and application configuration files for unauthorized modifications.

- **Credential Access:** Alert on credential dumping tools, unusual authentication attempts, and access to credential stores.

### Application-Level Detection

- **Web Application Firewall (WAF):** Deploy signatures for known CVEs and common attack patterns. Regularly update rule sets.

- **Database Activity Monitoring:** Track unusual query patterns, bulk data exports, and access to sensitive tables outside normal business hours.

- **API Monitoring:** Log API authentication failures, unusual request rates, and access to sensitive endpoints.

### Behavioral Analytics

- **User Behavior Analytics (UBA):** Establish baselines for normal user and service account behavior. Alert on deviations such as unusual access times, geographic anomalies, or privilege escalation.

- **Data Exfiltration Detection:** Monitor for large outbound data transfers, connections to unusual external IPs, and use of non-standard protocols.

### Log Aggregation and Correlation

- **Centralized Logging:** Ensure all critical systems forward logs to a central SIEM or log management platform with sufficient retention.

- **Correlation Rules:** Implement rules that detect multi-stage attacks by correlating events across different systems and time windows.

- **Alert Prioritization:** Tune detection rules to reduce false positives while maintaining visibility into genuine threats."""

    def _render_footer(self) -> str:
        """Render report footer."""
        return """---

## Disclaimer

This report contains confidential information about security vulnerabilities identified during an authorized assessment. It is intended solely for the client organization's internal use. Unauthorized distribution may result in disclosure of sensitive security information.

**Confidential — For Authorized Recipients Only**"""
