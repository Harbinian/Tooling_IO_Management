# Notification Service Framework

## Purpose

The notification service framework standardizes how Tool IO workflow events become stored notifications.

It provides:

- stable notification event types
- consistent message title and body generation
- internal notification persistence
- query support for current-user inbox scenarios
- read-status updates for future frontend notification pages

This framework is intentionally limited to internal notification storage. External delivery adapters, such as Feishu, build on top of this service instead of replacing it.

## Notification Event Types

The current framework uses these stable event types:

| Event Type | Purpose |
|---|---|
| `ORDER_CREATED` | draft order created |
| `ORDER_SUBMITTED` | order submitted by initiator |
| `KEEPER_CONFIRM_REQUIRED` | keeper must review and confirm the order |
| `TRANSPORT_REQUIRED` | transport operator must handle a confirmed order |
| `ORDER_COMPLETED` | final confirmation completed the order |
| `ORDER_CANCELLED` | order was cancelled |
| `ORDER_REJECTED` | order was rejected |

Service-layer integrations must reuse these constants so notification semantics remain stable across workflow steps.

## Message Structure

Each logical notification is normalized to this structure before persistence:

| Field | Meaning |
|---|---|
| `notification_type` | stable event type |
| `order_id` | stored order number |
| `target_user_id` | intended user id if known |
| `target_user_name` | intended display name if known |
| `target_role` | intended role such as `initiator`, `keeper`, `transport_operator` |
| `message_title` | concise title for UI and delivery adapters |
| `message_body` | operational message body |
| `created_time` | notification creation time from database |
| `status` | internal lifecycle state such as `unread` or `read` |
| `metadata` | lightweight JSON payload for future extension |

The existing notification table is reused. Structured metadata is serialized into the existing `copy_text` field for internal-channel records so the schema does not need to change.

## Service Architecture

Primary module:

- `backend/services/notification_service.py`

Core responsibilities:

1. define stable event types
2. build standardized title and body text from templates
3. persist internal notification records to the existing notification table
4. query notifications for the current user
5. query notifications by order id
6. mark notifications as read

Order workflow integration remains in:

- `backend/services/tool_io_service.py`

That service decides when a business transition should emit a notification, while the notification service owns the storage and normalization details.

## Workflow Integration

Current workflow integration points:

- order creation -> `ORDER_CREATED`
- order submission -> `ORDER_SUBMITTED`
- order submission -> `KEEPER_CONFIRM_REQUIRED`
- keeper confirmation -> `TRANSPORT_REQUIRED`
- final confirmation -> `ORDER_COMPLETED`
- order cancellation -> `ORDER_CANCELLED`
- order rejection -> `ORDER_REJECTED`

These writes are best-effort and must not break the main order workflow if notification persistence fails.

## Query Support

The current backend prepares the following query capabilities:

- list current-user notifications: `GET /api/notifications`
- list order notification records: `GET /api/tool-io-orders/<order_no>/notification-records`
- mark one notification as read: `POST /api/notifications/<notification_id>/read`

Current-user matching is resolved from stored receiver markers such as:

- `user:<user_id>`
- `name:<display_name>`
- `role:<role_code>`

This keeps the current schema compatible while still allowing targeted notification queries.

## Failure Handling

Notification persistence is non-blocking by design.

- business state transitions must still succeed if notification writing fails
- failures are logged through the Python logger
- notification write helpers return structured failure information for later troubleshooting

## Future Feishu Integration

The next extension layer is an external delivery adapter.

Recommended flow:

1. create internal notification record through `notification_service`
2. pass the normalized notification payload to a delivery adapter
3. persist send result back into the existing notification record
4. keep delivery failure non-blocking for the core business transaction

This keeps internal notification storage as the source of truth while allowing Feishu and future delivery channels to share the same business events.
