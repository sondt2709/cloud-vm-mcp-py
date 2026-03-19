# alibaba-ecs-provider Specification

## Purpose
Alibaba Cloud ECS provider implementation — listing, details, start/stop/reboot for ECS instances with multi-account and multi-region support.

## Requirements

### Requirement: Alibaba ECS Instance Listing

The system SHALL support listing Alibaba Cloud ECS instances across configured accounts and regions through the existing `list_vms` MCP tool.

#### Scenario: List all ECS instances
- **WHEN** a user calls `list_vms` with an Alibaba Cloud account configured
- **THEN** the system returns all ECS instances from all configured regions
- **AND** each instance includes `id` (composite), `name`, `state`, `region`, `provider` ("alibaba"), and `tenant_alias`

#### Scenario: Filter by provider
- **WHEN** a user calls `list_vms` with `provider="alibaba"`
- **THEN** only Alibaba Cloud ECS instances are returned

#### Scenario: Filter by region
- **WHEN** a user calls `list_vms` with `region="cn-hangzhou"`
- **THEN** only ECS instances from that region are returned

#### Scenario: Multiple Alibaba accounts
- **WHEN** multiple Alibaba accounts are configured
- **THEN** instances from all accounts are returned with distinct `tenant_alias` values

### Requirement: Alibaba ECS Instance Details

The system SHALL support retrieving detailed information for a specific Alibaba Cloud ECS instance through the existing `get_vm_details` MCP tool.

#### Scenario: Get ECS instance details
- **WHEN** a user calls `get_vm_details` with a valid Alibaba composite ID
- **THEN** the system returns detailed information including instance type, public/private IP addresses, creation time, and current state

#### Scenario: Instance not found
- **WHEN** a user calls `get_vm_details` with an Alibaba composite ID for a non-existent instance
- **THEN** the system returns an error indicating the instance was not found

### Requirement: Alibaba ECS Instance Start

The system SHALL support starting a stopped Alibaba Cloud ECS instance through the existing `start_vm` MCP tool.

#### Scenario: Start a stopped instance
- **WHEN** a user calls `start_vm` with a valid Alibaba composite ID for a stopped instance
- **THEN** the system sends a start request to the Alibaba ECS API
- **AND** returns success with a confirmation message

#### Scenario: Start an already running instance
- **WHEN** a user calls `start_vm` with a composite ID for an already running instance
- **THEN** the system returns an appropriate message indicating the instance is already running

### Requirement: Alibaba ECS Instance Stop

The system SHALL support stopping a running Alibaba Cloud ECS instance through the existing `stop_vm` MCP tool.

#### Scenario: Graceful stop
- **WHEN** a user calls `stop_vm` with a valid Alibaba composite ID and `force=False`
- **THEN** the system sends a stop request with `ForceStop=false` to the Alibaba ECS API
- **AND** returns success with a confirmation message

#### Scenario: Force stop
- **WHEN** a user calls `stop_vm` with a valid Alibaba composite ID and `force=True`
- **THEN** the system sends a stop request with `ForceStop=true` to the Alibaba ECS API

### Requirement: Alibaba ECS Instance Reboot

The system SHALL support rebooting a running Alibaba Cloud ECS instance through the existing `reboot_vm` MCP tool.

#### Scenario: Reboot a running instance
- **WHEN** a user calls `reboot_vm` with a valid Alibaba composite ID for a running instance
- **THEN** the system sends a reboot request to the Alibaba ECS API
- **AND** returns success with a confirmation message

### Requirement: Alibaba ECS State Mapping

The system SHALL map Alibaba Cloud ECS instance states to the existing `VMState` enum.

#### Scenario: Running instance
- **WHEN** an ECS instance has status `Running`
- **THEN** the system maps it to `VMState.RUNNING`

#### Scenario: Starting instance
- **WHEN** an ECS instance has status `Starting` or `Pending`
- **THEN** the system maps it to `VMState.STARTING`

#### Scenario: Stopping instance
- **WHEN** an ECS instance has status `Stopping`
- **THEN** the system maps it to `VMState.STOPPING`

#### Scenario: Stopped instance
- **WHEN** an ECS instance has status `Stopped`
- **THEN** the system maps it to `VMState.STOPPED`

#### Scenario: Expired instance
- **WHEN** an ECS instance has status `Expired`
- **THEN** the system maps it to `VMState.TERMINATED`

### Requirement: Alibaba Composite ID Format

The system SHALL use the standard composite ID format for Alibaba Cloud ECS instances.

#### Scenario: Composite ID structure
- **WHEN** the system creates a composite ID for an Alibaba ECS instance
- **THEN** the format SHALL be `alibaba:{tenant_alias}:{region}:{instance_id}`
- **AND** the instance ID uses the Alibaba format (e.g., `i-bp1234567890abcdef`)

### Requirement: Alibaba SDK Async Bridge

The system SHALL wrap synchronous Alibaba Cloud SDK calls with `asyncio.to_thread()` to prevent blocking the event loop.

#### Scenario: Non-blocking API calls
- **WHEN** the system queries the Alibaba ECS API
- **THEN** the SDK call is executed in a thread pool via `asyncio.to_thread()`
- **AND** the MCP server event loop remains responsive
