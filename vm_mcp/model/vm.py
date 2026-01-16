"""Pydantic models for VM data."""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class VMState(str, Enum):
    """Normalized VM power states across providers."""

    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    TERMINATED = "terminated"
    UNKNOWN = "unknown"


class VMInfo(BaseModel):
    """Basic VM information for listing."""

    id: str  # Composite ID: {provider}:{tenant_alias}:{region}:{instance_id}
    name: str
    provider: str  # aws, azure
    tenant_alias: str  # User-defined account/directory name
    region: str
    state: VMState
    instance_type: str


class VMDetails(VMInfo):
    """Detailed VM information."""

    public_ip: str | None = None
    private_ip: str | None = None
    provider_metadata: dict[str, Any] = {}


class ProviderInfo(BaseModel):
    """Information about a configured provider."""

    provider: str
    tenant_alias: str
    regions: list[str]


class ProviderError(BaseModel):
    """Error information from a provider query."""

    provider: str
    tenant_alias: str
    error: str
