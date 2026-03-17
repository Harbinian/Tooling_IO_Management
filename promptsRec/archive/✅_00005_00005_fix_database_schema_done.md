Primary Executor: Codex

Task Type: Database Schema and Code Alignment Fix

Goal:
Fix and align the existing SQL Server database module with the revised schema design documented in:

docs/SQLSERVER_SCHEMA_REVISION.md

This task must correct schema/code mismatches in the current database implementation while preserving the existing database access architecture.

---

# Context

The project already contains an existing database module implemented with:

- SQL Server
- pyodbc
- connection pool
- DatabaseManager
- existing Tool IO related CRUD functions

This existing database module is the implementation baseline.

The project does NOT want a new ORM-first or repository-first persistence redesign.

The goal is to correct and stabilize the current implementation.

---

# Required Inputs

Read and follow these files before making changes:

- docs/PRD.md
- docs/ARCHITECTURE.md
- docs/DB_SCHEMA.md
- docs/INHERITED_DB_ACCESS_REVIEW.md
- docs/SQLSERVER_SCHEMA_REVISION.md
- existing database module in the project

---

# Core Rules

1. Reuse the existing DatabaseManager and pyodbc access style.
2. Do NOT replace the current persistence architecture.
3. Keep Chinese table names and Chinese column names.
4. Do NOT rename physical database objects unless explicitly required by docs.
5. Fix schema/code mismatches first before extending functionality.
6. Use English in code, comments, and new helper names.
7. All file operations must assume UTF-8.

---

# Required Work

## A. Fix CREATE TABLE definitions

Update the current table creation SQL so it matches the corrected design in:

docs/SQLSERVER_SCHEMA_REVISION.md

Check and fix at least:

- 工装出入库单_主表
- 工装出入库单_明细
- 工装出入库单_操作日志
- 工装出入库单_通知记录
- 工装位置表

Make sure all fields referenced by code are actually present in the table definitions.

Examples of potential issues to verify and fix:
- fields referenced in UPDATE but missing in CREATE TABLE
- fields referenced in INSERT but missing in CREATE TABLE
- missing audit fields
- missing notification fields
- missing final confirmation related fields

---

## B. Fix CRUD function field mismatches

Review the current database functions and align them with the corrected schema.

Target functions include at least:

- create_tool_io_order
- submit_tool_io_order
- keeper_confirm_order
- final_confirm_order
- reject_tool_io_order
- cancel_tool_io_order
- add_order_log
- add_notification_record
- get_tool_io_orders
- get_tool_io_order_detail
- search_tools

For each function:
1. confirm all referenced fields exist
2. confirm status updates are valid
3. confirm SQL parameters align with the updated schema
4. confirm Chinese column names are used consistently

---

## C. Preserve existing usable logic

Do NOT rewrite working logic without reason.

Prefer:
- minimal invasive fixes
- precise schema/code alignment
- incremental correction

If a function is already correct, keep it.

---

## D. Ensure workflow completeness

Verify the backend can support these business actions:

- create order
- submit order
- keeper confirm
- notify transport
- final confirm
- reject
- cancel
- list query
- detail query
- tool search

If a required function is missing, add it using the same existing database access pattern.

---

## E. Improve audit logging

Make sure critical actions write logs consistently.

Required logged actions:
- create
- submit
- keeper confirm
- notify transport
- final confirm
- reject
- cancel

Each log must include:
- order id
- action type
- operator
- previous state
- next state
- action content
- created time

---

## F. Improve notification persistence

Ensure notification records support:
- order id
- notification type
- channel
- receiver
- content
- send status
- send time
- retry count
- response payload

If missing in schema or code, fix them.

---

## G. SQL Server compatibility

Verify:
- SQL syntax is valid for SQL Server
- identity columns are handled correctly
- datetime usage is appropriate
- indexes or keys are not broken by the change

Do not introduce PostgreSQL-specific syntax.

---

# Required Deliverables

1. Updated existing database module
2. If needed, updated SQL initialization logic
3. A short implementation summary document:

docs/DATABASE_ALIGNMENT_IMPLEMENTATION.md

This document must include:
- what schema mismatches were fixed
- what functions were updated
- what fields were added or corrected
- any remaining risks
- any assumptions that still require confirmation

---

# Validation Requirement

Before considering the task complete, verify:

1. CREATE TABLE definitions and CRUD functions are consistent
2. no code references missing fields
3. order workflow functions remain logically correct
4. notification persistence works structurally
5. audit logging works structurally

If there are constraints preventing full runtime validation, document them honestly in the implementation summary.

---

# Completion Criteria

The task is complete when:

1. the existing database module has been updated
2. schema/code mismatches are corrected
3. docs/DATABASE_ALIGNMENT_IMPLEMENTATION.md exists
4. no new independent persistence stack was introduced
5. the code remains aligned with SQL Server + pyodbc + existing DatabaseManager