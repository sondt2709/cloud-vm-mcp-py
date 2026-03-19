## ADDED Requirements

### Requirement: Alibaba Cloud Account Credentials

The system SHALL support Alibaba Cloud credentials with the following fields:
- `alias` (required): User-defined name for the account
- `access_key_id` (required): Alibaba Cloud AccessKey ID
- `access_key_secret` (required): Alibaba Cloud AccessKey Secret
- `regions` (required): List of Alibaba Cloud region IDs to query (e.g., `cn-hangzhou`, `ap-southeast-1`)

#### Scenario: Valid Alibaba credentials
- **WHEN** Alibaba Cloud credentials are configured with all required fields
- **THEN** the system validates and stores the credentials for use

#### Scenario: Missing required field
- **WHEN** Alibaba Cloud credentials are missing `access_key_secret`
- **THEN** the system raises a validation error with specific details about the missing field

#### Scenario: Multiple Alibaba accounts
- **WHEN** multiple Alibaba Cloud accounts are configured
- **THEN** the system can query ECS instances from all configured accounts

### Requirement: Alibaba Provider Listed in Provider Listing

The system SHALL include configured Alibaba Cloud accounts in the `list_providers` MCP tool output.

#### Scenario: Alibaba provider in listing
- **WHEN** a user calls `list_providers` with Alibaba Cloud accounts configured
- **THEN** each Alibaba account appears in the provider list with `provider: "alibaba"`, `tenant_alias`, and `regions`
- **AND** sensitive credentials (AccessKey Secret) are NOT included in the response
