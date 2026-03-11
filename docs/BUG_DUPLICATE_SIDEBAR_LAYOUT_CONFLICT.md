# Bug Report: Duplicate Sidebar Layout Conflict

## Observed Symptom
The application displayed two navigation systems simultaneously:
1. A legacy narrow left sidebar from the old Element Plus layout.
2. A new Mist-style sidebar from the ongoing UI migration.
This caused the main content area to be visually squeezed and the overall layout to feel structurally inconsistent.

## Root Cause
The legacy layout was globally defined in `App.vue`, wrapping the `<router-view />`. When new pages (like the Dashboard) were migrated to use the new `MainLayout.vue`, they ended up nested inside the old layout, leading to duplicated headers and sidebars.

## Fix Applied
1. **Simplified App.vue**: Removed all UI elements (header, sidebar, container) from `App.vue`. It now only contains the root `<router-view />`.
2. **Global Layout Implementation**: Refactored `router/index.js` to use `MainLayout.vue` as a parent layout for all business routes. This ensures a consistent UI shell across the entire application.
3. **Feature Merging**: 
    - Moved session management inputs (User Name, User ID, Role) from the old header into the new `MainLayout.vue` sidebar.
    - Integrated session persistence logic into `MainLayout.vue`.
4. **Layout Standardization**:
    - Updated `MainLayout.vue` to dynamically display page titles from route metadata.
    - Cleaned up manual layout wrapping in `DashboardOverview.vue`.
    - Optimized sidebar styling and scroll behavior.

## Verification Result
- **Navigation**: The Mist-style sidebar is now the single source of navigation.
- **Visuals**: The duplicate sidebar is gone. Content area now uses the full available width (with max-width constraints for readability).
- **Functionality**: Session switching (Name/ID/Role) works correctly from the new sidebar and persists across reloads.
- **Consistency**: All pages (Dashboard, List, Create, Keeper, Detail) now share the same modern shell.

## Remaining Limitations
None identified. The layout is now stable and ready for further page-specific UI refinements.
