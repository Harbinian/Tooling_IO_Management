# Fix Integration Test Database Connection Configuration

## Context / 上下文

The integration tests in `tests/` fail with 8 failures because they require a real SQL Server database connection that is not available in the test environment. Tests were failing with connection errors, not skip messages.

## Core Task / 核心任务

Fix the integration test environment so tests can run without requiring a real SQL Server connection.

### Approach: pytest markers + skip logic

1. Created `tests/conftest.py` with skip logic:
   - Registers `integration` marker
   - Auto-skips integration tests when `TESTING_DB_URL` is not configured

2. Added `@pytest.mark.integration` to integration test files:
   - `tests/test_get_tool_io_orders.py` — ToolIOFinalConfirmationServiceTests class + 2 specific tests
   - `tests/test_tool_io_service_submit.py` — ToolIoServiceSubmitTests class

3. Created `tests/README.md` documenting how to run tests

## Completion Criteria / 完成标准

1. Integration tests that need real DB are marked with `pytest.mark.integration`
2. Running `python -m pytest tests/` locally shows clear SKIP messages, NOT FAIL
3. Unit tests that don't need DB continue to pass
4. `tests/README.md` documents how to run integration tests with proper DB

## Execution Report / 执行报告

**Commit**: `43d87b8` - pushed to `main`
**Verification**: 242 passed, 7 skipped (integration), 2 failed (pre-existing)

**Changes made**:
1. Created `tests/conftest.py` with pytest marker and skip logic
2. Added `@pytest.mark.integration` to `test_get_tool_io_orders.py`
3. Added `@pytest.mark.integration` to `test_tool_io_service_submit.py`
4. Created `tests/README.md`

**Note**: 2 failed tests in `test_rbac_enforcement.py` (missing `list_roles` attribute) are pre-existing issues unrelated to this fix.
