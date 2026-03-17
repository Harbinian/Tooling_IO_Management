# Incident: Order List API 500 Error

## Summary

API endpoint `/api/tool-io-orders` returns 500 Internal Server Error when accessed via frontend.

## Affected Area

Backend - API Layer

## Severity

High (API failure affecting core functionality)

## Error Message

```
GET http://localhost:5177/api/tool-io-orders?keyword=&order_type=&order_status=&initiator_id=&keeper_id=&date_from=&date_to=&page_no=1&page_size=20 500 (INTERNAL SERVER ERROR)
```

## Stack Trace

```
getOrderList @ orders.js:21
loadOrders @ OrderList.vue:364
```

## Observed Behavior

Frontend receives 500 error when loading order list page.

## Expected Behavior

Order list should load successfully (or return auth error if not logged in).

## Root Cause

**RESOLVED** - Parameter mismatch in database.py and tool_io_service.py

The service layer was calling `get_tool_io_orders()` with incorrect parameter names:
- `order_status` instead of `status`
- `page_no` instead of `page`
- `initiator_id` instead of `applicant_id`

And the wrapper function in database.py was passing wrong params to repository:
- `status` instead of `order_status`
- `page` instead of `page_no`
- `applicant_id` instead of `initiator_id`

## Fix Applied

Commit: bc9ab4d - fix: resolve parameter mismatches in database.py

Files modified:
- `backend/services/tool_io_service.py` - Fixed list_orders() and get_dashboard_stats()
- `database.py` - Fixed get_tool_io_orders() and search_tools() wrapper mappings

## Status

RESOLVED - Backend API is now returning 401 (auth required) instead of 500.

## Next Steps

Verify the frontend loads correctly after clearing browser cache or refreshing.
