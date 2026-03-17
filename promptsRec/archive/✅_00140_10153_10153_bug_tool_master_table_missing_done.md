# Bug Fix: 工装身份卡_主表 Table Missing

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (10153)
**Stage**: Root Cause Analysis & Fix
**Goal**: Fix the missing external system table `工装身份卡_主表` causing 500 errors on all tool-related APIs
**Execution**: RUNPROMPT

---

## Context

During Human E2E testing on 2026-03-26, critical blockers were discovered:

1. **CRITICAL**: `工装身份卡_主表` table does not exist in SQL Server database
   - Error: `('42S02', "[Microsoft][ODBC SQL Server Driver][SQL Server]对象名 '工装身份卡_主表' 无效。 (208)")`
   - Impact: ALL tool search APIs fail with 500 error
   - Impact: Order creation cannot validate tool codes

2. **HIGH**: SQL syntax error in order creation
   - Error: `('42000', '[Microsoft][ODBC SQL Server Driver][SQL Server]"{" 附近有语法错误。 (102)')`
   - Impact: Order creation blocked
   - Likely cascading from Issue #1

---

## Required References

- `backend/database/repositories/tool_repository.py` - ToolRepository using TOOL_MASTER_TABLE
- `backend/database/core/database_manager.py` - Database queries referencing 工装身份卡_主表
- `backend/database/schema/column_names.py` - TOOL_MASTER_COLUMNS definition (lines 277-350)
- `config/settings.py` - Database connection configuration
- `docs/RBAC_PERMISSION_MATRIX.md` - Permission matrix

---

## Core Task

### Investigate and Fix Issue #1: Missing Table

1. **Verify Database Connection**
   - Check `config/settings.py` for correct SQL Server connection string
   - Confirm the database being queried matches expected database

2. **Determine Root Cause**
   - Check if `工装身份卡_主表` exists in the SQL Server database
   - If it exists under a different name, identify the correct table name
   - If it doesn't exist, this is an external system table that should be read-only via views

3. **Check for View or Alternative Access**
   - Search for any existing views that might wrap this table
   - Look at `backend/database/core/database_manager.py` lines 476 for LEFT JOIN pattern

4. **Fix the Issue**
   - If table exists with different name: Update `TOOL_MASTER_TABLE` constant in tool_repository.py
   - If table is truly external: Add graceful error handling with informative message
   - Ensure tool search APIs return proper error (not 500) when table is unavailable

### Investigate Issue #2: SQL Syntax Error

1. Trace the exact SQL query causing syntax error in order creation
2. Determine if it's cascading from Issue #1 (when tool validation fails)
3. Fix error handling to produce meaningful errors instead of malformed SQL

---

## Required Work

1. **Diagnosis Phase**
   - [ ] Verify database connection and current database
   - [ ] Check if `工装身份卡_主表` exists in SQL Server
   - [ ] If exists: identify exact column structure
   - [ ] If not exists: check for alternative table names or views

2. **Fix Phase**
   - [ ] Update configuration if table name is different
   - [ ] OR implement graceful error handling for missing external table
   - [ ] Fix order creation SQL error handling

3. **Verification Phase**
   - [ ] Test `/api/tools/search` returns 200 (or proper error, not 500)
   - [ ] Test order creation with valid tool code
   - [ ] Verify all tool-related APIs work correctly

---

## Constraints

- **DO NOT modify the external system table schema** - `工装身份卡_主表` is external
- Use `TOOL_MASTER_COLUMNS` constants for all column references
- Maintain existing error handling patterns
- All changes must follow project coding conventions (English variables, 4-space indent)

---

## Completion Criteria

1. `/api/tools/search` returns 200 with data or empty array (not 500)
2. Order creation API accepts requests without SQL syntax errors
3. Error messages are informative and not generic 500 errors
4. Backend syntax check passes: `python -m py_compile backend/database/repositories/tool_repository.py backend/services/tool_io_service.py`

---

## Test Data

Use existing test tooling data:
- Serial Number: T000001
- Drawing Number: Tooling_IO_TEST
- Tool Name: 测试用工装
