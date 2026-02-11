# Change: Migrate from SSH MCP to Cloud VM Management MCP

## Why

The current SSH MCP server focuses on executing commands on remote hosts via SSH configuration. The project needs to pivot to a cloud-native VM management tool that can list, view, and control virtual machines across multiple cloud providers (AWS, Azure) and multiple accounts/directories. This enables AI assistants to manage cloud infrastructure without requiring pre-configured SSH access to each VM.

## What Changes

- **BREAKING**: Remove SSH-based command execution architecture
- **BREAKING**: Remove SSH config file parsing (`~/.ssh/config`)
- **BREAKING**: Remove SOCKS5 proxy configuration support
- **BREAKING**: Rename package from `ssh-mcp-py` to `vm-mcp`
- Add multi-provider credential management (AWS, Azure) via YAML config
- Add configuration file watching for hot-reload
- Add support for multiple accounts per provider
- Add VM listing across all configured providers/accounts
- Add filtering by provider, tenant (account/directory), and region
- Add VM detail viewing (region, instance ID, public IP)
- Add VM power management (start, stop)
- Replace Paramiko/PySocks with cloud provider SDKs (boto3, azure-sdk, pyyaml, watchdog)

### Future Phases (Not in This Proposal)
- Alibaba Cloud provider support
- Firewall rules viewing
- Elastic IP management
- RAM/CPU/GPU details
- Scheduled start/stop operations

## Impact

- **Affected specs**: All current SSH-related specs will be removed
- **New specs**: `vm-listing`, `vm-details`, `vm-power-management`, `provider-credentials`
- **Affected code**:
  - `ssh_mcp/` → rename to `vm_mcp/`
  - `ssh_mcp/ssh_client.py` → remove, replace with provider clients
  - `ssh_mcp/mcp.py` → rewrite MCP tools for VM operations
  - `ssh_mcp/model/proxy.py` → remove, replace with credential models
  - `pyproject.toml` → update name, dependencies
  - `cli.py` → update for new functionality
  - `tests/` → rewrite all tests
- **Dependencies to remove**: `paramiko`, `pysocks`
- **Dependencies to add**: `boto3`, `azure-identity`, `azure-mgmt-compute`, `azure-mgmt-network`, `pyyaml`, `watchdog`
