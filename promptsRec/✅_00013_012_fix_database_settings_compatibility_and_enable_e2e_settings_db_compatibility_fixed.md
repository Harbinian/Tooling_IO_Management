Primary Executor: Codex
Task Type: Backend Fix
Stage: 012
Goal: Fix settings.db compatibility issue so database.py can be imported safely and the backend service can start for end-to-end testing.
Execution: RUNPROMPT

---

# Context

The previous stage completed tool master search integration using the real SQL Server table:

工装身份卡_主表

Tool search now works and the frontend can retrieve tool data.

However a repository configuration problem still exists:

Importing database.py directly fails because settings.db structure does not match what the code expects.

This issue was not introduced by the previous changes but blocks:

- Flask server startup
- backend API runtime
- end-to-end testing
- order submission testing

This task focuses on fixing this compatibility problem safely.

Do NOT modify the tool master integration logic implemented in the previous stage.

---

# Required References

Read before implementing:

docs/PRD.md  
docs/ARCHITECTURE.md  
docs/DB_SCHEMA.md  
docs/SQLSERVER_SCHEMA_REVISION.md  
docs/TOOL_MASTER_FIELD_MAPPING.md  
docs/TOOL_SEARCH_DB_INTEGRATION.md  
docs/AI_DEVOPS_ARCHITECTURE.md  

Also inspect the following backend files:

database.py  
web_server.py  
backend/services/tool_io_service.py  

---

# Core Problem

The current repository contains a configuration database or configuration structure referred to as:

settings.db

The code expects a certain schema but the actual structure does not match.

Because of this:

import database.py

fails.

The goal of this task is to make database initialization robust so the backend can start even if settings.db differs.

---

# Required Work

## A. Diagnose the settings.db Dependency

Inspect:

database.py

Determine:

1. how settings.db is loaded
2. what tables or keys are expected
3. what schema mismatch causes the import failure

Document the root cause.

---

## B. Make Database Initialization Robust

Modify database initialization so that:

- importing database.py does NOT fail
- missing settings tables or keys do not crash the module
- reasonable defaults are used if settings.db content is incomplete

Possible safe approaches include:

- conditional loading
- fallback configuration
- defensive schema checks
- lazy initialization

Do NOT hide real SQL Server errors.

Only protect configuration loading.

---

## C. Preserve Existing Behavior

Ensure the following still works:

- SQL Server connection through pyodbc
- DatabaseManager functionality
- tool search using 工装身份卡_主表
- existing CRUD utilities

Do NOT rewrite the database architecture.

Only fix the configuration compatibility issue.

---

## D. Backend Startup Validation

After implementing the fix, verify that:

- importing database.py succeeds
- web_server.py can start
- tool search API works
- no configuration exception occurs at import time

---

## E. Documentation

Create:

docs/DATABASE_SETTINGS_COMPATIBILITY_FIX.md

Include:

1. description of the settings.db mismatch
2. root cause analysis
3. code changes made
4. fallback logic introduced
5. limitations or assumptions

---

# Constraints

1. Do NOT modify 工装身份卡_主表 integration logic.
2. Do NOT redesign the database layer.
3. Keep SQL Server as the primary data source.
4. Keep English for code and comments.
5. Preserve existing working backend behavior.
6. Use defensive programming instead of hardcoding schema assumptions.
7. Keep changes minimal and production-safe.

---

# Completion Criteria

The task is complete when:

1. database.py can be imported without failure
2. settings.db mismatch no longer crashes initialization
3. web_server.py can start normally
4. tool search API still functions
5. docs/DATABASE_SETTINGS_COMPATIBILITY_FIX.md exists