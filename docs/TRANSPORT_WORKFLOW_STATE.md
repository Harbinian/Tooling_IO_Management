# Transport Workflow State

## Updated State Machine

The Tool IO workflow now includes explicit transport states between keeper confirmation and final confirmation.

Current practical sequence:

1. `draft`
2. `submitted`
3. `keeper_confirmed` or `partially_confirmed`
4. `transport_notified` or assigned
5. `transport_in_progress`
6. `transport_completed`
7. `completed`

Compatibility note:

- `transport_notified` is preserved as a compatible pending-transport state
- `final_confirmation_pending` remains accepted by final confirmation checks for compatibility

## Transport Responsibilities

Transport responsibilities are captured with the existing assignment fields on the order:

- `transport_assignee_id`
- `transport_assignee_name`

Assignment may happen during keeper confirmation or later through the dedicated transport assignment API.

## Transport APIs

Current transport-related APIs:

| Endpoint | Purpose | Permission |
|---|---|---|
| `POST /api/tool-io-orders/<order_no>/assign-transport` | set or update transport assignee | `order:keeper_confirm` |
| `POST /api/tool-io-orders/<order_no>/transport-start` | move order to `transport_in_progress` | `order:transport_execute` |
| `POST /api/tool-io-orders/<order_no>/transport-complete` | move order to `transport_completed` | `order:transport_execute` |

Final confirmation now accepts `transport_completed` as a valid predecessor state.

## Notification Integration

Current notification behavior:

- keeper confirmation emits `TRANSPORT_REQUIRED`
- transport assignment may re-emit `TRANSPORT_REQUIRED` to the newly assigned operator
- transport start emits `TRANSPORT_STARTED`
- transport completion emits `TRANSPORT_COMPLETED`

These events continue to use the unified notification service and may auto-deliver to Feishu through the adapter where configured.

## Audit Logging Behavior

Current transport-specific audit events:

- `transport_assign`
- `transport_start`
- `transport_complete`
- existing `transport_notify`

Each audit write records:

- order number
- operator id
- operator name
- operator role
- previous status
- new status
- remark

Audit failures remain non-blocking.

## Workflow Example

Example outbound flow:

1. initiator creates and submits an order
2. keeper confirms items and assigns a transport operator
3. system emits transport-required notification
4. transport operator starts the move -> `transport_in_progress`
5. transport operator completes the move -> `transport_completed`
6. initiator performs final confirmation -> `completed`

## Frontend Compatibility

Frontend compatibility updates include:

- status label support for `transport_in_progress`
- status label support for `transport_completed`
- final-confirm entry points now accept `transport_completed`
- order detail workflow timeline now displays the transport phase more explicitly

## Validation Notes

Validated in this implementation:

- backend syntax for service, route, audit, RBAC, and adapter integration
- frontend source compatibility via status mapping updates

Still environment-dependent:

- live SQL Server workflow transitions
- live permission propagation for existing users after RBAC table upgrade
- end-to-end UI behavior with a running frontend build and live backend
