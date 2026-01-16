"""Provider registry and factory."""

from vm_mcp.config import get_config
from vm_mcp.model.credentials import AWSConfig, AzureConfig
from vm_mcp.providers.aws import AWSProvider
from vm_mcp.providers.azure import AzureProvider
from vm_mcp.providers.base import BaseProvider


def get_providers(
    provider: str | None = None,
    tenant: str | None = None,
) -> list[BaseProvider]:
    """Get list of providers based on filters.

    Args:
        provider: Optional provider filter ('aws', 'azure')
        tenant: Optional tenant alias filter

    Returns:
        List of provider instances matching filters
    """
    config = get_config()
    providers: list[BaseProvider] = []

    # AWS providers
    if provider is None or provider == "aws":
        aws_config = config.providers.get("aws")
        if isinstance(aws_config, AWSConfig):
            for account in aws_config.accounts:
                if tenant is None or account.alias == tenant:
                    providers.append(AWSProvider(account))

    # Azure providers
    if provider is None or provider == "azure":
        azure_config = config.providers.get("azure")
        if isinstance(azure_config, AzureConfig):
            for directory in azure_config.directories:
                if tenant is None or directory.alias == tenant:
                    providers.append(AzureProvider(directory))

    return providers


def get_provider_by_composite_id(composite_id: str) -> BaseProvider | None:
    """Get the provider for a specific VM by composite ID.

    Args:
        composite_id: The composite VM ID

    Returns:
        Provider instance or None if not found
    """
    parsed = BaseProvider.parse_composite_id(composite_id)
    if not parsed:
        return None

    provider_name, tenant_alias, _, _ = parsed
    providers = get_providers(provider=provider_name, tenant=tenant_alias)

    return providers[0] if providers else None
