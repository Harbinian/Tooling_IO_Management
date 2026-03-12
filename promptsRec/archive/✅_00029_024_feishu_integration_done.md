Primary Executor: Codex
Task Type: Backend + Frontend Integration
Stage: 024
Goal: Implement Feishu notification integration using the existing notification record workflow and structured message generation, while preserving current business logic and database architecture.
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
- notification record usage

The next step is to implement actual Feishu notification integration.

At this stage, the system should be able to:

1. generate notification content
2. send notification content to Feishu
3. store send results into notification records
4. display send status in the UI
5. keep the workflow stable if Feishu sending fails

Important:

Do NOT implement WeChat integration in this task.
WeChat remains copy-only for now.

---

# Required References

Read before implementing:

docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/STRUCTURED_MESSAGE_PREVIEW_UI.md
docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md
docs/API_SPEC.md
docs/AI_DEVOPS_ARCHITECTURE.md

Also inspect relevant backend and frontend files, including but not limited to:

- web_server.py
- database.py
- backend/services/tool_io_service.py
- backend files related to notification creation
- order detail page
- keeper processing page
- frontend API wrappers
- any current configuration files related to environment variables or webhook settings

---

# Core Task

Implement Feishu integration using the existing workflow and notification record storage.

The system must support:

1. sending a structured notification to Feishu
2. associating that send attempt with an order
3. writing notification send result to the notification record table
4. exposing send status to the frontend
5. keeping the system safe if Feishu is unavailable or misconfigured

Use the current business workflow and real database schema.

---

# Required Work

## A. Inspect Current Notification Record Design

Using the real schema and current codebase, inspect how notification records are currently stored.

Determine:

1. how records are linked to orders
2. what fields can store:
   - notification type
   - message content
   - receiver or target
   - send status
   - send time
   - retry count
   - response payload or remarks
3. how Feishu send results should be mapped into the existing schema

Do not assume exact field names.
Use real schema inspection.

---

## B. Inspect Feishu Configuration Strategy

Determine how Feishu webhook configuration should be loaded safely.

Possible sources may include:

- environment variables
- existing config system
- settings object

The implementation must be robust:

1. if webhook config is missing, the system must not crash
2. configuration errors must be visible
3. send attempts must fail gracefully and be recorded

Do not hardcode secrets into source code.

---

## C. Implement Backend Feishu Send Logic

Implement or complete backend logic for sending structured messages to Feishu.

Requirements:

1. accept or generate a structured message payload
2. call the Feishu webhook using the configured endpoint
3. capture success or failure result
4. store the result in notification records
5. return a clear response to frontend

The implementation must:

- follow the current backend architecture
- keep SQL Server integration unchanged
- keep notification storage aligned with the current record model

Do NOT redesign the notification subsystem from scratch.

---

## D. Integrate with Existing Workflow

Integrate Feishu sending into the appropriate workflow points.

Use the current business flow and current available structured message generation.

Possible trigger points may include:

- keeper request notification
- transport notification

Choose only workflow points that already exist and are stable in the current system.

Do not invent unsupported workflow branches.

---

## E. Frontend Integration

Update the relevant frontend page(s) so users can trigger Feishu send actions where appropriate.

Possible pages include:

- keeper processing page
- order detail page
- structured message preview area

The UI should support:

1. send to Feishu action
2. loading state during sending
3. success feedback
4. failure feedback
5. display of latest notification send status

Do not redesign unrelated UI pages.

---

## F. Failure Handling

The system must handle Feishu send failures safely.

If sending fails:

1. the order workflow must not be corrupted
2. the failure must be recorded
3. the UI must show a clear message
4. retry should remain possible later if supported by the current design

Do not let external messaging failure break the core order workflow.

---

## G. Verification

After implementation, verify all of the following:

1. a real Feishu send attempt can be triggered
2. notification content is sent in the expected format
3. send success is stored in notification records
4. send failure is also stored correctly
5. frontend can display send result
6. core business workflow remains stable

If a real webhook is unavailable in the current environment, implement safe verification with the actual configured integration path and document the limitation clearly.

---

## H. Documentation

Create:

docs/FEISHU_INTEGRATION_IMPLEMENTATION.md

This document must include:

1. schema inspection summary
2. configuration loading strategy
3. send flow description
4. notification record mapping
5. frontend trigger placement
6. failure handling strategy
7. verification result
8. remaining limitations or assumptions

---

# Constraints

1. Do not implement WeChat integration yet.
2. Do not hardcode secrets.
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

1. Feishu send action is implemented
2. send result is stored in notification records
3. frontend can trigger and view Feishu send status
4. failures are handled safely
5. docs/FEISHU_INTEGRATION_IMPLEMENTATION.md exists