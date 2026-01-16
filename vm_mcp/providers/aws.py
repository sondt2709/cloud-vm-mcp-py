"""AWS EC2 provider implementation."""

import asyncio
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from vm_mcp.model.credentials import AWSAccount
from vm_mcp.model.vm import VMDetails, VMInfo, VMState
from vm_mcp.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Map AWS instance states to normalized VMState
AWS_STATE_MAP = {
    "pending": VMState.STARTING,
    "running": VMState.RUNNING,
    "shutting-down": VMState.STOPPING,
    "terminated": VMState.TERMINATED,
    "stopping": VMState.STOPPING,
    "stopped": VMState.STOPPED,
}


class AWSProvider(BaseProvider):
    """AWS EC2 provider for VM management."""

    def __init__(self, account: AWSAccount):
        self._account = account
        self._clients: dict[str, Any] = {}

    @property
    def provider_name(self) -> str:
        return "aws"

    @property
    def tenant_alias(self) -> str:
        return self._account.alias

    def _get_client(self, region: str):
        """Get or create EC2 client for a region."""
        if region not in self._clients:
            self._clients[region] = boto3.client(
                "ec2",
                region_name=region,
                aws_access_key_id=self._account.access_key_id,
                aws_secret_access_key=self._account.secret_access_key,
            )
        return self._clients[region]

    async def list_vms(self, region: str | None = None) -> list[VMInfo]:
        """List EC2 instances, optionally filtered by region."""
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
        """List EC2 instances in a specific region."""
        client = self._get_client(region)

        def _describe():
            paginator = client.get_paginator("describe_instances")
            instances = []
            for page in paginator.paginate():
                for reservation in page.get("Reservations", []):
                    instances.extend(reservation.get("Instances", []))
            return instances

        instances = await asyncio.to_thread(_describe)
        vms = []

        for instance in instances:
            instance_id = instance.get("InstanceId", "")
            state_name = instance.get("State", {}).get("Name", "unknown")

            # Get instance name from tags
            name = instance_id
            for tag in instance.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", instance_id)
                    break

            vms.append(
                VMInfo(
                    id=self.make_composite_id(region, instance_id),
                    name=name,
                    provider=self.provider_name,
                    tenant_alias=self.tenant_alias,
                    region=region,
                    state=AWS_STATE_MAP.get(state_name, VMState.UNKNOWN),
                    instance_type=instance.get("InstanceType", "unknown"),
                )
            )

        return vms

    async def get_vm_details(self, vm_id: str) -> VMDetails | None:
        """Get detailed information about an EC2 instance."""
        # Find which region this instance is in
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
                response = client.describe_instances(InstanceIds=[instance_id])
                reservations = response.get("Reservations", [])
                if reservations:
                    instances = reservations[0].get("Instances", [])
                    if instances:
                        return instances[0]
            except ClientError as e:
                if e.response["Error"]["Code"] != "InvalidInstanceID.NotFound":
                    raise
            return None

        instance = await asyncio.to_thread(_describe)
        if not instance:
            return None

        state_name = instance.get("State", {}).get("Name", "unknown")

        # Get instance name from tags
        name = instance_id
        for tag in instance.get("Tags", []):
            if tag.get("Key") == "Name":
                name = tag.get("Value", instance_id)
                break

        return VMDetails(
            id=self.make_composite_id(region, instance_id),
            name=name,
            provider=self.provider_name,
            tenant_alias=self.tenant_alias,
            region=region,
            state=AWS_STATE_MAP.get(state_name, VMState.UNKNOWN),
            instance_type=instance.get("InstanceType", "unknown"),
            public_ip=instance.get("PublicIpAddress"),
            private_ip=instance.get("PrivateIpAddress"),
            provider_metadata={
                "launch_time": str(instance.get("LaunchTime", "")),
                "vpc_id": instance.get("VpcId"),
                "subnet_id": instance.get("SubnetId"),
                "architecture": instance.get("Architecture"),
                "platform": instance.get("Platform", "linux"),
            },
        )

    async def start_vm(self, vm_id: str) -> tuple[bool, str]:
        """Start an EC2 instance."""
        for region in self._account.regions:
            try:
                result = await self._start_vm_in_region(vm_id, region)
                if result[0]:
                    return result
            except ClientError as e:
                if e.response["Error"]["Code"] != "InvalidInstanceID.NotFound":
                    logger.exception("Failed to start VM %s", vm_id)
                    return (False, str(e))
            except Exception:
                logger.exception("Failed to start VM %s", vm_id)

        return (False, f"Instance {vm_id} not found in any configured region")

    async def _start_vm_in_region(
        self, instance_id: str, region: str
    ) -> tuple[bool, str]:
        """Start an instance in a specific region."""
        client = self._get_client(region)

        def _start():
            response = client.start_instances(InstanceIds=[instance_id])
            current_state = (
                response.get("StartingInstances", [{}])[0]
                .get("CurrentState", {})
                .get("Name", "unknown")
            )
            return current_state

        state = await asyncio.to_thread(_start)
        return (True, f"Instance {instance_id} is now {state}")

    async def stop_vm(self, vm_id: str, force: bool = False) -> tuple[bool, str]:
        """Stop an EC2 instance."""
        for region in self._account.regions:
            try:
                result = await self._stop_vm_in_region(vm_id, region, force)
                if result[0]:
                    return result
            except ClientError as e:
                if e.response["Error"]["Code"] != "InvalidInstanceID.NotFound":
                    logger.exception("Failed to stop VM %s", vm_id)
                    return (False, str(e))
            except Exception:
                logger.exception("Failed to stop VM %s", vm_id)

        return (False, f"Instance {vm_id} not found in any configured region")

    async def _stop_vm_in_region(
        self, instance_id: str, region: str, force: bool = False
    ) -> tuple[bool, str]:
        """Stop an instance in a specific region."""
        client = self._get_client(region)

        def _stop():
            response = client.stop_instances(InstanceIds=[instance_id], Force=force)
            current_state = (
                response.get("StoppingInstances", [{}])[0]
                .get("CurrentState", {})
                .get("Name", "unknown")
            )
            return current_state

        state = await asyncio.to_thread(_stop)
        return (True, f"Instance {instance_id} is now {state}")
