# VM Power Management Specification

## ADDED Requirements

### Requirement: Start VM

The system SHALL provide an MCP tool `start_vm` to start a stopped virtual machine.

#### Scenario: Start a stopped VM
- **WHEN** a user calls `start_vm` with a valid VM ID for a stopped VM
- **THEN** the system initiates the start operation
- **AND** returns a success message with the VM's new state (starting)

#### Scenario: Start an already running VM
- **WHEN** a user calls `start_vm` with a VM ID for an already running VM
- **THEN** the system returns a message indicating the VM is already running
- **AND** no error is raised

#### Scenario: Start non-existent VM
- **WHEN** a user calls `start_vm` with a non-existent VM ID
- **THEN** the system returns an error indicating the VM was not found

#### Scenario: Start VM without permission
- **WHEN** the configured credentials lack permission to start the VM
- **THEN** the system returns an authorization error with details

### Requirement: Stop VM

The system SHALL provide an MCP tool `stop_vm` to stop a running virtual machine.

#### Scenario: Stop a running VM
- **WHEN** a user calls `stop_vm` with a valid VM ID for a running VM
- **THEN** the system initiates the stop operation
- **AND** returns a success message with the VM's new state (stopping)

#### Scenario: Stop an already stopped VM
- **WHEN** a user calls `stop_vm` with a VM ID for an already stopped VM
- **THEN** the system returns a message indicating the VM is already stopped
- **AND** no error is raised

#### Scenario: Stop non-existent VM
- **WHEN** a user calls `stop_vm` with a non-existent VM ID
- **THEN** the system returns an error indicating the VM was not found

#### Scenario: Stop VM without permission
- **WHEN** the configured credentials lack permission to stop the VM
- **THEN** the system returns an authorization error with details

### Requirement: Force Stop VM

The system SHALL support a `force` parameter for the `stop_vm` tool to force stop a VM.

#### Scenario: Force stop a VM
- **WHEN** a user calls `stop_vm` with `force=true`
- **THEN** the system forcefully stops the VM without graceful shutdown

#### Scenario: Default graceful stop
- **WHEN** a user calls `stop_vm` without the `force` parameter
- **THEN** the system performs a graceful shutdown (default behavior)

### Requirement: Power Operation Timeout

The system SHALL support a `timeout` parameter for power operations to wait for state change confirmation.

#### Scenario: Wait for state change
- **WHEN** a user calls `start_vm` or `stop_vm` with `wait=true` and `timeout=60`
- **THEN** the system waits up to 60 seconds for the VM to reach the target state
- **AND** returns the final state of the VM

#### Scenario: Timeout exceeded
- **WHEN** the VM does not reach the target state within the timeout period
- **THEN** the system returns a timeout warning with the current state
- **AND** does not raise an error (the operation was initiated)

#### Scenario: Default no-wait behavior
- **WHEN** a user calls power operations without `wait` parameter
- **THEN** the system returns immediately after initiating the operation
- **AND** reports the transitional state (starting/stopping)
