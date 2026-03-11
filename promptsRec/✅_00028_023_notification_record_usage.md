Primary Executor: Codex
Task Type: Backend + Frontend Integration
Stage: 023
Goal: Implement notification record usage in the workflow so structured notification content and delivery status can be stored, viewed, and prepared for future external integration.
Execution: RUNPROMPT

---

# Context

The project has already completed or planned:

- tool master search integration
- order submission workflow
- order list loading
- keeper confirmation workflow
- structured message preview UI
- final confirmation workflow

The next business step is to implement notification record usage.

Important:

At this stage, the system should store and manage notification-related records, but it does NOT need to actually send Feishu or WeChat messages yet.

This task focuses on:

1. storing notification content
2. storing notification metadata
3. exposing notification records in the workflow
4. preparing the system for future external messaging integration

Do NOT implement actual Feishu sending in this task.

---

# Required References

Read before implementing:

docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/STRUCTURED_MESSAGE_PREVIEW_UI.md
docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md
docs/FINAL_CONFIRMATION_IMPLEMENTATION.md
docs/API_SPEC.md
docs/AI_DEVOPS_ARCHITECTURE.md

Also inspect relevant backend and frontend files, including but not limited to:

- web_server.py
- database.py
- backend/services/tool_io_service.py
- order detail page
- keeper processing page
- frontend API wrappers

---

# Core Task

Implement notification record usage using the real database schema and existing workflow.

The system must support:

1. creating notification records from structured message content
2. associating notification records with an order
3. storing notification type and current status
4. displaying notification records in the UI
5. keeping the implementation ready for future external send integration

The workflow should support internal storage first.

---

# Required Work

## A. Inspect Notification Record Storage

Using the real schema, inspect the table used for notification record storage.

Determine:

1. how notification records are stored
2. what fields exist for:
   - order association
   - notification type
   - content
   - receiver
   - send status
   - send time
   - retry count
   - response or remarks
3. what fields need to be used by the current workflow

Do not assume exact field names.
Use real schema inspection.

---

## B. Define Notification Use Cases

From the current workflow, identify where notification records should be created.

At minimum support internal record creation for:

1. keeper request message
2. transport notification message
3. any other structured workflow message already supported by the current system

Do not invent unsupported workflow branches.

---

## C. Backend Notification Record Logic

Implement or complete backend logic so that notification records can be created and queried.

At minimum support:

1. create notification record for a given order
2. query notification records for a given order
3. update notification status fields if applicable
4. return notification records to frontend

The implementation must:

- follow the existing DatabaseManager style
- preserve existing workflow logic
- not require external send integration yet

Do NOT redesign the backend architecture.

---

## D. Integration with Existing Workflow

Integrate notification record creation into the existing workflow where appropriate.

Possible trigger points may include:

- structured message generation
- keeper confirmation
- transport preparation
- order detail review

Use the current business flow and actual available data to decide the safest integration points.

The goal is to ensure notification records are not isolated data, but are tied to real workflow events.

---

## E. Frontend Display

Update the relevant frontend page(s) so notification records can be displayed.

Possible pages include:

- order detail page
- keeper processing page

The UI should support:

1. viewing notification history for the order
2. viewing notification type
3. viewing notification content summary
4. viewing send status
5. viewing send time if available

Use the current UI migration direction.
Do not redesign the entire page again.

---

## F. Status Handling

Notification records should support an internal status model appropriate for current non-external usage.

Possible practical states may include:

- generated
- pending
- sent
- failed

Use the real schema and current business meaning.
Do not invent unsupported states if the schema already defines them.

At this stage, records may remain in generated or pending status if no real external send action happens yet.

---

## G. Documentation

Create:

docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md

This document must include:

1. schema inspection summary
2. notification record fields actually used
3. creation trigger points
4. query/display integration
5. status handling strategy
6. frontend display integration
7. limitations before Feishu integration

---

# Constraints

1. Do not implement actual Feishu sending yet.
2. Do not implement actual WeChat sending yet.
3. Do not hardcode field names.
4. Always inspect the real schema first.
5. Do not redesign the database architecture.
6. Preserve current workflow logic.
7. Keep SQL Server compatibility.
8. Keep code and comments in English.
9. Keep changes minimal, safe, and production-oriented.

---

# Completion Criteria

The task is complete when:

1. notification records can be created and stored
2. notification records are associated with orders
3. notification records can be queried and displayed in UI
4. status handling is defined and working
5. docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md exists and is up-to-date