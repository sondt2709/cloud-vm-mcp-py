"""Tests for the confirmation gate (vm_mcp/confirmation.py)."""

import pytest

from tests.conftest import (
    make_accept_context,
    make_cancel_context,
    make_decline_context,
)
from vm_mcp.confirmation import Confirm, confirm, requires_confirmation


class TestConfirmSchema:
    """The Confirm model must satisfy the MCP elicitation schema constraints.

    Regression: a `Literal[...]` annotation is rejected by the SDK's
    `_validate_elicitation_schema`, which raised a TypeError at runtime and
    silently turned every confirmation into a decline. The annotation must be a
    primitive `str`, with the Yes/No constraint applied via the JSON Schema enum.
    """

    def test_schema_passes_sdk_validation(self):
        # Imported here so the test is self-contained / skips cleanly if the
        # SDK internal moves.
        from mcp.server.elicitation import _validate_elicitation_schema

        _validate_elicitation_schema(Confirm)  # must not raise

    def test_schema_exposes_yes_no_enum(self):
        prop = Confirm.model_json_schema()["properties"]["confirmation"]
        assert prop["type"] == "string"
        assert prop["enum"] == ["Yes", "No"]

    def test_schema_field_is_required(self):
        # The SDK only registers `accept` when the response carries non-empty
        # content, so the field must be required (an empty schema breaks accept).
        assert "confirmation" in Confirm.model_json_schema().get("required", [])


class TestRequiresConfirmation:
    """Tests for the configurable required-tool set."""

    def test_default_set(self):
        """With no env var, the destructive power tools require confirmation."""
        assert requires_confirmation("start_vm") is True
        assert requires_confirmation("stop_vm") is True
        assert requires_confirmation("reboot_vm") is True

    def test_read_only_tools_not_required(self):
        """Read-only tools never require confirmation by default."""
        assert requires_confirmation("list_vms") is False
        assert requires_confirmation("list_providers") is False
        assert requires_confirmation("get_vm_details") is False

    def test_override_set(self, monkeypatch):
        """An explicit list overrides the default set exactly."""
        monkeypatch.setenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", "stop_vm")
        assert requires_confirmation("stop_vm") is True
        assert requires_confirmation("start_vm") is False
        assert requires_confirmation("reboot_vm") is False

    def test_empty_disables_all(self, monkeypatch):
        """An empty value disables confirmation for all tools."""
        monkeypatch.setenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", "")
        assert requires_confirmation("start_vm") is False
        assert requires_confirmation("stop_vm") is False
        assert requires_confirmation("reboot_vm") is False

    def test_whitespace_is_trimmed(self, monkeypatch):
        """Tool names are trimmed and blanks ignored."""
        monkeypatch.setenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", " start_vm , , reboot_vm ")
        assert requires_confirmation("start_vm") is True
        assert requires_confirmation("reboot_vm") is True
        assert requires_confirmation("stop_vm") is False


class TestConfirm:
    """Tests for the confirm() gate behavior."""

    @pytest.mark.asyncio
    async def test_fail_open_when_unsupported(self, noelicit_ctx):
        """Client without elicitation capability proceeds without prompting."""
        assert await confirm(noelicit_ctx, "Proceed?") is True
        assert noelicit_ctx.elicit_calls == []

    @pytest.mark.asyncio
    async def test_accept_yes(self):
        """Accept + 'Yes' proceeds."""
        ctx = make_accept_context("Yes")
        assert await confirm(ctx, "Proceed?") is True
        assert ctx.elicit_calls == ["Proceed?"]

    @pytest.mark.asyncio
    async def test_accept_no(self):
        """Accept + 'No' does not proceed."""
        ctx = make_accept_context("No")
        assert await confirm(ctx, "Proceed?") is False

    @pytest.mark.asyncio
    async def test_decline(self):
        """Declining the prompt does not proceed."""
        ctx = make_decline_context()
        assert await confirm(ctx, "Proceed?") is False

    @pytest.mark.asyncio
    async def test_cancel(self):
        """Cancelling the prompt does not proceed."""
        ctx = make_cancel_context()
        assert await confirm(ctx, "Proceed?") is False
