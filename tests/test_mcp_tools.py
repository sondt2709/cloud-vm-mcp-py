"""Tests for MCP tools."""

import pytest
import yaml

from vm_mcp.mcp import (
    get_vm_details,
    list_providers,
    list_vms,
    start_vm,
    stop_vm,
)


class TestMCPTools:
    """Tests for MCP tool functions."""

    @pytest.mark.asyncio
    async def test_list_vms_no_providers(self, monkeypatch):
        """Test list_vms with no providers configured."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        result = await list_vms()
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "PROVIDERS_CONFIG_PATH" in data["error"]

    @pytest.mark.asyncio
    async def test_list_providers_no_config(self, monkeypatch):
        """Test list_providers with no config."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        result = await list_providers()
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No providers configured" in data["error"] or "PROVIDERS_CONFIG_PATH" in data["error"]

    @pytest.mark.asyncio
    async def test_get_vm_details_invalid_id(self):
        """Test get_vm_details with invalid VM ID."""
        result = await get_vm_details("invalid-id")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_start_vm_invalid_id(self):
        """Test start_vm with invalid VM ID."""
        result = await start_vm("invalid")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_stop_vm_invalid_id(self):
        """Test stop_vm with invalid VM ID."""
        result = await stop_vm("bad-id")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_list_vms_with_invalid_provider_filter(self, sample_providers_yaml, monkeypatch):
        """Test list_vms with non-existent provider filter."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await list_vms(provider="nonexistent")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No providers found" in data["error"]

    @pytest.mark.asyncio
    async def test_get_vm_details_no_provider(self, sample_providers_yaml, monkeypatch):
        """Test get_vm_details with non-existent provider."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await get_vm_details("gcp:tenant:region:instance")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No provider found" in data["error"]

    @pytest.mark.asyncio
    async def test_yaml_output_is_valid(self, monkeypatch):
        """Test that all tools return valid YAML."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        # All results should be parseable YAML
        results = [
            await list_vms(),
            await list_providers(),
            await get_vm_details("aws:test:us-east-1:i-123"),
            await start_vm("aws:test:us-east-1:i-123"),
            await stop_vm("aws:test:us-east-1:i-123"),
        ]

        for result in results:
            data = yaml.safe_load(result)
            assert isinstance(data, dict)
            assert "status" in data
