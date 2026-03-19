"""Alibaba Cloud ECS provider implementation."""

import asyncio
import logging
from typing import Any

from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_tea_openapi import models as open_api_models

from vm_mcp.model.credentials import AlibabaAccount
from vm_mcp.model.vm import VMDetails, VMInfo, VMState
from vm_mcp.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Map Alibaba ECS instance states to normalized VMState
ALIBABA_STATE_MAP = {
    "Running": VMState.RUNNING,
    "Starting": VMState.STARTING,
    "Stopping": VMState.STOPPING,
    "Stopped": VMState.STOPPED,
    "Pending": VMState.STARTING,
    "Expired": VMState.TERMINATED,
}


class AlibabaProvider(BaseProvider):
    """Alibaba Cloud ECS provider for VM management."""

    def __init__(self, account: AlibabaAccount):
        self._account = account
        self._clients: dict[str, EcsClient] = {}

    @property
    def provider_name(self) -> str:
        return "alibaba"

    @property
    def tenant_alias(self) -> str:
        return self._account.alias

    def _get_client(self, region: str) -> EcsClient:
        """Get or create ECS client for a region."""
        if region not in self._clients:
            config = open_api_models.Config(
                access_key_id=self._account.access_key_id,
                access_key_secret=self._account.access_key_secret,
                region_id=region,
            )
            config.endpoint = f"ecs.{region}.aliyuncs.com"
            self._clients[region] = EcsClient(config)
        return self._clients[region]

    async def list_vms(self, region: str | None = None) -> list[VMInfo]:
        """List ECS instances, optionally filtered by region."""
        regions = [region] if region else self._account.regions
        all_vms: list[VMInfo] = []

        for reg in regions:
            try:
                vms = await self._list_vms_in_region(reg)
                all_vms.extend(vms)
            except Exception:
                logger.exception("Failed to list VMs in region %s", reg)

        return all_vms

    async def _list_vms_in_region(self, region: str) -> list[VMInfo]:
        """List ECS instances in a specific region."""
        client = self._get_client(region)

        def _describe() -> list[Any]:
            instances: list[Any] = []
            page_number = 1
            page_size = 100

            while True:
                request = ecs_models.DescribeInstancesRequest(
                    region_id=region,
                    page_number=page_number,
                    page_size=page_size,
                )
                response = client.describe_instances(request)
                body = response.body

                if body.instances and body.instances.instance:
                    instances.extend(body.instances.instance)

                total = body.total_count or 0
                if len(instances) >= total:
                    break
                page_number += 1

            return instances

        instances = await asyncio.to_thread(_describe)
        vms = []

        for instance in instances:
            instance_id = instance.instance_id or ""
            state = instance.status or "unknown"
            name = instance.instance_name or instance_id

            vms.append(
                VMInfo(
                    id=self.make_composite_id(region, instance_id),
                    name=name,
                    provider=self.provider_name,
                    tenant_alias=self.tenant_alias,
                    region=region,
                    state=ALIBABA_STATE_MAP.get(state, VMState.UNKNOWN),
                    instance_type=instance.instance_type or "unknown",
                )
            )

        return vms

    async def get_vm_details(self, vm_id: str) -> VMDetails | None:
        """Get detailed information about an ECS instance."""
        for region in self._account.regions:
            try:
                details = await self._get_vm_details_in_region(vm_id, region)
                if details:
                    return details
            except Exception:
                logger.exception("Failed to get VM details for %s in region %s", vm_id, region)

        return None

    async def _get_vm_details_in_region(
        self, instance_id: str, region: str
    ) -> VMDetails | None:
        """Get instance details in a specific region."""
        client = self._get_client(region)

        def _describe():
            try:
                request = ecs_models.DescribeInstanceAttributeRequest(
                    instance_id=instance_id,
                )
                response = client.describe_instance_attribute(request)
                return response.body
            except Exception as e:
                error_msg = str(e)
                if "InvalidInstanceId.NotFound" in error_msg:
                    return None
                raise

        body = await asyncio.to_thread(_describe)
        if not body:
            return None

        state = body.status or "unknown"

        # Extract public IPs
        public_ip = None
        if body.public_ip_address and body.public_ip_address.ip_address:
            ips = body.public_ip_address.ip_address
            if ips:
                public_ip = ips[0]

        # Extract private IPs
        private_ip = None
        if body.inner_ip_address and body.inner_ip_address.ip_address:
            ips = body.inner_ip_address.ip_address
            if ips:
                private_ip = ips[0]
        elif body.vpc_attributes and body.vpc_attributes.private_ip_address and body.vpc_attributes.private_ip_address.ip_address:
            ips = body.vpc_attributes.private_ip_address.ip_address
            if ips:
                private_ip = ips[0]

        return VMDetails(
            id=self.make_composite_id(region, instance_id),
            name=body.instance_name or instance_id,
            provider=self.provider_name,
            tenant_alias=self.tenant_alias,
            region=region,
            state=ALIBABA_STATE_MAP.get(state, VMState.UNKNOWN),
            instance_type=body.instance_type or "unknown",
            public_ip=public_ip,
            private_ip=private_ip,
            provider_metadata={
                "creation_time": body.creation_time or "",
                "vpc_id": body.vpc_attributes.vpc_id if body.vpc_attributes else None,
                "zone_id": body.zone_id,
                "os_type": body.ostype,
                "image_id": body.image_id,
            },
        )

    async def start_vm(self, vm_id: str) -> tuple[bool, str]:
        """Start an ECS instance."""
        for region in self._account.regions:
            try:
                result = await self._start_vm_in_region(vm_id, region)
                if result[0]:
                    return result
            except Exception as e:
                error_msg = str(e)
                if "InvalidInstanceId.NotFound" in error_msg:
                    continue
                logger.exception("Failed to start VM %s", vm_id)
                return (False, str(e))

        return (False, f"Instance {vm_id} not found in any configured region")

    async def _start_vm_in_region(
        self, instance_id: str, region: str
    ) -> tuple[bool, str]:
        """Start an instance in a specific region."""
        client = self._get_client(region)

        def _start():
            request = ecs_models.StartInstanceRequest(
                instance_id=instance_id,
            )
            client.start_instance(request)

        await asyncio.to_thread(_start)
        return (True, f"Instance {instance_id} is now starting")

    async def stop_vm(self, vm_id: str, force: bool = False) -> tuple[bool, str]:
        """Stop an ECS instance."""
        for region in self._account.regions:
            try:
                result = await self._stop_vm_in_region(vm_id, region, force)
                if result[0]:
                    return result
            except Exception as e:
                error_msg = str(e)
                if "InvalidInstanceId.NotFound" in error_msg:
                    continue
                logger.exception("Failed to stop VM %s", vm_id)
                return (False, str(e))

        return (False, f"Instance {vm_id} not found in any configured region")

    async def _stop_vm_in_region(
        self, instance_id: str, region: str, force: bool = False
    ) -> tuple[bool, str]:
        """Stop an instance in a specific region."""
        client = self._get_client(region)

        def _stop():
            request = ecs_models.StopInstanceRequest(
                instance_id=instance_id,
                force_stop=force,
            )
            client.stop_instance(request)

        await asyncio.to_thread(_stop)
        return (True, f"Instance {instance_id} is now stopping")

    async def reboot_vm(self, vm_id: str) -> tuple[bool, str]:
        """Reboot an ECS instance."""
        for region in self._account.regions:
            try:
                result = await self._reboot_vm_in_region(vm_id, region)
                if result[0]:
                    return result
            except Exception as e:
                error_msg = str(e)
                if "InvalidInstanceId.NotFound" in error_msg:
                    continue
                logger.exception("Failed to reboot VM %s", vm_id)
                return (False, str(e))

        return (False, f"Instance {vm_id} not found in any configured region")

    async def _reboot_vm_in_region(
        self, instance_id: str, region: str
    ) -> tuple[bool, str]:
        """Reboot an instance in a specific region."""
        client = self._get_client(region)

        def _reboot():
            request = ecs_models.RebootInstanceRequest(
                instance_id=instance_id,
            )
            client.reboot_instance(request)

        await asyncio.to_thread(_reboot)
        return (True, f"Instance {instance_id} is now rebooting")
