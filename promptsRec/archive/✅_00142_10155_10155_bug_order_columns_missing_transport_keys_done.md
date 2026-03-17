# Prompt: Fix ORDER_COLUMNS Missing Transport Assignment Keys

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (P1 Critical)
**Priority**: P1
**Stage**: 10155
**Goal**: Fix KeyError in assign-transport and notify-transport APIs by adding missing ORDER_COLUMNS keys
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

During E2E testing, the assign-transport and notify-transport API endpoints were found to be completely non-functional, blocking the entire transport workflow. When a KEEPER attempts to assign transport or send transport notification, the backend returns a KeyError because `ORDER_COLUMNS` dictionary is missing critical key mappings.

**Error observed**:
```
KeyError: 'transport_assignee_id'
```

**Affected operations**:
1. `POST /api/tool-io-orders/<order_no>/assign-transport`
2. `POST /api/tool-io-orders/<order_no>/notify-transport`

**Impact**: Orders get stuck in `keeper_confirmed` status - transport cannot be assigned or notified.

---

## Required References

- `backend/database/schema/column_names.py` - The file needing the fix
- `backend/services/tool_io_service.py` - Where the missing keys are used in f-strings
- `database.py` or actual DB schema - To verify actual column names in the database
- `docs/RBAC_PERMISSION_MATRIX.md` - RBAC documentation

---

## Core Task

Fix the `KeyError: 'transport_assignee_id'` issue by adding missing column name constants to `ORDER_COLUMNS` in `backend/database/schema/column_names.py`.

The following keys are missing and need to be added:
- `transport_assignee_id`
- `transport_assignee_name`
- `transport_type`

---

## Required Work

1. **Inspect the current `ORDER_COLUMNS`** in `column_names.py` to understand the existing structure and naming patterns

2. **Verify actual database column names** by:
   - Checking `database.py` for how these columns are referenced
   - Looking at the `tool_io_order` table schema
   - Using the `_pick_value` patterns that show alternative names

3. **Identify correct Chinese column names** - Based on patterns in `tool_io_service.py`:
   - `transport_assignee_id` may map to `运输AssigneeID` or `运输人ID`
   - `transport_assignee_name` may map to `运输AssigneeName` or `运输人姓名`
   - `transport_type` may map to `运输类型`

4. **Add missing keys to `ORDER_COLUMNS`** dictionary in `column_names.py`

5. **Verify the fix** by checking that all f-string references in `tool_io_service.py` will now resolve correctly

---

## Constraints

- Do NOT assume column names - always verify against actual database schema
- Do NOT modify any other files except `column_names.py`
- Follow the existing naming patterns in `ORDER_COLUMNS`
- The actual database columns already exist - this is only adding constant mappings

---

## Completion Criteria

1. `ORDER_COLUMNS` in `column_names.py` contains `transport_assignee_id`, `transport_assignee_name`, and `transport_type` keys with correct Chinese column name values
2. The assign-transport API no longer raises KeyError
3. The notify-transport API no longer raises KeyError
4. Orders can progress from `keeper_confirmed` to `transport_notified` status

---

## Bug Investigation Required

Before making any changes, you MUST:

1. Read `backend/database/schema/column_names.py` to see current `ORDER_COLUMNS` structure
2. Search `backend/services/tool_io_service.py` for all uses of `transport_assignee` and `transport_type`
3. Check `database.py` for how these columns are referenced in SQL queries
4. Identify the exact Chinese column names used in the actual database schema
