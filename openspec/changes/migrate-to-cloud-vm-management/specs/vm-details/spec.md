# VM Details Specification

## ADDED Requirements

### Requirement: Get VM Details

The system SHALL provide an MCP tool `get_vm_details` to retrieve detailed information about a specific virtual machine.

#### Scenario: Get details for existing VM
- **WHEN** a user calls `get_vm_details` with a valid composite VM ID
- **THEN** the system returns detailed information about the VM
- **AND** the response includes: name, provider, account, region, instance ID, state, public IP, instance type

#### Scenario: VM not found
- **WHEN** a user calls `get_vm_details` with a non-existent VM ID
- **THEN** the system returns an error indicating the VM was not found

#### Scenario: Invalid VM ID format
- **WHEN** a user calls `get_vm_details` with an invalid composite ID format
- **THEN** the system returns an error explaining the expected format

### Requirement: VM Basic Details

The system SHALL return the following basic details for every VM:
- `id`: Composite identifier
- `name`: VM display name
- `provider`: Cloud provider (aws, azure)
- `account_alias`: User-defined account name
- `region`: Cloud region/location
- `state`: Current power state
- `instance_type`: VM size/type

#### Scenario: Display basic VM details
- **WHEN** retrieving VM details
- **THEN** all basic fields are included in the response
- **AND** fields with no value are returned as null rather than omitted

### Requirement: VM Public IP Address

The system SHALL return the public IP address of a VM if one is assigned.

#### Scenario: VM with public IP
- **WHEN** retrieving details for a VM with a public IP assigned
- **THEN** the `public_ip` field contains the IP address

#### Scenario: VM without public IP
- **WHEN** retrieving details for a VM without a public IP
- **THEN** the `public_ip` field is null
- **AND** no error is raised

### Requirement: VM Power State

The system SHALL return a normalized power state for VMs across all providers.

Supported states:
- `running`: VM is running and accessible
- `stopped`: VM is stopped/deallocated
- `starting`: VM is in the process of starting
- `stopping`: VM is in the process of stopping
- `terminated`: VM has been terminated/deleted
- `unknown`: State could not be determined

#### Scenario: Running VM state
- **WHEN** an AWS EC2 instance is in "running" state
- **THEN** the `state` field returns "running"

#### Scenario: Stopped Azure VM state
- **WHEN** an Azure VM is in "deallocated" state
- **THEN** the `state` field returns "stopped"

#### Scenario: Transitional state
- **WHEN** a VM is transitioning between states
- **THEN** the `state` field returns the appropriate transitional state (starting/stopping)
