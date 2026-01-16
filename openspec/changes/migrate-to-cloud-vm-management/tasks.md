# Tasks: Migrate to Cloud VM Management MCP

## 1. Project Restructuring
- [ ] 1.1 Rename package from `ssh_mcp` to `vm_mcp` in all files
- [ ] 1.2 Update `pyproject.toml` with new package name `vm-mcp`
- [ ] 1.3 Update dependencies: remove paramiko/pysocks, add boto3/azure-sdk/pyyaml/watchdog
- [ ] 1.4 Update README.md with new project description and usage
- [ ] 1.5 Update entry point from `ssh-mcp-py` to `vm-mcp`

## 2. Credential Management
- [ ] 2.1 Create `vm_mcp/model/credentials.py` with Pydantic models for provider credentials
- [ ] 2.2 Implement AWS credential model (access key, secret key, region, account alias)
- [ ] 2.3 Implement Azure credential model (tenant ID, client ID, client secret, subscription ID, alias)
- [ ] 2.4 Create credential loader from YAML config file (`PROVIDERS_CONFIG_PATH` env var)
- [ ] 2.5 Support multiple accounts per provider in configuration
- [ ] 2.6 Implement config file watcher using watchdog for hot-reload
- [ ] 2.7 Handle invalid config gracefully (keep previous valid config)

## 3. AWS Provider Implementation
- [ ] 3.1 Create `vm_mcp/providers/aws.py` with AWS VM client
- [ ] 3.2 Implement EC2 instance listing across all configured AWS accounts
- [ ] 3.3 Implement EC2 instance detail retrieval (region, instance ID, public IP, state)
- [ ] 3.4 Implement EC2 instance start operation
- [ ] 3.5 Implement EC2 instance stop operation
- [ ] 3.6 Handle pagination for large instance lists

## 4. Azure Provider Implementation
- [ ] 4.1 Create `vm_mcp/providers/azure.py` with Azure VM client
- [ ] 4.2 Implement Azure VM listing across all configured subscriptions
- [ ] 4.3 Implement Azure VM detail retrieval (region, resource ID, public IP, state)
- [ ] 4.4 Implement Azure VM start operation
- [ ] 4.5 Implement Azure VM stop operation

## 5. Provider Abstraction Layer
- [ ] 5.1 Create `vm_mcp/providers/base.py` with abstract provider interface
- [ ] 5.2 Implement provider registry for dynamic provider loading
- [ ] 5.3 Create unified VM data model across providers

## 6. MCP Tools Implementation
- [ ] 6.1 Rewrite `vm_mcp/mcp.py` with new MCP server configuration
- [ ] 6.2 Implement `list_vms` tool with filters (provider, tenant, region)
- [ ] 6.3 Implement `list_providers` tool - list configured providers and accounts
- [ ] 6.4 Implement `get_vm_details` tool - get detailed VM information
- [ ] 6.5 Implement `start_vm` tool - start a specific VM
- [ ] 6.6 Implement `stop_vm` tool - stop a specific VM
- [ ] 6.7 Implement per-request timeout (60s) and total query timeout (180s)

## 7. CLI Updates
- [ ] 7.1 Update `cli.py` for new VM management commands
- [ ] 7.2 Add `list` subcommand for VM listing
- [ ] 7.3 Add `info` subcommand for VM details
- [ ] 7.4 Add `start`/`stop` subcommands for power management

## 8. Testing
- [ ] 8.1 Remove old SSH-related tests
- [ ] 8.2 Create mock fixtures for AWS/Azure API responses
- [ ] 8.3 Write unit tests for YAML credential loading
- [ ] 8.4 Write unit tests for config file watching
- [ ] 8.5 Write unit tests for AWS provider
- [ ] 8.6 Write unit tests for Azure provider
- [ ] 8.7 Write unit tests for MCP tools (with filter combinations)
- [ ] 8.8 Write unit tests for timeout handling
- [ ] 8.9 Write integration tests with mocked cloud APIs

## 9. Documentation
- [ ] 9.1 Update README.md with new usage examples
- [ ] 9.2 Create example YAML credential configuration file
- [ ] 9.3 Update `openspec/project.md` with new architecture details
- [ ] 9.4 Document environment variables
- [ ] 9.5 Document filtering options (provider, tenant, region)

## 10. Cleanup
- [ ] 10.1 Remove `ssh_mcp/ssh_client.py`
- [ ] 10.2 Remove `ssh_mcp/model/proxy.py`
- [ ] 10.3 Remove SSH config example files
- [ ] 10.4 Remove proxy config example files
- [ ] 10.5 Clean up old build artifacts
