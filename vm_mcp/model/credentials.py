"""Pydantic models for provider credentials."""

from pydantic import BaseModel


class AWSAccount(BaseModel):
    """AWS account credentials configuration."""

    alias: str
    access_key_id: str
    secret_access_key: str
    regions: list[str]


class AzureDirectory(BaseModel):
    """Azure directory (tenant) credentials configuration."""

    alias: str
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_ids: list[str]


class AWSConfig(BaseModel):
    """AWS provider configuration with multiple accounts."""

    accounts: list[AWSAccount] = []


class AzureConfig(BaseModel):
    """Azure provider configuration with multiple directories."""

    directories: list[AzureDirectory] = []


class ProvidersConfig(BaseModel):
    """Root configuration for all cloud providers."""

    providers: dict[str, AWSConfig | AzureConfig] = {}

    def get_aws_accounts(self) -> list[AWSAccount]:
        """Get all configured AWS accounts."""
        aws_config = self.providers.get("aws")
        if isinstance(aws_config, AWSConfig):
            return aws_config.accounts
        return []

    def get_azure_directories(self) -> list[AzureDirectory]:
        """Get all configured Azure directories."""
        azure_config = self.providers.get("azure")
        if isinstance(azure_config, AzureConfig):
            return azure_config.directories
        return []
