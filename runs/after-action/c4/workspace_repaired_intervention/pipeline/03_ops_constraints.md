 # Operational Constraints for After-Action Collector

## Runtime Environment

- The tool should be designed to run on a Linux-based operating system.
- The tool should not require root privileges to run.
- The tool should be able to operate in a network-restricted environment.

## Secrets & Evidence Handling

- The tool should not store any secrets or credentials in the source code or configuration files.
- The tool should support the use of environment variables or a secure key vault for the storage of secrets.
- The tool should not commit any sensitive data to version control.
- The OPSEC Reviewer must document the use of secrets and the measures taken to protect them.

## Operator Workflow

- The tool should be invoked from the command line using a simple and intuitive interface.
- The tool should support the use of a configuration file to customize its behavior.
- The tool should provide clear and concise documentation on how to use it.

## Safety Defaults

- The tool should support a dry-run mode that allows operators to test its functionality without making any changes to the data.
- The tool should support the use of allowlists to restrict the types of data that it can process.
- The tool should require explicit confirmation from the operator before making any changes to the data.

## Degradation Modes

- The tool should be able to operate offline and should cache data locally until it can be synced with a remote server.
- The tool should be able to handle partial failures gracefully and should continue to operate as much as possible.
- The tool should provide clear and concise error messages to the operator when it encounters a failure.

## Plan Deltas

- The Architect must ensure that the tool is designed to handle large log files efficiently.
- The Architect must ensure that the tool is able to handle missing or inconsistent data gracefully.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by providing a mechanism for capturing them in a structured format.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by integrating it with the existing decision logging mechanism.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by adding a new module for decision logging if necessary.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by working closely with the operators to understand their decision-making process and to design the tool accordingly.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by incorporating user feedback into the design of the tool.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by conducting user research to understand the needs and pain points of the operators.
- The Architect must ensure that the tool is able to handle operator decisions that are not explicitly logged by designing the tool to be flexible and adaptable to the changing needs of the operators.