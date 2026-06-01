## 1. Configuration

- [x] 1.1 Add `VM_MCP_CONFIRM_REQUIRED_TOOLS` parsing to `vm_mcp/config.py` (comma-separated, default `start_vm,stop_vm,reboot_vm`, empty value = no tools)
- [x] 1.2 Expose the parsed set via the config object and document the variable in `.env.example` and `README.md`

## 2. Confirmation Gate Helper

- [x] 2.1 Create `vm_mcp/confirmation.py` with a `Confirm` pydantic model (single required `confirmation: str` field carrying a Yes/No JSON-Schema enum — not `Literal`, which the SDK rejects)
- [x] 2.2 Implement `supports_elicitation(ctx)` that checks the client's advertised elicitation capability
- [x] 2.3 Implement `async confirm(ctx, message) -> bool`: fail-open (return True) when unsupported; otherwise call `ctx.elicit(message, Confirm)` and return True only on accept + "Yes"; return False on decline/cancel/timeout
- [x] 2.4 Implement `requires_confirmation(tool_name)` reading the configured set

## 3. Wire Tools

- [x] 3.1 Add `ctx: Context` parameter to every tool in `vm_mcp/mcp.py` (power tools `start_vm`/`stop_vm`/`reboot_vm` and read-only `list_vms`/`list_providers`/`get_vm_details`)
- [x] 3.2 At the top of each tool, if `requires_confirmation(<name>)`, build a content-aware message (include `vm_id`; for `stop_vm` highlight `force`) and call `confirm(...)`
- [x] 3.3 On non-confirmation, return YAML `status: "cancelled"` with an explanatory message and perform no provider call
- [x] 3.4 Ensure the elicitation wait is excluded from / does not trip the existing `PER_REQUEST_TIMEOUT` provider timeout

## 4. Tests

- [x] 4.1 Unit tests for `confirm()`: accept→True, decline→False, cancel→False, unsupported client→True (fail-open)
- [x] 4.2 Unit tests for `requires_confirmation()`: default set, custom override, empty disables all
- [x] 4.3 Integration tests for `start_vm`/`stop_vm`/`reboot_vm`: confirmed path mutates, declined path returns `cancelled` and does not call the provider
- [x] 4.4 Test that `stop_vm(force=true)` confirmation message highlights the forced stop
- [x] 4.5 Test read-only tool gating: not gated by default; when added to the config set, prompts and declines block the result (and accept lets it run)

## 5. Verify

- [x] 5.1 Run `uv run ty check` and `uv run ruff check` clean
- [x] 5.2 Run `uv run pytest` — all tests pass
- [x] 5.3 Manual smoke test in an elicitation-capable client (e.g. MCP Inspector / Claude Code): confirm and decline a `stop_vm`
- [x] 5.4 Run `openspec validate add-tool-confirmation --strict`
