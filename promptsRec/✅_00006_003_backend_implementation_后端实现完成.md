Primary Executor: Codex

Task Type: Backend Implementation on Top of Existing SQL Server Database Module

Goal:
Implement and complete the Tool IO backend by reusing and correcting the existing database module.

---

# Context

The project already contains an existing database module that provides:

- SQL Server connection management
- pyodbc query execution
- table initialization
- tool search
- order creation
- order submission
- keeper confirmation
- final confirmation
- reject / cancel
- logs
- notification records

This is the implementation baseline.

Do NOT create a brand-new persistence architecture unless strictly required.

---

# Inputs

Required docs:
- docs/PRD.md
- docs/ARCHITECTURE.md
- docs/DB_SCHEMA.md
- docs/API_SPEC.md
- docs/INHERITED_DB_ACCESS_REVIEW.md

Required code baseline:
- existing database module already in the project

---

# Core Objectives

1. Audit the existing database module for schema/code mismatches
2. Fix field inconsistencies
3. Reuse the current DatabaseManager and CRUD functions where possible
4. Add any missing wrappers/services/API handlers required by API_SPEC.md
5. Keep SQL Server + pyodbc compatibility
6. Preserve existing usable logic

---

# Implementation Rules

1. Do not replace the current DatabaseManager with ORM-first architecture
2. Do not rename existing Chinese tables or columns unless explicitly required by docs
3. Wrap existing database functions with service/API layers where appropriate
4. Fix schema mismatches before expanding functionality
5. Keep all file operations and code changes production-oriented

---

# Required Work

## A. Database Consistency Fix

Check for mismatches between:
- table definitions
- insert statements
- update statements

Fix missing fields or adjust code according to docs/DB_SCHEMA.md.

## B. Service Layer

Implement or complete service wrappers for:
- create order
- submit order
- keeper confirm
- final confirm
- reject
- cancel
- query detail
- query list
- search tools
- notification persistence

## C. API Layer

Implement APIs defined in docs/API_SPEC.md.

## D. Logging

Ensure every critical action records logs:
- create
- submit
- keeper confirm
- notify
- final confirm
- reject
- cancel

## E. Notification

Persist notification records and update send status.

---

# Completion Criteria

The task is complete when:

1. existing database module inconsistencies are fixed
2. backend APIs are implemented
3. service layer aligns with current database module
4. logging is complete
5. notification persistence works
6. no new independent persistence stack was introduced