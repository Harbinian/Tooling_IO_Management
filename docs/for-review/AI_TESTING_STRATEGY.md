# AI Review: Testing Strategy

## Test Files

| File | Purpose |
|------|---------|
| tests/test_org_service.py | Organization service tests |
| tests/test_rbac_service.py | RBAC service tests |
| tests/test_auth_system.py | Authentication tests |
| tests/test_rbac_data_scope_service.py | Data scope tests |
| tests/test_get_tool_io_orders.py | Order query tests |

## Test Framework

- **Framework**: pytest
- **Database**: Uses actual SQL Server database
- **Coverage**: pytest-cov

## Running Tests

```powershell
# Backend syntax check
python -m py_compile web_server.py database.py

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

## Frontend Testing

- Manual testing via browser
- `npm run dev` starts dev server at localhost:5173
- E2E tests (if configured)

## Manual Testing Checklist

### Order Workflow
- [ ] Create order (draft)
- [ ] Submit order
- [ ] Keeper confirmation
- [ ] Transport notification
- [ ] Transport start/complete
- [ ] Final confirmation
- [ ] Order completion

### RBAC
- [ ] Login with different roles
- [ ] Permission-based UI visibility
- [ ] API authorization

### UI Components
- [ ] Dashboard loads
- [ ] Order list displays
- [ ] Order create form works
- [ ] Order detail shows history
- [ ] Keeper process shows pending items
- [ ] Admin user page works

## Debug Mode

- Frontend: `?debugUI=1` query param
- Backend: `FLASK_DEBUG=True` env var

## Database Testing

- Database created on first API call via `ensure_tool_io_tables()`
- Test via: GET /api/db/test

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| GET /api/health | Basic health |
| GET /api/system/health | Detailed health |
| GET /api/system/diagnostics/recent-errors | Error logs |
| GET /api/system/diagnostics/notification-failures | Notification failures |
