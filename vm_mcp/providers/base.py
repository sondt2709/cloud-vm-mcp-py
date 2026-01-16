"""Abstract base class for cloud providers."""

from abc import ABC, abstractmethod

from vm_mcp.model.vm import VMDetails, VMInfo


class BaseProvider(ABC):
    """Abstract base class for cloud VM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'aws', 'azure')."""
        ...

    @property
    @abstractmethod
    def tenant_alias(self) -> str:
        """Return the tenant alias (account/directory name)."""
        ...

    @abstractmethod
    async def list_vms(self, region: str | None = None) -> list[VMInfo]:
        """List all VMs, optionally filtered by region.

        Args:
            region: Optional region filter

        Returns:
            List of VMInfo objects
        """
        ...

    @abstractmethod
    async def get_vm_details(self, vm_id: str) -> VMDetails | None:
        """Get detailed information about a specific VM.

        Args:
            vm_id: The instance ID (not composite ID)

        Returns:
            VMDetails or None if not found
        """
        ...

    @abstractmethod
    async def start_vm(self, vm_id: str) -> tuple[bool, str]:
        """Start a VM.

        Args:
            vm_id: The instance ID (not composite ID)

        Returns:
            Tuple of (success, message)
        """
        ...

    @abstractmethod
    async def stop_vm(self, vm_id: str, force: bool = False) -> tuple[bool, str]:
        """Stop a VM.

        Args:
            vm_id: The instance ID (not composite ID)
            force: Force stop without graceful shutdown

        Returns:
            Tuple of (success, message)
        """
        ...

    def make_composite_id(self, region: str, instance_id: str) -> str:
        """Create a composite VM ID.

        Format: {provider}:{tenant_alias}:{region}:{instance_id}
        """
        return f"{self.provider_name}:{self.tenant_alias}:{region}:{instance_id}"

    @staticmethod
    def parse_composite_id(composite_id: str) -> tuple[str, str, str, str] | None:
        """Parse a composite VM ID.

        Args:
            composite_id: The composite ID to parse

        Returns:
            Tuple of (provider, tenant_alias, region, instance_id) or None if invalid
        """
        parts = composite_id.split(":")
        if len(parts) != 4:
            return None
        return (parts[0], parts[1], parts[2], parts[3])
