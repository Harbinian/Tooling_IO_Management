# Release Preparation and Go-Live Checklist

**Date:** 2026-03-13
**Version:** 1.0
**Classification:** Internal Release

---

## 1. Release Scope Summary

### 1.1 Implemented Capabilities

| Capability | Status | Notes |
|------------|--------|-------|
| Authentication & Login | ✅ Complete | Session-based auth with role/permission support |
| RBAC & Permission Enforcement | ✅ Complete | Role-based access with org-scoped data |
| Organization Structure | ✅ Complete | Hierarchical org structure |
| Order Creation | ✅ Complete | Draft → Submit workflow |
| Order List | ✅ Complete | Paginated with filters |
| Order Detail | ✅ Complete | Items, logs, notifications |
| Keeper Workflow | ✅ Complete | Confirmation with item validation |
| Transport Workflow | ✅ Complete | Assign, start, complete states |
| Final Confirmation | ✅ Complete | Team leader (outbound) / Keeper (inbound) |
| Notification Records | ✅ Complete | Persistent notification history |
| Feishu Delivery | ✅ Complete | Webhook-based notifications |
| Dashboard Metrics | ✅ Complete | Real-time statistics |
| Audit Logging | ✅ Complete | Operation trail for all actions |
| Tool Location Management | ✅ Complete | Location tracking |

### 1.2 Partially Complete / Optional for First Release

| Capability | Status | Notes |
|------------|--------|-------|
| API Contract Snapshot | ✅ Complete | Documented for regression baseline |
| Transport Assignment | ✅ Complete | Assign transport operator to order |

### 1.3 Not Release-Ready

None identified.

---

## 2. Deployment Prerequisites

### 2.1 Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CESOFT_DB_SERVER` | Yes | 192.168.19.220,1433 | SQL Server host |
| `CESOFT_DB_DATABASE` | Yes | CXSYSYS | Database name |
| `CESOFT_DB_USERNAME` | Yes | sa | Database user |
| `CESOFT_DB_PASSWORD` | Yes | (empty) | Database password |
| `SECRET_KEY` | Yes | tooling-io-secret-key | Flask session secret |
| `FLASK_ENV` | No | production | Environment mode |
| `FLASK_HOST` | No | 0.0.0.0 | Server bind address |
| `FLASK_PORT` | No | 5000 | Server port |

### 2.2 Feishu Configuration (Required for Notifications)

| Variable | Required | Description |
|----------|----------|-------------|
| `FEISHU_APP_ID` | Yes | Feishu application ID |
| `FEISHU_APP_SECRET` | Yes | Feishu application secret |
| `FEISHU_APP_TOKEN` | Yes | Feishu application token |
| `FEISHU_WEBHOOK_URL` | Yes | Default webhook URL |
| `FEISHU_WEBHOOK_TRANSPORT` | Yes | Transport notification webhook |
| `FEISHU_NOTIFICATION_TIMEOUT_SECONDS` | No | Notification timeout (default: 10) |

### 2.3 Database Requirements

- SQL Server 2016+
- Compatible ODBC Driver (pyodbc)
- Network access to database server
- Initial schema auto-created on first API call

### 2.4 RBAC Bootstrap

- Initial users must be created in database
- Roles: `admin`, `team_leader`, `keeper`
- Permissions must be assigned per role
- See `docs/RBAC_INIT_DATA.md` for seed data

### 2.5 Backend Startup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python web_server.py
```

### 2.6 Frontend Build/Deploy

```powershell
cd frontend
npm install
npm run build
# Deploy frontend/dist/ to web server
```

---

## 3. Release Readiness Assessment

### 3.1 Functional Completeness

| Item | Status | Notes |
|------|--------|-------|
| Authentication | ✅ Ready | Login/logout with session |
| Order Lifecycle | ✅ Ready | Full workflow implemented |
| Tool Search | ✅ Ready | Paginated with filters |
| Notifications | ✅ Ready | Persistent + Feishu delivery |
| Organization | ✅ Ready | CRUD + tree structure |

### 3.2 Security & Authentication

| Item | Status | Notes |
|------|--------|-------|
| Session-based Auth | ✅ Ready | Flask session management |
| Password Handling | ✅ Ready | Plain text (legacy) |
| RBAC Enforcement | ✅ Ready | Permission decorators |
| Org Data Scoping | ✅ Ready | Multi-tenant isolation |

### 3.3 RBAC Correctness

| Item | Status | Notes |
|------|--------|-------|
| Role Definitions | ✅ Ready | admin, team_leader, keeper |
| Permission Matrix | ✅ Ready | Per-endpoint enforcement |
| Workflow Guards | ✅ Ready | Role-based state transitions |

### 3.4 Data Scope Correctness

| Item | Status | Notes |
|------|--------|-------|
| Org-based Filtering | ✅ Ready | Users see only own org data |
| Query Filtering | ✅ Ready | Backend enforces scope |

### 3.5 Workflow State Consistency

| Item | Status | Notes |
|------|--------|-------|
| State Machine | ✅ Ready | All transitions validated |
| Invalid Transitions | ✅ Ready | Rejected with error |
| Partial Confirmation | ✅ Ready | Support partially confirmed |

### 3.6 Notification Safety

| Item | Status | Notes |
|------|--------|-------|
| Persistent Records | ✅ Ready | Stored in database |
| Webhook Fallback | ✅ Ready | On failure, record saved |
| Retry Logic | ⚠️ Needs Attention | No automatic retry |

### 3.7 Auditability

| Item | Status | Notes |
|------|--------|-------|
| Operation Logs | ✅ Ready | All key actions logged |
| Log Fields | ✅ Ready | User, time, action, details |

### 3.8 UI Availability

| Item | Status | Notes |
|------|--------|-------|
| Login Page | ✅ Ready | Element Plus form |
| Order List | ✅ Ready | Filtered, paginated |
| Order Detail | ✅ Ready | Items, logs, actions |
| Order Create | ✅ Ready | Multi-item support |
| Keeper View | ✅ Ready | Pending confirm list |
| Dashboard | ✅ Ready | Statistics view |

### 3.9 Environment Configuration

| Item | Status | Notes |
|------|--------|-------|
| Settings Module | ✅ Ready | Centralized in config/settings.py |
| .env Support | ✅ Ready | Environment-based config |
| Defaults | ✅ Ready | Sensible defaults provided |

### 3.10 Operational Recoverability

| Item | Status | Notes |
|------|--------|-------|
| Health Check | ✅ Ready | /api/health endpoint |
| DB Connection Test | ✅ Ready | /api/db/test endpoint |
| Error Logging | ✅ Ready | Python logging module |
| Order Cancellation | ✅ Ready | Can cancel non-completed orders |

---

## 4. Risk Assessment

### 4.1 High Severity Risks

None identified.

### 4.2 Medium Severity Risks

| # | Risk | Affected Layer | Severity | Mitigation | Release Impact |
|---|------|----------------|----------|------------|----------------|
| 1 | No automatic notification retry | Notification | Medium | Monitor Feishu delivery; implement retry job if needed | Notifications may fail silently |
| 2 | Password stored plain text | Security | Medium | Accept for internal pilot; add hashing for production | Security concern for production |

### 4.3 Low Severity Risks

| # | Risk | Affected Layer | Severity | Mitigation | Release Impact |
|---|------|----------------|----------|------------|----------------|
| 1 | Limited test coverage | Testing | Low | Add tests before production | Harder to detect regressions |
| 2 | No backup/restore procedure | Operations | Low | Standard SQL Server backup applies | Standard DB backup needed |
| 3 | No rate limiting | Security | Low | Consider adding for production | Potential abuse vector |

---

## 5. Go-Live Checklist

### 5.1 Database Readiness

- [ ] SQL Server instance accessible
- [ ] Network connectivity verified (port 1433)
- [ ] Initial schema created (auto-created on first API call)
- [ ] RBAC seed data loaded
- [ ] Test users created (at least one per role)

### 5.2 RBAC Initialization

- [ ] Admin user account created
- [ ] Team leader role assigned to appropriate users
- [ ] Keeper role assigned to appropriate users
- [ ] Permission assignments verified

### 5.3 Auth Configuration

- [ ] `SECRET_KEY` set to secure random value
- [ ] `FLASK_ENV` set to `production`
- [ ] Session timeout configured appropriately

### 5.4 Backend Startup

- [ ] Python virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured
- [ ] Backend starts without errors
- [ ] Health endpoint returns OK: `GET /api/health`
- [ ] Database connection test passes: `GET /api/db/test`

### 5.5 Frontend Build/Deploy

- [ ] Node.js dependencies installed
- [ ] Build completes successfully: `npm run build`
- [ ] Build output deployed to web server
- [ ] Frontend loads without console errors

### 5.6 Feishu Configuration

- [ ] Feishu app credentials configured
- [ ] Webhook URLs configured and accessible
- [ ] Test notification sent successfully

### 5.7 Smoke Tests

| Test | Expected Result |
|------|-----------------|
| Login with valid credentials | Success, redirect to dashboard |
| Login with invalid credentials | Error message displayed |
| Create new order | Order appears in list |
| Submit order | Status changes to "submitted" |
| Keeper confirms order | Status changes to "keeper_confirmed" |
| Final confirm outbound (team leader) | Status changes to "completed" |
| Final confirm inbound (keeper) | Status changes to "completed" |
| Reject order | Status changes to "rejected" |
| Cancel order | Status changes to "cancelled" |
| Search tools | Results displayed |
| View organization tree | Tree structure displayed |

### 5.8 Role-Based Test Accounts

| Role | Test Account | Verification |
|------|--------------|-------------|
| Admin | (create) | Full access to all functions |
| Team Leader | (create) | Can create orders, final confirm outbound |
| Keeper | (create) | Can confirm items, final confirm inbound |

### 5.9 Order Workflow Verification

- [ ] Outbound workflow: Draft → Submitted → Keeper Confirmed → Team Leader Final Confirm → Completed
- [ ] Inbound workflow: Draft → Submitted → Keeper Confirmed → Keeper Final Confirm → Completed
- [ ] Rejection workflow: Any state → Rejected (authorized roles only)
- [ ] Cancellation workflow: Non-terminal states → Cancelled

### 5.10 Notification Verification

- [ ] Keeper notification sent on confirmation
- [ ] Transport notification sent on transport trigger
- [ ] Notification records visible in order detail

### 5.11 Rollback / Fallback Considerations

- [ ] Database backup available before deployment
- [ ] Previous version backup available
- [ ] Rollback procedure documented
- [ ] Feishu webhook URLs point to correct environment

---

## 6. Release Recommendation

### 6.1 Assessment Summary

| Dimension | Assessment |
|-----------|------------|
| Functional Completeness | ✅ Ready |
| Security | ⚠️ Needs Attention (password storage) |
| RBAC | ✅ Ready |
| Data Scope | ✅ Ready |
| Workflow | ✅ Ready |
| Notifications | ⚠️ Needs Attention (retry logic) |
| Auditability | ✅ Ready |
| UI | ✅ Ready |
| Configuration | ✅ Ready |
| Recoverability | ⚠️ Needs Attention (backup procedure) |

### 6.2 Recommendation

**✅ Ready for Internal Test Release**

The system is functionally complete and ready for controlled internal testing. Before production deployment, address:

1. **High Priority:** Implement password hashing for production use
2. **Medium Priority:** Add notification retry mechanism
3. **Low Priority:** Document full backup/restore procedure

### 6.3 Release Classification

| Level | Status |
|-------|--------|
| Internal Test Release | ✅ Recommended |
| Pilot Release | ⚠️ After internal testing |
| Production Release | ⚠️ After pilot validation |

---

## 7. Appendix

### A. Key Documentation References

| Document | Purpose |
|----------|---------|
| `docs/ARCHITECTURE_INDEX.md` | Architecture reference |
| `docs/API_CONTRACT_SNAPSHOT.md` | API contract baseline |
| `docs/API_REGRESSION_CHECKLIST.md` | Regression test checklist |
| `docs/RBAC_DESIGN.md` | RBAC design specification |
| `docs/RBAC_INIT_DATA.md` | Seed data reference |
| `docs/RELEASE_PRECHECK_REPORT.md` | Previous release check |

### B. API Endpoints Summary

Total: 32 endpoints
- Authentication: 2
- Tools: 2
- Orders: 18
- Organizations: 5
- Notifications: 2
- System: 3

### C. Database Tables

| Table | Purpose |
|-------|---------|
| 工装出入库单_主表 | Order main table |
| 工装出入库单_明细 | Order line items |
| 工装出入库单_操作日志 | Audit trail |
| 工装出入库单_通知记录 | Notification history |

---

*Document Version: 1.0*
*Last Updated: 2026-03-13*
