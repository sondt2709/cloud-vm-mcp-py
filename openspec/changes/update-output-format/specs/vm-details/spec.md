# VM Details Output Format

## ADDED Requirements

### Requirement: YAML Output Format for VM Details

The `get_vm_details` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful VM details retrieval
- **WHEN** a user calls `get_vm_details` with a valid VM ID
- **THEN** the output is valid YAML with the following structure:
  - `status`: "success"
  - `vm`: object containing id, name, provider, tenant_alias, region, state, instance_type, public_ip, private_ip, provider_metadata

#### Scenario: VM not found
- **WHEN** a user calls `get_vm_details` with a non-existent VM ID
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: "VM not found" message

#### Scenario: Invalid VM ID format
- **WHEN** a user calls `get_vm_details` with an invalid ID format
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: message explaining the expected format

### Requirement: Console Error Logging for VM Details

The `get_vm_details` tool SHALL log errors to console using Python's `logging` module in addition to returning them via MCP.

#### Scenario: API exception logged to console
- **WHEN** a provider API throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response

#### Scenario: Timeout logged to console
- **WHEN** the API call times out
- **THEN** the timeout is logged using `logging.exception()`
- **AND** the error is included in the YAML response
