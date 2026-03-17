# Bug Fix: tool:search API HTTP 500 Due to TRY_CONVERT

**Priority**: P0
**Stage**: 10145
**Executor**: Claude Code (Simplified Task - Direct Fix)

---

## Context

The `GET /api/tools/search` endpoint returns HTTP 500 Internal Server Error for **ALL users**, including SYS_ADMIN with full permissions.

### Error Response
```json
{
    "error": "('42000', \"[Microsoft][ODBC SQL Server Driver][SQL Server] \
        TRY_CONVERT 不是可以识别的内置函数名称。\")",
    "success": false
}
```

### Impact
- ALL users cannot search for tools
- Outbound and inbound workflows are completely blocked at step 1
- This is a P0 critical issue

---

## Required References

1. `backend/database/repositories/tool_repository.py` - Contains the problematic `TRY_CONVERT` usage
2. `docs/RBAC_INIT_DATA.md` - Documents expected KEEPER permissions
3. `backend/database/schema/column_names.py` - Column name constants

---

## Core Task

Replace `TRY_CONVERT` function with SQL Server compatible alternative in `tool_repository.py`.

### Root Cause
`TRY_CONVERT` is a SQL Server 2012+ function. The ODBC driver or SQL Server version in use does not support it.

### Solution
Replace:
```sql
TRY_CONVERT(DATE, m.{inspection_expiry_date_col})
```

With compatible syntax:
```sql
CASE WHEN ISDATE(m.{inspection_expiry_date_col}) = 1
     AND m.{inspection_expiry_date_col} IS NOT NULL
     THEN CAST(m.{inspection_expiry_date_col} AS DATE)
END
```

---

## Required Work

1. Read `backend/database/repositories/tool_repository.py`
2. Find all uses of `TRY_CONVERT` in the file
3. Replace `TRY_CONVERT(DATE, ...)` patterns with the compatible `CASE WHEN ISDATE()` pattern
4. Ensure the replacement handles NULL values properly
5. Run syntax check: `python -m py_compile backend/database/repositories/tool_repository.py`
6. Test the fix with a tool search API call

---

## Constraints

- Do NOT change business logic
- Only replace SQL compatibility issue
- Maintain proper NULL handling
- Keep the same query results

---

## Completion Criteria

1. `TRY_CONVERT` is completely removed from the file
2. Syntax check passes: `python -m py_compile backend/database/repositories/tool_repository.py`
3. Tool search API returns HTTP 200 (empty array is OK if no data matches)
4. All existing tests pass
