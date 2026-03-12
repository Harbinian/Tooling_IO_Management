# API Regression Checklist

**Version:** 1.0
**Date:** 2026-03-13
**Purpose:** Regression baseline for future refactors

---

## Authentication

- [ ] `POST /api/auth/login` returns `success: true` with user object
- [ ] `POST /api/auth/login` returns `success: false` with error message on invalid credentials
- [ ] `GET /api/auth/me` returns current user with `roles` and `permissions` arrays
- [ ] Unauthenticated requests to protected endpoints return 401

---

## Tool Search

- [ ] `GET /api/tools/search` returns paginated results
- [ ] Response includes `data` array with tool objects
- [ ] Response includes `pagination` object with `page_no`, `page_size`, `total_count`
- [ ] Frontend-required fields are present: `tool_id`, `tool_code`, `tool_name`, `current_location_text`, `status_text`
- [ ] `POST /api/tools/batch-query` accepts `tool_codes` array and returns matching tools

---

## Order List

- [ ] `GET /api/tool-io-orders` returns paginated order list
- [ ] Response includes `data` array with order objects
- [ ] Response includes `pagination` object
- [ ] Frontend-required fields present: `order_no`, `order_type`, `order_status`, `initiator_id`, `initiator_name`, `keeper_id`, `keeper_name`, `org_id`, `org_name`, `created_at`, `updated_at`
- [ ] Filtering works: `order_type`, `order_status`, `keyword`, `date_from`, `date_to`
- [ ] Pagination works: `page_no`, `page_size`

---

## Order Detail

- [ ] `GET /api/tool-io-orders/<order_no>` returns order with items
- [ ] Items array contains: `tool_code`, `tool_name`, `quantity`, `confirmed_quantity`, `location`
- [ ] Returns 404 for non-existent order
- [ ] Returns error for orders outside user's org scope

---

## Order Creation

- [ ] `POST /api/tool-io-orders` creates new order
- [ ] Requires `order_type` and `items` array
- [ ] Returns 201 with created order on success
- [ ] Returns 400 with error message on validation failure

---

## Order Submission

- [ ] `POST /api/tool-io-orders/<order_no>/submit` transitions order from "draft" to "submitted"
- [ ] Only initiator can submit their own draft orders
- [ ] Returns success/error appropriately

---

## Keeper Confirmation

- [ ] `POST /api/tool-io-orders/<order_no>/keeper-confirm` requires `items` array
- [ ] Each item should have `tool_code`, `quantity`, `confirmed` (optional)
- [ ] Only keeper can confirm orders assigned to them
- [ ] Transitions order to "keeper_confirmed" status

---

## Final Confirmation

- [ ] `POST /api/tool-io-orders/<order_no>/final-confirm` transitions order to "completed"
- [ ] Outbound orders: requires team_leader role
- [ ] Inbound orders: requires keeper role
- [ ] `GET /api/tool-io-orders/<order_no>/final-confirm-availability` returns availability status

---

## Order Rejection/Cancellation

- [ ] `POST /api/tool-io-orders/<order_no>/reject` requires `reject_reason`
- [ ] `POST /api/tool-io-orders/<order_no>/cancel` allows cancellation
- [ ] Only authorized roles can reject/cancel

---

## Notifications

- [ ] `GET /api/tool-io-orders/<order_no>/logs` returns operation logs
- [ ] `GET /api/tool-io-orders/<order_no>/notification-records` returns notification history
- [ ] `GET /api/tool-io-orders/<order_no>/generate-keeper-text` generates keeper notification
- [ ] `GET /api/tool-io-orders/<order_no>/generate-transport-text` generates transport notification
- [ ] `POST /api/tool-io-orders/<order_no>/notify-transport` sends Feishu notification
- [ ] `POST /api/tool-io-orders/<order_no>/notify-keeper` sends keeper notification

---

## Keeper Pending List

- [ ] `GET /api/tool-io-orders/pending-keeper` returns orders pending keeper confirmation
- [ ] Filters by `keeper_id` parameter
- [ ] Only accessible to users with `order:keeper_confirm` permission

---

## Organizations

- [ ] `GET /api/orgs` returns organization list
- [ ] `GET /api/orgs/tree` returns hierarchical org structure
- [ ] `GET /api/orgs/<org_id>` returns single org detail
- [ ] `POST /api/orgs` creates new organization (admin only)
- [ ] `PUT /api/orgs/<org_id>` updates organization (admin only)

---

## Health & System

- [ ] `GET /api/health` returns system health status
- [ ] `GET /api/health` checks database connectivity
- [ ] `GET /api/db/test` returns database connection status (authenticated)

---

## RBAC Enforcement

- [ ] Users can only access orders within their organization
- [ ] Permission checks work correctly for all protected endpoints
- [ ] Role-based workflow transitions enforced:
  - Only initiator can submit draft orders
  - Only assigned keeper can confirm
  - Only team_leader can final-confirm outbound
  - Only keeper can final-confirm inbound

---

## Error Handling

- [ ] All endpoints return consistent error format: `{ "success": false, "error": "..." }`
- [ ] Validation errors return 400 status
- [ ] Not found returns 404 status
- [ ] Unauthorized returns 401 status
- [ ] Server errors return 500 status

---

## Pagination Standard

- [ ] All list endpoints support `page_no` and `page_size` parameters
- [ ] All list endpoints return `pagination` object with `page_no`, `page_size`, `total_count`
- [ ] Default `page_no` is 1
- [ ] Default `page_size` is 20
