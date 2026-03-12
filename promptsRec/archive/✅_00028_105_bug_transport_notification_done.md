Primary Executor: Codex
Task Type: Bug Fix
Stage: 105
Goal: Prevent transport notification failures from advancing order workflow state
Execution: RUNPROMPT

## Context / 上下文

Code review and Dev Inspector found a backend workflow bug in the transport notification path.

`backend/services/tool_io_service.py` now attempts to send a Feishu webhook inside `notify_transport()`.
However, when the webhook is missing or the send fails, the function still:

- updates the notification record
- advances the order status to `transport_notified`
- writes a log with `after_status = transport_notified`
- returns `success: True`

This creates a false-positive workflow transition: the system records that transport was notified even when no notification was actually delivered.

This is a backend bug and must be handled by Codex.

## Required References / 必需参考

- `backend/services/tool_io_service.py`
- `database.py`
- `docs/API_SPEC.md`
- `docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md`
- `docs/FINAL_CONFIRMATION_IMPLEMENTATION.md`
- `docs/BUG_WORKFLOW_RULES.md`
- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`
- `docs/README_AI_SYSTEM.md`

## Core Task / 核心任务

Investigate and fix the transport notification workflow so that order state changes remain consistent with actual delivery results.

The fix must ensure that:

- failed notification delivery does not incorrectly advance the order to `transport_notified`
- API response semantics match the real send result
- notification records, order status, and operation logs remain internally consistent

## Required Work / 必需工作

1. Inspect the real implementation in `backend/services/tool_io_service.py`, including:
   - `notify_transport()`
   - related notification-record helpers
   - any existing send-status and workflow-state assumptions

2. Inspect the real database integration in `database.py` before changing behavior:
   - confirm how `add_tool_io_notification()` and `update_notification_status()` persist status
   - confirm whether any helper already exists for partial-send / failed-send handling

3. Inspect the documented workflow contract before modifying code:
   - expected transition into `transport_notified`
   - whether final confirmation depends on successful transport notification
   - whether docs need correction after the code fix

4. Implement a minimal safe fix.
   The implementation must be based on the real codebase, not assumptions.

5. Verify the result with appropriate local checks.
   At minimum:
   - targeted reasoning over success path and failure path
   - backend syntax validation for touched Python files
   - any focused test or manual verification that is feasible in the current environment

6. If the fix changes real behavior, complete the repository prompt workflow:
   - archive this prompt using the repository archive convention
   - write a run report under `logs/prompt_task_runs/`
   - write a rectification log under `logs/codex_rectification/` if a real correction is implemented

## Constraints / 约束条件

- Do not assume database field names, notification semantics, or workflow states without inspecting the real implementation.
- Do not redesign the broader workflow unless inspection proves it is necessary.
- Keep the change minimal and safe.
- Do not hand-edit generated frontend artifacts.
- Do not skip the required reporting and archive steps if the prompt is executed.

## Completion Criteria / 完成标准

This task is complete only if:

1. The root cause is identified from the actual code and documented in the execution record.
2. `notify_transport()` no longer reports success while silently failing delivery and still advancing workflow state.
3. Order status, notification record status, and operation log behavior are consistent in both success and failure scenarios.
4. Any affected documentation is updated if the fix changes the documented contract.
5. Required RUNPROMPT lifecycle artifacts are produced when the task is executed.
