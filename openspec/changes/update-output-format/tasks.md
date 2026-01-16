# Implementation Tasks

## 1. Update Output Format

- [x] 1.1 Add yaml import to `vm_mcp/mcp.py`
- [x] 1.2 Update `list_vms` tool to return YAML formatted output
- [x] 1.3 Update `list_providers` tool to return YAML formatted output
- [x] 1.4 Update `get_vm_details` tool to return YAML formatted output
- [x] 1.5 Update `start_vm` tool to return YAML formatted output
- [x] 1.6 Update `stop_vm` tool to return YAML formatted output

## 2. Ensure Console Error Logging

- [x] 2.1 Add logging module setup to `vm_mcp/mcp.py`
- [x] 2.2 Replace `traceback.print_exc()` with `logging.exception()` in mcp.py
- [x] 2.3 Replace `print(..., file=sys.stderr)` with `logging.exception()` for timeouts
- [x] 2.4 Replace `traceback.print_exc()` with `logging.exception()` in providers
- [x] 2.5 Replace `traceback.print_exc()` with `logging.exception()` in config.py

## 3. Testing

- [x] 3.1 Update `test_mcp_tools.py` to validate YAML output format
- [x] 3.2 Add tests for error console output (verify traceback is printed)
- [x] 3.3 Run full test suite

## 4. Documentation

- [ ] 4.1 Update README.md with YAML output examples
