# AI Review: Frontend Structure

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Vue 3 | Frontend framework |
| Tailwind CSS | Styling |
| shadcn/ui (Custom) | UI component library (Mist design style) |
| Element Plus | UI component library (Being migrated to shadcn/ui) |
| Vite | Build tool |
| Vue Router | Routing |
| Pinia | State management |

## Directory Structure

```
frontend/src/
├── main.js                 # App entry point
├── App.vue                # Root component
├── api/                   # API wrappers
│   └── adminUsers.js     # Admin user API
├── components/
│   ├── mist/             # Mist features components
│   │   ├── MistFeatures.vue
│   │   └── MistStats.vue
│   ├── tool-io/          # Tool IO components
│   │   ├── LogTimeline.vue
│   │   ├── NotificationPreview.vue
│   │   ├── OrderStatusTag.vue
│   │   ├── ToolSearchDialog.vue
│   │   └── ToolSelectionTable.vue
│   └── ui/               # Base UI components
│       ├── Badge.vue
│       ├── Button.vue
│       ├── Card.vue
│       ├── CardContent.vue
│       ├── CardDescription.vue
│       ├── CardFooter.vue
│       ├── CardHeader.vue
│       ├── CardTitle.vue
│       ├── Input.vue
│       ├── Select.vue
│       ├── TabsList.vue
│       ├── TabsTrigger.vue
│       └── Textarea.vue
├── debug/
│   └── debugIds.js       # Debug ID constants
├── directives/
│   └── vDebugId.js       # Debug ID directive
├── layouts/
│   └── MainLayout.vue    # Main layout with sidebar
├── pages/
│   ├── admin/
│   │   └── UserAdminPage.vue
│   ├── auth/
│   │   └── LoginPage.vue
│   ├── dashboard/
│   │   └── DashboardOverview.vue
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

### Reusable Components

| Component | Purpose |
|-----------|---------|
| ToolSearchDialog | Search tools in inventory |
| ToolSelectionTable | Select tools for order |
| LogTimeline | Display order operation logs |
| NotificationPreview | Show notification preview |
| OrderStatusTag | Display order status badge |

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

| API | File |
|-----|------|
| Auth | Built-in fetch to `/api/auth/*` |
| Orders | Built-in fetch to `/api/tool-io-orders/*` |
| Tools | Built-in fetch to `/api/tools/*` |
| Admin Users | `api/adminUsers.js` |

## Development Commands

```powershell
cd frontend
npm install
npm run dev     # Start dev server at localhost:5173
npm run build   # Production build
```

## Entry Point

- `frontend/src/main.js` - Creates Vue app
- Registers `v-debug-id` directive
- Mounts to `#app` element
