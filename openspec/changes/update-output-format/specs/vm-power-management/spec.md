# VM Power Management Output Format

## ADDED Requirements

### Requirement: YAML Output Format for Start VM

The `start_vm` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful VM start
- **WHEN** a user calls `start_vm` and the operation succeeds
- **THEN** the output is valid YAML with:
  - `status`: "success"
  - `message`: success message from provider

#### Scenario: Failed VM start
- **WHEN** a user calls `start_vm` and the operation fails
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: error message from provider

### Requirement: YAML Output Format for Stop VM

The `stop_vm` tool SHALL return output in valid YAML format with a consistent structure.

#### Scenario: Successful VM stop
- **WHEN** a user calls `stop_vm` and the operation succeeds
- **THEN** the output is valid YAML with:
  - `status`: "success"
  - `message`: success message from provider

#### Scenario: Failed VM stop
- **WHEN** a user calls `stop_vm` and the operation fails
- **THEN** the output is valid YAML with:
  - `status`: "error"
  - `error`: error message from provider

### Requirement: Console Error Logging for Power Management

Power management tools SHALL log errors to console using Python's `logging` module in addition to returning them via MCP.

#### Scenario: Start VM exception logged
- **WHEN** `start_vm` throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response

#### Scenario: Stop VM exception logged
- **WHEN** `stop_vm` throws an exception
- **THEN** the full traceback is logged using `logging.exception()`
- **AND** a summary error is included in the YAML response
