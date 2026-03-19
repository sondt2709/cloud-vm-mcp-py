## 1. Dependencies and Configuration

- [x] 1.1 Add `alibabacloud-ecs20140526` and `alibabacloud-tea-openapi` to `pyproject.toml` dependencies
- [x] 1.2 Create `AlibabaAccount` Pydantic model in `vm_mcp/model/credentials.py` with fields: `alias`, `access_key_id`, `access_key_secret`, `regions`
- [x] 1.3 Create `AlibabaConfig` Pydantic model with `accounts: list[AlibabaAccount]`
- [x] 1.4 Update `ProvidersConfig` to accept `AlibabaConfig` in the providers dict and add `get_alibaba_accounts()` method

## 2. Provider Implementation

- [x] 2.1 Create `vm_mcp/providers/alibaba.py` with `AlibabaProvider` class extending `BaseProvider`
- [x] 2.2 Implement `provider_name` property returning `"alibaba"` and `tenant_alias` property
- [x] 2.3 Implement `ALIBABA_STATE_MAP` mapping ECS states (Running, Starting, Stopping, Stopped, Pending, Expired) to `VMState` enum
- [x] 2.4 Implement lazy ECS client initialization per region using `alibabacloud-ecs20140526` SDK
- [x] 2.5 Implement `list_vms()` — query `DescribeInstances` per region, paginate results, wrap in `asyncio.to_thread()`
- [x] 2.6 Implement `get_vm_details()` — query `DescribeInstanceAttribute`, extract IPs, type, creation time
- [x] 2.7 Implement `start_vm()` — call `StartInstance` API
- [x] 2.8 Implement `stop_vm()` — call `StopInstance` API with `ForceStop` parameter
- [x] 2.9 Implement `reboot_vm()` — call `RebootInstance` API

## 3. Registry Integration

- [x] 3.1 Update `vm_mcp/providers/registry.py` to import `AlibabaProvider` and instantiate it from `AlibabaConfig` accounts
- [x] 3.2 Verify `list_providers` MCP tool includes Alibaba accounts (no code change expected — follows existing pattern)

## 4. Testing

- [x] 4.1 Add credential validation tests for `AlibabaAccount` and `AlibabaConfig` in `tests/test_credentials.py`
- [x] 4.2 Create `tests/test_alibaba_provider.py` with unit tests for state mapping, composite ID format, and mocked SDK calls
- [x] 4.3 Add Alibaba provider to registry tests in `tests/test_providers.py`
- [x] 4.4 Add Alibaba scenarios to MCP tool tests in `tests/test_mcp_tools.py`

## 5. Configuration and Documentation

- [x] 5.1 Add example Alibaba Cloud section to `providers.yaml` (commented out or with placeholder values)
- [x] 5.2 Update `README.md` with Alibaba Cloud setup instructions and credential requirements
