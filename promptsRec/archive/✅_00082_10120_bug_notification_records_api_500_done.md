Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 120
Goal: Fix notification records API returns 500 internal server error
Dependencies: None
Execution: RUNPROMPT

---

## Context

获取订单通知记录 API 返回 500 内部服务器错误。

**Error:**
```
GET http://localhost:8150/api/tool-io-orders/TO-OUT-20260316-003/notification-records 500 (INTERNAL SERVER ERROR)
```

**API Endpoint:** `GET /api/tool-io-orders/<order_no>/notification-records`

## Required References

1. `backend/routes/order_routes.py` - notification-records endpoint (L315-325)
2. `backend/services/tool_io_service.py` - get_notification_records function (L626-630)
3. `backend/services/notification_service.py` - list_notifications_by_order function (L307-330)

## Core Task

调查并修复通知记录 API 返回 500 错误的问题。

## Required Work

1. **Investigate the Error:**
   - 查看后端日志获取详细错误信息
   - 检查 `get_notification_records` 函数的执行流程
   - 验证 `list_notifications_by_order` 函数是否有异常

2. **Check Database Table:**
   - 确认 `工装出入库单_通知记录` 表是否存在
   - 验证表结构是否正确

3. **Fix the Root Cause:**
   - 修复发现的问题（可能是表不存在、字段缺失或代码逻辑错误）

4. **Verify the Fix:**
   - 调用 API 确认返回 200 和正确的通知记录数据

## Constraints

- 不要修改 API 接口契约
- 保持现有功能不变

## Completion Criteria

- [ ] GET /api/tool-io-orders/<order_no>/notification-records 返回 200
- [ ] 返回正确的通知记录数据
- [ ] 不影响其他 API 功能
