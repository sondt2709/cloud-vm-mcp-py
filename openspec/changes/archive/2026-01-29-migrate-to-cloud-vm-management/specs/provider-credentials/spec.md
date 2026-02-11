# Provider Credentials Specification

## ADDED Requirements

### Requirement: Multi-Provider Credential Configuration

The system SHALL support loading credentials for multiple cloud providers from a YAML configuration file specified by the `PROVIDERS_CONFIG_PATH` environment variable.

#### Scenario: Load credentials from configuration file
- **WHEN** the system starts with `PROVIDERS_CONFIG_PATH` set to a valid YAML file
- **THEN** the system loads all provider credentials from the file
- **AND** credentials are validated for required fields per provider type

#### Scenario: Missing configuration file
- **WHEN** the system starts with `PROVIDERS_CONFIG_PATH` set to a non-existent file
- **THEN** the system raises a clear error indicating the file was not found

#### Scenario: Invalid configuration format
- **WHEN** the configuration file contains invalid YAML or missing required fields
- **THEN** the system raises a validation error with specific details about the issue

### Requirement: Configuration Hot-Reload

The system SHALL watch the configuration file for changes and automatically reload credentials without requiring a restart.

#### Scenario: Configuration file modified
- **WHEN** the configuration file is modified while the system is running
- **THEN** the system detects the change and reloads the credentials
- **AND** subsequent API calls use the updated credentials

#### Scenario: Configuration file becomes invalid
- **WHEN** the configuration file is modified with invalid content
- **THEN** the system logs an error and continues using the previous valid configuration
- **AND** no service interruption occurs

### Requirement: AWS Account Credentials

The system SHALL support AWS credentials with the following fields:
- `alias` (required): User-defined name for the account
- `access_key_id` (required): AWS access key ID
- `secret_access_key` (required): AWS secret access key
- `regions` (required): List of AWS regions to query

#### Scenario: Valid AWS credentials
- **WHEN** AWS credentials are configured with all required fields
- **THEN** the system validates and stores the credentials for use

#### Scenario: Multiple AWS accounts
- **WHEN** multiple AWS accounts are configured
- **THEN** the system can query VMs from all configured accounts

### Requirement: Azure Directory Credentials

The system SHALL support Azure credentials with the following fields:
- `alias` (required): User-defined name for the directory
- `tenant_id` (required): Azure Active Directory tenant ID
- `client_id` (required): Service principal client ID
- `client_secret` (required): Service principal client secret
- `subscription_ids` (required): List of subscription IDs to query

#### Scenario: Valid Azure credentials
- **WHEN** Azure credentials are configured with all required fields
- **THEN** the system validates and stores the credentials for use

#### Scenario: Multiple Azure directories
- **WHEN** multiple Azure directories are configured
- **THEN** the system can query VMs from all configured directories and subscriptions

### Requirement: List Configured Providers

The system SHALL provide an MCP tool `list_providers` to list all configured providers and their accounts.

#### Scenario: List all providers
- **WHEN** a user calls the `list_providers` tool
- **THEN** the system returns a list of all configured providers
- **AND** each provider entry includes the account/directory aliases
- **AND** sensitive credentials (keys, secrets) are NOT included in the response

#### Scenario: No providers configured
- **WHEN** a user calls `list_providers` with no credentials configured
- **THEN** the system returns an empty list with an informative message
