Primary Executor: Claude Code

Task Type: Architecture & Implementation Consistency Audit

Goal:
Perform a deep consistency review between the architecture documents, database schema documentation, API specifications, and the existing database implementation script.

This task must detect design mismatches, schema inconsistencies, missing fields, and architectural risks.

---

# Context

The project already contains:

Documentation:
- docs/PRD.md
- docs/ARCHITECTURE.md
- docs/DB_SCHEMA.md
- docs/API_SPEC.md
- docs/INHERITED_DB_ACCESS_REVIEW.md

Implementation baseline:
- existing SQL Server database module implemented with pyodbc

Important facts:

1. The database uses SQL Server.
2. The project uses pyodbc and a DatabaseManager with connection pooling.
3. Tables and columns are primarily named in Chinese.
4. Several CRUD functions already exist in the database module.
5. This system is NOT greenfield — implementation already exists.

---

# Review Objectives

Perform a full system audit focusing on the following areas:

1. Schema vs code consistency
2. State machine correctness
3. API contract integrity
4. Audit logging completeness
5. Notification persistence
6. Integration with inherited CRUD layer

This task must produce a detailed report.

Do NOT modify code during this task.

---

# Review Areas

## 1. Database Schema vs Code

Compare:

docs/DB_SCHEMA.md

with the actual SQL Server table creation SQL inside the database module.

Check for:

- fields referenced in UPDATE but not defined in CREATE TABLE
- fields referenced in INSERT but not defined in schema
- fields missing indexes
- inconsistent field naming
- mismatched data types

Examples to look for:

- update statements referencing fields not defined in tables
- missing audit fields
- missing status fields
- incomplete notification record fields

All detected mismatches must be listed.

---

## 2. Chinese Table / Field Naming Mapping

Verify that the documentation correctly maps:

logical English entities → Chinese SQL Server tables.

Examples:

tool_io_order → 工装出入库单_主表  
tool_io_order_item → 工装出入库单_明细  

Check whether documentation reflects the real schema naming.

---

## 3. State Machine Integrity

Verify state definitions.

Expected order states include values such as:

draft  
submitted  
keeper_confirmed  
partially_confirmed  
transport_notified  
completed  
rejected  
cancelled  

Check:

- transitions are valid
- no unreachable states
- no missing transitions
- state transitions align with business rules

Business rules:

Outbound completion → confirmed by initiator  
Inbound completion → confirmed by keeper  

---

## 4. API Contract Consistency

Compare:

docs/API_SPEC.md

with the operations supported by the database module.

Verify:

- API operations can be implemented with existing CRUD functions
- required parameters exist
- state transitions align with database operations

Identify APIs that require new backend logic.

---

## 5. Audit Logging

Verify that the following actions produce audit logs:

order creation  
order submission  
keeper confirmation  
transport notification  
final confirmation  
reject  
cancel  

Audit logs must contain:

order_id  
operator  
timestamp  
previous_state  
next_state  

---

## 6. Notification Persistence

Verify notification persistence logic.

The system must store notification records including:

order_id  
notification_type  
receiver  
content  
send_status  
send_time  

Check whether the schema supports this.

---

## 7. Concurrency Risk

Check potential risks such as:

- multiple keepers confirming the same order
- duplicate submission
- inconsistent order status update
- race conditions during final confirmation

Identify risky update patterns.

---

## 8. SQL Server Compatibility

Verify that the schema and queries are appropriate for SQL Server.

Check for:

- incompatible SQL syntax
- misuse of identity columns
- missing indexes for join-heavy tables

---

# Output

Generate a report:

docs/ARCHITECTURE_REVIEW.md

The report must contain:

1. System overview
2. Detected schema mismatches
3. State machine issues
4. API design gaps
5. Logging completeness review
6. Notification persistence review
7. Concurrency risks
8. SQL Server design notes
9. Recommended fixes

---

# Severity Classification

Each issue must be categorized:

Critical
High
Medium
Low

Critical examples:

- schema/code mismatch causing runtime errors
- missing primary keys
- broken state transitions

---

# Completion Criteria

The task is complete when:

docs/ARCHITECTURE_REVIEW.md exists

and includes:

- schema vs code comparison
- state machine verification
- API contract verification
- logging review
- notification persistence review
- concurrency risk analysis
- SQL Server compatibility notes