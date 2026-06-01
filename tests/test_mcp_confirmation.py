"""Integration tests: confirmation gate wired into the power tools."""

import sys
from unittest.mock import AsyncMock

import pytest
import yaml

from tests.conftest import make_accept_context, make_decline_context
from vm_mcp.mcp import (
    list_providers,
    reboot_vm,
    start_vm,
    stop_vm,
)

# vm_mcp/__init__.py rebinds the name `mcp` to the FastMCP instance, shadowing
# the submodule, so fetch the real module object from sys.modules.
mcp_module = sys.modules["vm_mcp.mcp"]

VALID_ID = "aws:test:us-east-1:i-123"


@pytest.fixture
def mock_provider(monkeypatch):
    """Patch provider lookup to return a mock that succeeds for all actions."""
    provider = AsyncMock()
    provider.start_vm = AsyncMock(return_value=(True, "started"))
    provider.stop_vm = AsyncMock(return_value=(True, "stopped"))
    provider.reboot_vm = AsyncMock(return_value=(True, "rebooting"))
    monkeypatch.setattr(
        mcp_module, "get_provider_by_composite_id", lambda vm_id: provider
    )
    return provider


class TestConfirmedPath:
    """When the user accepts, the provider action runs."""

    @pytest.mark.asyncio
    async def test_start_vm_confirmed_runs(self, mock_provider):
        result = await start_vm(VALID_ID, make_accept_context())
        data = yaml.safe_load(result)
        assert data["status"] == "success"
        mock_provider.start_vm.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stop_vm_confirmed_runs(self, mock_provider):
        result = await stop_vm(VALID_ID, make_accept_context())
        data = yaml.safe_load(result)
        assert data["status"] == "success"
        mock_provider.stop_vm.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_reboot_vm_confirmed_runs(self, mock_provider):
        result = await reboot_vm(VALID_ID, make_accept_context())
        data = yaml.safe_load(result)
        assert data["status"] == "success"
        mock_provider.reboot_vm.assert_awaited_once()


class TestDeclinedPath:
    """When the user declines, the provider action does NOT run."""

    @pytest.mark.asyncio
    async def test_start_vm_declined_no_action(self, mock_provider):
        result = await start_vm(VALID_ID, make_decline_context())
        data = yaml.safe_load(result)
        assert data["status"] == "cancelled"
        mock_provider.start_vm.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_stop_vm_declined_no_action(self, mock_provider):
        result = await stop_vm(VALID_ID, make_decline_context())
        data = yaml.safe_load(result)
        assert data["status"] == "cancelled"
        mock_provider.stop_vm.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_reboot_vm_declined_no_action(self, mock_provider):
        result = await reboot_vm(VALID_ID, make_decline_context())
        data = yaml.safe_load(result)
        assert data["status"] == "cancelled"
        mock_provider.reboot_vm.assert_not_awaited()


class TestForceMessage:
    """stop_vm(force=True) confirmation message highlights the forced stop."""

    @pytest.mark.asyncio
    async def test_force_message_mentions_force(self, mock_provider):
        ctx = make_accept_context()
        await stop_vm(VALID_ID, ctx, force=True)
        assert len(ctx.elicit_calls) == 1
        assert "FORCED" in ctx.elicit_calls[0]

    @pytest.mark.asyncio
    async def test_graceful_message_omits_force(self, mock_provider):
        ctx = make_accept_context()
        await stop_vm(VALID_ID, ctx, force=False)
        assert "FORCED" not in ctx.elicit_calls[0]

    @pytest.mark.asyncio
    async def test_message_names_vm(self, mock_provider):
        ctx = make_accept_context()
        await start_vm(VALID_ID, ctx)
        assert VALID_ID in ctx.elicit_calls[0]


class TestReadOnlyToolsGating:
    """Read-only tools are not gated by default, but are gateable via config."""

    @pytest.mark.asyncio
    async def test_not_gated_by_default(self):
        # Default set excludes read-only tools: accept_ctx, but no prompt fires.
        ctx = make_accept_context()
        await list_providers(ctx)
        assert ctx.elicit_calls == []

    @pytest.mark.asyncio
    async def test_gateable_via_config_declined(self, monkeypatch):
        # When configured, a read-only tool prompts; declining blocks it.
        monkeypatch.setenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", "list_providers")
        result = await list_providers(make_decline_context())
        data = yaml.safe_load(result)
        assert data["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_gateable_via_config_accepted(self, monkeypatch):
        # When configured and accepted, the read-only tool runs normally.
        monkeypatch.setenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", "list_providers")
        ctx = make_accept_context()
        result = await list_providers(ctx)
        data = yaml.safe_load(result)
        assert ctx.elicit_calls  # prompt was shown
        assert data["status"] in ("success", "error")  # ran (result depends on config presence)
