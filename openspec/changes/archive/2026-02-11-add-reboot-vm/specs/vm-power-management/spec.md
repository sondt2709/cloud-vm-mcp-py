# vm-power-management Specification Delta

## ADDED Requirements

### Requirement: Reboot VM

The system SHALL provide an MCP tool `reboot_vm` to reboot a running virtual machine.

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

### Requirement: YAML Output Format for Reboot VM

The `reboot_vm` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful VM reboot
- **WHEN** a user calls `reboot_vm` and the operation succeeds
- **THEN** the output is valid YAML with:
  - `status`: "success"
  - `message`: success message from provider

#### Scenario: Failed VM reboot
- **WHEN** a user calls `reboot_vm` and the operation fails
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: error message from provider

### Requirement: Console Error Logging for Reboot VM

The `reboot_vm` tool SHALL log errors to console using Python's `logging` module in addition to returning them via MCP.

#### Scenario: Reboot VM exception logged
- **WHEN** `reboot_vm` throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response
