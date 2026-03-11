Primary Executor: Codex
Task Type: Backend + Frontend Integration
Stage: 014
Goal: Implement the keeper confirmation workflow using the real database schema and existing order data.
Execution: RUNPROMPT

---

# Context

The project has already completed:

- tool master search using real SQL Server data
- tool selection in the order creation page
- order submission workflow
- order list loading
- database table creation for tool IO workflow

The next business step is:

Keeper confirmation workflow.

The system must now support the keeper side of the process.

Important constraint:

Do NOT assume fixed database field names.
Inspect the actual schema and existing implementation before making changes.

---

# Required References

Read before implementing:

docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/ORDER_SUBMISSION_IMPLEMENTATION.md
docs/AI_DEVOPS_ARCHITECTURE.md

Also inspect relevant backend and frontend files, including but not limited to:

- web_server.py
- database.py
- backend/services/tool_io_service.py
- frontend order list page
- frontend keeper processing page
- frontend API wrappers

---

# Core Task

Implement the keeper confirmation workflow so that a keeper can:

1. view pending orders
2. open an order for processing
3. inspect tool items in the order
4. confirm actual location and status information
5. submit keeper confirmation
6. update order workflow state
7. write operation logs

This workflow must use the real database schema and existing order data.

---

# Required Work

## A. Inspect Existing Order Data Structures

Using the existing backend connection and current codebase:

1. identify the order header table
2. identify the order item table
3. identify the operation log table
4. inspect how current order status is stored
5. inspect how current item-level confirmation data can be stored or extended

Do not assume exact field names.
Use real schema inspection.

---

## B. Identify Keeper Pending Orders

Implement backend logic to identify orders that are pending keeper action.

Determine from the real schema:

- which order status represents submitted but not yet keeper-confirmed
- how the keeper processing page should query these orders

Do not hardcode arbitrary status values if the existing workflow already defines them.

---

## C. Backend API for Keeper Workflow

Implement or complete APIs needed for keeper processing.

At minimum support:

1. query keeper-pending orders
2. query one order with item details
3. submit keeper confirmation

If existing APIs already partially cover this, extend them instead of inventing duplicates.

The keeper confirmation backend logic must:

- validate the target order
- validate the submitted tool item data
- update keeper-related fields in order items
- update order workflow state
- insert operation log records
- return updated order information or confirmation result

Follow the existing DatabaseManager style.
Do NOT redesign the backend architecture.

---

## D. Frontend Keeper Processing Page

Implement or complete the keeper processing page so that it supports:

1. loading pending orders
2. selecting one order
3. displaying order basic information
4. displaying the tool item list
5. editing keeper-confirmed values where appropriate
6. entering keeper remarks if supported
7. submitting keeper confirmation

Keep the UI aligned with the existing Element Plus style.

Do NOT redesign unrelated pages.

---

## E. Item-Level Confirmation

For each tool item in the selected order, support keeper-side confirmation data based on the real schema.

Possible keeper-confirmed information may include:

- confirmed location
- confirmed status
- keeper remark
- keeper result / availability result

Do not invent fields blindly.
Use what actually exists in the schema or apply minimal safe extension if clearly necessary and consistent with current table design.

---

## F. Order Status Transition

When keeper confirmation is submitted:

1. update order status to the correct next workflow state
2. keep item-level status aligned if item-level state exists
3. ensure the transition is consistent with PRD and architecture workflow

Do not invent a new workflow state if the real system already has one that fits.

---

## G. Operation Logging

Insert keeper confirmation logs into the operation log table.

At minimum record:

- order identifier
- operator identifier
- action type
- previous state
- next state
- timestamp
- remarks if available

Use the real schema.

---

## H. Documentation

Create:

docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md

This document must include:

1. tables used
2. schema inspection summary
3. keeper pending order rule
4. APIs implemented or updated
5. request/response structure
6. frontend page changes
7. status transition used
8. logging behavior
9. any schema limitations or assumptions

---

# Constraints

1. Do not hardcode field names.
2. Always inspect the real schema first.
3. Do not redesign the database architecture.
4. Preserve current working order submission logic.
5. Keep SQL Server compatibility.
6. Keep code and comments in English.
7. Keep frontend style consistent with existing UI.
8. Keep changes minimal, safe, and production-oriented.

---

# Completion Criteria

The task is complete when:

1. keeper can view pending orders
2. keeper can open an order and view tool items
3. keeper can submit confirmation
4. order workflow state is updated correctly
5. operation logs are written
6. docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md exists