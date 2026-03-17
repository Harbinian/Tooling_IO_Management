Primary Executor: Codex
Task Type: Feature Implementation
Stage: 038
Goal: Implement the operation audit log system for the Tool IO workflow so every important business action is recorded in the audit table.
Execution: RUNPROMPT

---

Context

The system already contains an audit log table:

工装出入库单_操作日志

However the backend services currently do not consistently record operation logs.

A production-grade system must record:

who did what
when it happened
which order it affected
what the previous and next status were

This task implements a unified operation audit logging mechanism.

---

Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md
docs/PRD.md
docs/API_CONTRACT_SNAPSHOT.md
docs/RBAC_DESIGN.md

Inspect the existing database schema for the operation log table.

---

Core Task

Implement an audit log recording system for order lifecycle actions.

The system must automatically write records into the operation log table when key workflow actions occur.

---

Key Actions That Must Be Logged

Order creation

Order submission

Keeper confirmation

Transport start (if implemented)

Final confirmation

Order cancellation if supported

System-level corrections if present

---

Log Content

Each log entry must include:

order_id

operation_type

operator_user_id

operator_role if available

operation_time

previous_status

new_status

optional remark

---

Implementation Approach

Create a logging utility module.

Suggested location:

backend/services/audit_log_service.py

Responsibilities:

write operation log records

ensure consistent log structure

allow service layers to call it easily

---

Service Integration

Integrate audit logging into:

order creation service

order submission service

keeper confirmation service

final confirmation service

future transport workflow services

The log write should occur after successful state transitions.

---

Error Handling

Audit logging must never break the main business flow.

If logging fails:

the main transaction must not fail

but the error should be logged in the server logs.

---

Documentation

Create:

docs/OPERATION_AUDIT_LOG_SYSTEM.md

Include:

audit log purpose

fields used

where logs are written

integration points in services

future extension ideas

---

Completion Criteria

The task is complete when:

order creation generates audit log

order submission generates audit log

keeper confirmation generates audit log

final confirmation generates audit log

audit records exist in the operation log table

docs/OPERATION_AUDIT_LOG_SYSTEM.md exists and is up-to-date