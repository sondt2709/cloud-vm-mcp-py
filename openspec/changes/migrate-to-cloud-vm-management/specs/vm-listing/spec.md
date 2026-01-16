# VM Listing Specification

## ADDED Requirements

### Requirement: List All VMs Across Providers

The system SHALL provide an MCP tool `list_vms` to list all virtual machines across all configured cloud providers and accounts.

#### Scenario: List VMs from all providers
- **WHEN** a user calls the `list_vms` tool without filters
- **THEN** the system queries all configured AWS accounts and Azure directories
- **AND** returns a unified list of all VMs with basic information
- **AND** each VM entry includes: composite ID, name, provider, account alias, region, state

#### Scenario: Empty VM list
- **WHEN** no VMs exist in any configured account
- **THEN** the system returns an empty list with an informative message

#### Scenario: Partial provider failure
- **WHEN** one provider fails to respond but others succeed
- **THEN** the system returns VMs from successful providers
- **AND** includes an error summary for failed providers

### Requirement: Filter VMs by Provider

The system SHALL support filtering VM list results by provider name.

#### Scenario: Filter by AWS provider
- **WHEN** a user calls `list_vms` with `provider="aws"`
- **THEN** the system queries only AWS accounts and returns their VMs

#### Scenario: Filter by Azure provider
- **WHEN** a user calls `list_vms` with `provider="azure"`
- **THEN** the system queries only Azure directories and returns their VMs

#### Scenario: Invalid provider filter
- **WHEN** a user calls `list_vms` with an unsupported provider name
- **THEN** the system returns an error indicating the provider is not supported

### Requirement: Filter VMs by Tenant

The system SHALL support filtering VM list results by tenant (AWS account alias or Azure directory alias).

#### Scenario: Filter by AWS account alias
- **WHEN** a user calls `list_vms` with `tenant="production"`
- **THEN** the system queries only the AWS account with alias "production"

#### Scenario: Filter by Azure directory alias
- **WHEN** a user calls `list_vms` with `tenant="corp-main"`
- **THEN** the system queries only the Azure directory with alias "corp-main"

#### Scenario: Non-existent tenant filter
- **WHEN** a user calls `list_vms` with a tenant alias that doesn't exist
- **THEN** the system returns an error indicating the tenant was not found

### Requirement: Filter VMs by Region

The system SHALL support filtering VM list results by cloud region.

#### Scenario: Filter by region
- **WHEN** a user calls `list_vms` with `region="us-east-1"`
- **THEN** the system queries only the specified region across applicable providers

#### Scenario: Combined filters
- **WHEN** a user calls `list_vms` with `provider="aws"`, `tenant="production"`, `region="us-east-1"`
- **THEN** the system queries only the specified provider, tenant, and region
- **AND** returns a narrowed list of VMs matching all filters

### Requirement: Query Timeout

The system SHALL enforce timeout limits on VM listing operations.

#### Scenario: Per-request timeout
- **WHEN** a single provider API call exceeds 60 seconds
- **THEN** the system aborts that request and reports a timeout error for that provider

#### Scenario: Total query timeout
- **WHEN** the total multi-provider query exceeds 180 seconds (3 minutes)
- **THEN** the system aborts remaining requests and returns partial results
- **AND** includes a warning about timed-out providers

### Requirement: VM Composite Identifier

Each VM SHALL be identified by a composite ID in the format: `{provider}:{account_alias}:{region}:{instance_id}`.

#### Scenario: AWS VM identifier
- **WHEN** listing an AWS EC2 instance
- **THEN** the ID format is `aws:{account_alias}:{region}:{instance_id}`
- **AND** example: `aws:production:us-east-1:i-1234567890abcdef0`

#### Scenario: Azure VM identifier
- **WHEN** listing an Azure VM
- **THEN** the ID format is `azure:{directory_alias}:{region}:{vm_name}`
- **AND** example: `azure:corp-main:eastus:web-server-01`
