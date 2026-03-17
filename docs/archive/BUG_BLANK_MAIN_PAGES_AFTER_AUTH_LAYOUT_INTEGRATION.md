# Bug Fix: Blank Main Pages After Auth Layout Integration

## Observed Symptom

After authentication and layout integration, the application shell (header, sidebar, user info) rendered successfully, but the main content area was blank for several core pages:
- Dashboard
- Order List
- New Order
- Keeper Workspace

## Confirmed Root Cause

The `MainLayout.vue` component, which serves as the parent component for all nested routes under `/`, used a `<slot />` tag in its main content area instead of `<router-view />`.

In Vue Router, nested child routes are injected into the parent component's `<router-view />` tag. While `<slot />` is used for content passed between parent and child components, it does not act as a mount point for router children.

Additionally, a minor issue was found in `DashboardOverview.vue` where it attempted to access `session.user.user_name` instead of `session.userName`, causing a potential "undefined" display for the welcome message.

## Affected Layers
- **Frontend Layout**: `MainLayout.vue`
- **Frontend Page**: `DashboardOverview.vue`

## Fix Applied
1.  **MainLayout.vue**: Replaced `<slot />` with `<router-view />` in the main content container.
2.  **DashboardOverview.vue**: Updated the welcome message to use the correct `session.userName` property.

## Pages Verified
- **Dashboard** (`/dashboard`): Now renders metrics and quick actions.
- **Order List** (`/inventory`): Now renders the order registry table and filters.
- **New Order** (`/inventory/create`): Now renders the order creation form.
- **Keeper Workspace** (`/inventory/keeper`): Now renders the keeper confirmation workbench.

## Remaining Edge Cases
None observed. The authentication shell and RBAC permission checks are functioning as expected.
