## Why

State-changing VM tools (`start_vm`, `stop_vm`, `reboot_vm`) currently execute immediately with no human checkpoint, so a single misdirected agent call can power-cycle a production VM with no chance to intervene. The MCP protocol's standard **elicitation** primitive lets a server pause mid-execution and ask the connected client to confirm — and the Python SDK already shipped in this project supports it. We can add a content-aware confirmation gate with no new dependency.

## What Changes

- Add a reusable confirmation gate that calls `ctx.elicit()` before a guarded tool performs its action, showing a per-tool message that names the specific VM and any risky flags (e.g. `force`).
- Apply the gate uniformly to **all** tools, each governed by the configurable set. By default only `start_vm`, `stop_vm`, and `reboot_vm` are guarded; read-only tools (`list_vms`, `list_providers`, `get_vm_details`) are not guarded by default but **can** be added to the set (useful for policy or for safely exercising the confirmation flow without mutating a VM).
- Make the guarded set **configurable** (env var, with a sensible default) so operators can add or remove tools without code changes — mirroring mongodb-mcp-server's `confirmationRequiredTools`.
- **Fail-open** when the client does not advertise elicitation capability: the tool runs as it does today, preserving compatibility with non-interactive clients.
- On an explicit decline/cancel, the tool performs no action and returns a `cancelled` YAML status instead of mutating the VM.

## Capabilities

### New Capabilities
- `tool-confirmation`: A cross-cutting confirmation gate using MCP elicitation — capability detection, configurable required-tool set, fail-open behavior, and per-tool confirmation messaging.

### Modified Capabilities
- `vm-power-management`: `start_vm`, `stop_vm`, and `reboot_vm` gain a requirement to request user confirmation (when the tool is in the configured set and the client supports elicitation) before performing the action.

## Impact

- **Code**: `vm_mcp/mcp.py` (add `ctx: Context` parameter and gate call to every tool), a new confirmation helper module, and `vm_mcp/config.py` (read the configurable required-tool set).
- **Config**: new optional environment variable (e.g. `VM_MCP_CONFIRM_REQUIRED_TOOLS`) with default `start_vm,stop_vm,reboot_vm`.
- **Dependencies**: none — uses `mcp[cli]>=1.13.1` already present.
- **Clients**: confirmation prompts appear only in elicitation-capable clients (Claude Code, MCP Inspector, etc.); others are unaffected (fail-open).
- **Tests**: new unit tests for the gate (supported/declined/cancelled/unsupported) and updated power-management tests.
