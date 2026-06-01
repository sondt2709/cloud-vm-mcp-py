## MODIFIED Requirements

### Requirement: Start VM

The system SHALL provide an MCP tool `start_vm` to start a stopped virtual machine. When `start_vm` is in the configured confirmation-required set and the client supports elicitation, the tool SHALL request user confirmation before initiating the start operation.

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

#### Scenario: Start VM requires confirmation
- **WHEN** a user calls `start_vm`, the tool is in the confirmation-required set, and the client supports elicitation
- **THEN** the system requests confirmation before starting the VM
- **AND** initiates the start operation only if the user accepts

#### Scenario: Start VM confirmation declined
- **WHEN** a user calls `start_vm` and declines or cancels the confirmation prompt
- **THEN** the system does not start the VM
- **AND** returns YAML with `status`: "cancelled" and an explanatory message

### Requirement: Stop VM

The system SHALL provide an MCP tool `stop_vm` to stop a running virtual machine. When `stop_vm` is in the configured confirmation-required set and the client supports elicitation, the tool SHALL request user confirmation before initiating the stop operation.

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

#### Scenario: Stop VM requires confirmation
- **WHEN** a user calls `stop_vm`, the tool is in the confirmation-required set, and the client supports elicitation
- **THEN** the system requests confirmation before stopping the VM
- **AND** initiates the stop operation only if the user accepts

#### Scenario: Stop VM confirmation declined
- **WHEN** a user calls `stop_vm` and declines or cancels the confirmation prompt
- **THEN** the system does not stop the VM
- **AND** returns YAML with `status`: "cancelled" and an explanatory message

### Requirement: Reboot VM

The system SHALL provide an MCP tool `reboot_vm` to reboot a running virtual machine. When `reboot_vm` is in the configured confirmation-required set and the client supports elicitation, the tool SHALL request user confirmation before initiating the reboot operation.

#### Scenario: Reboot a running VM
- **WHEN** a user calls `reboot_vm` with a valid VM ID for a running VM
- **THEN** the system initiates the reboot operation
- **AND** returns a success message indicating the VM is rebooting

#### Scenario: Reboot a stopped VM
- **WHEN** a user calls `reboot_vm` with a VM ID for a stopped VM
- **THEN** the system returns an error indicating the VM must be running to reboot

#### Scenario: Reboot non-existent VM
- **WHEN** a user calls `reboot_vm` with a non-existent VM ID
- **THEN** the system returns an error indicating the VM was not found

#### Scenario: Reboot VM without permission
- **WHEN** the configured credentials lack permission to reboot the VM
- **THEN** the system returns an authorization error with details

#### Scenario: Reboot VM requires confirmation
- **WHEN** a user calls `reboot_vm`, the tool is in the confirmation-required set, and the client supports elicitation
- **THEN** the system requests confirmation before rebooting the VM
- **AND** initiates the reboot operation only if the user accepts

#### Scenario: Reboot VM confirmation declined
- **WHEN** a user calls `reboot_vm` and declines or cancels the confirmation prompt
- **THEN** the system does not reboot the VM
- **AND** returns YAML with `status`: "cancelled" and an explanatory message

### Requirement: Force Stop VM

The system SHALL support a `force` parameter for the `stop_vm` tool to force stop a VM. When `stop_vm` requires confirmation, the confirmation message SHALL indicate that the stop will be forced (non-graceful) when `force=true`.

#### Scenario: Force stop a VM
- **WHEN** a user calls `stop_vm` with `force=true`
- **THEN** the system forcefully stops the VM without graceful shutdown

#### Scenario: Default graceful stop
- **WHEN** a user calls `stop_vm` without the `force` parameter
- **THEN** the system performs a graceful shutdown (default behavior)

#### Scenario: Force stop confirmation highlights force
- **WHEN** a user calls `stop_vm` with `force=true` and confirmation is required
- **THEN** the confirmation message indicates the stop will be forced (non-graceful)
