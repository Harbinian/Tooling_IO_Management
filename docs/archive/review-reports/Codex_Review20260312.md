# Codex Review 2026-03-12

Repository: `E:\CA001\Tooling_IO_Management`

Review basis:
- `docs/ARCHITECTURE_INDEX.md`
- `docs/RBAC_DESIGN.md`
- `docs/RBAC_DATABASE_SCHEMA.md`
- `docs/API_SPEC.md`
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md`
- `docs/AI_PIPELINE.md`
- `docs/PROMPT_TASK_CONVENTION.md`

This review is based on the current workspace state and checks whether the implementation still matches the documented architecture, RBAC model, API contract, and prompt workflow conventions.

## Findings

### 1. High: ORG data scope violates the documented role-assignment model by expanding across all user organizations

Files:
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L80)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L97)

Problem:
- `_resolve_scope_context()` first loads all role scopes for the user, then merges every discovered scope type into one set.
- Once `ORG` or `ORG_AND_CHILDREN` appears anywhere in that set, the code builds `direct_org_ids` from `current_org`, `default_org`, and every entry in `role_orgs`.
- There is no preservation of the role-to-org binding, so a user with one org-limited role and another role in a different organization receives the union of both organizations.

Document mismatch:
- `docs/RBAC_DESIGN.md` defines `sys_user_role_rel.org_id` as part of the user-role assignment model and explicitly states that a user may have multiple roles in different organizations.
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md` says merged scopes should not broaden beyond active role assignments.
- The implementation does broaden beyond the specific role assignment that granted the data scope.

Impact:
- Multi-organization users can see orders outside the org that should actually be constrained by the scoped role.
- This is a real authorization expansion, not just a UI inconsistency.

Recommendation:
- Carry role-to-org bindings through scope resolution.
- Evaluate scope per role assignment, then union only the data actually granted by each assignment.

### 2. High: Order visibility semantics are weaker than the repository’s stated organization-isolation model

Files:
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L136)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L148)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L171)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L177)

Problem:
- For `ORG` and `ORG_AND_CHILDREN`, the SQL filter and the in-memory matcher both allow an order when `initiator_id`, `keeper_id`, or `transport_assignee_id` belongs to the allowed org user set.
- That means an order created for another organization becomes visible to org A users as soon as a keeper or transporter from org A touches it.

Document mismatch:
- `docs/RBAC_DESIGN.md` frames data scope as data-level isolation, not participant overlap.
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md` documents the current participant-based approximation, but that directly weakens the organization access model defined by RBAC design.
- The repo currently treats an implementation limitation as if it were a valid authorization model.

Impact:
- Data isolation becomes participant-based instead of organization-owned.
- Visibility can grow over time simply because workflow participants change, which is usually not acceptable for organizational access control.

Recommendation:
- Define and persist a single authoritative order ownership field, then filter by that field.
- Until then, document the weaker semantics explicitly because the current behavior does not match a strict org-scope model.

### 3. High: The order schema is missing the organization ownership field needed to satisfy the documented RBAC data-scope model

Files:
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1535)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1554)
- [backend/services/tool_io_service.py](/E:/CA001/Tooling_IO_Management/backend/services/tool_io_service.py#L40)

Problem:
- The `tool_io_orders` schema stores user references such as initiator, keeper, and transport assignee, but no `org_id` or org snapshot.
- Order creation also does not stamp the current organization into the record.

Document mismatch:
- `docs/RBAC_DESIGN.md` defines organization and data scope as first-class RBAC concepts.
- `docs/RBAC_DATABASE_SCHEMA.md` establishes the organization-aware RBAC foundation through `sys_org` and `sys_user_role_rel.org_id`.
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md` explicitly admits that the current implementation has no dedicated `org_id` on orders.
- That limitation means the repository still does not have the persistence model required for stable org-scoped authorization.

Impact:
- For users who belong to multiple organizations, a created order cannot later be attributed to the organization context in which it was created.
- As a result, `ORG` and `ORG_AND_CHILDREN` access control remains inference-based and unstable even if the service logic is refined.

Recommendation:
- Add a persisted organization ownership field to the order record.
- Populate it at creation time from the authenticated organization context and migrate historical data with an explicit policy.

### 4. Medium: Prompt archive sequence numbers violate the documented pipeline/archive convention

Files:
- [promptsRec/✅_00037_030_rbac_permission_enforcement.md](/E:/CA001/Tooling_IO_Management/promptsRec/%E2%9C%85_00037_030_rbac_permission_enforcement.md)
- [promptsRec/✅_00037_033_login_page_and_auth_flow_ui_done.md](/E:/CA001/Tooling_IO_Management/promptsRec/%E2%9C%85_00037_033_login_page_and_auth_flow_ui_done.md)

Problem:
- Two archived prompt files share the same archive sequence `00037`.
- The repository workflow documents describe the archive number as a sequencing convention, so duplicates undermine ordering and dashboard assumptions.

Document mismatch:
- `docs/AI_PIPELINE.md` defines archived prompts as a sequential lifecycle artifact.
- `docs/PROMPT_TASK_CONVENTION.md` defines a single archive-number-based completion format.
- Duplicate archive sequence numbers break that convention and make prompt history non-canonical.

Impact:
- Any tooling that sorts by archive sequence can report the wrong completion order or collide on identifiers.
- This is especially risky for the `pipeline-dashboard` skill, which depends on prompt archive naming conventions.

Recommendation:
- Reassign one of the duplicate archive numbers and update any linked reports if they embed the old archive identifier.
- Add a pre-archive validation step to catch duplicate sequence numbers.

## Residual Risk / Gaps

- I did not treat build artifacts under `frontend/dist/` as review targets unless they affected source behavior.
- The highest-risk issues are backend authorization issues; those should be fixed before treating the RBAC rollout as complete.
- The current test suite appears to miss a multi-role, multi-organization authorization scenario, so the first three findings are unlikely to be caught automatically.
- I did not mark every documented approximation as a bug. Findings were limited to places where the code materially contradicts the architecture/RBAC intent or breaks repository workflow guarantees.
