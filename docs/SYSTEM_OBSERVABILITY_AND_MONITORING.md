# System Observability and Monitoring

**Date:** 2026-03-13
**Version:** 1.0

---

## 1. Overview

This document describes the runtime observability and monitoring capabilities of the Tooling IO Management System.

---

## 2. Logging Structure

### 2.1 Centralized Logging

The system uses Python's built-in `logging` module across all backend modules:

```
backend/routes/          - HTTP request/response logging
backend/services/        - Business logic operation logging
backend/database/        - Database operation logging
```

### 2.2 Log Format

Each log entry includes:

- **timestamp** - ISO format datetime
- **module** - Python module name
- **level** - DEBUG, INFO, WARNING, ERROR
- **message** - Descriptive log message
- **context** - Additional context (user_id, order_no, etc.)

Example:
```
2026-03-13 10:30:45,123 - backend.services.tool_io_service - INFO - Order CK20260313001 submitted by user 张三
```

### 2.3 Logged Operations

| Operation | Module | Log Level |
|-----------|--------|-----------|
| Order Creation | tool_io_service | INFO |
| Order Submission | tool_io_service | INFO |
| Keeper Confirmation | tool_io_service | INFO |
| Transport Actions | tool_io_service | INFO |
| Final Confirmation | tool_io_service | INFO |
| Notification Sending | feishu_notification_adapter | INFO/ERROR |
| Authentication | auth_service | INFO/WARNING |
| RBAC Denial | rbac_service | WARNING |
| Database Errors | database/* | ERROR |

---

## 3. Error Classification

### 3.1 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `AUTH_ERROR` | Authentication | Login failures, session issues |
| `RBAC_DENIED` | Authorization | Permission denied for operation |
| `WORKFLOW_ERROR` | Workflow | Invalid state transitions |
| `VALIDATION_ERROR` | Validation | Input validation failures |
| `DATABASE_ERROR` | Database | DB connection or query failures |
| `NOTIFICATION_ERROR` | Notification | Feishu send failures |
| `EXTERNAL_SERVICE_ERROR` | External | Third-party service failures |

### 3.2 Logged Error Patterns

```python
# Example: Workflow error
logger.error(f"WORKFLOW_ERROR: Invalid state transition for order {order_no}: {current_status} -> {target_status}")

# Example: Notification error
logger.error(f"NOTIFICATION_ERROR: Failed to send Feishu notification: {exc}")

# Example: RBAC denial
logger.warning(f"RBAC_DENIED: User {user_id} denied access to {resource}")
```

---

## 4. Health Check Endpoints

### 4.1 Basic Health Check

```
GET /api/health
```

Returns basic system health:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### 4.2 Comprehensive Health Check

```
GET /api/system/health
```

Returns detailed health status:

```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "ok",
      "message": "connected"
    },
    "feishu": {
      "status": "configured",
      "message": "Feishu app credentials configured"
    }
  }
}
```

**Status values:**
- `healthy` - All checks pass
- `degraded` - Non-critical check failed (e.g., Feishu not configured)
- `unhealthy` - Critical check failed (e.g., database unreachable)

---

## 5. Notification Monitoring

### 5.1 Notification Status Tracking

All notifications are persisted with status:

| Status | Description |
|--------|-------------|
| `pending` | Created, not yet sent |
| `sent` | Successfully sent to Feishu |
| `failed` | Failed to send |

### 5.2 Failure Detection

Notification failures are detected and logged:

```python
# From feishu_notification_adapter.py
except requests.Timeout:
    logger.error("NOTIFICATION_ERROR: Feishu request timeout")
    return {"status": "failed", "error": "timeout"}

except Exception as exc:
    logger.error("NOTIFICATION_ERROR: %s", exc)
    return {"status": "failed", "error": str(exc)}
```

### 5.3 Querying Failed Notifications

Admin endpoint to query recent notification failures:

```
GET /api/system/diagnostics/notification-failures
```

Requires `admin:user_manage` permission.

---

## 6. Workflow Diagnostics

### 6.1 Operation Error Logs

Query recent workflow errors:

```
GET /api/system/diagnostics/recent-errors
```

Requires `admin:user_manage` permission.

### 6.2 Audit Log Reference

All workflow transitions are recorded in:

```
Table: 工装出入库单_操作日志
```

Fields:
- `出入库单号` - Order number
- `操作类型` - Operation type
- `操作人` - Operator
- `操作时间` - Timestamp
- `备注` - Remarks

---

## 7. Operational Debugging Guidelines

### 7.1 Common Issues and Diagnostics

| Issue | Diagnostic Approach |
|-------|---------------------|
| Order not progressing | Check `/api/tool-io-orders/<order_no>/logs` for audit trail |
| Notification not sent | Check `/api/system/diagnostics/notification-failures` |
| Database connection failed | Check `/api/health` response |
| Feishu not working | Check `/api/system/health` for Feishu config status |
| Permission denied | Check logs for `RBAC_DENIED` entries |

### 7.2 Log Aggregation

For production deployment, consider:

1. **File-based**: Python's rotating file handler
2. **External**: Integrate with log aggregation service (ELK, Datadog, etc.)
3. **Monitoring**: Set up alerts on ERROR level logs

### 7.3 Recommended Monitoring Rules

| Rule | Action |
|------|--------|
| `WORKFLOW_ERROR` rate > 10/min | Alert on-call |
| `NOTIFICATION_ERROR` rate > 5/min | Alert on-call |
| `DATABASE_ERROR` any | Alert immediately |
| Health check failure | Alert immediately |

---

## 8. API Reference

### Health Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | None | Basic health check |
| `/api/system/health` | GET | None | Comprehensive health |
| `/api/db/test` | GET | `dashboard:view` | DB connection test |

### Diagnostic Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/system/diagnostics/recent-errors` | GET | `admin:user_manage` | Recent workflow errors |
| `/api/system/diagnostics/notification-failures` | GET | `admin:user_manage` | Recent notification failures |

---

## 9. Implementation Notes

### 9.1 Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| Structured Logging | ✅ Implemented | Python logging across modules |
| Error Classification | ✅ Implemented | ERROR codes in logs |
| Basic Health Check | ✅ Implemented | `/api/health` |
| Enhanced Health Check | ✅ Implemented | `/api/system/health` |
| Notification Failure Tracking | ✅ Implemented | Status in DB + logs |
| Diagnostic Endpoints | ✅ Implemented | Admin-only access |
| Log Aggregation | 🔲 Not Implemented | Requires external setup |

### 9.2 Future Enhancements

Consider adding for production:
- Automated log rotation
- External log aggregation (ELK, Datadog)
- Alerting rules
- Metrics dashboard (Prometheus/Grafana)

---

*Document Version: 1.0*
*Last Updated: 2026-03-13*
