# Provider Credentials Output Format

## ADDED Requirements

### Requirement: YAML Output Format for List Providers

The `list_providers` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful provider listing
- **WHEN** a user calls `list_providers` and providers are configured
- **THEN** the output is valid YAML with:
  - `status`: "success"
  - `count`: number of providers
  - `providers`: list of provider objects with provider, tenant_alias, regions

#### Scenario: No providers configured
- **WHEN** no providers are configured
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: message indicating no providers configured

### Requirement: Console Error Logging for Provider Listing

The `list_providers` tool SHALL log errors to console using Python's `logging` module in addition to returning them via MCP.

#### Scenario: Configuration exception logged
- **WHEN** loading configuration throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response
