# Change: Add Reboot VM Support

## Why

Users need the ability to reboot VMs without performing separate stop and start operations. Reboot is a common operational task for applying configuration changes, recovering from hangs, or refreshing system state while maintaining the VM's resource allocation.

## What Changes

- Add `reboot_vm` abstract method to `BaseProvider`
- Implement `reboot_vm` in AWS provider (using EC2 `reboot_instances` API)
- Implement `reboot_vm` in Azure provider (using `begin_restart` API)
- Add `reboot_vm` MCP tool with YAML output format
- Add `force` parameter for hard reboot support (where supported)

## Impact

- Affected specs: `vm-power-management`
- Affected code:
  - `vm_mcp/providers/base.py` - Add abstract method
  - `vm_mcp/providers/aws.py` - Add AWS implementation
  - `vm_mcp/providers/azure.py` - Add Azure implementation
  - `vm_mcp/mcp.py` - Add MCP tool
  - `tests/test_mcp_tools.py` - Add tests
