# Cloud VM MCP: Model Context Protocol for Cloud VM Management

Cloud VM MCP is a Model Context Protocol (MCP) server for managing and viewing virtual machines across multiple cloud providers (AWS, Azure). It enables AI assistants to list, inspect, and control VMs through a unified interface.

-----

## Installation 📦

```bash
# Install from PyPI
pip install cloud-vm-mcp-py

# Or using uv
uv add cloud-vm-mcp-py
```

-----

## Usage Guide 📖

VM MCP can be used in two ways: as an MCP server or as a direct command-line tool.

### MCP Server Usage

Start the MCP server:

```bash
uv run vm-mcp
```

**Available MCP Tools:**

1. **list_vms**: List all VMs across configured providers
   - Parameters: `provider` (optional), `tenant` (optional), `region` (optional)

2. **list_providers**: List all configured cloud providers
   - Parameters: None

3. **get_vm_details**: Get detailed information about a specific VM
   - Parameters: `vm_id` (composite ID format: `provider:tenant:region:instance`)

4. **start_vm**: Start a virtual machine
   - Parameters: `vm_id`

5. **stop_vm**: Stop a virtual machine
   - Parameters: `vm_id`, `force` (optional, default: false)

### Integration with Claude Desktop

To use Cloud VM MCP with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vm": {
      "command": "uvx",
      "args": ["cloud-vm-mcp-py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "PROVIDERS_CONFIG_PATH": "/path/to/your/providers.yaml"
      }
    }
  }
}
```

**Configuration File Location:**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Direct Command-Line Usage

You can manage VMs directly using the CLI:

**List all VMs:**

```bash
PROVIDERS_CONFIG_PATH=./providers.yaml uv run python cli.py list
```

**Filter by provider/tenant/region:**

```bash
uv run python cli.py list --provider aws --tenant production --region us-east-1
```

**Get VM details:**

```bash
uv run python cli.py info aws:production:us-east-1:i-1234567890abcdef0
```

**Start/Stop VMs:**

```bash
uv run python cli.py start aws:production:us-east-1:i-1234567890abcdef0
uv run python cli.py stop azure:corp-main:eastus:web-server --force
```

**List configured providers:**

```bash
uv run python cli.py providers
```

### MCP Inspector

You can inspect and test the MCP server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run vm-mcp -e PROVIDERS_CONFIG_PATH=/path/to/providers.yaml
```

-----

## Key Features 🚀

- **Multi-Provider Support**: Manage VMs across AWS and Azure from a single interface
- **Multi-Account Support**: Configure multiple AWS accounts and Azure directories
- **Unified VM Model**: Consistent VM representation across providers
- **Filtering**: Filter VMs by provider, tenant (account/directory), or region
- **Power Management**: Start and stop VMs with optional force flag
- **Hot-Reload**: Configuration changes are automatically detected and applied
- **MCP Integration**: Provides tools for AI assistants through the Model Context Protocol

-----

## Requirements 📋

- **Python 3.10 or higher**
- **boto3**: For AWS EC2 operations
- **azure-identity, azure-mgmt-compute, azure-mgmt-network**: For Azure VM operations
- **pyyaml**: For YAML configuration parsing
- **watchdog**: For configuration file watching

-----

## Configuration ⚙️

Cloud VM MCP uses a YAML configuration file to define cloud provider credentials. Set the `PROVIDERS_CONFIG_PATH` environment variable to point to your configuration file.

### Configuration File Setup

Create a `providers.yaml` file with your provider credentials:

**Example `providers.yaml`:**

```yaml
providers:
  aws:
    accounts:
      - alias: production
        access_key_id: AKIAIOSFODNN7EXAMPLE
        secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        regions:
          - us-east-1
          - us-west-2

      - alias: staging
        access_key_id: AKIAI44QH8DHBEXAMPLE
        secret_access_key: je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
        regions:
          - us-east-1

  azure:
    directories:
      - alias: corp-main
        tenant_id: 00000000-0000-0000-0000-000000000000
        client_id: 11111111-1111-1111-1111-111111111111
        client_secret: your-client-secret-here
        subscription_ids:
          - 22222222-2222-2222-2222-222222222222
```

### Environment Variables

- `MCP_TRANSPORT`: stdio, sse, streamable-http (defaults to stdio)
- `PROVIDERS_CONFIG_PATH`: Path to YAML configuration file (required)

### Security Recommendations

- Store the configuration file with restricted permissions (`chmod 600 providers.yaml`)
- Never commit credentials to version control
- Consider using environment variables for sensitive values in production

-----

## VM Identifier Format 🔖

VMs are identified using a composite ID format:

```
{provider}:{tenant_alias}:{region}:{instance_id}
```

**Examples:**
- AWS: `aws:production:us-east-1:i-1234567890abcdef0`
- Azure: `azure:corp-main:eastus:web-server-01`

-----

## Timeout Configuration ⏱️

- **Per-request timeout**: 60 seconds
- **Total query timeout**: 180 seconds (3 minutes) for multi-provider queries

-----

## Development & Testing 🧪

### Setup

1. Clone the repository
2. Install dependencies: `uv sync`
3. Setup pre-commit: `uv run pre-commit install`

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=vm_mcp --cov-report=html
```

### Code Quality

```bash
uv run ruff check .
uv run ruff format .
```

### Publishing to PyPI

```bash
rm -rf dist
uv build
uv publish --username __token__ --password YOUR_PYPI_API_KEY
```

-----

## Future Roadmap 🗺️

- Alibaba Cloud provider support
- Firewall rules viewing
- Elastic IP management
- RAM/CPU/GPU details
- Scheduled start/stop operations

-----

## License

MIT License - See [LICENSE](LICENSE) for details.
