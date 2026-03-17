# Prompt: Fix notify_transport Uses Non-Existent DB Columns

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (P1 Critical)
**Priority**: P1
**Stage**: 10158
**Goal**: Fix notify-transport API to not use non-existent database columns
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

During E2E testing (Round 2), the `notify-transport` API was found to be completely non-functional, blocking the entire transport workflow. The API returns a SQL error because it tries to update columns that don't exist in the database.

**Error observed**:
```
('42S22', "[Microsoft][ODBC SQL Server Driver][SQL Server]列名 'transport_notify_text' 无效。 (207)")
```

**Affected operation**: `POST /api/tool-io-orders/<order_no>/notify-transport`

**Impact**: Orders cannot progress from `keeper_confirmed` → `transport_notified`. The entire transport workflow is blocked.

---

## Required References

- `backend/services/tool_io_service.py` - The file with two bugs:
  1. `generate_transport_text()` function (lines ~1133-1143) - Uses ORDER_COLUMNS that map to non-existent columns
  2. `notify_transport()` function (lines ~1218-1229) - Uses garbled/corrupted Chinese table/column names in SQL
- `backend/database/schema/column_names.py` - ORDER_COLUMNS definition
- Actual database schema - To verify which columns actually exist

---

## Core Task

Fix the `notify-transport` API SQL errors by:

1. **In `generate_transport_text()`**: Remove the UPDATE statement that tries to set `transport_notify_text` and `wechat_copy_text` columns (lines ~1133-1143). The notification text doesn't need to be stored in the order table - it's already stored in the notification record.

2. **In `notify_transport()`**: Fix the garbled Chinese table/column names in the SQL UPDATE (lines ~1218-1229). Use proper English table name `tool_io_order` and proper column references. The notification text storage should be removed since those columns don't exist.

---

## Required Work

### 1. Fix `generate_transport_text()` (around line 1133)

**Current problematic code**:
```python
DatabaseManager().execute_query(
    f"""
    UPDATE tool_io_order
    SET {ORDER_COLUMNS['transport_notify_text']}=?,
        {ORDER_COLUMNS['wechat_copy_text']}=?,
        {ORDER_COLUMNS['updated_at']}=GETDATE()
    WHERE {ORDER_COLUMNS['order_no']}=?
    """,
    (text, wechat_text, order_no),
    fetch=False,
)
```

**Fix**: Remove this UPDATE entirely. The notification text is already stored in the notification record via `_create_notification_record()` call at line ~1144. There is no need to update the order table with notification text.

### 2. Fix `notify_transport()` (around line 1218)

**Current problematic code** (with garbled Chinese):
```python
DatabaseManager().execute_query(
    """
    UPDATE 宸ヨ鍚哄垹搴撳崟_涓昏〃
    SET 鍗曟嵁鐘舵€?= 'transport_notified',
        杩愯緭閫氱煡鏂囨湰 = ?,
        寰甯楀嶅埗鏂囨湰 = ?,
        淇鏍囧噯鏃堕棿 = GETDATE()
    WHERE 鍑哄叆搴撳崟鍙?= ?
    """,
    (content, copy_text, order_no),
    fetch=False,
)
```

**Fix**: Remove the notification text storage UPDATE entirely. Just update the status to `transport_notified` without trying to store the notification text:
```python
DatabaseManager().execute_query(
    f"""
    UPDATE [{TABLE_NAMES['ORDER']}]
    SET {ORDER_COLUMNS['order_status']} = 'transport_notified',
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (order_no,),
    fetch=False,
)
```

---

## Constraints

- Do NOT add new columns to the database schema
- Do NOT use garbled/corrupted Chinese table/column names in SQL
- The notification text should only be stored in the `tool_io_notification` table (via `_create_notification_record`), NOT in the `tool_io_order` table
- Keep the audit log entry via `write_order_audit_log()`
- Preserve the return structure of both functions

---

## Completion Criteria

1. The `notify-transport` API no longer raises SQL errors
2. Orders can successfully transition from `keeper_confirmed` to `transport_notified`
3. The notification record is still created in `tool_io_notification` table
4. The audit log entry is still written via `write_order_audit_log()`
5. `python -m py_compile backend/services/tool_io_service.py` passes without errors

---

## Bug Investigation Notes

The root cause is that someone previously tried to store notification text in the `tool_io_order` table by adding `transport_notify_text` and `wechat_copy_text` keys to `ORDER_COLUMNS` (in a previous incomplete fix), but these columns were never actually created in the database. The proper design is to store notification text only in the `tool_io_notification` table, which is already implemented correctly.

The second issue (garbled Chinese) suggests the original code used Chinese table/column names directly which got corrupted through some encoding issue. The correct approach is to use the English table name `tool_io_order` and proper ORDER_COLUMNS references.
