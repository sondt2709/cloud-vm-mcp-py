"""Tests for credential models."""

from vm_mcp.model.credentials import (
    AWSAccount,
    AWSConfig,
    AzureConfig,
    AzureDirectory,
    ProvidersConfig,
)


class TestAWSAccount:
    """Tests for AWS account model."""

    def test_valid_aws_account(self, sample_aws_config):
        """Test creating a valid AWS account."""
        account = AWSAccount(**sample_aws_config)
        assert account.alias == "test-aws"
        assert account.access_key_id == "AKIAIOSFODNN7EXAMPLE"
        assert account.secret_access_key == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert account.regions == ["us-east-1", "us-west-2"]

    def test_missing_required_field(self):
        """Test validation error for missing required field."""
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AWSAccount(alias="test", access_key_id="key")  # missing secret_access_key and regions


class TestAzureDirectory:
    """Tests for Azure directory model."""

    def test_valid_azure_directory(self, sample_azure_config):
        """Test creating a valid Azure directory."""
        directory = AzureDirectory(**sample_azure_config)
        assert directory.alias == "test-azure"
        assert directory.tenant_id == "00000000-0000-0000-0000-000000000000"
        assert directory.client_id == "11111111-1111-1111-1111-111111111111"
        assert directory.client_secret == "test-client-secret"
        assert directory.subscription_ids == ["sub-1", "sub-2"]


class TestProvidersConfig:
    """Tests for providers configuration."""

    def test_get_aws_accounts(self, sample_aws_config):
        """Test getting AWS accounts from config."""
        account = AWSAccount(**sample_aws_config)
        config = ProvidersConfig(
            providers={"aws": AWSConfig(accounts=[account])}
        )

        accounts = config.get_aws_accounts()
        assert len(accounts) == 1
        assert accounts[0].alias == "test-aws"

    def test_get_azure_directories(self, sample_azure_config):
        """Test getting Azure directories from config."""
        directory = AzureDirectory(**sample_azure_config)
        config = ProvidersConfig(
            providers={"azure": AzureConfig(directories=[directory])}
        )

        directories = config.get_azure_directories()
        assert len(directories) == 1
        assert directories[0].alias == "test-azure"

    def test_empty_config(self):
        """Test empty configuration."""
        config = ProvidersConfig(providers={})
        assert config.get_aws_accounts() == []
        assert config.get_azure_directories() == []
