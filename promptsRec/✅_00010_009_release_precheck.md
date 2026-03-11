Primary Executor: Claude Code
Task Type: Release Precheck
Stage: 009
Goal: Perform final system consistency review before release.
Execution: RUNPROMPT

---

# Context

The project has completed most development stages using the prompt-driven pipeline.

Key documents and modules may include:

docs/PRD.md  
docs/ARCHITECTURE.md  
docs/DB_SCHEMA.md  
docs/API_SPEC.md  
docs/SQLSERVER_SCHEMA_REVISION.md  
docs/FRONTEND_DESIGN.md  

backend/ implementation  
frontend/ implementation  

The purpose of this task is to verify that the system is internally consistent before release.

---

# Task

Perform a full system consistency review.

---

## 1 API Consistency

Verify that backend API implementations match:

docs/API_SPEC.md

Check:

- endpoint paths
- request parameters
- response fields
- HTTP methods

Report any mismatch.

---

## 2 Database Consistency

Verify that database schema usage matches:

docs/DB_SCHEMA.md  
docs/SQLSERVER_SCHEMA_REVISION.md

Check:

- tables referenced in code exist
- fields referenced in code exist
- no UPDATE/INSERT referencing missing columns

---

## 3 State Machine Validation

Verify order workflow states.

Expected states may include:

draft  
submitted  
keeper_confirmed  
transport_notified  
completed  
rejected  
cancelled  

Check:

- transitions are valid
- no unreachable states
- no missing transitions

---

## 4 Audit Logging

Verify that the following operations generate logs:

create order  
submit order  
keeper confirm  
notify transport  
final confirm  
reject  
cancel  

Logs should include:

order_id  
operator  
action_type  
timestamp  

---

## 5 Notification Persistence

Verify that notification records are stored.

Check:

- notification table exists
- content stored
- send status recorded
- timestamps stored

---

## 6 Frontend / API Mapping

Verify that frontend fields match backend API responses.

Check:

- field names
- required fields
- status fields
- ID references

---

# Output

Generate report:

docs/RELEASE_PRECHECK_REPORT.md

The report must contain:

System overview  
Detected inconsistencies  
Severity classification  

Severity levels:

Critical  
High  
Medium  
Low  

Also include recommended fixes.

---

# Completion Criteria

Task is complete when:

docs/RELEASE_PRECHECK_REPORT.md exists
and the system consistency review is fully documented.