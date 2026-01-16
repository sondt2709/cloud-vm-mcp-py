"""VM MCP - Model Context Protocol for cloud VM management."""

from vm_mcp.mcp import mcp


def main():
    """Entry point for the VM MCP server."""
    mcp.run()


__all__ = ["main", "mcp"]
