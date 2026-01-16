"""Cloud VM MCP server for managing VMs across cloud providers."""

import asyncio
import logging

import yaml
from mcp.server.fastmcp import FastMCP

from vm_mcp.config import get_config
from vm_mcp.model.credentials import AWSConfig, AzureConfig
from vm_mcp.model.vm import ProviderError, ProviderInfo, VMInfo
from vm_mcp.providers import get_provider_by_composite_id, get_providers
from vm_mcp.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Timeout settings (in seconds)
PER_REQUEST_TIMEOUT = 60
TOTAL_QUERY_TIMEOUT = 180

mcp = FastMCP(
    name="vm-mcp",
    instructions="A Model Context Protocol for managing and viewing virtual machines across multiple cloud providers (AWS, Azure)",
)


async def _query_provider_with_timeout(
    provider: BaseProvider,
    region: str | None,
) -> tuple[list[VMInfo], ProviderError | None]:
    """Query a provider with timeout, returning VMs and optional error."""
    try:
        vms = await asyncio.wait_for(
            provider.list_vms(region=region),
            timeout=PER_REQUEST_TIMEOUT,
        )
        return (vms, None)
    except asyncio.TimeoutError:
        logger.exception(
            "Provider %s:%s timed out after %ss",
            provider.provider_name,
            provider.tenant_alias,
            PER_REQUEST_TIMEOUT,
        )
        return (
            [],
            ProviderError(
                provider=provider.provider_name,
                tenant_alias=provider.tenant_alias,
                error=f"Request timed out after {PER_REQUEST_TIMEOUT}s",
            ),
        )
    except Exception as e:
        logger.exception(
            "Provider %s:%s failed",
            provider.provider_name,
            provider.tenant_alias,
        )
        return (
            [],
            ProviderError(
                provider=provider.provider_name,
                tenant_alias=provider.tenant_alias,
                error=str(e),
            ),
        )


@mcp.tool()
async def list_vms(
    provider: str | None = None,
    tenant: str | None = None,
    region: str | None = None,
) -> str:
    """List all virtual machines across configured cloud providers.

    Args:
        provider: Optional filter by provider ('aws' or 'azure')
        tenant: Optional filter by tenant alias (AWS account alias or Azure directory alias)
        region: Optional filter by cloud region (e.g., 'us-east-1', 'eastus')

    Returns:
        YAML formatted string containing VM list or error information
    """
    try:
        providers = get_providers(provider=provider, tenant=tenant)

        if not providers:
            if provider or tenant:
                return yaml.dump({
                    "status": "error",
                    "error": f"No providers found matching filters: provider={provider}, tenant={tenant}",
                }, default_flow_style=False)
            return yaml.dump({
                "status": "error",
                "error": "No providers configured. Set PROVIDERS_CONFIG_PATH environment variable.",
            }, default_flow_style=False)

        # Query all providers with total timeout
        tasks = [_query_provider_with_timeout(p, region) for p in providers]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=TOTAL_QUERY_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.exception("Total query timeout exceeded (%ss)", TOTAL_QUERY_TIMEOUT)
            return yaml.dump({
                "status": "error",
                "error": f"Total query timeout exceeded ({TOTAL_QUERY_TIMEOUT}s)",
            }, default_flow_style=False)

        all_vms: list[VMInfo] = []
        errors: list[ProviderError] = []

        for result in results:
            if isinstance(result, Exception):
                logger.exception("Unexpected exception in provider query")
                continue
            vms, error = result
            all_vms.extend(vms)
            if error:
                errors.append(error)

        # Build YAML output
        vms_data = [
            {
                "id": vm.id,
                "name": vm.name,
                "provider": vm.provider,
                "tenant_alias": vm.tenant_alias,
                "region": vm.region,
                "instance_type": vm.instance_type,
                "state": vm.state.value,
            }
            for vm in sorted(all_vms, key=lambda v: (v.provider, v.tenant_alias, v.name))
        ]

        errors_data = [
            {
                "provider": err.provider,
                "tenant_alias": err.tenant_alias,
                "error": err.error,
            }
            for err in errors
        ]

        if errors and all_vms:
            status = "partial"
        elif errors:
            status = "error"
        else:
            status = "success"

        output = {
            "status": status,
            "count": len(all_vms),
            "vms": vms_data,
        }

        if not all_vms and not errors:
            output["message"] = "No VMs found in any configured provider."

        if errors:
            output["errors"] = errors_data

        return yaml.dump(output, default_flow_style=False)

    except Exception as e:
        logger.exception("Failed to list VMs")
        return yaml.dump({
            "status": "error",
            "error": f"Failed to list VMs: {str(e)}",
        }, default_flow_style=False)


@mcp.tool()
async def list_providers() -> str:
    """List all configured cloud providers and their accounts/directories.

    Returns:
        YAML formatted string containing provider information
    """
    try:
        config = get_config()
        providers_info: list[ProviderInfo] = []

        # AWS accounts
        aws_config = config.providers.get("aws")
        if isinstance(aws_config, AWSConfig):
            for account in aws_config.accounts:
                providers_info.append(
                    ProviderInfo(
                        provider="aws",
                        tenant_alias=account.alias,
                        regions=account.regions,
                    )
                )

        # Azure directories
        azure_config = config.providers.get("azure")
        if isinstance(azure_config, AzureConfig):
            for directory in azure_config.directories:
                providers_info.append(
                    ProviderInfo(
                        provider="azure",
                        tenant_alias=directory.alias,
                        regions=directory.subscription_ids,  # subscriptions as "regions"
                    )
                )

        if not providers_info:
            return yaml.dump({
                "status": "error",
                "error": "No providers configured. Set PROVIDERS_CONFIG_PATH environment variable.",
            }, default_flow_style=False)

        providers_data = [
            {
                "provider": info.provider,
                "tenant_alias": info.tenant_alias,
                "regions": info.regions,
            }
            for info in providers_info
        ]

        return yaml.dump({
            "status": "success",
            "count": len(providers_info),
            "providers": providers_data,
        }, default_flow_style=False)

    except Exception as e:
        logger.exception("Failed to list providers")
        return yaml.dump({
            "status": "error",
            "error": f"Failed to list providers: {str(e)}",
        }, default_flow_style=False)


@mcp.tool()
async def get_vm_details(vm_id: str) -> str:
    """Get detailed information about a specific virtual machine.

    Args:
        vm_id: The composite VM ID (format: provider:tenant:region:instance_id)

    Returns:
        YAML formatted string containing VM details or error information
    """
    try:
        parsed = BaseProvider.parse_composite_id(vm_id)
        if not parsed:
            return yaml.dump({
                "status": "error",
                "error": "Invalid VM ID format. Expected: provider:tenant:region:instance_id",
            }, default_flow_style=False)

        provider_name, tenant_alias, region, instance_id = parsed

        provider = get_provider_by_composite_id(vm_id)
        if not provider:
            return yaml.dump({
                "status": "error",
                "error": f"No provider found for {provider_name}:{tenant_alias}",
            }, default_flow_style=False)

        try:
            details = await asyncio.wait_for(
                provider.get_vm_details(instance_id),
                timeout=PER_REQUEST_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.exception("get_vm_details for %s timed out after %ss", vm_id, PER_REQUEST_TIMEOUT)
            return yaml.dump({
                "status": "error",
                "error": f"Request timed out after {PER_REQUEST_TIMEOUT}s",
            }, default_flow_style=False)

        if not details:
            return yaml.dump({
                "status": "error",
                "error": f"VM '{vm_id}' not found",
            }, default_flow_style=False)

        vm_data = {
            "id": details.id,
            "name": details.name,
            "provider": details.provider,
            "tenant_alias": details.tenant_alias,
            "region": details.region,
            "state": details.state.value,
            "instance_type": details.instance_type,
            "public_ip": details.public_ip,
            "private_ip": details.private_ip,
            "provider_metadata": details.provider_metadata,
        }

        return yaml.dump({
            "status": "success",
            "vm": vm_data,
        }, default_flow_style=False)

    except Exception as e:
        logger.exception("Failed to get VM details for %s", vm_id)
        return yaml.dump({
            "status": "error",
            "error": f"Failed to get VM details: {str(e)}",
        }, default_flow_style=False)


@mcp.tool()
async def start_vm(vm_id: str) -> str:
    """Start a virtual machine.

    Args:
        vm_id: The composite VM ID (format: provider:tenant:region:instance_id)

    Returns:
        YAML formatted string indicating success or failure
    """
    try:
        parsed = BaseProvider.parse_composite_id(vm_id)
        if not parsed:
            return yaml.dump({
                "status": "error",
                "error": "Invalid VM ID format. Expected: provider:tenant:region:instance_id",
            }, default_flow_style=False)

        provider_name, tenant_alias, region, instance_id = parsed

        provider = get_provider_by_composite_id(vm_id)
        if not provider:
            return yaml.dump({
                "status": "error",
                "error": f"No provider found for {provider_name}:{tenant_alias}",
            }, default_flow_style=False)

        try:
            success, message = await asyncio.wait_for(
                provider.start_vm(instance_id),
                timeout=PER_REQUEST_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.exception("start_vm for %s timed out after %ss", vm_id, PER_REQUEST_TIMEOUT)
            return yaml.dump({
                "status": "error",
                "error": f"Request timed out after {PER_REQUEST_TIMEOUT}s",
            }, default_flow_style=False)

        if success:
            return yaml.dump({
                "status": "success",
                "message": message,
            }, default_flow_style=False)
        else:
            return yaml.dump({
                "status": "error",
                "error": message,
            }, default_flow_style=False)

    except Exception as e:
        logger.exception("Failed to start VM %s", vm_id)
        return yaml.dump({
            "status": "error",
            "error": f"Failed to start VM: {str(e)}",
        }, default_flow_style=False)


@mcp.tool()
async def stop_vm(vm_id: str, force: bool = False) -> str:
    """Stop a virtual machine.

    Args:
        vm_id: The composite VM ID (format: provider:tenant:region:instance_id)
        force: Force stop without graceful shutdown (default: False)

    Returns:
        YAML formatted string indicating success or failure
    """
    try:
        parsed = BaseProvider.parse_composite_id(vm_id)
        if not parsed:
            return yaml.dump({
                "status": "error",
                "error": "Invalid VM ID format. Expected: provider:tenant:region:instance_id",
            }, default_flow_style=False)

        provider_name, tenant_alias, region, instance_id = parsed

        provider = get_provider_by_composite_id(vm_id)
        if not provider:
            return yaml.dump({
                "status": "error",
                "error": f"No provider found for {provider_name}:{tenant_alias}",
            }, default_flow_style=False)

        try:
            success, message = await asyncio.wait_for(
                provider.stop_vm(instance_id, force=force),
                timeout=PER_REQUEST_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.exception("stop_vm for %s timed out after %ss", vm_id, PER_REQUEST_TIMEOUT)
            return yaml.dump({
                "status": "error",
                "error": f"Request timed out after {PER_REQUEST_TIMEOUT}s",
            }, default_flow_style=False)

        if success:
            return yaml.dump({
                "status": "success",
                "message": message,
            }, default_flow_style=False)
        else:
            return yaml.dump({
                "status": "error",
                "error": message,
            }, default_flow_style=False)

    except Exception as e:
        logger.exception("Failed to stop VM %s", vm_id)
        return yaml.dump({
            "status": "error",
            "error": f"Failed to stop VM: {str(e)}",
        }, default_flow_style=False)
