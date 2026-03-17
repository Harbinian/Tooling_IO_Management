# Prompt: Fix transport_notify_time Column Not Exist in Database

## Metadata

| Field | Value |
|-------|-------|
| **Prompt ID** | 10152 |
| **Type** | Bug Fix |
| **Executor** | Codex |
| **Priority** | CRITICAL |
| **Created** | 2026-03-25 |
| **Test Report** | HUMAN_SIMULATED_E2E_TEST_REPORT_20260325_210000.md |

---

## Context

The E2E test report identified a **CRITICAL** issue that blocks ALL order list APIs:

**Error**: `[Microsoft][ODBC SQL Server Driver][SQL Server]列名 'transport_notify_time' 无效。 (207)`

**Affected APIs**:
- `GET /api/tool-io-orders` (all users get SQL Error 42S22)

**Root Cause**: The code in `order_repository.py` references a column `transport_notify_time` that does NOT exist in the `tool_io_order` database table.

---

## Required References

1. **Schema Snapshot**: `docs/SCHEMA_SNAPSHOT_20260325.md:168` - Confirms column does not exist
2. **Affected File**: `backend/database/repositories/order_repository.py` lines 378 and 795
3. **Column Constants**: `backend/database/schema/column_names.py:60`

---

## Core Task

### Step 1: Remove `transport_notify_time` from SELECT query (line 378)

In `backend/database/repositories/order_repository.py`, find and remove the following line from the SELECT column list around line 378:

```python
"[transport_notify_time] AS [transport_notify_time]",
```

### Step 2: Remove `transport_notify_time` from UPDATE query (line 795)

In the same file, find the UPDATE query around line 795 and remove the reference to `transport_notify_time`. The column does not exist in the table, so setting it to NULL should be removed.

### Step 3: Verify column_names.py consistency

Check `backend/database/schema/column_names.py`:
- If `transport_notify_time` is defined in `ORDER_COLUMNS` or `ORDER_CHINESE_COLUMNS`, do NOT remove it - these are used for legacy compatibility
- The issue is that the actual SQL queries reference a column that doesn't exist in the DB

### Step 4: Syntax verification

After making changes, run:
```powershell
python -m py_compile backend/database/repositories/order_repository.py
```

---

## Constraints

1. **Do NOT modify `column_names.py`** - These are legacy constants used for compatibility with views
2. **Only modify the actual SQL query strings** in `order_repository.py`
3. **Do NOT change any other business logic**
4. **Preserve all other columns in the SELECT and UPDATE queries**

---

## Completion Criteria

1. The `transport_notify_time` column reference is removed from both SELECT (line 378) and UPDATE (line 795) queries
2. Python syntax check passes: `python -m py_compile backend/database/repositories/order_repository.py`
3. The ORDER query in order_repository.py no longer references the non-existent column

---

## Expected Outcome

After this fix, the `GET /api/tool-io-orders` API should no longer return SQL Error 42S22.
