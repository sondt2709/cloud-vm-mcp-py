"""Pytest configuration and fixtures for Cloud VM MCP tests."""

import pytest


class _FakeSession:
    """Stand-in for the MCP server session used by the confirmation gate."""

    def __init__(self, supports_elicitation: bool):
        self._supports = supports_elicitation

    def check_client_capability(self, capability) -> bool:
        return self._supports


class _FakeContext:
    """Minimal fake of FastMCP Context for confirmation tests.

    ``supports`` toggles advertised elicitation capability. ``elicit_result``
    is returned from ``elicit`` when the client supports elicitation.
    """

    def __init__(self, supports: bool = False, elicit_result=None):
        self.session = _FakeSession(supports)
        self._elicit_result = elicit_result
        self.elicit_calls: list[str] = []

    async def elicit(self, message: str, schema):
        self.elicit_calls.append(message)
        return self._elicit_result


def make_accept_context(answer: str = "Yes"):
    """Context whose client supports elicitation and accepts with ``answer``."""
    from mcp.server.elicitation import AcceptedElicitation

    from vm_mcp.confirmation import Confirm

    return _FakeContext(
        supports=True,
        elicit_result=AcceptedElicitation(data=Confirm(confirmation=answer)),
    )


def make_decline_context():
    """Context whose client supports elicitation and declines."""
    from mcp.server.elicitation import DeclinedElicitation

    return _FakeContext(supports=True, elicit_result=DeclinedElicitation())


def make_cancel_context():
    """Context whose client supports elicitation and cancels."""
    from mcp.server.elicitation import CancelledElicitation

    return _FakeContext(supports=True, elicit_result=CancelledElicitation())


@pytest.fixture
def noelicit_ctx():
    """Context whose client does NOT support elicitation (fail-open)."""
    return _FakeContext(supports=False)


@pytest.fixture
def accept_ctx():
    """Context that accepts the confirmation prompt."""
    return make_accept_context()


@pytest.fixture
def decline_ctx():
    """Context that declines the confirmation prompt."""
    return make_decline_context()


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    """Reset config loader before and after each test."""
    # Clear any env var that might cause issues
    monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)
    monkeypatch.delenv("VM_MCP_CONFIRM_REQUIRED_TOOLS", raising=False)

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
