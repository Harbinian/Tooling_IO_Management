# Codex Review 2026-03-13

Repository: `E:\CA001\Tooling_IO_Management`

Review basis:
- current workspace state on 2026-03-13
- all prompt run reports written today under `logs/prompt_task_runs/`
- `docs/ARCHITECTURE_INDEX.md`
- `docs/RBAC_DESIGN.md`
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md`
- `docs/API_SPEC.md`
- `docs/AI_PIPELINE.md`
- `AGENTS.md`

This review combines repository inspection with log-backed validation of today's prompt-task outputs. I used the run reports to distinguish what was actually verified today versus what was only claimed or only syntax/build checked.

## Validated Today

- `promptsRec/archive/` exists and is populated, matching the `049_safe_repo_context_slimming` run report.
- the current frontend still passes `npm run build`
- the review-relevant 039-042 run reports explicitly record that live SQL Server / Feishu verification was not performed

## Findings

### 1. High: users without resolved data-scope configuration are still granted order visibility by fallback logic

Files:
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L91)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L133)
- [backend/services/rbac_data_scope_service.py](/E:/CA001/Tooling_IO_Management/backend/services/rbac_data_scope_service.py#L140)

Problem:
- `resolve_order_data_scope()` falls back to `["SELF", "ASSIGNED"]` whenever no scope rows resolve and `user_id` exists.
- This means missing or incomplete RBAC data-scope configuration no longer denies access; it silently grants a compatibility scope instead.

Why this matters after today's log review:
- today's prompt logs include RBAC-related fixes, but there is no log evidence that this fallback was intentionally approved as the final authorization policy
- in practice, this hides configuration defects instead of surfacing them

Impact:
- users can continue to see self-created and assigned orders even when their explicit data-scope setup is broken or absent
- RBAC rollout defects become operationally invisible

Recommendation:
- deny by default when no scope rows resolve, or gate the compatibility fallback behind an explicit feature flag / documented policy
- add diagnostics so administrators can detect fallback-scoped users

### 2. High: the preview flow still persists a real order record for a read-intent action

Files:
- [frontend/src/pages/tool-io/OrderCreate.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/tool-io/OrderCreate.vue#L343)
- [frontend/src/pages/tool-io/OrderCreate.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/tool-io/OrderCreate.vue#L346)
- [frontend/src/pages/tool-io/OrderCreate.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/tool-io/OrderCreate.vue#L352)

Problem:
- `handlePreview()` calls `createOrder(buildPayload())`, then uses the created `order_no` to generate preview text.
- Preview therefore allocates a real order number and writes a draft order even if the user only wants to preview content.

Why this matters after today's log review:
- several workflow tasks today focused on audit logs, notifications, transport states, and location updates
- every preview-generated draft can now also affect downstream metrics, logs, and operational traceability

Impact:
- orphan draft orders accumulate from non-committal preview actions
- dashboard counts, audit trails, and order history are polluted by records that were never intended as real business operations

Recommendation:
- add a non-persistent preview endpoint that renders keeper text from transient payload data
- if temporary persistence is unavoidable, mark and clean up preview-only drafts explicitly

### 3. Medium: `database.py` still carries duplicate definitions of core workflow functions, leaving dead code that can absorb future fixes

Files:
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1724)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1873)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1799)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L1977)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L2123)
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L2185)

Problem:
- `create_tool_io_order`, `submit_tool_io_order`, and `search_tools` are each defined twice in the same file.
- Python only uses the later definition, so the earlier bodies are dead at runtime but still visible to reviewers and future editors.

Why this matters after today's log review:
- today's backend refactor and bug-fix tasks touched adjacent workflow code heavily
- leaving duplicate implementations in place materially raises the chance of a future fix being applied to the wrong copy

Impact:
- review conclusions can drift from real runtime behavior
- future changes can appear merged yet have no effect if they land in the shadowed definition

Recommendation:
- remove the earlier shadowed implementations
- keep one authoritative implementation per function and move compatibility concerns into wrappers, not duplicated bodies

### 4. Medium: today's 039-042 task logs confirm that critical workflow changes were not validated against live integrations

Files:
- [run_20260313_142215_039_notification_service_framework.md](/E:/CA001/Tooling_IO_Management/logs/prompt_task_runs/run_20260313_142215_039_notification_service_framework.md)
- [run_20260313_142441_040_feishu_notification_adapter.md](/E:/CA001/Tooling_IO_Management/logs/prompt_task_runs/run_20260313_142441_040_feishu_notification_adapter.md)
- [run_20260313_142847_041_transport_workflow_state.md](/E:/CA001/Tooling_IO_Management/logs/prompt_task_runs/run_20260313_142847_041_transport_workflow_state.md)
- [run_20260313_143119_042_tool_location_management.md](/E:/CA001/Tooling_IO_Management/logs/prompt_task_runs/run_20260313_143119_042_tool_location_management.md)

Problem:
- the run reports explicitly state that live SQL Server mutation tests, live notification persistence tests, live Feishu delivery tests, and real transport-state transition verification were not executed
- current repository state still contains those features, but there is no log-backed evidence from today that they were exercised end to end

Impact:
- notification, transport, and location-management changes remain only partially validated
- release-readiness confidence should not be inferred from syntax checks and frontend builds alone

Recommendation:
- treat 039-042 as source-verified but integration-unverified until a live environment run is recorded
- add one reproducible end-to-end validation script or checklist per critical workflow milestone

### 5. Medium: copy-to-clipboard still relies entirely on `navigator.clipboard` with no degraded path

Files:
- [frontend/src/components/tool-io/NotificationPreview.vue](/E:/CA001/Tooling_IO_Management/frontend/src/components/tool-io/NotificationPreview.vue#L129)
- [frontend/src/components/tool-io/NotificationPreview.vue](/E:/CA001/Tooling_IO_Management/frontend/src/components/tool-io/NotificationPreview.vue#L133)

Problem:
- `handleCopy()` assumes `navigator.clipboard.writeText` is available and permitted
- there is no fallback path for restricted browser contexts or embedded shells

Impact:
- a common operator workflow can fail in constrained environments with only a generic toast

Recommendation:
- feature-detect clipboard support and add a textarea/select fallback
- at minimum, offer a manual select/copy path when direct clipboard write fails

## Residual Risk / Gaps

- I validated today's run reports as evidence, but I did not replay every prompt task in a live SQL Server / Feishu environment.
- The strongest current evidence is static validation: source inspection, prompt logs, and a successful frontend build.
- The highest-risk unresolved items remain authorization fallback and preview side effects, because both can alter real business visibility or data shape without obvious operator intent.
