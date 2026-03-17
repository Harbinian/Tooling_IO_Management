Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 201
Goal: Split monolithic database.py into layered architecture without changing behavior
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

The current database module is implemented as a single large file (`database.py`) containing multiple responsibilities:

- Connection pool management
- Database manager (singleton)
- SQL helpers
- Schema alignment logic
- Business queries (tooling, dispatch, TPITR, acceptance)
- Order creation logic
- Statistics aggregation
- Utility functions

This violates separation of concerns and makes the system difficult to maintain, extend, and debug.

The refactor must preserve all existing behavior.

---

## Required References / 必需参考

- Existing `database.py` full implementation
- Current backend routes (order_routes, tool_routes, dashboard_routes)
- Existing SQL queries and table structures (DO NOT assume changes)
- Existing API responses

---

## Core Task / 核心任务

Refactor the database layer into a modular layered architecture while preserving all functionality and external interfaces.

---

## Required Work / 必需工作

### 1. Define target architecture

Split into the following modules:

- db/core/connection_pool.py
  - ConnectionPool class

- db/core/database_manager.py
  - DatabaseManager (singleton)
  - connection lifecycle

- db/core/executor.py
  - execute_query abstraction
  - logging + error handling

- db/schema/schema_manager.py
  - ensure_tool_io_tables
  - schema alignment SQL

- db/repositories/
  - tool_repository.py
  - dispatch_repository.py
  - tpitr_repository.py
  - acceptance_repository.py
  - order_repository.py

- db/services/
  - order_service.py (generate_order_no_atomic, create order)
  - dashboard_service.py (stats aggregation)

- db/utils/
  - date_utils.py
  - sql_utils.py

---

### 2. Move logic into correct layers

- ALL SQL → repositories
- ALL business aggregation → services
- DatabaseManager → only connection + execution
- Remove business logic from DB layer

---

### 3. Preserve public API

- Existing function names MUST remain callable:
  - get_tool_basic_info
  - get_dispatch_info
  - get_monitor_stats
  - create_tool_io_order
  - etc.

Implement compatibility layer:

- database.py becomes a thin facade
- Delegates to new modules

---

### 4. Remove direct SQL building from business logic

- Extract SQL strings into repository layer
- No SQL inside service layer

---

### 5. Ensure connection lifecycle safety

- All DB operations must use context manager
- No leaked connections
- Pool usage must remain consistent

---

### 6. Logging normalization

- Centralize logging in executor layer
- Remove duplicated logging logic

---

### 7. Gradual migration support

- Keep backward compatibility
- Do NOT break existing imports

---

## Constraints / 约束条件

- DO NOT change database schema
- DO NOT change SQL semantics
- DO NOT change API response structure
- DO NOT rename public methods
- DO NOT introduce new dependencies
- MUST preserve connection pool behavior
- MUST maintain thread safety

---

## Completion Criteria / 完成标准

1. database.py size reduced by at least 60%
2. All logic moved into structured modules
3. All existing APIs still return identical results
4. No change in SQL execution behavior
5. No connection leaks under stress test
6. Existing endpoints (order_routes, dashboard_routes) run without modification
7. New architecture passes:
   - order creation
   - dashboard loading
   - tool query
8. Codebase clearly reflects layered separation:
   - core / repositories / services / utils
