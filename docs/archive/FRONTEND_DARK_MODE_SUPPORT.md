# Frontend Dark Mode CSS Theme Support

This document describes the implementation of the dark mode theme support for the Tooling IO Management System.

## Overview

The system now supports a full Dark Mode theme alongside the existing Light Mode. The theme can be toggled in the Settings page and persists across page refreshes.

## Implementation Details

### 1. CSS Variables
Location: `frontend/src/assets/index.css`

Comprehensive CSS variables have been defined for both Light and Dark themes under `:root` and `.dark` layers. These include:
- **Core colors**: background, foreground, card, primary, secondary, muted, accent, destructive.
- **Borders & Inputs**: border, input, ring.
- **Layout specific**: sidebar, header (with backgrounds, foregrounds, and borders).

Added a smooth transition for all color-related properties to ensure a pleasant switching experience.

### 2. Theme Logic
- **Initialization**: Moved to `frontend/src/App.vue`. On application mount, it checks `localStorage` for a saved preference. If none exists, it defaults to the user's system color scheme preference.
- **Persistence**: Theme selection is saved to `localStorage` under the key `theme`.
- **Toggle**: Handled in `frontend/src/pages/settings/SettingsPage.vue`. It updates both the `localStorage` and the `document.documentElement` class list.

### 3. UI Adaptation
All major pages and components have been updated to use the CSS variables:
- **MainLayout.vue**: Sidebar and Header backgrounds now adapt correctly.
- **DashboardOverview.vue**: The hero section and information cards are now theme-aware.
- **Order Management Pages**: Order List, Create, and Detail pages use semantic color classes (e.g., `bg-card`, `text-foreground`).
- **Common Components**: `OrderStatusTag`, `NotificationPreview`, `LogTimeline`, and UI primitives (`Card`, `Input`, `Badge`, `Button`) all respect the active theme.

## Verification

- **Theme Persistence**: Switching to dark mode and refreshing the page correctly restores the dark theme.
- **System Preference**: On first visit, the app correctly respects the system's light/dark setting.
- **Visual Consistency**: Audited all pages to ensure readability and aesthetic quality in both modes.
- **Build**: Successfully ran `npm run build` in the frontend directory.
