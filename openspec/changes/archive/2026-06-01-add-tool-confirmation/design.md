## Context

`vm_mcp/mcp.py` registers tools as plain FastMCP `@mcp.tool()` async functions. State-changing tools (`start_vm`, `stop_vm`, `reboot_vm`) run their provider action immediately. The MCP spec (revision 2025-06-18) defines **elicitation**, a server-initiated request that asks the connected client to collect a response from the user mid-execution. The installed `mcp[cli]>=1.13.1` SDK exposes this via `Context.elicit(message, schema)`, returning `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation`.

Reference implementation studied: `mongodb-mcp-server` (`src/elicitation.ts`, `src/tools/tool.ts`). It wraps `server.elicitInput` in a small `Elicitation` class, gates execution on a configurable `confirmationRequiredTools` list, fails open when the client lacks the capability, and lets each tool override a `getConfirmationMessage(args)` for a content-aware prompt.

## Goals / Non-Goals

**Goals:**
- A single reusable confirmation gate, not per-tool inlined logic.
- Content-aware messages (name the VM id; surface `force`).
- Configurable required-tool set with default `{start_vm, stop_vm, reboot_vm}`.
- Fail-open when the client does not support elicitation.
- No new dependency; no behavior change for any tool by default.
- Gate applies uniformly to every tool so the config set alone decides what is guarded (lets read-only tools be gated for policy or safe testing).

**Non-Goals:**
- Replacing the host's own tool-permission prompt (Claude Code already gates all MCP calls; this is a complementary, content-aware second check).
- Collecting structured form input (only yes/no confirmation for now).
- Per-tool custom message overrides as a public extension API (messages are built inline per guarded tool; can generalize later).
- A fail-closed mode (explicitly deferred — see Open Questions).

## Decisions

### Decision 1: Use MCP elicitation via `ctx.elicit()`
Standard, transport-agnostic, already supported by the SDK and by Claude Code / MCP Inspector. **Alternative considered:** an extra `confirm: bool` tool argument — rejected as the *primary* mechanism because the model can fabricate `confirm=true` without a human ever seeing it, defeating the purpose. (May still be added later as a non-interactive escape hatch.)

### Decision 2: Centralized helper + config-driven gate, applied to every tool
Add a small helper (e.g. `vm_mcp/confirmation.py`) exposing `async def confirm(ctx, message) -> bool` plus a `requires_confirmation(tool_name)` check. **Every** tool takes a `ctx: Context` and calls the gate at the top, passing its own name — so whether a tool is guarded depends solely on the configured set, not on which tools have gate code. This lets read-only tools (e.g. `list_providers`) be gated via config for policy or to exercise the confirmation flow safely without mutating a VM. **Alternative considered:** a decorator wrapping each tool — rejected because FastMCP introspects the wrapped function's signature for the tool schema, and a naive decorator risks dropping or distorting `ctx`/arguments; an explicit call at the top of each tool is simpler and transparent.

### Decision 3: Capability detection + fail-open
Before eliciting, check whether the client advertises elicitation capability (mirrors mongodb's `supportsElicitation()`). If not supported, return `True` (proceed) so non-interactive clients keep working unchanged. **Alternative considered:** fail-closed — rejected as the default for compatibility; left as a future config toggle.

### Decision 4: Configurable required-tool set
Read `VM_MCP_CONFIRM_REQUIRED_TOOLS` (comma-separated) in `vm_mcp/config.py`, defaulting to `start_vm,stop_vm,reboot_vm`. Operators can shrink or extend the set without code changes — direct parallel to mongodb's `confirmationRequiredTools`.

### Decision 5: Decline/cancel returns a structured non-error result
On decline/cancel, the tool performs no provider call and returns YAML `status: cancelled` with an explanatory message. (mongodb returns `isError: true`; here a non-error `cancelled` status reads more naturally as "user chose not to proceed" and keeps the existing YAML contract.)

### Decision 6: Confirm schema uses a required `str` + enum field
Two Python-SDK constraints shape the schema, both discovered during live testing:
1. `_validate_elicitation_schema` only accepts primitive annotations
   (`str`/`int`/`float`/`bool` or Optional/Union of these). A
   `Literal["Yes", "No"]` field raises `TypeError` at call time, which the gate
   catches and turns into a (safe) decline — silently breaking *all*
   confirmations. So the Yes/No constraint is applied via
   `Field(json_schema_extra={"enum": ["Yes", "No"]})` on a plain `str`.
2. `elicit_with_validation` only returns `AcceptedElicitation` when the response
   has **non-empty content** (`if result.action == "accept" and result.content`);
   an `accept` with empty content falls through and raises. So an empty schema
   (pure Accept/Decline, no fields) does **not** work — at least one required
   field is necessary for the client to return content on accept. This means the
   client renders a "Confirm the action? [Yes/No]" field in addition to its
   Accept/Decline affordance; the duplication is inherent to this SDK version.

The gate proceeds only on `action == "accept"` *and* `confirmation == "Yes"`.
Regression tests assert the model passes `_validate_elicitation_schema`, exposes
the enum, and keeps the field required — gate unit tests that mock `ctx.elicit`
do not exercise real schema validation or the content constraint.

## Risks / Trade-offs

- **Fail-open means no guard for non-interactive agents** → Accepted deliberately for compatibility; documented, and a future fail-closed toggle / `confirm` arg can mitigate when needed.
- **`ctx` parameter changes tool signatures** → FastMCP injects `Context` by type annotation and excludes it from the tool's input schema, so the public tool API is unchanged; covered by tests.
- **5-minute elicitation timeout (SDK default) could hang an automated caller** → Timeout surfaces as a non-accept result → treated as "not confirmed" → returns `cancelled`, no mutation.
- **Message must not leak sensitive data** → messages include only the VM composite id and flags the user already supplied; no credentials.

## Migration Plan

Additive and backward-compatible. No data migration. Rollback = revert the change; with no env var set, default guarded set applies; in elicitation-incapable clients behavior is identical to today (fail-open).

## Open Questions

- Should a future `confirm: bool` argument be offered as an explicit non-interactive override? (Out of scope here.)
- Should fail-closed become an opt-in config mode for high-security deployments? (Deferred.)
