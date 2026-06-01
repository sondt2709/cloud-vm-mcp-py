"""Tests for MCP tools."""

import pytest
import yaml

from vm_mcp.mcp import (
    get_vm_details,
    list_providers,
    list_vms,
    reboot_vm,
    start_vm,
    stop_vm,
)


class TestMCPTools:
    """Tests for MCP tool functions."""

    @pytest.mark.asyncio
    async def test_list_vms_no_providers(self, monkeypatch, noelicit_ctx):
        """Test list_vms with no providers configured."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        result = await list_vms(noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "PROVIDERS_CONFIG_PATH" in data["error"]

    @pytest.mark.asyncio
    async def test_list_providers_no_config(self, monkeypatch, noelicit_ctx):
        """Test list_providers with no config."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        result = await list_providers(noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No providers configured" in data["error"] or "PROVIDERS_CONFIG_PATH" in data["error"]

    @pytest.mark.asyncio
    async def test_get_vm_details_invalid_id(self, noelicit_ctx):
        """Test get_vm_details with invalid VM ID."""
        result = await get_vm_details("invalid-id", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_start_vm_invalid_id(self, noelicit_ctx):
        """Test start_vm with invalid VM ID."""
        result = await start_vm("invalid", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_stop_vm_invalid_id(self, noelicit_ctx):
        """Test stop_vm with invalid VM ID."""
        result = await stop_vm("bad-id", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_reboot_vm_invalid_id(self, noelicit_ctx):
        """Test reboot_vm with invalid VM ID."""
        result = await reboot_vm("bad-id", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "Invalid VM ID format" in data["error"]

    @pytest.mark.asyncio
    async def test_reboot_vm_no_provider(self, sample_providers_yaml, monkeypatch, noelicit_ctx):
        """Test reboot_vm with non-existent provider."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await reboot_vm("gcp:tenant:region:instance", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No provider found" in data["error"]

    @pytest.mark.asyncio
    async def test_reboot_vm_no_alibaba_provider(self, sample_providers_yaml, monkeypatch, noelicit_ctx):
        """Test reboot_vm with non-existent Alibaba provider."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await reboot_vm("alibaba:tenant:cn-hangzhou:i-bp123", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No provider found" in data["error"]

    @pytest.mark.asyncio
    async def test_list_vms_with_invalid_provider_filter(self, sample_providers_yaml, monkeypatch, noelicit_ctx):
        """Test list_vms with non-existent provider filter."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await list_vms(noelicit_ctx, provider="nonexistent")
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No providers found" in data["error"]

    @pytest.mark.asyncio
    async def test_get_vm_details_no_provider(self, sample_providers_yaml, monkeypatch, noelicit_ctx):
        """Test get_vm_details with non-existent provider."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        result = await get_vm_details("gcp:tenant:region:instance", noelicit_ctx)
        data = yaml.safe_load(result)
        assert data["status"] == "error"
        assert "No provider found" in data["error"]

    @pytest.mark.asyncio
    async def test_yaml_output_is_valid(self, monkeypatch, noelicit_ctx):
        """Test that all tools return valid YAML."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        # All results should be parseable YAML
        results = [
            await list_vms(noelicit_ctx),
            await list_providers(noelicit_ctx),
            await get_vm_details("aws:test:us-east-1:i-123", noelicit_ctx),
            await start_vm("aws:test:us-east-1:i-123", noelicit_ctx),
            await stop_vm("aws:test:us-east-1:i-123", noelicit_ctx),
            await reboot_vm("aws:test:us-east-1:i-123", noelicit_ctx),
        ]

        for result in results:
            data = yaml.safe_load(result)
            assert isinstance(data, dict)
            assert "status" in data
