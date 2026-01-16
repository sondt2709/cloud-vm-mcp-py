# Project Context

## Purpose

SSH MCP (ssh-mcp-py) is a Model Context Protocol (MCP) server for managing and interacting with multiple virtual machines over SSH. It enables AI assistants and MCP clients to execute commands on remote servers by leveraging standard SSH configuration files.

**Goals:**
- Provide MCP tools for remote command execution via SSH
- Support standard `~/.ssh/config` format for server configuration
- Enable optional SOCKS5 proxy connections with authentication
- Offer both MCP server mode and direct CLI usage

## Tech Stack

- **Language:** Python 3.10+
- **Package Manager:** uv (modern Python package manager)
- **MCP Framework:** FastMCP (`mcp[cli]>=1.13.1`)
- **SSH Library:** Paramiko (`paramiko>=4.0.0`)
- **Data Validation:** Pydantic (`pydantic>=2.0.0`)
- **Proxy Support:** PySocks (`pysocks>=1.7.1`)
- **Environment:** python-dotenv (`python-dotenv>=1.1.1`)

**Dev Dependencies:**
- **Linter/Formatter:** Ruff
- **Type Checker:** ty
- **Testing:** pytest, pytest-asyncio, pytest-mock
- **Pre-commit Hooks:** pre-commit

## Project Conventions

### Code Style

- **Formatter/Linter:** Ruff with import sorting (`extend-select = ["I"]`)
- **Structure:** Simple and clear - favor readability over cleverness
- **Error Handling:** Use `logging.exception()` for exceptions to include full traceback in logs
- **Type Hints:** Use Python type hints for function signatures
- **Docstrings:** Use triple-quoted docstrings with Args/Returns sections for public functions

### Architecture Patterns

- **Separation of Concerns:**
  - `ssh_mcp/ssh_client.py` - SSH configuration and client logic
  - `ssh_mcp/mcp.py` - MCP server and tool definitions
  - `ssh_mcp/model/` - Pydantic models for data validation
  
- **Singleton Pattern:** SSH client uses lazy initialization via `get_ssh_client()`
- **Configuration:** Environment variables for paths (`SSH_CONFIG_PATH`, `PROXY_CONFIG_PATH`, `MCP_TRANSPORT`)
- **Async Tools:** MCP tools are async functions decorated with `@mcp.tool()`

### Testing Strategy

- **Framework:** pytest with pytest-asyncio for async tests
- **Mocking:** pytest-mock for mocking external dependencies
- **Test Structure:** Class-based test organization (e.g., `TestSSHConfigBasic`)
- **Naming:** Test methods prefixed with `test_` and descriptive names
- **Coverage:** Unit tests for SSH config, client, and MCP tools

### Git Workflow

- **Default Branch:** main
- **Repository:** github.com/sondt2709/ssh-mcp-py
- **Pre-commit:** Configured with pre-commit hooks for linting

## Domain Context

**SSH Configuration:**
- Uses Paramiko's `SSHConfig` class to parse standard SSH config files
- Supports Host aliases, HostName, Port, User, and IdentityFile directives
- Default config location: `~/.ssh/config`

**MCP Tools Provided:**
1. `execute_ssh_command` - Execute commands on remote hosts (with timeout and output length limits)
2. `list_ssh_hosts` - List all configured SSH hosts
3. `get_host_info` - Get detailed host configuration
4. `test_ssh_connection` - Test SSH connectivity

**Proxy Support:**
- Optional SOCKS5 proxy per host via JSON configuration
- Proxy config includes: host, port, username, password

## Important Constraints

- **Python Version:** Requires Python 3.10 or higher
- **Timeout Limits:** SSH command timeout: 1-300 seconds
- **Output Limits:** Max stdout/stderr length: 1-10,000,000 characters
- **Security:** Uses SSH keys from config files (no password authentication in code)
- **Transport:** Supports stdio, sse, and streamable-http MCP transports

## External Dependencies

- **SSH Config File:** Standard `~/.ssh/config` (or custom path via `SSH_CONFIG_PATH`)
- **Proxy Config File:** Optional JSON file (path via `PROXY_CONFIG_PATH`)
- **SSH Keys:** Identity files referenced in SSH config
- **Remote Hosts:** Target VMs/servers accessible via SSH

**Documentation References:**
- https://modelcontextprotocol.io/quickstart/server
- https://github.com/modelcontextprotocol/quickstart-resources
- https://docs.paramiko.org/en/stable/
