# Prompt: Fix start_transport and complete_transport Missing f-string Prefix

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (P1 Critical)
**Priority**: P1
**Stage**: 10159
**Goal**: Fix SQL syntax errors in transport functions by adding f-string prefix
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

During E2E testing (Round 3), the `transport-start` API was found to return a SQL syntax error, completely blocking the transport workflow.

**Error observed**:
```
SQL syntax error or violation access rules (0)
```

**Affected operations**:
1. `POST /api/tool-io-orders/<order_no>/transport-start` - Blocks transport from starting
2. `POST /api/tool-io-orders/<order_no>/transport-complete` - Would also be affected (same bug pattern)

**Impact**: Transport workflow is completely blocked - orders cannot progress from `keeper_confirmed` to `transport_in_progress` to `transport_completed`.

---

## Root Cause

In `backend/services/tool_io_service.py`, the `start_transport` and `complete_transport` functions use Python f-string placeholder syntax `{ORDER_COLUMNS['...']}` inside regular strings (without `f` prefix). This means Python does NOT interpolate the placeholders - instead, the literal string `{ORDER_COLUMNS['order_status']}` is passed to SQL Server, causing a syntax error.

---

## Required References

- `backend/services/tool_io_service.py`
  - `start_transport()` function: lines ~480-491
  - `complete_transport()` function: lines ~529-538

---

## Core Task

Add the missing `f` prefix to SQL strings in two functions:

### 1. Fix `start_transport()` (lines 480-491)

**Current code** (MISSING `f` prefix):
```python
DatabaseManager().execute_query(
    """
    UPDATE tool_io_order
    SET {ORDER_COLUMNS['order_status']} = 'transport_in_progress',
        {ORDER_COLUMNS['transport_operator_id']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_id']}),
        {ORDER_COLUMNS['transport_operator_name']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_name']}),
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (payload.get("operator_id", ""), payload.get("operator_name", ""), order_no),
    fetch=False,
)
```

**Fix**: Add `f` before the opening triple-quote:
```python
DatabaseManager().execute_query(
    f"""
    UPDATE tool_io_order
    SET {ORDER_COLUMNS['order_status']} = 'transport_in_progress',
        {ORDER_COLUMNS['transport_operator_id']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_id']}),
        {ORDER_COLUMNS['transport_operator_name']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_name']}),
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (payload.get("operator_id", ""), payload.get("operator_name", ""), order_no),
    fetch=False,
)
```

### 2. Fix `complete_transport()` (lines 529-538)

**Current code** (MISSING `f` prefix):
```python
DatabaseManager().execute_query(
    """
    UPDATE tool_io_order
    SET {ORDER_COLUMNS['order_status']} = 'transport_completed',
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (order_no,),
    fetch=False,
)
```

**Fix**: Add `f` before the opening triple-quote:
```python
DatabaseManager().execute_query(
    f"""
    UPDATE tool_io_order
    SET {ORDER_COLUMNS['order_status']} = 'transport_completed',
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (order_no,),
    fetch=False,
)
```

---

## Constraints

- Only add `f` prefix to existing SQL strings - do not change any other code
- Do not modify any other functions
- Do not change SQL logic or parameters
- Verify syntax with `python -m py_compile`

---

## Completion Criteria

1. Both SQL strings now have `f` prefix so placeholders are properly interpolated
2. `python -m py_compile backend/services/tool_io_service.py` passes without errors
3. Transport workflow can successfully transition from `keeper_confirmed` to `transport_in_progress` to `transport_completed`
