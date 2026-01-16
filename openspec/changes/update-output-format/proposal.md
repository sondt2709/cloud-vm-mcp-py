# Change: Update MCP Tool Output Format to YAML

## Why

Currently, MCP tools return human-readable formatted strings that are difficult to parse programmatically. AI assistants and MCP clients would benefit from structured YAML output that is both human-readable and machine-parseable. Additionally, errors are only returned via MCP responses, making debugging difficult for operators monitoring the server console.

## What Changes

- All MCP tool outputs changed from formatted text strings to YAML format
- Error logging via Python's `logging` module with `logging.exception()` for full tracebacks
- Replace all `traceback.print_exc()` and `print(..., file=sys.stderr)` with proper logging
- Consistent YAML structure across all tools with `status`, `data`, and optional `errors` fields

## Impact

- Affected specs: vm-listing, vm-details, vm-power-management, provider-credentials
- Affected code: `vm_mcp/mcp.py` (all tool functions)
- **BREAKING**: Output format changes from text to YAML
