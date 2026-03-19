## Why

The VM MCP server currently supports AWS and Azure, but Alibaba Cloud (Aliyun) is the largest cloud provider in Asia-Pacific and the third-largest globally. Adding Alibaba Cloud ECS (Elastic Compute Service) support enables users to manage VMs across all three major cloud platforms through a single unified MCP interface — critical for organizations with multi-cloud deployments spanning Western and Asian markets.

## What Changes

- Add a new `AlibabaProvider` implementing `BaseProvider` for Alibaba Cloud ECS instances
- Add `AlibabaAccount` credential model with AccessKey ID, AccessKey Secret, and region list
- Register the `alibaba` provider in the provider registry
- Extend `providers.yaml` configuration to support `alibaba` provider entries
- Add `alibabacloud-credentials` dependency (`alibabacloud-ecs20140526` SDK) to `pyproject.toml`
- Map Alibaba ECS instance states (Running, Starting, Stopping, Stopped) to the existing `VMState` enum

## Capabilities

### New Capabilities
- `alibaba-ecs-provider`: Alibaba Cloud ECS provider implementation — listing, details, start/stop/reboot for ECS instances with multi-account and multi-region support

### Modified Capabilities
- `provider-credentials`: Add Alibaba Cloud credential fields (access_key_id, access_key_secret, regions) and configuration validation

## Impact

- **Code**: New `vm_mcp/providers/alibaba.py`, updated `credentials.py`, `registry.py`
- **Dependencies**: New `alibabacloud-ecs20140526` and `alibabacloud-tea-openapi` packages
- **Configuration**: `providers.yaml` schema extended with `alibaba.accounts[]` section
- **Tests**: New test module for Alibaba provider, updated credential validation tests
- **No breaking changes**: Existing AWS/Azure functionality is unaffected
