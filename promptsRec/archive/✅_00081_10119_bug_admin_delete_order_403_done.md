Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: 119
Goal: Fix admin delete order API returns 403 permission denied
Dependencies: None
Execution: RUNPROMPT

---

## Context

管理员调用 `DELETE /api/tool-io-orders/<order_no>` API 时返回 403 FORBIDDEN 错误。虽然 admin 角色在 RBAC 设计中应该拥有所有权限（包括 `order:delete`），但权限检查失败。

**Error:**
```
DELETE http://localhost:8150/api/tool-io-orders/TO-OUT-20260316-002 403 (FORBIDDEN)
Delete error: AxiosError: Request failed with status code 403
```

**Expected:** Admin should be able to delete orders.

## Required References

1. `backend/routes/order_routes.py` - DELETE endpoint (L279-299)
2. `backend/services/rbac_service.py` - Permission loading logic
3. `backend/services/auth_service.py` - Authentication and permission check
4. `backend/routes/common.py` - require_permission decorator

## Core Task

调查并修复管理员删除订单时权限检查失败的问题。

## Required Work

1. **Investigate Permission Loading:**
   - 检查 admin 用户的权限是如何加载的
   - 验证 `load_permissions_for_role_ids` 函数是否正确加载权限
   - 检查数据库中 `sys_role_permission_rel` 表是否有 admin 的权限记录

2. **Check RBAC Bootstrap Logic:**
   - 审查 `_bootstrap_initial_data` 函数中的 admin 权限分配逻辑
   - 确认 admin 角色是否正确获取所有权限

3. **Fix the Root Cause:**
   - 如果是权限加载问题，修复 `rbac_service.py`
   - 如果是数据库初始化问题，添加迁移逻辑

4. **Verify the Fix:**
   - 使用 admin 账号调用 DELETE API
   - 确认返回 200 而不是 403

## Constraints

- 只修改必要的代码，不要破坏现有的 RBAC 逻辑
- 保持权限检查的安全性

## Completion Criteria

- [ ] Admin 用户可以成功删除订单
- [ ] API 返回 200 而不是 403
- [ ] 其他角色权限不受影响
