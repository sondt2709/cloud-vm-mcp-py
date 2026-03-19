## Context

The VM MCP server provides a unified interface for managing VMs across cloud providers. It currently supports AWS EC2 and Azure Compute via the `BaseProvider` abstract class, a provider registry, and Pydantic credential models. Each provider maps cloud-specific instance states to a shared `VMState` enum and uses `asyncio.to_thread()` to wrap synchronous SDKs.

Alibaba Cloud ECS follows a similar API pattern: REST-based with AccessKey authentication, region-scoped instance queries, and a well-defined set of instance states.

## Goals / Non-Goals

**Goals:**
- Add Alibaba Cloud ECS as a third provider following existing patterns
- Support multi-account, multi-region ECS instance management
- Maintain consistency with existing composite ID format (`alibaba:{alias}:{region}:{instance_id}`)
- Reuse the existing `BaseProvider` interface without modifications

**Non-Goals:**
- Supporting Alibaba Cloud services beyond ECS (e.g., RDS, SLB, OSS)
- Implementing Alibaba-specific features not in `BaseProvider` (e.g., security groups, VPC details)
- STS/RAM role-based authentication (AccessKey pair only for now)
- Region auto-discovery — regions are explicitly configured like AWS/Azure

## Decisions

### 1. SDK Choice: `alibabacloud-ecs20140526` (OpenAPI SDK v2)

Use Alibaba's official OpenAPI-based ECS SDK (`alibabacloud-ecs20140526`) rather than the older `aliyunsdkecs` (v1 SDK).

**Rationale**: The v2 SDK is actively maintained, has better typing, and follows the Tea/OpenAPI generation pattern used across all modern Alibaba Cloud SDKs. The v1 SDK is in maintenance mode.

**Alternative considered**: Raw HTTP calls via `alibabacloud-tea-openapi` — rejected because the typed ECS SDK provides better ergonomics and reduces error surface.

### 2. Credential Model: AccessKey ID + AccessKey Secret

Follow the same pattern as AWS: `access_key_id`, `access_key_secret`, plus `alias` and `regions`.

**Rationale**: This mirrors the AWS credential shape and is the most common authentication method for Alibaba Cloud programmatic access. The credential model maps naturally to the existing `ProvidersConfig` discriminated union pattern.

### 3. Provider Structure: Single file `alibaba.py`

Create `vm_mcp/providers/alibaba.py` following the same structure as `aws.py` — one class implementing `BaseProvider`, lazy client initialization per region, and `asyncio.to_thread()` for SDK calls.

**Rationale**: Keeps the provider pattern consistent. The ECS API surface for VM management is comparable to EC2, so the implementation complexity is similar (~250-300 lines).

### 4. State Mapping

Map Alibaba ECS instance states to `VMState`:
- `Running` → `running`
- `Starting` → `starting`
- `Stopping` → `stopping`
- `Stopped` → `stopped`
- `Pending` → `starting`
- `Expired` → `terminated`

**Rationale**: Direct semantic mapping. `Pending` is the initial creation state (similar to AWS `pending`). `Expired` maps to `terminated` as the instance is no longer usable.

### 5. Registry Integration

Add Alibaba to the existing `get_providers()` function in `registry.py` by checking for `alibaba` key in the providers config and instantiating `AlibabaProvider` per account.

**Rationale**: Same pattern as AWS/Azure registration — no changes to registry architecture needed.

## Risks / Trade-offs

- **[SDK availability]** The `alibabacloud-ecs20140526` package adds ~5 transitive dependencies (Tea, OpenAPI core, etc.) → Acceptable; these are lightweight and well-maintained. Pin versions in pyproject.toml.
- **[API rate limits]** Alibaba Cloud has per-region API rate limits that differ from AWS/Azure → Mitigation: the existing 60s per-provider timeout handles slow responses; document rate limit awareness in provider comments.
- **[Region naming]** Alibaba uses region IDs like `cn-hangzhou`, `ap-southeast-1` (some overlap with AWS naming) → Mitigation: no conflict since composite IDs include the provider prefix (`alibaba:...`).
- **[No STS support]** AccessKey-only auth means no temporary credentials or role assumption → Acceptable for v1; STS support can be added later without breaking changes.
