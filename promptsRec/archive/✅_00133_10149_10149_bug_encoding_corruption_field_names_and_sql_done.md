# Prompt: Bug Fix - Encoding Corruption in Field Names and SQL

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10149
Goal: Fix encoding corruption bugs in generate_transport_text and tool_io_runtime SQL
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, multiple encoding corruption bugs were discovered:

### Bug 1: generate_transport_text field name corruption
**Location:** `backend/services/tool_io_service.py` line 1102

The `_pick_value` function is checking for item status with a corrupted field name:
```python
if _pick_value(item, ["item_status", "status", "确认数量�?"], "") == "approved"
```

The field `确认数量�?` is corrupted (extra `?` embedded in the Chinese characters). This causes the function to never find the correct field, so `approved_items` is always empty, causing `notify-transport` to fail with "no approved items are available".

### Bug 2: tool_io_runtime.py SQL corruption
**Location:** `backend/services/tool_io_runtime.py` lines 87-89 and 105-109

SQL queries have corrupted Chinese table names:
```python
# Line 87-89:
FROM 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織  -- CORRUPTED

# Line 105-109:
FROM 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍  -- CORRUPTED
```

### Bug Impact
- `notify-transport` API returns error: "no approved items are available for transport preparation"
- Workflow blocked at step 5 (send transport notification)
- Cannot proceed to transport execution steps

---

## Required References / 必需参考

1. **Correct Field Names:** `backend/database/schema/column_names.py`
   - `ITEM_COLUMNS['item_status']` = `明细状态`
   - `ITEM_COLUMNS['status']` = (status field)

2. **Correct Table Names:** `backend/database/schema/column_names.py`
   - `LOG_COLUMNS` table name: `工装出入库单_操作日志`
   - `NOTIFY_COLUMNS` table name: `工装出入库单_通知记录`

3. **Reference for _pick_value usage:** `backend/services/tool_io_service.py` lines 1099-1103

4. **Column name constants:**
   ```python
   from backend.database.schema.column_names import ITEM_COLUMNS, LOG_COLUMNS, NOTIFY_COLUMNS
   ```

---

## Core Task / 核心任务

### Fix 1: tool_io_service.py generate_transport_text

**File:** `backend/services/tool_io_service.py`
**Line:** ~1102

**Corrupted code:**
```python
approved_items = [
    _extract_item_values(item)
    for item in order.get("items", [])
    if _pick_value(item, ["item_status", "status", "确认数量�?"], "") == "approved"
]
```

**Fix:** Replace `确认数量�?` with proper field reference. The correct field is `明细状态` which should have value `approved` when confirmed. Use `ITEM_COLUMNS` constants:

```python
from backend.database.schema.column_names import ITEM_COLUMNS

approved_items = [
    _extract_item_values(item)
    for item in order.get("items", [])
    if _pick_value(item, [ITEM_COLUMNS['item_status'], "status"], "") == "approved"
]
```

### Fix 2: tool_io_runtime.py SQL corruption

**File:** `backend/services/tool_io_runtime.py`
**Lines:** ~87-89, ~105-109

**Corrupted code (lines 87-89):**
```python
SELECT TOP (?) *
FROM 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織
WHERE 1=1
ORDER BY 鎿嶄綔鏃堕棿 DESC
```

**Corrupted code (lines 105-109):**
```python
SELECT TOP (?) *
FROM 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍
WHERE 1=1
ORDER BY 鍙戦€佹椂闂?DESC
```

**Fix:** Use proper table names:
```python
from backend.database.schema.column_names import LOG_COLUMNS, NOTIFY_COLUMNS

# Replace corrupted table names with:
# LOG_COLUMNS table: 工装出入库单_操作日志
# NOTIFY_COLUMNS table: 工装出入库单_通知记录

SELECT TOP (?) *
FROM {LOG_COLUMNS['table_name']}  -- 工装出入库单_操作日志
WHERE 1=1
ORDER BY {LOG_COLUMNS['operation_time']} DESC

SELECT TOP (?) *
FROM {NOTIFY_COLUMNS['table_name']}  -- 工装出入库单_通知记录
WHERE 1=1
ORDER BY {NOTIFY_COLUMNS['send_time']} DESC
```

Note: You may need to check what fields are available in `LOG_COLUMNS` and `NOTIFY_COLUMNS` and use appropriate time fields for ordering.

---

## Required Work / 必需工作

1. **Inspect the corrupted code** in `backend/services/tool_io_service.py` around line 1102
2. **Verify correct field names** from `backend/database/schema/column_names.py` - `ITEM_COLUMNS`
3. **Fix the _pick_value call** to use proper field name constants
4. **Inspect corrupted SQL** in `backend/services/tool_io_runtime.py` lines 87-89 and 105-109
5. **Verify correct table names** from `column_names.py` - `LOG_COLUMNS`, `NOTIFY_COLUMNS`
6. **Fix the SQL queries** to use proper table name constants
7. **Run syntax check** via `python -m py_compile` on both files
8. **Verify the fix** by checking that `generate_transport_text` now correctly identifies approved items

---

## Constraints / 约束条件

1. **Must use column name constants** from `column_names.py` for all Chinese field/table names
2. **Do not change business logic** - only fix the corrupted strings
3. **Preserve parameterization** - keep using `?` placeholders for SQL parameters
4. **Follow encoding standards** - ensure files are UTF-8 without BOM

---

## Completion Criteria / 完成标准

1. `_pick_value` call uses correct field name from `ITEM_COLUMNS`
2. SQL queries use correct table names from `LOG_COLUMNS` and `NOTIFY_COLUMNS`
3. `python -m py_compile backend/services/tool_io_service.py` passes without syntax errors
4. `python -m py_compile backend/services/tool_io_runtime.py` passes without syntax errors
5. `notify-transport` API returns success (or at least different error) instead of "no approved items"
6. Workflow can proceed past transport notification step

---

## Expected Behavior After Fix

After this bug is fixed:
1. `generate_transport_text()` will correctly identify items with `明细状态 = approved`
2. `notify-transport` API will successfully generate transport notification text
3. Outbound workflow can proceed: keeper_confirmed → transport_notified → transport_in_progress → completed
