# Human Simulated E2E Test Report

**Report Type:** Revised for scripted-e2e-builder intake
**Original Report:** `HUMAN_SIMULATED_E2E_TEST_REPORT_20260318_170500.md`
**Revision Date:** 2026-03-18
**Reviewer:** Codex
**Purpose:** Normalize the original report into a reliable input for automated API/E2E test design without inventing unverified workflows.

---

## 1. Executive Assessment

The original report is usable as a partial source for automation, but not as a complete end-to-end workflow baseline.

It contains:

- verified success paths for admin authentication, tool search, dashboard metrics, and empty order list retrieval
- one verified critical failure blocking order creation
- blocked downstream workflow steps caused by that failure
- inferred RBAC conclusions that should not be treated as executed evidence

This revised version separates:

- executed and evidenced results
- code-inferred observations
- blocked scenarios
- automation candidates that are safe to implement now

---

## 2. Test Data Constraint

Per `scripted-e2e-builder`, automated tests must use only the approved tooling record below.

| Field | Value |
|-------|-------|
| Serial Number | `T000001` |
| Tooling Drawing Number | `Tooling_IO_TEST` |
| Tool Name | Use exact value returned by the system at runtime |
| Model | Use exact value returned by the system at runtime |

Notes:

- The original report contains mojibake/encoding corruption in some Chinese text fields.
- Because of that corruption, automated tests should avoid hard-coding the corrupted tool name or model text from the report.
- For now, automation should assert stable identifiers such as `tool_code = T000001` and `drawing_no = Tooling_IO_TEST`.

---

## 3. Evidence Classification

### 3.1 Executed and Verified

The following scenarios were actually exercised and have usable evidence:

| Scenario | Result | Evidence Quality | Can Be Automated Now |
|----------|--------|------------------|----------------------|
| Admin login | PASS | High | Yes |
| Token-authenticated access | PASS | Medium | Yes |
| Search tool by serial number `T000001` | PASS | High | Yes |
| Search tool by drawing number `Tooling_IO_TEST` | PASS | High | Yes |
| Tool details returned for test tool | PASS | Medium | Yes |
| `GET /api/dashboard/metrics` | PASS | High | Yes |
| List orders when system has no orders | PASS | High | Yes |
| Create order with valid tool test data | FAIL | High | Yes, as a known-failure regression until fixed |

### 3.2 Executed but Not Conclusive

| Scenario | Result | Reason |
|----------|--------|--------|
| Team Leader login | FAIL | Password unavailable; not a permission denial conclusion |
| Keeper login | FAIL | Password unavailable; not a permission denial conclusion |

### 3.3 Blocked

| Scenario | Result | Blocking Cause |
|----------|--------|----------------|
| Get created order detail | BLOCKED | No order could be created |
| Submit order | BLOCKED | Order creation failed |
| Keeper confirm | BLOCKED | Order creation failed |
| Transport workflow | BLOCKED | Order creation failed |
| Final confirm | BLOCKED | Order creation failed |

### 3.4 Code-Inferred Only

The original report included RBAC and workflow capability conclusions derived from code reading. These are useful engineering notes, but they are not valid substitutes for executed end-to-end evidence.

The following should be treated as inferred only until tested with real accounts and executable scenarios:

- Team Leader can complete initiator workflow
- Keeper can complete keeper-only actions
- Unauthorized users are denied specific protected operations
- Organization data-scope isolation is enforced correctly in live requests

---

## 4. Verified Scenarios

### 4.1 Authentication

| Test | Status | Notes |
|------|--------|-------|
| `POST /api/auth/login` with `admin` | PASS | Token-based auth works |
| Authenticated requests with returned token | PASS | Protected requests can be executed after login |
| `taidongxu` login | NOT VERIFIED | Password unknown |
| `hutingting` login | NOT VERIFIED | Password unknown |

### 4.2 Tool Search Using Approved Test Data

| Test | Status | Notes |
|------|--------|-------|
| Search by serial number `T000001` | PASS | Returns correct tooling record |
| Search by drawing number `Tooling_IO_TEST` | PASS | Returns correct tooling record |
| Tool details payload includes expected stable identifiers | PASS | `tool_code` and `drawing_no` were present |

Observed stable fields from the original report:

```json
{
  "tool_code": "T000001",
  "drawing_no": "Tooling_IO_TEST",
  "current_location_text": "A00"
}
```

### 4.3 Dashboard Metrics

| Test | Status | Notes |
|------|--------|-------|
| `GET /api/dashboard/metrics` | PASS | Response returned expected metric keys |

Observed response shape:

```json
{
  "active_orders_total": 0,
  "today_outbound_orders": 0,
  "today_inbound_orders": 0,
  "orders_pending_keeper_confirmation": 0,
  "orders_in_transport": 0,
  "orders_pending_final_confirmation": 0
}
```

### 4.4 Order Management

| Test | Status | Notes |
|------|--------|-------|
| `GET /api/tool-io-orders` | PASS | Returns empty list |
| `POST /api/tool-io-orders` | FAIL | Database schema mismatch blocks order creation |
| `GET /api/tool-io-orders/<order_no>` | BLOCKED | No order was created |

---

## 5. Confirmed Critical Defect

### Defect: Existing database schema is missing `org_id`

| Field | Value |
|-------|-------|
| Severity | Critical |
| Module | Backend database schema migration/alignment |
| User Impact | All order creation is blocked on existing databases missing `org_id` |
| Confidence | High |

Observed backend error from the original report:

```text
('42S22', "[42S22] 列名 'org_id' 无效。 (207)")
```

Why this conclusion is reliable:

- The order insert path includes `org_id`.
- The schema creation SQL includes `org_id` for new table creation.
- The schema alignment path is responsible for retrofitting old databases.
- The original report shows runtime failure on an existing database, which is consistent with a missing migration/alignment step.

Relevant repository evidence:

- [schema_manager.py](/E:/CA001/Tooling_IO_Management/backend/database/schema/schema_manager.py#L50)
- [schema_manager.py](/E:/CA001/Tooling_IO_Management/backend/database/schema/schema_manager.py#L88)
- [order_repository.py](/E:/CA001/Tooling_IO_Management/backend/database/repositories/order_repository.py#L98)
- [order_repository.py](/E:/CA001/Tooling_IO_Management/backend/database/repositories/order_repository.py#L120)

---

## 6. RBAC Assessment Boundary

The original report included a permission matrix. That matrix should not be consumed as executed truth for automation generation.

What is safe to say:

- Protected routes exist and are decorated with permission checks.
- Route-level permission wiring is present for order creation, listing, submit, keeper confirm, final confirm, transport actions, and dashboard access.

What is not yet proven by the report:

- Team Leader login success
- Keeper login success
- Role-specific allowed behavior in live execution
- Role-specific denied behavior in live execution

Relevant code references:

- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L24)
- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L52)
- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L83)
- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L106)
- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L128)
- [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py#L189)
- [dashboard_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/dashboard_routes.py#L11)
- [common.py](/E:/CA001/Tooling_IO_Management/backend/routes/common.py#L109)

Automation rule:

- API tests may verify unauthenticated `401` and unauthorized `403` behavior only when valid credentials/tokens for the target roles are available.
- Do not generate passing RBAC workflow tests for Team Leader or Keeper from this report alone.

---

## 7. Frontend Verification Boundary

| Test | Status | Notes |
|------|--------|-------|
| `npm run build` | PASS | Frontend builds successfully |
| Bundle size warning | WARNING | Non-blocking; not a workflow defect |

This is sufficient to support:

- a basic build verification step in the automation pipeline

This is not sufficient to support:

- browser-level workflow assertions for order creation and completion

---

## 8. Safe Automation Scope for scripted-e2e-builder

The following automated tests are safe to generate immediately from this revised report.

### 8.1 API Regression Tests

1. Admin login success using `admin`
2. Authenticated identity/token validation
3. Tool search by `T000001`
4. Tool search by `Tooling_IO_TEST`
5. Dashboard metrics endpoint returns expected keys
6. Empty order list endpoint returns success structure
7. Order creation currently fails clearly when database lacks `org_id`

### 8.2 Frontend / E2E Smoke Tests

Only if a runnable browser path already exists and credentials are available:

1. Admin can log in
2. Admin can navigate to tool search
3. Admin can search for `T000001`
4. Admin can open dashboard and see metric cards

Do not generate passing browser tests for:

- create order
- submit order
- keeper confirm
- transport execution
- final confirmation

until the schema defect is fixed and the roles can actually log in.

---

## 9. Required Follow-Up Before Full Workflow Automation

The following gaps must be closed before converting the full business flow into automated regression tests:

1. Fix database schema alignment so existing databases gain `org_id`
2. Confirm test credentials for `taidongxu`
3. Confirm test credentials for `hutingting`
4. Re-run human or scripted validation for:
   - create order
   - submit order
   - keeper confirm
   - transport start
   - transport complete
   - final confirm
5. Re-run RBAC denied-path checks with real role accounts
6. Re-run organization data-scope checks with users across different orgs

---

## 10. Intake Decision for scripted-e2e-builder

**Decision:** Accept as a partial intake document only.

Use this report to generate:

- stable API smoke tests
- known-failure regression coverage for the `org_id` schema defect
- limited admin-path frontend smoke coverage

Do not use this report alone to generate:

- full order lifecycle automation
- keeper/team leader passing workflows
- production-grade RBAC completion matrix
- data-scope isolation regression tests

---

## 11. Source Files Reviewed During Revision

1. [HUMAN_SIMULATED_E2E_TEST_REPORT_20260318_170500.md](/E:/CA001/Tooling_IO_Management/test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260318_170500.md)
2. [schema_manager.py](/E:/CA001/Tooling_IO_Management/backend/database/schema/schema_manager.py)
3. [order_repository.py](/E:/CA001/Tooling_IO_Management/backend/database/repositories/order_repository.py)
4. [auth_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/auth_routes.py)
5. [dashboard_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/dashboard_routes.py)
6. [order_routes.py](/E:/CA001/Tooling_IO_Management/backend/routes/order_routes.py)
7. [common.py](/E:/CA001/Tooling_IO_Management/backend/routes/common.py)

