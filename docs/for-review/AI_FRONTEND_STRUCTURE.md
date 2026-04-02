# AI Review: Frontend Structure

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Vue 3 | Frontend framework |
| Element Plus | UI component library |
| Vite | Build tool |
| Vue Router | Routing |
| Pinia | State management |

## Directory Structure

```
frontend/src/
├── main.js                 # App entry point
├── App.vue                # Root component
├── api/                   # API wrappers
│   ├── auth.js           # Auth API
│   ├── toolIO.js        # Tool IO API
│   ├── dashboard.js     # Dashboard API
│   ├── adminUsers.js    # Admin user API
│   ├── feedback.js      # Feedback API
│   └── org.js           # Organization API
├── components/
│   └── tool-io/         # Tool IO components
│       ├── LogTimeline.vue
│       ├── NotificationPreview.vue
│       ├── OrderStatusTag.vue
│       ├── ToolSearchDialog.vue
│       ├── ToolSelectionTable.vue
│       ├── TransportIssueDialog.vue
│       └── WorkflowStepper.vue
├── layouts/
│   └── MainLayout.vue    # Main layout with sidebar
├── pages/
│   ├── admin/
│   │   └── UserAdminPage.vue
│   ├── auth/
│   │   └── LoginPage.vue
│   ├── dashboard/
│   │   └── DashboardOverview.vue
│   ├── settings/
│   │   └── SettingsPage.vue
│   └── tool-io/
│       ├── KeeperProcess.vue
│       ├── OrderCreate.vue
│       ├── OrderDetail.vue
│       └── OrderList.vue
├── router/
│   └── index.js          # Vue Router config
├── store/
│   └── session.js        # Session store (Pinia)
└── utils/
    └── toolIO.js         # Tool IO utilities
```

## Routes

| Path | Component | Permission |
|------|-----------|------------|
| /login | LoginPage | public |
| /dashboard | DashboardOverview | dashboard:view |
| /inventory | OrderList | order:list |
| /inventory/create | OrderCreate | order:create |
| /inventory/keeper | KeeperProcess | order:keeper_confirm |
| /inventory/:orderNo | OrderDetail | order:view |
| /admin/users | UserAdminPage | admin:user_manage |
| /settings | SettingsPage | authenticated |

## Key Components

### Pages

| Component | Purpose |
|-----------|---------|
| LoginPage | User login, redirect handling |
| DashboardOverview | Dashboard with metrics cards |
| OrderList | Order listing with filters |
| OrderCreate | Create new order form |
| OrderDetail | View order, workflow actions |
| KeeperProcess | Keeper workspace for confirmations |
| UserAdminPage | Admin user management |
| SettingsPage | User settings and feedback |

### Reusable Components

| Component | Purpose |
|-----------|---------|
| ToolSearchDialog | Search tools in inventory |
| ToolSelectionTable | Select tools for order |
| LogTimeline | Display order operation logs |
| NotificationPreview | Show notification preview |
| OrderStatusTag | Display order status badge |
| WorkflowStepper | Display workflow progress |
| TransportIssueDialog | Report transport issues |

## State Management

**File**: `store/session.js`

- User authentication state
- Token management
- Permission checking
- Session hydration from storage

## Debug System

**Files**:
- `directives/vDebugId.js` - Vue directive for debug IDs
- `debug/debugIds.js` - Debug ID constants

**Usage**: Add `v-debug-id` attribute to elements
```html
<div v-debug-id="'DASHBOARD.CARD_1'">Content</div>
```

**Enable**: Add `?debugUI=1` to URL

## API Integration

### Frontend API Calls

All API calls go through the `api/` directory wrappers:

| API | File |
|-----|------|
| Auth | `api/auth.js` |
| Orders | `api/toolIO.js` |
| Tools | `api/toolIO.js` |
| Dashboard | `api/dashboard.js` |
| Admin Users | `api/adminUsers.js` |
| Feedback | `api/feedback.js` |
| Organization | `api/org.js` |

## Development Commands

```powershell
cd frontend
npm install
npm run dev     # Start dev server at localhost:8150
npm run build   # Production build
```

## Entry Point

- `frontend/src/main.js` - Creates Vue app
- Mounts to `#app` element
