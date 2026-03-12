Primary Executor: Claude Code
Task Type: Platform Reliability
Stage: 045
Goal: Introduce runtime observability and monitoring capabilities so system health, workflow errors, and notification failures can be detected and diagnosed in production.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System has reached late-stage development.

The platform now includes:

authentication
RBAC
organization scope
order workflow
transport workflow
notification framework
Feishu integration
audit logging
dashboard metrics
tool location management

However, the system still lacks runtime observability.

Without observability:

workflow failures may go unnoticed

notification delivery failures cannot be tracked

system health cannot be quickly diagnosed

production incidents become difficult to debug

This task introduces basic observability for the platform.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  
docs/NOTIFICATION_SERVICE_FRAMEWORK.md  
docs/FEISHU_NOTIFICATION_ADAPTER.md  
docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md  

---

# Core Task

Introduce runtime monitoring and observability features.

The system must support:

structured runtime logging

workflow failure detection

notification delivery failure visibility

system health inspection endpoints

basic runtime diagnostics

---

# Part 1 — Structured Logging

Introduce structured logging across the backend.

Logs must include:

timestamp  
module  
action  
user_id if available  
order_id if applicable  
result status  

Logging should be applied to:

order workflow transitions

transport actions

notification generation

Feishu message sending

authentication events

RBAC permission failures

Use a centralized logging utility.

Suggested module:

backend/utils/logger.py

---

# Part 2 — Notification Failure Monitoring

Extend notification records so failures can be tracked.

Detect and log:

Feishu send failure

HTTP request failure

timeout

invalid webhook configuration

Failures must be visible through logs and queryable in the notification table.

---

# Part 3 — Workflow Error Detection

Introduce error detection for workflow transitions.

Examples:

invalid order state transition

missing transport assignment

unexpected location state

RBAC denial for expected operator

Such errors must be logged with enough context for debugging.

---

# Part 4 — System Health Endpoint

Introduce a health-check endpoint.

Example:

GET /api/system/health

The endpoint should check:

database connectivity

notification service readiness

Feishu adapter configuration presence

Return a structured health response.

---

# Part 5 — Error Classification

Introduce standardized error classification for server logs.

Examples:

AUTH_ERROR

RBAC_DENIED

WORKFLOW_ERROR

DATABASE_ERROR

NOTIFICATION_ERROR

EXTERNAL_SERVICE_ERROR

This helps operators diagnose incidents faster.

---

# Part 6 — Runtime Diagnostics

Add minimal diagnostic utilities.

Examples:

recent notification failures

recent workflow errors

recent authentication failures

These can be logged or optionally queryable.

Do not build a full admin console.

Focus on backend diagnostics.

---

# Part 7 — Documentation

Create:

docs/SYSTEM_OBSERVABILITY_AND_MONITORING.md

The document must include:

logging structure

error classification

health check endpoint

notification monitoring

workflow diagnostics

operational debugging guidelines

---

# Constraints

Do not redesign workflow logic.

Do not redesign RBAC.

Keep monitoring lightweight.

Do not introduce heavy external monitoring dependencies.

Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

structured logging is implemented

notification failures are traceable

workflow errors are logged

health endpoint exists

docs/SYSTEM_OBSERVABILITY_AND_MONITORING.md exists and is up to date with the latest features, logging structure, error classification, health check endpoint, notification monitoring, workflow diagnostics, and operational debugging guidelines