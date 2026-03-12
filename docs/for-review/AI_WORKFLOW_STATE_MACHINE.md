# AI Review: Workflow State Machine

## Overview

The Tooling IO Management System implements a state machine for managing 工装 (tool) inbound and outbound orders.

## Order Types

| Type | Description |
|------|-------------|
| 出库 | Outbound (tool leaves warehouse) |
| 入库 | Inbound (tool enters warehouse) |

## State Flow

### Outbound Order (出库)

```
draft → submitted → keeper_confirmed → transport_in_progress → transport_completed → final_confirmed → completed
         ↓              ↓                    ↓                   ↓                    ↓
      (reject)     (reject)           (reject)            (reject)            (reject)
```

### Inbound Order (入库)

```
draft → submitted → keeper_confirmed → transport_in_progress → transport_completed → keeper_final_confirmed → completed
         ↓              ↓                    ↓                   ↓                       ↓
      (reject)     (reject)           (reject)            (reject)               (reject)
```

## States

| State | Description | Next States |
|-------|-------------|-------------|
| draft | Initial draft | submitted, cancelled |
| submitted | Submitted for approval | keeper_confirmed, rejected |
| keeper_confirmed | Keeper approved items | transport_notified, rejected |
| partially_confirmed | Some items confirmed | transport_notified, rejected |
| transport_notified | Transport notified | transport_in_progress, rejected |
| transport_in_progress | Transport in progress | transport_completed, rejected |
| transport_completed | Transport completed | final_confirmed/keeper_final_confirmed, rejected |
| final_confirmed | Team leader confirmed (outbound) | completed |
| keeper_final_confirmed | Keeper confirmed (inbound) | completed |
| completed | Order finished | - |
| rejected | Order rejected | - |
| cancelled | Order cancelled | - |

## Workflow Actions

### Submit Order

- **From**: draft
- **To**: submitted
- **Role**: Any authenticated user
- **API**: POST /api/tool-io-orders/{order_no}/submit

### Keeper Confirm

- **From**: submitted
- **To**: keeper_confirmed (all items approved) or partially_confirmed (partial)
- **Role**: keeper
- **API**: POST /api/tool-io-orders/{order_no}/keeper-confirm
- **Payload**: Array of items with approved/rejected status

### Assign Transport

- **From**: keeper_confirmed, partially_confirmed, transport_notified
- **To**: (no state change, assigns transport)
- **Role**: keeper
- **API**: POST /api/tool-io-orders/{order_no}/assign-transport

### Start Transport

- **From**: keeper_confirmed, partially_confirmed, transport_notified
- **To**: transport_in_progress
- **Role**: transport staff
- **API**: POST /api/tool-io-orders/{order_no}/transport-start

### Complete Transport

- **From**: transport_in_progress, transport_notified
- **To**: transport_completed
- **Role**: transport staff
- **API**: POST /api/tool-io-orders/{order_no}/transport-complete

### Final Confirm (Outbound)

- **From**: transport_completed, transport_notified, final_confirmation_pending
- **To**: completed
- **Role**: team_leader
- **API**: POST /api/tool-io-orders/{order_no}/final-confirm

### Final Confirm (Inbound)

- **From**: transport_completed
- **To**: completed
- **Role**: keeper
- **API**: POST /api/tool-io-orders/{order_no}/final-confirm

### Reject Order

- **From**: Any intermediate state
- **To**: rejected
- **Role**: keeper
- **API**: POST /api/tool-io-orders/{order_no}/reject
- **Payload**: Reason for rejection

### Cancel Order

- **From**: draft
- **To**: cancelled
- **Role**: Order creator
- **API**: POST /api/tool-io-orders/{order_no}/cancel

## Key Files

| File | Purpose |
|------|---------|
| backend/services/tool_io_service.py | Core workflow logic |
| backend/routes/order_routes.py | Order API endpoints |

## State Validation

Each workflow function validates current state before transitioning:

```python
if current_status not in allowed_statuses:
    return {"success": False, "error": f"current status does not allow action: {current_status}"}
```

## Notifications

| Trigger | Notification Type |
|---------|-------------------|
| Submit | Keeper notification |
| Keeper confirm | Transport notification |
| Transport complete | Final confirmation notification |
