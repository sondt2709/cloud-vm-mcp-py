"""Pytest configuration and fixtures for Cloud VM MCP tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    """Reset config loader before and after each test."""
    # Clear any env var that might cause issues
    monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)
    
    from vm_mcp.config import reset_config_loader
    reset_config_loader()
    yield
    reset_config_loader()


@pytest.fixture
def sample_aws_config():
    """Sample AWS configuration."""
    return {
        "alias": "test-aws",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "regions": ["us-east-1", "us-west-2"],
    }


@pytest.fixture
def sample_azure_config():
    """Sample Azure configuration."""
    return {
        "alias": "test-azure",
        "tenant_id": "00000000-0000-0000-0000-000000000000",
        "client_id": "11111111-1111-1111-1111-111111111111",
        "client_secret": "test-client-secret",
        "subscription_ids": ["sub-1", "sub-2"],
    }


@pytest.fixture
def sample_alibaba_config():
    """Sample Alibaba Cloud configuration."""
    return {
        "alias": "test-alibaba",
        "access_key_id": "LTAI5tExampleKeyId",
        "access_key_secret": "ExampleAccessKeySecretValue123",
        "regions": ["cn-hangzhou", "ap-southeast-1"],
    }


@pytest.fixture
def sample_providers_yaml(tmp_path, sample_aws_config, sample_azure_config):
    """Create a sample providers.yaml file."""
    import yaml

    config = {
        "providers": {
            "aws": {"accounts": [sample_aws_config]},
            "azure": {"directories": [sample_azure_config]},
        }
    }

    config_file = tmp_path / "providers.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)

    return config_file
