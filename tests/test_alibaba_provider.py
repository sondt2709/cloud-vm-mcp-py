"""Tests for Alibaba Cloud ECS provider."""

from unittest.mock import MagicMock, patch

import pytest

from vm_mcp.model.credentials import AlibabaAccount
from vm_mcp.model.vm import VMState
from vm_mcp.providers.alibaba import ALIBABA_STATE_MAP, AlibabaProvider


class TestAlibabaStateMap:
    """Tests for Alibaba ECS state mapping."""

    def test_running_state(self):
        assert ALIBABA_STATE_MAP["Running"] == VMState.RUNNING

    def test_starting_state(self):
        assert ALIBABA_STATE_MAP["Starting"] == VMState.STARTING

    def test_stopping_state(self):
        assert ALIBABA_STATE_MAP["Stopping"] == VMState.STOPPING

    def test_stopped_state(self):
        assert ALIBABA_STATE_MAP["Stopped"] == VMState.STOPPED

    def test_pending_state(self):
        assert ALIBABA_STATE_MAP["Pending"] == VMState.STARTING

    def test_expired_state(self):
        assert ALIBABA_STATE_MAP["Expired"] == VMState.TERMINATED

    def test_unknown_state_fallback(self):
        assert ALIBABA_STATE_MAP.get("NonExistent", VMState.UNKNOWN) == VMState.UNKNOWN


class TestAlibabaProvider:
    """Tests for AlibabaProvider class."""

    @pytest.fixture
    def account(self):
        return AlibabaAccount(
            alias="test-alibaba",
            access_key_id="LTAI5tExampleKeyId",
            access_key_secret="ExampleAccessKeySecretValue123",
            regions=["cn-hangzhou", "ap-southeast-1"],
        )

    @pytest.fixture
    def provider(self, account):
        return AlibabaProvider(account)

    def test_provider_name(self, provider):
        assert provider.provider_name == "alibaba"

    def test_tenant_alias(self, provider):
        assert provider.tenant_alias == "test-alibaba"

    def test_composite_id_format(self, provider):
        composite_id = provider.make_composite_id("cn-hangzhou", "i-bp1234567890abcdef")
        assert composite_id == "alibaba:test-alibaba:cn-hangzhou:i-bp1234567890abcdef"

    @pytest.mark.asyncio
    async def test_list_vms_empty(self, provider):
        """Test list_vms with mocked empty response."""
        mock_response = MagicMock()
        mock_response.body.instances.instance = []
        mock_response.body.total_count = 0

        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.describe_instances.return_value = mock_response
            mock_get_client.return_value = mock_client

            vms = await provider.list_vms(region="cn-hangzhou")
            assert vms == []

    @pytest.mark.asyncio
    async def test_list_vms_with_instances(self, provider):
        """Test list_vms with mocked instances."""
        mock_instance = MagicMock()
        mock_instance.instance_id = "i-bp1234567890abcdef"
        mock_instance.instance_name = "test-vm"
        mock_instance.status = "Running"
        mock_instance.instance_type = "ecs.g6.large"

        mock_response = MagicMock()
        mock_response.body.instances.instance = [mock_instance]
        mock_response.body.total_count = 1

        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.describe_instances.return_value = mock_response
            mock_get_client.return_value = mock_client

            vms = await provider.list_vms(region="cn-hangzhou")
            assert len(vms) == 1
            assert vms[0].name == "test-vm"
            assert vms[0].state == VMState.RUNNING
            assert vms[0].id == "alibaba:test-alibaba:cn-hangzhou:i-bp1234567890abcdef"

    @pytest.mark.asyncio
    async def test_start_vm_not_found(self, provider):
        """Test start_vm when instance not found in any region."""
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.start_instance.side_effect = Exception("InvalidInstanceId.NotFound")
            mock_get_client.return_value = mock_client

            success, message = await provider.start_vm("i-nonexistent")
            assert not success
            assert "not found" in message

    @pytest.mark.asyncio
    async def test_stop_vm_not_found(self, provider):
        """Test stop_vm when instance not found in any region."""
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.stop_instance.side_effect = Exception("InvalidInstanceId.NotFound")
            mock_get_client.return_value = mock_client

            success, message = await provider.stop_vm("i-nonexistent")
            assert not success
            assert "not found" in message

    @pytest.mark.asyncio
    async def test_reboot_vm_not_found(self, provider):
        """Test reboot_vm when instance not found in any region."""
        with patch.object(provider, "_get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.reboot_instance.side_effect = Exception("InvalidInstanceId.NotFound")
            mock_get_client.return_value = mock_client

            success, message = await provider.reboot_vm("i-nonexistent")
            assert not success
            assert "not found" in message
