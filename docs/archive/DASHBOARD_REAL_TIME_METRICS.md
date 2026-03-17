# Dashboard Real-Time Metrics

## Overview

The Tooling IO Management System dashboard provides real-time operational indicators to help users monitor the status of tool IO operations and workflow progress.

## Metric Definitions

The following metrics are displayed on the dashboard:

| Metric | Definition | Data Source |
|---|---|---|
| `today_outbound_orders` | Number of outbound orders created today | `工装出入库单_主表` (单据类型='outbound', 创建时间=today) |
| `today_inbound_orders` | Number of inbound orders created today | `工装出入库单_主表` (单据类型='inbound', 创建时间=today) |
| `orders_pending_keeper_confirmation` | Orders awaiting keeper confirmation | `工装出入库单_主表` (单据状态='submitted') |
| `orders_in_transport` | Orders currently in transport phase | `工装出入库单_主表` (单据状态 in 'keeper_confirmed', 'transport_notified', 'transport_in_progress') |
| `orders_pending_final_confirmation` | Orders awaiting final confirmation | `工装出入库单_主表` (单据状态 in 'transport_completed', 'final_confirmation_pending') |
| `active_orders_total` | Total number of non-completed/non-cancelled orders | `工装出入库单_主表` (单据状态 not in 'completed', 'rejected', 'cancelled') |

## Backend Aggregation Logic

### API Endpoint

`GET /api/dashboard/metrics`

### RBAC Filtering

The metrics are automatically filtered based on the current user's organization scope and role permissions.

- **Admin**: Sees global metrics.
- **Team Leader**: Sees metrics for their own organization and descendant organizations.
- **Keeper**: Sees metrics for orders they are responsible for (if scoped).

Aggregation is performed using efficient SQL `SUM(CASE ...)` queries to minimize database load.

## Frontend Layout Structure

The dashboard uses **Mist-style** UI blocks:

- **MistStats**: Statistics cards for key metrics with real-time updates.
- **MistFeatures**: Quick access actions for common workflows (Create Order, Tool Search, Order List, Keeper Workbench).

## Refresh Strategy

- **On Load**: Metrics are fetched when the dashboard page is mounted.
- **Manual Refresh**: Users can refresh the page to update metrics.
- **Navigation**: Metrics are refreshed when navigating back to the dashboard.

## Validation Scenarios

1. **Empty State**: Dashboard displays "0" for all metrics when no data exists.
2. **RBAC Isolation**: Users from different organizations see only their own metrics.
3. **Real-time Transition**: After submitting an order, the "Pending Keeper Confirmation" count increases.
4. **Transport State**: After keeper confirmation, the "In Transport" count increases.
