 # Chrome-MV3-Kit Operational Constraints

## Runtime Environment

1. The tool should be designed to run on the Chrome browser, which is a multi-process architecture.
2. The tool should have the minimum required privileges to perform its functions.
3. The tool should be able to operate in a network environment with varying levels of connectivity.
4. The tool should be designed to handle the specific security sandboxing and isolation measures implemented by Chrome extensions.

## Secrets & Evidence Handling

1. The tool should never commit sensitive data, such as authentication tokens or credentials, to version control or any other storage medium.
2. The tool should handle all data in a secure and encrypted manner, both in transit and at rest.
3. The tool should not store any sensitive data on the operator's machine without explicit consent and appropriate security measures.
4. The OPSEC Reviewer must document all data handling and storage mechanisms used by the tool.

## Operator Workflow

1. The tool should be invoked by the operator through the Chrome Extension Management page.
2. The operator should be able to configure the tool's settings through a user-friendly interface.
3. The tool should provide clear and concise feedback to the operator about its status and any errors that occur.

## Safety Defaults

1. The tool should operate in a dry-run mode by default, allowing the operator to preview the results of data capture and phishlet generation without making any changes.
2. The tool should have a list of allowlisted domains that it is allowed to capture data from.
3. The tool should require explicit confirmation from the operator before generating a phishlet or saving static HTML snapshots.

## Degradation Modes

1. If the tool is unable to connect to the internet, it should operate in offline mode, allowing the operator to view previously captured data and generate phishlets.
2. If the tool encounters a partial failure during data capture or phishlet generation, it should continue operating and provide feedback to the operator about the failed components.

## Plan Deltas

1. The Architect must ensure that the tool's data capture module handles multi-origin navigations and requests in a secure and accurate manner.
2. The Architect must implement a mechanism for the tool to determine which origins require optional host permissions and handle cases where the operator does not grant the required permissions.
3. The Architect must ensure that the tool can handle cases where the service worker is suspended or restarted without losing data or functionality.
4. The Architect must implement a mechanism for the tool to handle non-HTTP(S) URLs that are observed during data capture.
5. The Architect must ensure that the tool's user interface is designed to be intuitive and easy to use, with clear instructions and feedback.
6. The Architect must ensure that the tool's data handling and storage mechanisms are secure and comply with all relevant data protection regulations.
7. The Architect must ensure that the tool's test plan includes manual tests for all critical functionality, such as optional host permissions and HTTP traffic pattern generation.
8. The Architect must ensure that the tool's documentation is comprehensive and up-to-date, covering all aspects of its usage, configuration, and output.