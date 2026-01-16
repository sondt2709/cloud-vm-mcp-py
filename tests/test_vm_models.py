"""Tests for VM models."""

from vm_mcp.model.vm import ProviderInfo, VMDetails, VMInfo, VMState


class TestVMState:
    """Tests for VM state enum."""

    def test_state_values(self):
        """Test VM state values."""
        assert VMState.RUNNING.value == "running"
        assert VMState.STOPPED.value == "stopped"
        assert VMState.STARTING.value == "starting"
        assert VMState.STOPPING.value == "stopping"
        assert VMState.TERMINATED.value == "terminated"
        assert VMState.UNKNOWN.value == "unknown"


class TestVMInfo:
    """Tests for VM info model."""

    def test_create_vm_info(self):
        """Test creating VM info."""
        vm = VMInfo(
            id="aws:prod:us-east-1:i-1234567890abcdef0",
            name="web-server-01",
            provider="aws",
            tenant_alias="prod",
            region="us-east-1",
            state=VMState.RUNNING,
            instance_type="t3.micro",
        )

        assert vm.id == "aws:prod:us-east-1:i-1234567890abcdef0"
        assert vm.name == "web-server-01"
        assert vm.provider == "aws"
        assert vm.state == VMState.RUNNING


class TestVMDetails:
    """Tests for VM details model."""

    def test_create_vm_details(self):
        """Test creating VM details."""
        vm = VMDetails(
            id="aws:prod:us-east-1:i-1234567890abcdef0",
            name="web-server-01",
            provider="aws",
            tenant_alias="prod",
            region="us-east-1",
            state=VMState.RUNNING,
            instance_type="t3.micro",
            public_ip="54.123.45.67",
            private_ip="10.0.1.100",
            provider_metadata={"vpc_id": "vpc-123"},
        )

        assert vm.public_ip == "54.123.45.67"
        assert vm.private_ip == "10.0.1.100"
        assert vm.provider_metadata["vpc_id"] == "vpc-123"

    def test_optional_fields(self):
        """Test VM details with optional fields omitted."""
        vm = VMDetails(
            id="azure:corp:eastus:web-vm",
            name="web-vm",
            provider="azure",
            tenant_alias="corp",
            region="eastus",
            state=VMState.STOPPED,
            instance_type="Standard_B1s",
        )

        assert vm.public_ip is None
        assert vm.private_ip is None
        assert vm.provider_metadata == {}


class TestProviderInfo:
    """Tests for provider info model."""

    def test_create_provider_info(self):
        """Test creating provider info."""
        info = ProviderInfo(
            provider="aws",
            tenant_alias="production",
            regions=["us-east-1", "us-west-2"],
        )

        assert info.provider == "aws"
        assert info.tenant_alias == "production"
        assert len(info.regions) == 2
