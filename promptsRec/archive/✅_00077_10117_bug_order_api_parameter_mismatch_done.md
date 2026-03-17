# Bug Fix: Order List API Parameter Mismatch

## Context

The application is experiencing 500 Internal Server Errors on two API endpoints:
- GET /api/tool-io-orders
- GET /api/dashboard/metrics

Backend logs show:
```
get_tool_io_orders() got an unexpected keyword argument 'page_no'
get_tool_io_orders() got an unexpected keyword argument 'order_status'
```

## Required References

- Backend service: `backend/services/tool_io_service.py`
- Database API: `database.py` (lines 238-268)
- Frontend API call: `frontend/src/pages/tool-io/OrderList.vue` (lines 364-374)

## Core Task

Fix the parameter mismatch in `backend/services/tool_io_service.py` where it calls `get_tool_io_orders()`.

## Required Work

1. **Analyze the parameter names** in the database function signature:
   - `database.py:get_tool_io_orders()` expects: `status`, `page`, `applicant_id`

2. **Fix the service layer calls** in `backend/services/tool_io_service.py`:
   - `list_orders()` function (around line 175) - change:
     - `order_status` → `status`
     - `page_no` → `page`
     - `initiator_id` → `applicant_id`
   - `get_dashboard_stats()` function (around line 207) - change:
     - `page_no` → `page`

3. **Verify no other calls** to `get_tool_io_orders` have similar issues.

## Constraints

- DO NOT change the database.py function signature (it's the source of truth)
- DO NOT change frontend parameters (frontend follows its own convention)
- Only fix the service layer to map frontend params to database params

## Completion Criteria

1. Backend syntax check passes: `python -m py_compile backend/services/tool_io_service.py`
2. API endpoints return 200 instead of 500
3. Order list loads correctly in the UI
4. Dashboard metrics load correctly
