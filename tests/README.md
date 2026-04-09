# Test Suite

## Running Tests

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run only unit tests (skip integration tests)
```bash
python -m pytest tests/ -v -m "not integration"
```

### Run integration tests (requires database)
```bash
TESTING_DB_URL="your-database-url" python -m pytest tests/ -v -m integration
```

### Run specific test file
```bash
python -m pytest tests/test_workflow_state_machine.py -v
```

## Test Categories

### Unit Tests
Unit tests use mocks and do not require a database connection. They should pass in any environment.

### Integration Tests
Integration tests require a real SQL Server database connection. They are marked with `@pytest.mark.integration` and will be automatically skipped when `TESTING_DB_URL` is not configured.

## Integration Test Requirements

Set the `TESTING_DB_URL` environment variable to run integration tests:

```bash
# Windows
set TESTING_DB_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=your-server;DATABASE=your-db;UID=user;PWD=pass

# Linux/Mac
export TESTING_DB_URL="DRIVER={ODBC Driver 17 for SQL Server};SERVER=your-server;DATABASE=your-db;UID=user;PWD=pass"
```

## Test Files

| File | Type | Description |
|------|------|-------------|
| `test_workflow_state_machine.py` | Unit | Workflow state machine tests |
| `test_tool_io_runtime.py` | Unit | Tool IO runtime tests |
| `test_order_repository.py` | Unit | Order repository tests (uses mocks) |
| `test_get_tool_io_orders.py` | Mixed | Contains both unit and integration tests |
| `test_tool_io_service_submit.py` | Integration | Submit service tests (requires DB) |
| `test_notification_service.py` | Unit | Notification service tests (uses mocks) |
| `test_auth_system.py` | Unit | Authentication tests |
| `test_rbac_enforcement.py` | Unit | RBAC enforcement tests |
| `test_api_e2e_cleanup.py` | E2E | API cleanup tests |

## Skipped Tests

When running without `TESTING_DB_URL`, the following integration tests will be skipped:

- `test_get_tool_io_orders.py::ToolIOFinalConfirmationServiceTests` (4 tests)
- `test_get_tool_io_orders.py::ToolIONotificationUsageTests::test_generate_keeper_text_creates_internal_notification_record`
- `test_get_tool_io_orders.py::ToolIONotificationUsageTests::test_generate_transport_text_creates_preview_record`
- `test_tool_io_service_submit.py::ToolIoServiceSubmitTests::test_idempotent_submit_skips_notification_side_effects`
