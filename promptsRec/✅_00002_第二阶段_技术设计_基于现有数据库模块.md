Primary Executor: Claude Code

Task Type: Technical Design Revision Based on Existing SQL Server Database Script

Goal:
Revise the technical design documents based on the actual existing database script used by the project.

---

# Context

The project already has an actual database module implemented in Python.

This module is the real database baseline for the project.

Important facts from the current implementation:

1. The system uses SQL Server via pyodbc.
2. The project already has a DatabaseManager and connection pool.
3. The project already contains Tool IO related table initialization and CRUD functions.
4. The database layer uses Chinese table names and Chinese column names.
5. This is NOT a greenfield persistence design.

The technical design documents must be aligned to this real implementation baseline.

---

# Inputs

Existing project database script:
- current database module file in the project

Existing docs:
- docs/PRD.md
- docs/ARCHITECTURE.md

---

# Deliverables

Generate or update the following documents:

1. docs/DB_SCHEMA.md
2. docs/API_SPEC.md
3. docs/TASKS.md
4. docs/COLLABORATION.md
5. docs/INHERITED_DB_ACCESS_REVIEW.md

---

# Requirements

## 1. docs/DB_SCHEMA.md

Must reflect the actual SQL Server schema style already used in the project.

Requirements:
- describe existing tables already present in the database script
- distinguish between:
  - existing implemented tables
  - recommended missing fields / corrections
  - future optional enhancements
- document Chinese table names and Chinese column names
- define suggested logical English aliases for backend code use

Key tables include:
- 工装出入库单_主表
- 工装出入库单_明细
- 工装出入库单_操作日志
- 工装出入库单_通知记录
- 工装位置表
- 工装身份卡_主表 (existing business source table used for tool search)

## 2. docs/API_SPEC.md

Define REST APIs for the module, but implementation notes must explicitly state:

- API service layer should reuse existing database functions where possible
- new APIs should wrap or extend the current database module, not replace it entirely
- keep SQL Server compatibility

## 3. docs/TASKS.md

Break tasks into realistic phases based on the current codebase, including:

Phase 1:
database script audit and field consistency fix

Phase 2:
service layer wrapping and API alignment

Phase 3:
keeper workflow completion

Phase 4:
notification persistence and Feishu integration

Phase 5:
final confirmation and audit completion

Phase 6:
frontend integration

Each task must indicate whether it is:
- fix existing implementation
- extend existing implementation
- newly add missing layer

## 4. docs/COLLABORATION.md

Clarify:

- Claude Code defines architecture and reviews consistency
- Codex must implement on top of the existing database module
- Codex must not introduce a brand-new ORM/repository pattern without approval
- Gemini remains frontend-focused

## 5. docs/INHERITED_DB_ACCESS_REVIEW.md

This document must review the existing database module and describe:

- connection strategy
- connection pool behavior
- query execution pattern
- transaction limitations
- current CRUD functions already available
- reuse opportunities
- missing abstractions
- identified schema inconsistencies
- integration recommendations

---

# Special Review Requirement

The output must explicitly identify any mismatch between:
- create table definitions
- update statements
- insert statements
- status fields
- audit fields

If a field is referenced in code but missing in schema, list it clearly.

---

# Constraints

1. Do not assume PostgreSQL.
2. Do not assume SQLAlchemy.
3. Do not redesign the whole database layer from scratch.
4. Follow the current database script as the actual baseline.
5. Focus on incremental correction and extension.

---

# Completion Criteria

The task is complete when all five documents exist and clearly reflect the existing SQL Server + pyodbc + inherited CRUD baseline.