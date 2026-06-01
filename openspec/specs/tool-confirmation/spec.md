# tool-confirmation Specification

## Purpose
Provide a reusable confirmation gate that prompts the user before guarded tools perform their actions, using the MCP elicitation primitive. The gate fails open when the client does not support elicitation, and the set of guarded tools is operator-configurable.

## Requirements
### Requirement: Confirmation Gate via MCP Elicitation

The system SHALL provide a reusable confirmation gate that, before a guarded tool performs its action, requests user confirmation from the connected client using the MCP elicitation primitive (`Context.elicit`). The gate SHALL return a boolean indicating whether the action may proceed.

#### Scenario: User confirms the action
- **WHEN** a guarded tool invokes the confirmation gate and the client supports elicitation
- **AND** the user accepts the confirmation prompt
- **THEN** the gate returns a value indicating the action may proceed
- **AND** the tool performs its action

#### Scenario: User declines the action
- **WHEN** a guarded tool invokes the confirmation gate and the client supports elicitation
- **AND** the user declines the confirmation prompt
- **THEN** the gate returns a value indicating the action must not proceed
- **AND** the tool performs no provider action

#### Scenario: User cancels the prompt
- **WHEN** a guarded tool invokes the confirmation gate and the client supports elicitation
- **AND** the user cancels the confirmation prompt or the elicitation times out
- **THEN** the gate returns a value indicating the action must not proceed
- **AND** the tool performs no provider action

### Requirement: Fail-Open When Elicitation Unsupported

The confirmation gate SHALL detect whether the connected client advertises elicitation capability. When the client does not support elicitation, the gate SHALL allow the action to proceed without prompting (fail-open).

#### Scenario: Client without elicitation capability
- **WHEN** a guarded tool invokes the confirmation gate
- **AND** the connected client does not advertise elicitation capability
- **THEN** the gate returns a value indicating the action may proceed
- **AND** no elicitation request is sent to the client

### Requirement: Configurable Required-Tool Set

The system SHALL determine which tools require confirmation from a configurable set, read from the `VM_MCP_CONFIRM_REQUIRED_TOOLS` environment variable as a comma-separated list of tool names. When the variable is unset, the set SHALL default to `start_vm`, `stop_vm`, and `reboot_vm`.

#### Scenario: Default required-tool set
- **WHEN** `VM_MCP_CONFIRM_REQUIRED_TOOLS` is not set
- **THEN** `start_vm`, `stop_vm`, and `reboot_vm` require confirmation
- **AND** read-only tools (`list_vms`, `list_providers`, `get_vm_details`) do not require confirmation by default

#### Scenario: Operator overrides the required-tool set
- **WHEN** `VM_MCP_CONFIRM_REQUIRED_TOOLS` is set to a comma-separated list of tool names
- **THEN** exactly the listed tools require confirmation
- **AND** tools not in the list run without a confirmation prompt

#### Scenario: Any tool is gateable, including read-only tools
- **WHEN** `VM_MCP_CONFIRM_REQUIRED_TOOLS` includes a read-only tool such as `list_providers`
- **THEN** that tool requests confirmation before producing its result
- **AND** declining the prompt returns `status`: "cancelled" without producing the result

#### Scenario: Confirmation disabled
- **WHEN** `VM_MCP_CONFIRM_REQUIRED_TOOLS` is set to an empty value
- **THEN** no tool requires confirmation

### Requirement: Content-Aware Confirmation Message

When a guarded tool requests confirmation, the message presented to the user SHALL identify the specific target VM and surface any destructive flags supplied by the caller.

#### Scenario: Message names the target VM
- **WHEN** a guarded power tool requests confirmation for a given `vm_id`
- **THEN** the confirmation message includes that `vm_id`

#### Scenario: Message surfaces the force flag
- **WHEN** `stop_vm` requests confirmation with `force=true`
- **THEN** the confirmation message indicates that the stop will be forced (non-graceful)
