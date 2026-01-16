# VM Listing Output Format

## ADDED Requirements

### Requirement: YAML Output Format for VM Listing

The `list_vms` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful VM listing
- **WHEN** a user calls `list_vms` and VMs are found
- **THEN** the output is valid YAML with the following structure:
  - `status`: "success"
  - `count`: number of VMs found
  - `vms`: list of VM objects with id, name, provider, tenant_alias, region, instance_type, state
- **AND** the YAML is parseable by standard YAML libraries

#### Scenario: Empty VM list
- **WHEN** no VMs exist in any configured account
- **THEN** the output is valid YAML with:
  - `status`: "success"
  - `count`: 0
  - `vms`: empty list
  - `message`: informative message about empty results

#### Scenario: Partial provider failure
- **WHEN** one provider fails but others succeed
- **THEN** the output is valid YAML with:
  - `status`: "partial"
  - `vms`: list of VMs from successful providers
  - `errors`: list of error objects with provider, tenant_alias, and error message

#### Scenario: Complete failure
- **WHEN** all providers fail or configuration is missing
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: error message string

### Requirement: Console Error Logging for VM Listing

The `list_vms` tool SHALL log errors to console using Python's `logging` module in addition to returning them via MCP.

#### Scenario: Provider timeout logged to console
- **WHEN** a provider API call times out
- **THEN** the error is logged using `logging.exception()` which includes the full traceback
- **AND** the error is included in the YAML response

#### Scenario: Provider exception logged to console
- **WHEN** a provider throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response
