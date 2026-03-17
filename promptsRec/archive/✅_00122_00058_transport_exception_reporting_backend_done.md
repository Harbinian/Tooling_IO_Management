# 00058: Transport Exception Reporting Backend

## Metadata

| Field | Value |
|-------|-------|
| **Prompt Number** | 00058 |
| **Type** | Feature |
| **Executor** | Codex |
| **Stage** | Execution |

---

## Task Outcome

Completed backend implementation for transport exception reporting workflow:

- `POST /api/tool-io-orders/<order_no>/report-transport-issue`
- `GET /api/tool-io-orders/<order_no>/transport-issues`
- `POST /api/tool-io-orders/<order_no>/resolve-transport-issue`

All three endpoints are permission-protected and wired to service/repository layers.

---

## Core Deliverables

1. Schema + constants
- Added `TRANSPORT_ISSUE_COLUMNS` in `backend/database/schema/column_names.py`
- Added `ensure_transport_issue_table()` in `backend/database/schema/schema_manager.py`

2. Repository
- New file: `backend/database/repositories/transport_issue_repository.py`
- Implemented: `create_issue`, `get_issues_by_order`, `resolve_issue`
- `create_issue` and `resolve_issue` use explicit DB transactions.

3. Service
- New file: `backend/services/transport_issue_service.py`
- Added validation, order scope checks, state transition checks, and audit log writing.

4. Routes
- Updated `backend/routes/order_routes.py` to expose all 3 APIs with `@require_permission`.

5. Documentation
- Updated `docs/API_SPEC.md`
- Updated `docs/RBAC_PERMISSION_MATRIX.md`

---

## Verification

`python -m py_compile backend\\database\\schema\\column_names.py backend\\database\\schema\\schema_manager.py backend\\database\\repositories\\transport_issue_repository.py backend\\services\\transport_issue_service.py backend\\routes\\order_routes.py` passed.
