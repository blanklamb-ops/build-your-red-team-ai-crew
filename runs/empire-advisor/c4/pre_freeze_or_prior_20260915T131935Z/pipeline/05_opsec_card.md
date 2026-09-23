 ### FILE: OPSEC_CARD.md

```markdown
# OPSEC Card

## Summary

Empire-Advisor is a tool that intercepts or wraps operator command submissions in a lab Empire-like interface. It scores commands against a transparent, documented heuristic, suggests documented alternative commands from a local knowledge base, and keeps humans in control by never auto-executing alternatives.

## Operator Risks

- **Misconfiguration:** If the rules file or knowledge base file is not properly configured, the tool may not function as intended.
- **Dependency Risks:** The tool relies on external Python libraries. If these libraries are not properly installed or updated, the tool may not function correctly or may be vulnerable to attacks.

## Artifacts Left Behind

- **Files:** The tool creates a `rules.yaml` file and a `knowledge_base.yaml` file. These files may contain sensitive information if not properly secured.
- **Logs:** The tool may generate logs that contain information about the commands that were intercepted and scored. These logs should be handled securely.

## Safer Operating Guidance

- **Configuration:** Ensure that the `rules.yaml` and `knowledge_base.yaml` files are properly secured and that they contain only the necessary information.
- **Evidence Handling:** Handle logs securely. Do not store them on unsecured systems or transmit them over unencrypted networks.

## Detection Recommendations

- **File Monitoring:** Monitor for the creation of `rules.yaml` and `knowledge_base.yaml` files.
- **Log Analysis:** Analyze logs for unusual patterns of command interception and scoring.
- **Anomaly Detection:** Use anomaly detection techniques to identify unusual command patterns.

## Residual Gaps

- The exact implementation of the command interception hook is not specified. This may make it difficult to detect the use of the tool.
- The exact format of the scoring engine's rules is not specified. This may make it difficult to understand how the tool scores commands.
- The exact source of the suggestion engine's local knowledge base is not specified. This may make it difficult to understand the basis for the tool's suggestions.
```

The OPSEC card provides a summary of the tool, identifies potential operator risks, lists artifacts left behind, provides safer operating guidance, and offers detection recommendations. The card also identifies residual gaps in the implementation that could not be addressed in this review.