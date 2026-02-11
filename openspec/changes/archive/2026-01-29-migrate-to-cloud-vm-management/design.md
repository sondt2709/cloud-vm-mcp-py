# Design: Cloud VM Management MCP

## Context

The project is pivoting from an SSH-based command execution tool to a cloud VM management tool. This requires:
- Integration with multiple cloud provider APIs (AWS EC2, Azure Compute)
- Support for multiple accounts/subscriptions per provider
- Unified data model for VMs across providers
- Secure credential management

## Goals / Non-Goals

**Goals:**
- Enable AI assistants to list and manage VMs across AWS and Azure
- Support multiple accounts per provider
- Provide consistent API regardless of cloud provider
- Maintain simple, clear architecture per project conventions

**Non-Goals (This Phase):**
- Alibaba Cloud support (next phase)
- Firewall/security group management (next phase)
- Elastic IP management (next phase)
- Detailed resource metrics (RAM/CPU/GPU) (next phase)
- Scheduled operations (next phase)
- VM creation/deletion operations

## Decisions

### 1. Credential Configuration Format

**Decision:** Use YAML configuration file with provider-account hierarchy

```yaml
providers:
  aws:
    accounts:
      - alias: production
        access_key_id: AKIA...
        secret_access_key: "..."
        regions:
          - us-east-1
          - us-west-2
      - alias: staging
        access_key_id: AKIA...
        secret_access_key: "..."
        regions:
          - us-east-1
  azure:
    directories:
      - alias: corp-main
        tenant_id: "..."
        client_id: "..."
        client_secret: "..."
        subscription_ids:
          - sub-1
          - sub-2
```

**Alternatives considered:**
- JSON: Less readable, no comments support
- Environment variables per account: Too complex for multiple accounts
- AWS profiles (~/.aws/credentials): Not supported - explicit credentials only
- Azure CLI auth: Not supported - service principal only

### 2. Provider Abstraction

**Decision:** Abstract base class with provider-specific implementations

```python
class BaseProvider(ABC):
    @abstractmethod
    async def list_vms(self) -> list[VMInfo]: ...
    
    @abstractmethod
    async def get_vm_details(self, vm_id: str) -> VMDetails: ...
    
    @abstractmethod
    async def start_vm(self, vm_id: str) -> bool: ...
    
    @abstractmethod
    async def stop_vm(self, vm_id: str) -> bool: ...
```

**Alternatives considered:**
- Protocol-based typing: Less explicit, harder to enforce
- No abstraction: Would lead to duplicated logic in MCP tools

### 3. VM Identifier Format

**Decision:** Use composite ID format: `{provider}:{account_alias}:{region}:{instance_id}`

Examples:
- `aws:production:us-east-1:i-1234567890abcdef0`
- `azure:corp-main:eastus:my-vm-resource-id`

**Rationale:** Enables unambiguous VM identification across providers and accounts

### 4. Unified VM Data Model

**Decision:** Pydantic model with common fields + provider-specific metadata

```python
class VMInfo(BaseModel):
    id: str                    # Composite ID
    name: str                  # Display name
    provider: str              # aws, azure
    account_alias: str         # User-defined account name
    region: str                # Cloud region
    state: VMState             # running, stopped, etc.
    public_ip: str | None      # Public IP if assigned
    instance_type: str         # e.g., t3.micro, Standard_B1s
    provider_metadata: dict    # Provider-specific fields
```

### 5. SDK Dependencies

**Decision:**
- AWS: `boto3` (official AWS SDK)
- Azure: `azure-identity` + `azure-mgmt-compute` + `azure-mgmt-network`
- Config: `pyyaml` for YAML parsing
- File watching: `watchdog` for config hot-reload

**Rationale:** Official SDKs ensure compatibility and security updates

### 6. Timeout Configuration

**Decision:**
- Per-request timeout: 60 seconds (1 minute)
- Total query timeout: 180 seconds (3 minutes) for multi-provider queries
- No caching of results

**Rationale:** Cloud API calls can be slow; generous timeouts prevent false failures while total timeout prevents hanging

### 7. Configuration Hot-Reload

**Decision:** Watch configuration file for changes and reload credentials automatically

**Rationale:** Allows adding/removing providers without restarting the MCP server

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Credential exposure in config | Document secure file permissions (0600), consider env var override |
| API rate limiting | Implement exponential backoff |
| Async complexity with SDKs | boto3 is sync-only, use `asyncio.to_thread()` |
| Large number of VMs | Implement pagination, filtering by provider/tenant/region |
| Config file changes | Watchdog monitors file, reloads on change |
| Long query times | Per-request 60s timeout, total 180s timeout |

## Migration Plan

1. **Phase 1**: Create new provider structure alongside existing SSH code
2. **Phase 2**: Implement AWS provider with full functionality
3. **Phase 3**: Implement Azure provider with full functionality
4. **Phase 4**: Rewrite MCP tools to use new providers
5. **Phase 5**: Remove old SSH code and update package naming
6. **Phase 6**: Update documentation and tests

**Rollback:** Old code remains on main branch until migration is complete

## Directory Structure (After Migration)

```
vm_mcp/
├── __init__.py
├── mcp.py                    # MCP server and tools
├── config.py                 # Configuration loading
├── model/
│   ├── __init__.py
│   ├── credentials.py        # Provider credential models
│   └── vm.py                 # VM data models
└── providers/
    ├── __init__.py
    ├── base.py               # Abstract provider interface
    ├── aws.py                # AWS EC2 implementation
    └── azure.py              # Azure Compute implementation
```

## Resolved Questions

- [x] ~~Should we support AWS profiles from `~/.aws/credentials`?~~ **No** - explicit credentials only
- [x] ~~Should we support Azure CLI authentication?~~ **No** - service principal only
- [x] ~~What timeout values are appropriate?~~ **60s per request, 180s total**
- [x] ~~Should VM list results be cached?~~ **No caching** - always fetch fresh data
- [x] ~~Configuration format?~~ **YAML** with file watching for hot-reload
