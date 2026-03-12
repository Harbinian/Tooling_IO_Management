# AI Review: Debug Infrastructure

## Frontend Debug System

### Overview

The frontend implements a debug ID overlay system for identifying UI elements during development and testing.

### Key Files

| File | Purpose |
|------|---------|
| frontend/src/directives/vDebugId.js | Vue directive for debug IDs |
| frontend/src/debug/debugIds.js | Debug ID constants |
| frontend/src/main.js | Directive registration |

### How It Works

1. **Debug ID Constants** (`debug/debugIds.js`):
   - Organized by page/component
   - Hierarchical naming (e.g., `DASHBOARD.CARD_1`)

2. **Directive** (`vDebugId.js`):
   - Registers global `v-debug-id` directive
   - Renders overlay badge when debug mode enabled

3. **Enabling Debug Mode**:
   - Add `?debugUI=1` to URL
   - Or set in sessionStorage via `sessionStorage.setItem('debugUI', '1')`

### Usage

```vue
<template>
  <div v-debug-id="'DASHBOARD.CARD_1'">
    Dashboard card content
  </div>
</template>
```

### Debug ID Examples

| Page | Element | Debug ID |
|------|---------|----------|
| Dashboard | Pending keeper metric | DASHBOARD.PENDING_KEEPER_METRIC |
| Dashboard | Pending transport metric | DASHBOARD.PENDING_TRANSPORT_METRIC |
| Order List | Table | ORDER_LIST.TABLE |
| Order Detail | Header | ORDER_DETAIL.HEADER |
| Order Create | Form | ORDER_CREATE.FORM |
| Keeper Process | List | KEEPER_PROCESS.LIST |

## Backend Debug

### Logging

- Python logging module configured in `web_server.py`
- Log levels: DEBUG, INFO, WARNING, ERROR
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Flask Debug

- Enabled via `FLASK_DEBUG` environment variable
- Set to `True` for development
- Set to `False` for production

```powershell
$env:FLASK_DEBUG = "True"
python web_server.py
```

### Health Checks

| Endpoint | Purpose |
|----------|---------|
| GET /api/health | Basic health check |
| GET /api/system/health | Detailed health |
| GET /api/system/diagnostics/recent-errors | Recent error logs |
| GET /api/system/diagnostics/notification-failures | Failed notifications |
| GET /api/db/test | Database connection test |

## Debug Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_DEBUG | True | Flask debug mode |
| FLASK_HOST | 0.0.0.0 | Server host |
| FLASK_PORT | 5000 | Server port |

### Settings

Located in `config/settings.py`:

```python
FLASK_DEBUG: bool
FLASK_HOST: str
FLASK_PORT: int
SECRET_KEY: str
```

## Documentation

See `docs/FRONTEND_DEBUG_ID_SYSTEM.md` for detailed frontend debug system documentation.
