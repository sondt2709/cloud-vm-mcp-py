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


class AlibabaAccount(BaseModel):
    """Alibaba Cloud account credentials configuration."""

    alias: str
    access_key_id: str
    access_key_secret: str
    regions: list[str]


class AWSConfig(BaseModel):
    """AWS provider configuration with multiple accounts."""

    accounts: list[AWSAccount] = []


class AzureConfig(BaseModel):
    """Azure provider configuration with multiple directories."""

    directories: list[AzureDirectory] = []


class AlibabaConfig(BaseModel):
    """Alibaba Cloud provider configuration with multiple accounts."""

    accounts: list[AlibabaAccount] = []


class ProvidersConfig(BaseModel):
    """Root configuration for all cloud providers."""

    providers: dict[str, AWSConfig | AzureConfig | AlibabaConfig] = {}

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

    def get_alibaba_accounts(self) -> list[AlibabaAccount]:
        """Get all configured Alibaba Cloud accounts."""
        alibaba_config = self.providers.get("alibaba")
        if isinstance(alibaba_config, AlibabaConfig):
            return alibaba_config.accounts
        return []
