Primary Executor: Claude Code

Task Type: SQL Server Schema Revision Design

Goal:
Design a corrected and production-ready SQL Server schema revision plan for the Tool Inventory IO Management System, based on the existing database script already present in the project.

This task must preserve the current database style:
- SQL Server
- pyodbc
- inherited DatabaseManager
- Chinese table names and Chinese column names

Do NOT redesign the whole persistence layer.
Do NOT switch to ORM-first architecture.

---

# Context

The project already has an existing database module with:
- SQL Server connection management
- pyodbc execution
- connection pool
- create table SQL
- CRUD functions for tool IO workflow

The current database script is the implementation baseline.

However, the existing script contains schema/code inconsistencies.
Some fields are referenced in code but are not defined in CREATE TABLE statements.

This task is to revise the schema design so that:
1. the existing business logic can run consistently
2. missing fields are identified
3. Chinese table names are preserved
4. auditability is improved
5. notification persistence is complete
6. state-machine related fields are stable

---

# Inputs

Use the following as source materials:

1. Existing database script in the project
2. docs/PRD.md
3. docs/ARCHITECTURE.md
4. docs/DB_SCHEMA.md if it already exists
5. docs/INHERITED_DB_ACCESS_REVIEW.md if it already exists

---

# Required Output

Generate a document:

docs/SQLSERVER_SCHEMA_REVISION.md

This document must be detailed and implementation-oriented.

---

# Core Requirements

## 1. Preserve existing Chinese table naming

The revised design must keep the current Chinese table naming style.

Expected core tables include at least:

- 工装出入库单_主表
- 工装出入库单_明细
- 工装出入库单_操作日志
- 工装出入库单_通知记录
- 工装位置表

If the current tool master data comes from another table, document it clearly as an existing dependency.

Do NOT rename existing tables into English physical names.

---

## 2. Distinguish clearly between:

- current implemented fields
- missing fields referenced by code
- recommended additional fields
- optional future enhancement fields

For every core table, provide four sections:

A. Existing fields already in script
B. Missing but required fields referenced by code
C. Recommended production fields
D. Optional future fields

---

## 3. Review and revise the main order table

For table:

工装出入库单_主表

You must propose a corrected field design.

It should support:
- order number
- order type
- order status
- initiator info
- keeper info
- usage purpose / project info
- planned times
- confirmation times
- final completion
- reject / cancel
- notification summary
- audit fields

Specially check whether fields like the following are needed because code references them:

- 工装数量
- 已确认数量
- 最终确认人
- 最终确认时间
- 驳回原因
- 取消原因

If code references them and schema lacks them, list them explicitly.

---

## 4. Review and revise the detail table

For table:

工装出入库单_明细

You must propose a corrected field design.

It should support:
- order reference
- tool reference
- tool code / name / spec snapshot
- quantity
- item status
- source location
- keeper confirmed location
- keeper check result
- keeper remark
- return check result
- completion tracking
- sorting

Specially check fields referenced by code, such as:

- 确认时间
- 出入库完成时间

If referenced but missing in schema, list them explicitly.

---

## 5. Review and revise the audit log table

For table:

工装出入库单_操作日志

The design must support:
- order id / order no
- action type
- operator
- operator role
- previous state
- next state
- action content
- created time

If current script lacks enough fields for full auditability, recommend additions.

---

## 6. Review and revise the notification record table

For table:

工装出入库单_通知记录

The design must support:
- order id
- notification type
- channel
- receiver
- content
- send status
- send time
- retry count
- response payload
- created time

Ensure this design supports:
- Feishu message persistence
- WeChat copy text tracking if needed

---

## 7. State-machine support

The revised schema must explicitly support the workflow state machine.

Document how the schema supports:

- order_status
- item_status
- tool_status (if stored externally, explain dependency)

Clarify which fields are the authoritative storage location for each state.

---

## 8. Index and key design

For every core table, define:

- primary key
- unique keys
- recommended indexes

Pay attention to SQL Server usage.

At minimum, consider indexes for:
- 单号
- 状态
- 发起人
- 保管员
- 创建时间
- 外键关联字段

---

## 9. English logical aliases

Although physical table/column names remain Chinese, provide logical English aliases for backend code understanding.

Example format:

工装出入库单_主表 -> tool_io_order
工装出入库单_明细 -> tool_io_order_item
出入库单号 -> order_no
当前状态 -> order_status

This is for documentation only, not a requirement to rename physical schema.

---

## 10. Output structure requirements

The document must include these sections:

1. Overview
2. Existing schema problems found in current script
3. Revised table design: 工装出入库单_主表
4. Revised table design: 工装出入库单_明细
5. Revised table design: 工装出入库单_操作日志
6. Revised table design: 工装出入库单_通知记录
7. Revised table design: 工装位置表
8. English logical alias mapping
9. SQL Server index recommendations
10. Mandatory fixes before backend implementation
11. Optional future enhancements

---

# Special Deliverable Requirement

At the end of the document, add a section:

## Mandatory Schema Fix Checklist

This checklist must list every schema inconsistency that must be fixed before or during backend implementation.

Examples:
- field referenced in UPDATE but missing in CREATE TABLE
- field referenced in INSERT but missing in schema
- missing audit field
- missing notification field

---

# Constraints

1. Keep Chinese physical schema naming.
2. Keep SQL Server compatibility.
3. Do not redesign the whole persistence layer.
4. Focus on correcting and stabilizing the current implementation baseline.
5. The result must be usable by Codex for actual schema/code alignment.

---

# Completion Criteria

The task is complete when:

docs/SQLSERVER_SCHEMA_REVISION.md exists

and includes:
- revised core tables
- missing field analysis
- logical alias mapping
- SQL Server index suggestions
- mandatory schema fix checklist