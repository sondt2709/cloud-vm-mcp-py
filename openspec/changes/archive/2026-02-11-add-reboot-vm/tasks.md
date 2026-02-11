# Tasks: Add Reboot VM Support

## 1. Implementation

- [x] Add `reboot_vm` abstract method to `BaseProvider` in `vm_mcp/providers/base.py`
- [x] Implement `reboot_vm` in AWS provider (`vm_mcp/providers/aws.py`) using `reboot_instances` API
- [x] Implement `reboot_vm` in Azure provider (`vm_mcp/providers/azure.py`) using `begin_restart` API
- [x] Add `reboot_vm` MCP tool in `vm_mcp/mcp.py` with YAML output format

## 2. Testing

- [x] Add unit tests for `reboot_vm` in `tests/test_mcp_tools.py`
- [x] Add unit tests for AWS provider reboot implementation
- [x] Add unit tests for Azure provider reboot implementation

## 3. Validation

- [x] Run `uv run ty check` to verify type safety
- [x] Run `uv run ruff check` to verify linting
- [x] Run `uv run pytest` to verify all tests pass
- [ ] Manual test with MCP inspector (`npx @modelcontextprotocol/inspector`)
