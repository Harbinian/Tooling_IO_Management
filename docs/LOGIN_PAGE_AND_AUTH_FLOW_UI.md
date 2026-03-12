# Login Page and Authentication Flow UI

This document describes the implementation of the frontend login experience and session management flow.

## 1. Login Page
- **Location**: `frontend/src/pages/auth/LoginPage.vue`
- **Design**: A modern, split-screen layout following the Mist-style design language.
  - **Left Side**: Branding, value proposition, and technical highlights (RBAC, Secure Auth).
  - **Right Side**: Clean, focused login form with validation and error feedback.
- **Features**:
  - Integrated with `lucide-vue-next` for iconography.
  - Loading states for the submit button.
  - Responsive design for mobile and desktop.

## 2. Authentication Flow
### Login
1. User enters `login_name` and `password`.
2. Frontend calls `POST /api/auth/login`.
3. On success, the `session` store saves the `token` and user object (including permissions and roles) to `localStorage`.
4. User is redirected to the Dashboard (or the previously requested URL).

### Session Restoration (Hydration)
- On app startup or page refresh, the `App.vue` or `router` triggers `session.hydrate()`.
- If a token exists, it calls `GET /api/auth/me` to fetch the latest user context.
- If the token is invalid or expired, the session is cleared, and the user is redirected to the login page.

### Logout
- User clicks the logout button in the `MainLayout.vue` sidebar.
- The `session.clear()` method removes the token from `localStorage` and resets the state.
- The app redirects to `/login`.

## 3. Store Integration
- **Store**: `frontend/src/store/session.js`
- **State**:
  - `token`: Bearer token for API requests.
  - `user_id`, `userName`, `loginName`: Basic identity.
  - `roles`, `permissions`: RBAC context for UI visibility and route guards.
  - `initialized`: Flag to prevent flash of unauthenticated content.

## 4. Route Guard
- Protected routes are wrapped in `MainLayout.vue`.
- The `router.beforeEach` guard ensures:
  - Public routes (like `/login`) are accessible.
  - Private routes require a valid session.
  - Granular permission checks are performed based on `meta.permission`.

## 5. Visual Consistency
- Uses the same Tailwind color palette and shadow system as the rest of the application.
- Integrated `ShieldCheck` icon as the new system logo for a professional "Secure/Enterprise" feel.
