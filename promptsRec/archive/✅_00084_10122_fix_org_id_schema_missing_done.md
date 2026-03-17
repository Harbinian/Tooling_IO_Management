# Primary Executor: Codex
# Task Type: Bug Fix
# Priority: P0
# Stage: 122
# Goal: Fix missing org_id column in database schema to unblock order creation
# Dependencies: None
# Execution: RUNPROMPT

---

## Context

A critical database schema defect is blocking all order creation on existing databases. The system cannot create any new tool-io orders because the database table is missing the `org_id` column that the application code expects.

**Error observed:**
```
('42S22', "[42S22] 列名 'org_id' 无效。 (207)")
```

This error occurs when attempting to call `POST /api/tool-io-orders`.

---

## Required References

1. **Backend Error Source**: Test report `test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260318_170500_REVISED_FOR_SCRIPTED_E2E.md` (Section 5: Confirmed Critical Defect)

2. **Schema Files**:
   - `backend/database/schema/schema_manager.py` (lines 50, 88)
   - `backend/database/repositories/order_repository.py` (lines 98, 120)

3. **API Endpoint**: `POST /api/tool-io-orders` in `backend/routes/order_routes.py`

4. **Documentation**:
   - `docs/DB_SCHEMA.md` - Database schema definition
   - `docs/ARCHITECTURE.md` - Architecture overview

---

## Core Task

Fix the database schema alignment so that existing databases gain the `org_id` column. The application code already expects `org_id` in the order insert path, and the schema creation SQL includes `org_id` for new table creation. The missing piece is the migration/alignment path that retrofits old databases.

---

## Required Work

1. **Investigation Phase**:
   - Read `backend/database/schema/schema_manager.py` to understand schema creation and alignment logic
   - Read `backend/database/repositories/order_repository.py` to understand how `org_id` is used in queries
   - Read `docs/DB_SCHEMA.md` to understand the intended schema design
   - Inspect the actual database to confirm the current state of the table schema

2. **Fix Implementation**:
   - Add schema migration/alignment code in `schema_manager.py` to add `org_id` column to existing tables
   - Ensure the migration is idempotent (safe to run on databases that already have the column)
   - The fix should handle both:
     - Tables that don't exist yet (create with org_id)
     - Tables that exist but lack org_id (add column)

3. **Verification**:
   - Run syntax check: `python -m py_compile backend/database/schema/schema_manager.py`
   - Test order creation API with valid payload:
     ```json
     {
       "order_type": "outbound",
       "order_items": [
         {
           "tool_code": "T000001",
           "quantity": 1
         }
       ]
     }
     ```
   - Verify the response returns success (not 500 error)

4. **Documentation**:
   - Update `docs/DB_SCHEMA.md` if schema definition needs clarification
   - No code comments required for this fix

---

## Constraints

- **MUST** preserve existing data in the database
- **MUST** be idempotent (can run multiple times without error)
- **MUST** not change the API contract or response format
- **MUST** not break new table creation (existing schema creation must still work)
- **MUST** use transactions for schema modifications
- Do NOT modify frontend code
- Do NOT change the business logic (only fix schema alignment)

---

## Completion Criteria

1. Schema migration code is added to `schema_manager.py`
2. Running the migration successfully adds `org_id` to existing tables
3. `POST /api/tool-io-orders` returns success response (201) with valid payload
4. Syntax check passes: `python -m py_compile backend/database/schema/schema_manager.py`
5. No data loss occurs during migration
6. The fix is idempotent - running it twice doesn't cause errors

### Acceptance Tests

| Test | Expected Result |
|------|-----------------|
| Migration runs on fresh database | Creates table with org_id |
| Migration runs on existing database | Adds org_id column without data loss |
| POST /api/tool-io-orders with valid payload | Returns 201 with order details |
| POST /api/tool-io-orders with valid payload twice | Both orders created successfully |
| GET /api/tool-io-orders | Returns list including newly created order |
