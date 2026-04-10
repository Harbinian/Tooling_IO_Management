# Codex Review 2026-03-24

Repository: `E:\CA001\Tooling_IO_Management`

Review basis:
- reviewer model output from current `review` action
- current workspace paths referenced by findings

## Findings

### 1. P0: invalid SQL identifiers break core order persistence

Files:
- [backend/database/repositories/order_repository.py](/E:/CA001/Tooling_IO_Management/backend/database/repositories/order_repository.py#L97)

Problem:
- order repository SQL literals contain mojibake and malformed bracketed identifiers
- SQL Server cannot parse/resolve these identifiers against existing schema

Impact:
- create/query/update order flows fail at runtime with syntax or object resolution errors
- core business operations for tool IO orders are blocked

Recommendation:
- restore correct table and column identifiers in all order DML statements
- run representative create/query/update integration checks against SQL Server

### 2. P1: reject wrapper signature and argument mapping regression

Files:
- [database.py](/E:/CA001/Tooling_IO_Management/database.py#L319)

Problem:
- `reject_tool_io_order` wrapper now accepts 4 args, while service callers still pass 5 args
- forwarded argument order to `repo.reject_order` is incorrect

Impact:
- rejection requests raise `TypeError` in current call path
- even 4-arg calls would map operator fields into wrong parameter slots

Recommendation:
- restore 5-argument wrapper signature: `order_no`, `reject_reason`, `operator_id`, `operator_name`, `operator_role`
- align forwarding order exactly with repository method signature

### 3. P2: feedback create path allows client-controlled status

Files:
- [backend/services/feedback_service.py](/E:/CA001/Tooling_IO_Management/backend/services/feedback_service.py#L216)

Problem:
- create path accepts and persists `payload.status` from client input
- authenticated users can submit feedback already marked `reviewed` or `resolved`

Impact:
- intended admin triage workflow can be bypassed
- workflow integrity and audit semantics are weakened

Recommendation:
- enforce initial status as server-side constant `pending` on create
- restrict status transitions to privileged/admin review flow only
