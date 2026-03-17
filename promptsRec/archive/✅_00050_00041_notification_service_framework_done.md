Primary Executor: Codex
Task Type: Feature Implementation
Stage: 039
Goal: Implement a unified notification service framework that supports structured internal notifications and prepares the system for Feishu / external messaging integration.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System workflow includes multiple human roles:

- Team Leader (initiates request)
- Keeper (confirms tool availability)
- Transport Operator (forklift / crane)
- Planner or Supervisor (future extension)

In the current workflow, important state transitions require notifying the next responsible person.

Examples:

Team Leader submits order  
→ Keeper must be notified

Keeper confirms order  
→ Transport operator must be notified

Transport completes movement  
→ Order initiator or keeper must confirm

The database already contains a table:

工装出入库单_通知记录

However, the backend currently does not have a unified notification service that writes records into this table or standardizes notification messages.

This task builds the **notification framework** used by the system.

External integrations such as Feishu will be implemented in a later task.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  
docs/RBAC_DESIGN.md  

Also inspect the notification record table schema in the database.

---

# Core Task

Create a notification service responsible for:

- generating notification records
- standardizing message structure
- linking notifications to order lifecycle events
- enabling later integration with Feishu / external systems

This task focuses on internal notification storage and message generation.

---

# Part 1 — Notification Service Module

Create a backend module.

Suggested location:

backend/services/notification_service.py

Responsibilities:

create notification records

generate standardized message content

store notifications in the notification table

support querying notifications later

---

# Part 2 — Notification Types

Define notification event types.

Examples:

ORDER_CREATED

ORDER_SUBMITTED

KEEPER_CONFIRM_REQUIRED

TRANSPORT_REQUIRED

ORDER_COMPLETED

ORDER_CANCELLED

These types must be used consistently across the system.

---

# Part 3 — Notification Content Structure

Each notification should include structured content.

Example fields:

notification_type

order_id

target_user_id

target_role

message_title

message_body

created_time

status (unread / read / processed)

optional metadata

The service should standardize message generation so service layers only pass core parameters.

---

# Part 4 — Integration with Order Workflow

Integrate notification creation into order lifecycle events.

Examples:

Order created  
→ notify keeper group or responsible keeper

Order submitted  
→ notify keeper confirmation

Keeper confirmed  
→ notify transport operator

Order finished  
→ notify initiator

The logic should be implemented in service layers where state transitions occur.

---

# Part 5 — Query API Preparation

Prepare backend support for future notification queries.

At minimum support:

fetch notifications for current user

fetch notifications by order_id

mark notification as read

Actual frontend UI for notifications will be implemented later.

---

# Part 6 — Error Handling

Notification writing must not block the main business flow.

If notification writing fails:

- the main operation must succeed
- the error must be logged
- the system should allow retry later

---

# Part 7 — Message Template Design

Implement a simple message template mechanism.

Example concept:

ORDER_SUBMITTED → "Order {order_no} has been submitted and requires keeper confirmation."

Templates should be stored in code for now.

Future tasks may externalize them.

---

# Part 8 — Documentation

Create:

docs/NOTIFICATION_SERVICE_FRAMEWORK.md

The document must include:

notification purpose

notification event types

message structure

service architecture

integration with order workflow

future Feishu integration design

---

# Constraints

1. Do not implement Feishu integration in this task.
2. Do not redesign database schema unless necessary.
3. Keep notification writing lightweight.
4. Preserve existing workflow logic.
5. Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

notification_service module exists

order lifecycle events generate notification records

notifications are written into the notification table

basic query functions exist

docs/NOTIFICATION_SERVICE_FRAMEWORK.md exists