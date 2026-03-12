Primary Executor: Codex
Task Type: Feature Implementation
Stage: 040
Goal: Implement the Feishu notification adapter on top of the existing notification service framework so internal notification records can be delivered to Feishu safely and traceably.
Execution: RUNPROMPT

---

# Context

The system has already completed or is completing:

- core tool IO workflow
- operation audit log system
- notification service framework
- RBAC / authentication / organization scope
- notification record storage

The notification framework already writes internal notification records into the database.

The next step is to add a Feishu delivery adapter so selected notification events can be sent externally.

This task must build on the existing notification service.

It must NOT redesign the notification model.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/NOTIFICATION_SERVICE_FRAMEWORK.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  
docs/RBAC_DESIGN.md  

Also inspect:

- current notification record table usage
- current backend notification service
- existing configuration loading approach
- current frontend notification-related UI if any

---

# Core Task

Implement a Feishu notification adapter that can:

1. transform internal notification records into Feishu message payloads
2. send messages to Feishu through configured webhook or adapter configuration
3. persist send result back into notification records
4. fail safely without breaking the main workflow
5. support future retry and status tracking

This task is about delivery integration, not about redesigning internal notification creation.

---

# Part 1 — Feishu Adapter Module

Create a backend module.

Suggested location:

backend/services/feishu_notification_adapter.py

Responsibilities:

- accept notification record or structured notification payload
- build Feishu-compatible message body
- send HTTP request to Feishu endpoint
- parse result
- return normalized send result

Keep the module isolated from business services.

---

# Part 2 — Configuration Loading

Load Feishu configuration from existing configuration mechanisms.

Examples may include:

- settings object
- environment variables
- config files already used by the project

The adapter must support at minimum:

- webhook URL
- enable / disable flag
- timeout
- optional default target identity if relevant to the current design

Do not hardcode secrets.

If configuration is missing:

- the system must not crash
- send attempt must fail gracefully
- the failure must be recorded

---

# Part 3 — Message Mapping

Map existing notification types to Feishu message content.

Use the current notification framework event types and message templates.

For each outgoing Feishu message, include enough business context such as:

- order number
- notification type
- concise workflow message
- responsible next action if available

Keep the message simple, operational, and readable.

Do not invent unsupported workflow data.

---

# Part 4 — Delivery Result Persistence

After each send attempt, update notification records with delivery result.

At minimum capture:

- send status
- send time
- response summary
- failure reason if any
- retry count if already modeled or safely extendable in current logic

Use the current notification record model where possible.

Do not redesign the table unless absolutely necessary and consistent with current architecture.

---

# Part 5 — Workflow Integration

Integrate Feishu delivery only at stable notification trigger points already supported by the current system.

Possible examples:

- keeper confirmation required
- transport required
- order completion notice

Use only trigger points already supported by current workflow and notification framework.

Do not invent new workflow branches.

---

# Part 6 — Safe Failure Handling

Feishu delivery must not block the main business transaction.

Rules:

- order state change must still succeed if Feishu send fails
- send failure must be recorded
- system must support later retry or manual re-send
- backend logs should contain useful diagnostics without leaking secrets

---

# Part 7 — Query / UI Compatibility

Ensure current or future frontend can read delivery status from notification records.

At minimum preserve or expose fields needed for UI such as:

- notification type
- status
- sent time
- failure summary

Do not redesign frontend pages in this task unless a very small compatibility update is needed.

---

# Part 8 — Verification

Validate the adapter under these scenarios:

1. valid Feishu configuration and successful send
2. missing configuration
3. invalid webhook
4. timeout or request failure
5. business workflow continues even if send fails

If no real Feishu environment is available, implement the real integration path and document what was verified versus what remains environment-dependent.

---

# Part 9 — Documentation

Create:

docs/FEISHU_NOTIFICATION_ADAPTER.md

The document must include:

1. adapter architecture
2. configuration loading rules
3. message mapping strategy
4. delivery result persistence
5. failure handling rules
6. workflow trigger points
7. verification notes
8. retry / future extension notes

---

# Constraints

1. Do not redesign the notification framework.
2. Do not redesign RBAC or workflow logic.
3. Do not hardcode secrets.
4. Do not let Feishu failure break core business flow.
5. Keep code and comments in English.
6. Keep implementation modular and production-oriented.

---

# Completion Criteria

The task is complete when:

1. Feishu adapter module exists
2. stable workflow notifications can be sent through Feishu
3. delivery results are persisted to notification records
4. send failure does not break business flow
5. docs/FEISHU_NOTIFICATION_ADAPTER.md exists and is up to date with the latest adapter architecture, configuration rules, message mapping, delivery result persistence, failure handling, workflow trigger points, verification notes, and retry / future extension notes