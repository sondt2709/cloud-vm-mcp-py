#!/usr/bin/env python3
"""Command line interface for Cloud VM MCP direct usage."""

import argparse
import asyncio
import logging
import sys

from vm_mcp.config import get_config
from vm_mcp.providers import get_provider_by_composite_id, get_providers

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Cloud VM MCP CLI - Manage VMs across cloud providers",
        prog="vm-mcp",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List all VMs")
    list_parser.add_argument("--provider", "-p", help="Filter by provider (aws, azure)")
    list_parser.add_argument("--tenant", "-t", help="Filter by tenant alias")
    list_parser.add_argument("--region", "-r", help="Filter by region")

    # info command
    info_parser = subparsers.add_parser("info", help="Get VM details")
    info_parser.add_argument("vm_id", help="Composite VM ID (provider:tenant:region:instance)")

    # start command
    start_parser = subparsers.add_parser("start", help="Start a VM")
    start_parser.add_argument("vm_id", help="Composite VM ID (provider:tenant:region:instance)")

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a VM")
    stop_parser.add_argument("vm_id", help="Composite VM ID (provider:tenant:region:instance)")
    stop_parser.add_argument("--force", "-f", action="store_true", help="Force stop")

    # providers command
    subparsers.add_parser("providers", help="List configured providers")

    return parser


async def cmd_list(args: argparse.Namespace) -> int:
    """List VMs."""
    import time
    
    providers = get_providers(provider=args.provider, tenant=args.tenant)

    if not providers:
        print("No providers configured or matching filters.")
        return 1

    all_vms = []
    for provider in providers:
        try:
            print(f"Querying {provider.provider_name}:{provider.tenant_alias}...", flush=True)
            start = time.time()
            vms = await provider.list_vms(region=args.region)
            elapsed = time.time() - start
            print(f"  Found {len(vms)} VMs in {elapsed:.2f}s")
            all_vms.extend(vms)
        except Exception:
            logger.exception("Failed to list VMs from provider %s", provider.provider_name)

    if not all_vms:
        print("No VMs found.")
        return 0

    print(f"\nVirtual Machines ({len(all_vms)} found):")
    print("=" * 60)

    for vm in sorted(all_vms, key=lambda v: (v.provider, v.tenant_alias, v.name)):
        print(f"\n{vm.name}")
        print(f"  ID: {vm.id}")
        print(f"  Provider: {vm.provider} | Tenant: {vm.tenant_alias}")
        print(f"  Region: {vm.region} | Type: {vm.instance_type}")
        print(f"  State: {vm.state.value}")

    return 0


async def cmd_info(args: argparse.Namespace) -> int:
    """Get VM details."""
    provider = get_provider_by_composite_id(args.vm_id)
    if not provider:
        print(f"ERROR: No provider found for VM ID: {args.vm_id}")
        return 1

    from vm_mcp.providers.base import BaseProvider
    parsed = BaseProvider.parse_composite_id(args.vm_id)
    if not parsed:
        print("ERROR: Invalid VM ID format")
        return 1

    _, _, _, instance_id = parsed

    try:
        details = await provider.get_vm_details(instance_id)
        if not details:
            print(f"ERROR: VM not found: {args.vm_id}")
            return 1

        print(f"\nVM Details: {details.name}")
        print("=" * 60)
        print(f"ID: {details.id}")
        print(f"Provider: {details.provider}")
        print(f"Tenant: {details.tenant_alias}")
        print(f"Region: {details.region}")
        print(f"State: {details.state.value}")
        print(f"Instance Type: {details.instance_type}")
        print(f"Public IP: {details.public_ip or 'N/A'}")
        print(f"Private IP: {details.private_ip or 'N/A'}")

        if details.provider_metadata:
            print("\nProvider Metadata:")
            for key, value in details.provider_metadata.items():
                if value:
                    print(f"  {key}: {value}")

        return 0

    except Exception:
        logger.exception("Failed to get VM info")
        return 1


async def cmd_start(args: argparse.Namespace) -> int:
    """Start a VM."""
    provider = get_provider_by_composite_id(args.vm_id)
    if not provider:
        print(f"ERROR: No provider found for VM ID: {args.vm_id}")
        return 1

    from vm_mcp.providers.base import BaseProvider
    parsed = BaseProvider.parse_composite_id(args.vm_id)
    if not parsed:
        print("ERROR: Invalid VM ID format")
        return 1

    _, _, _, instance_id = parsed

    try:
        success, message = await provider.start_vm(instance_id)
        if success:
            print(f"SUCCESS: {message}")
            return 0
        else:
            print(f"ERROR: {message}")
            return 1
    except Exception:
        logger.exception("Failed to start VM %s", args.vm_id)
        return 1


async def cmd_stop(args: argparse.Namespace) -> int:
    """Stop a VM."""
    provider = get_provider_by_composite_id(args.vm_id)
    if not provider:
        print(f"ERROR: No provider found for VM ID: {args.vm_id}")
        return 1

    from vm_mcp.providers.base import BaseProvider
    parsed = BaseProvider.parse_composite_id(args.vm_id)
    if not parsed:
        print("ERROR: Invalid VM ID format")
        return 1

    _, _, _, instance_id = parsed

    try:
        success, message = await provider.stop_vm(instance_id, force=args.force)
        if success:
            print(f"SUCCESS: {message}")
            return 0
        else:
            print(f"ERROR: {message}")
            return 1
    except Exception:
        logger.exception("Failed to stop VM %s", args.vm_id)
        return 1


async def cmd_providers(args: argparse.Namespace) -> int:
    """List configured providers."""
    config = get_config()

    from vm_mcp.model.credentials import AWSConfig, AzureConfig

    providers_count = 0

    aws_config = config.providers.get("aws")
    if isinstance(aws_config, AWSConfig):
        for account in aws_config.accounts:
            providers_count += 1
            print(f"\nAWS: {account.alias}")
            print(f"  Regions: {', '.join(account.regions)}")

    azure_config = config.providers.get("azure")
    if isinstance(azure_config, AzureConfig):
        for directory in azure_config.directories:
            providers_count += 1
            print(f"\nAzure: {directory.alias}")
            print(f"  Subscriptions: {', '.join(directory.subscription_ids)}")

    if providers_count == 0:
        print("No providers configured.")
        return 1

    print(f"\n{providers_count} provider(s) configured.")
    return 0


async def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "list": cmd_list,
        "info": cmd_info,
        "start": cmd_start,
        "stop": cmd_stop,
        "providers": cmd_providers,
    }

    handler = commands.get(args.command)
    if handler:
        return await handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
