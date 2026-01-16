"""Azure Compute provider implementation."""

import asyncio
import logging

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

from vm_mcp.model.credentials import AzureDirectory
from vm_mcp.model.vm import VMDetails, VMInfo, VMState
from vm_mcp.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Map Azure power states to normalized VMState
AZURE_STATE_MAP = {
    "PowerState/running": VMState.RUNNING,
    "PowerState/deallocated": VMState.STOPPED,
    "PowerState/stopped": VMState.STOPPED,
    "PowerState/starting": VMState.STARTING,
    "PowerState/stopping": VMState.STOPPING,
    "PowerState/deallocating": VMState.STOPPING,
}


class AzureProvider(BaseProvider):
    """Azure Compute provider for VM management."""

    def __init__(self, directory: AzureDirectory):
        self._directory = directory
        self._credential = ClientSecretCredential(
            tenant_id=directory.tenant_id,
            client_id=directory.client_id,
            client_secret=directory.client_secret,
        )
        self._compute_clients: dict[str, ComputeManagementClient] = {}
        self._network_clients: dict[str, NetworkManagementClient] = {}

    @property
    def provider_name(self) -> str:
        return "azure"

    @property
    def tenant_alias(self) -> str:
        return self._directory.alias

    def _get_compute_client(self, subscription_id: str) -> ComputeManagementClient:
        """Get or create Compute client for a subscription."""
        if subscription_id not in self._compute_clients:
            self._compute_clients[subscription_id] = ComputeManagementClient(
                credential=self._credential,
                subscription_id=subscription_id,
            )
        return self._compute_clients[subscription_id]

    def _get_network_client(self, subscription_id: str) -> NetworkManagementClient:
        """Get or create Network client for a subscription."""
        if subscription_id not in self._network_clients:
            self._network_clients[subscription_id] = NetworkManagementClient(
                credential=self._credential,
                subscription_id=subscription_id,
            )
        return self._network_clients[subscription_id]

    async def list_vms(self, region: str | None = None) -> list[VMInfo]:
        """List Azure VMs across all subscriptions, optionally filtered by region."""
        all_vms: list[VMInfo] = []

        for subscription_id in self._directory.subscription_ids:
            try:
                vms = await self._list_vms_in_subscription(subscription_id, region)
                all_vms.extend(vms)
            except Exception:
                logger.exception("Failed to list VMs in subscription %s", subscription_id)

        return all_vms

    async def _list_vms_in_subscription(
        self, subscription_id: str, region: str | None = None
    ) -> list[VMInfo]:
        """List VMs in a specific subscription."""
        client = self._get_compute_client(subscription_id)

        def _list():
            return list(client.virtual_machines.list_all())

        vms_list = await asyncio.to_thread(_list)
        
        # Filter by region if specified
        filtered_vms = [vm for vm in vms_list if not region or vm.location == region]
        
        if not filtered_vms:
            return []
        
        # Fetch all instance views in parallel for better performance
        async def fetch_instance_view(vm):
            """Fetch instance view for a single VM, returning (vm, state)."""
            state = VMState.UNKNOWN
            try:
                resource_group = vm.id.split("/")[4]
                instance_view = await self._get_instance_view(client, resource_group, vm.name)
                if instance_view and instance_view.statuses:
                    for status in instance_view.statuses:
                        if status.code and status.code.startswith("PowerState/"):
                            state = AZURE_STATE_MAP.get(status.code, VMState.UNKNOWN)
                            break
            except Exception:
                logger.exception("Failed to get instance view for VM %s", vm.name)
            return (vm, state)
        
        # Gather all instance views in parallel
        results = await asyncio.gather(
            *[fetch_instance_view(vm) for vm in filtered_vms],
            return_exceptions=True
        )
        
        vms = []
        for result in results:
            if isinstance(result, BaseException):
                logger.exception("Failed to process VM: %s", result)
                continue
            vm, state = result
            vms.append(
                VMInfo(
                    id=self.make_composite_id(vm.location, vm.name),
                    name=vm.name,
                    provider=self.provider_name,
                    tenant_alias=self.tenant_alias,
                    region=vm.location,
                    state=state,
                    instance_type=vm.hardware_profile.vm_size if vm.hardware_profile else "unknown",
                )
            )

        return vms

    async def _get_instance_view(self, client, resource_group: str, vm_name: str):
        """Get instance view for power state."""

        def _get():
            return client.virtual_machines.instance_view(resource_group, vm_name)

        return await asyncio.to_thread(_get)

    async def get_vm_details(self, vm_id: str) -> VMDetails | None:
        """Get detailed information about an Azure VM."""
        for subscription_id in self._directory.subscription_ids:
            try:
                details = await self._get_vm_details_in_subscription(
                    vm_id, subscription_id
                )
                if details:
                    return details
            except Exception:
                logger.exception("Failed to get VM details for %s in subscription %s", vm_id, subscription_id)

        return None

    async def _get_vm_details_in_subscription(
        self, vm_name: str, subscription_id: str
    ) -> VMDetails | None:
        """Get VM details in a specific subscription."""
        compute_client = self._get_compute_client(subscription_id)
        network_client = self._get_network_client(subscription_id)

        def _list():
            return list(compute_client.virtual_machines.list_all())

        vms_list = await asyncio.to_thread(_list)

        for vm in vms_list:
            if vm.name != vm_name:
                continue

            parts = vm.id.split("/")
            resource_group = parts[4] if len(parts) > 4 else ""

            # Get power state
            state = VMState.UNKNOWN
            try:
                instance_view = await self._get_instance_view(
                    compute_client, resource_group, vm.name
                )
                if instance_view and instance_view.statuses:
                    for status in instance_view.statuses:
                        if status.code and status.code.startswith("PowerState/"):
                            state = AZURE_STATE_MAP.get(status.code, VMState.UNKNOWN)
                            break
            except Exception:
                logger.exception("Failed to get instance view for VM %s", vm.name)

            # Get public IP
            public_ip = None
            private_ip = None
            try:
                if vm.network_profile and vm.network_profile.network_interfaces:
                    nic_id = vm.network_profile.network_interfaces[0].id
                    nic_parts = nic_id.split("/")
                    nic_rg = nic_parts[4]
                    nic_name = nic_parts[-1]

                    def _get_nic():
                        return network_client.network_interfaces.get(nic_rg, nic_name)

                    nic = await asyncio.to_thread(_get_nic)

                    if nic.ip_configurations:
                        ip_config = nic.ip_configurations[0]
                        private_ip = ip_config.private_ip_address

                        if ip_config.public_ip_address:
                            pip_id = ip_config.public_ip_address.id
                            pip_parts = pip_id.split("/")
                            pip_rg = pip_parts[4]
                            pip_name = pip_parts[-1]

                            def _get_pip():
                                return network_client.public_ip_addresses.get(
                                    pip_rg, pip_name
                                )

                            pip = await asyncio.to_thread(_get_pip)
                            public_ip = pip.ip_address
            except Exception:
                logger.exception("Failed to get network info for VM %s", vm.name)

            return VMDetails(
                id=self.make_composite_id(vm.location, vm.name),
                name=vm.name,
                provider=self.provider_name,
                tenant_alias=self.tenant_alias,
                region=vm.location,
                state=state,
                instance_type=vm.hardware_profile.vm_size if vm.hardware_profile else "unknown",
                public_ip=public_ip,
                private_ip=private_ip,
                provider_metadata={
                    "resource_group": resource_group,
                    "subscription_id": subscription_id,
                    "vm_id": vm.vm_id,
                    "os_type": vm.storage_profile.os_disk.os_type if vm.storage_profile and vm.storage_profile.os_disk else None,
                },
            )

        return None

    async def start_vm(self, vm_id: str) -> tuple[bool, str]:
        """Start an Azure VM."""
        for subscription_id in self._directory.subscription_ids:
            try:
                result = await self._start_vm_in_subscription(vm_id, subscription_id)
                if result[0]:
                    return result
            except Exception:
                logger.exception("Failed to start VM %s", vm_id)

        return (False, f"VM {vm_id} not found in any configured subscription")

    async def _start_vm_in_subscription(
        self, vm_name: str, subscription_id: str
    ) -> tuple[bool, str]:
        """Start a VM in a specific subscription."""
        client = self._get_compute_client(subscription_id)

        # Find the VM to get resource group
        def _list():
            return list(client.virtual_machines.list_all())

        vms_list = await asyncio.to_thread(_list)

        for vm in vms_list:
            if vm.name == vm_name:
                parts = vm.id.split("/")
                resource_group = parts[4] if len(parts) > 4 else ""

                def _start():
                    poller = client.virtual_machines.begin_start(
                        resource_group, vm_name
                    )
                    return poller

                await asyncio.to_thread(_start)
                return (True, f"VM {vm_name} is starting")

        return (False, f"VM {vm_name} not found")

    async def stop_vm(self, vm_id: str, force: bool = False) -> tuple[bool, str]:
        """Stop an Azure VM."""
        for subscription_id in self._directory.subscription_ids:
            try:
                result = await self._stop_vm_in_subscription(
                    vm_id, subscription_id, force
                )
                if result[0]:
                    return result
            except Exception:
                logger.exception("Failed to stop VM %s", vm_id)

        return (False, f"VM {vm_id} not found in any configured subscription")

    async def _stop_vm_in_subscription(
        self, vm_name: str, subscription_id: str, force: bool = False
    ) -> tuple[bool, str]:
        """Stop a VM in a specific subscription."""
        client = self._get_compute_client(subscription_id)

        # Find the VM to get resource group
        def _list():
            return list(client.virtual_machines.list_all())

        vms_list = await asyncio.to_thread(_list)

        for vm in vms_list:
            if vm.name == vm_name:
                parts = vm.id.split("/")
                resource_group = parts[4] if len(parts) > 4 else ""

                def _stop():
                    # Azure uses deallocate to stop and release resources
                    poller = client.virtual_machines.begin_deallocate(
                        resource_group, vm_name
                    )
                    return poller

                await asyncio.to_thread(_stop)
                return (True, f"VM {vm_name} is stopping (deallocating)")

        return (False, f"VM {vm_name} not found")
