# Prompt: Bug Fix - assign_transport SQL Encoding Corruption

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10148
Goal: Fix SQL encoding corruption in assign_transport() function where Chinese column names contain embedded ? characters
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a critical bug was discovered in the `assign_transport` API endpoint (`POST /api/tool-io-orders/<order_no>/assign-transport`).

**Error Response:**
```json
{
  "error": "('The SQL contains 6 parameter markers, but 4 parameters were supplied', 'HY000')",
  "success": false
}
```

**Root Cause:** The SQL UPDATE statement in `assign_transport()` function has corrupted Chinese column names with embedded `?` characters:
- `运输AssigneeName?= ?` should be `运输AssigneeName = ?`
- `出入库单号?= ?` should be `出入库单号 = ?`

**Impact:**
- All outbound/inbound workflows blocked at transport assignment step
- Order `TO-OUT-20260324-005` stuck at `keeper_confirmed` status
- Production cannot complete transport operations

---

## Required References / 必需参考

1. **Correct SQL Reference:** `backend/database/repositories/order_repository.py` lines 503-508
   ```python
   sql = """
   UPDATE 工装出入库单_主表
   SET 运输AssigneeID = ?,
       运输AssigneeName = ?,
       运输类型 = ?,
       修改时间 = GETDATE()
   WHERE 出入库单号 = ?
   """
   ```

2. **Column Names Schema:** `backend/database/schema/column_names.py`

3. **API Spec:** `docs/API_SPEC.md` - assign-transport endpoint

4. **RBAC Spec:** `docs/RBAC_PERMISSION_MATRIX.md`

---

## Core Task / 核心任务

Fix the SQL encoding corruption in `backend/services/tool_io_service.py` `assign_transport()` function.

The corrupted SQL at lines 433-441:
```python
DatabaseManager().execute_query(
    """
    UPDATE 宸ヨ�鍑哄叆搴撳崟_涓昏〃
    SET 杩愯緭浜篒D = ?,
        杩愯緭浜哄�鍚?= ?,
        杩愯緭绫诲瀷 = ?,
        淇敼鏃堕棿 = GETDATE()
    WHERE 鍑哄叆搴撳崟鍙?= ?
    """,
    (transport_assignee_id, transport_assignee_name, transport_type, order_no),
    fetch=False,
)
```

**Must be replaced with properly encoded SQL using column name constants from `column_names.py`:**

```python
from backend.database.schema.column_names import ORDER_COLUMNS

DatabaseManager().execute_query(
    f"""
    UPDATE {ORDER_COLUMNS['table_name']}
    SET {ORDER_COLUMNS['transport_assignee_id']} = ?,
        {ORDER_COLUMNS['transport_assignee_name']} = ?,
        {ORDER_COLUMNS['transport_type']} = ?,
        {ORDER_COLUMNS['modified_time']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (transport_assignee_id, transport_assignee_name, transport_type, order_no),
    fetch=False,
)
```

---

## Required Work / 必需工作

1. **Inspect the corrupted code** in `backend/services/tool_io_service.py` around line 433
2. **Verify correct column names** from `backend/database/schema/column_names.py`
3. **Check the reference implementation** in `backend/database/repositories/order_repository.py` lines 503-508
4. **Replace the corrupted SQL** with properly encoded version using `ORDER_COLUMNS` constants
5. **Run syntax check** via `python -m py_compile backend/services/tool_io_service.py`
6. **Verify the fix** by checking the SQL statement has exactly 4 parameter markers (`?`)

---

## Constraints / 约束条件

1. **Must use `ORDER_COLUMNS` constants** from `column_names.py` for all Chinese column names
2. **Do not change business logic** - only fix the corrupted SQL string
3. **Do not modify table name** - keep `工装出入库单_主表` (the corrupted prefix `宸ヨ�` should be removed, but the correct table name should be used)
4. **Parameter count must remain 4** - transport_assignee_id, transport_assignee_name, transport_type, order_no
5. **Follow encoding standards** - ensure file is UTF-8 without BOM

---

## Completion Criteria / 完成标准

1. SQL UPDATE statement has exactly 4 `?` parameter markers (not 6)
2. Chinese column names are properly encoded without corruption
3. `python -m py_compile backend/services/tool_io_service.py` passes without syntax errors
4. The `assign-transport` API can be called successfully without SQL parameter mismatch error
5. Test order `TO-OUT-20260324-005` can progress past `keeper_confirmed` status

---

## Expected Workflow After Fix

After this bug is fixed, the outbound workflow should be able to continue:
1. TEAM_LEADER creates order (done)
2. TEAM_LEADER submits order (done)
3. KEEPER confirms order (done)
4. **KEEPER assigns transport** (BLOCKED - will be unblocked)
5. KEEPER sends notification
6. PRODUCTION_PREP starts transport
7. PRODUCTION_PREP completes transport
8. TEAM_LEADER final confirm
