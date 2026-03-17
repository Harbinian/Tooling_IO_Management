# 10134_bug_notification_create_permission_unassigned

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10134
Goal: Assign notification:create permission to KEEPER role to fix 403 on generate-text APIs
Dependencies: None
Execution: RUNPROMPT

---

## Context

### 问题描述

**API**:
- `GET /api/tool-io-orders/<order_no>/generate-keeper-text`
- `GET /api/tool-io-orders/<order_no>/generate-transport-text`

**症状**: HTTP 403 FORBIDDEN - 没有任何角色可以访问这两个 API

**原因**: `notification:create` 权限未分配给任何角色

```python
# order_routes.py:380-381
@require_permission("notification:create")  # ⚠️ NO ROLE ASSIGNED
def api_generate_keeper_text(order_no):

# order_routes.py:395-396
@require_permission("notification:create")  # ⚠️ NO ROLE ASSIGNED
def api_generate_transport_text(order_no):
```

### 业务分析

| API | 用途 | 应该在哪个角色下工作 |
|-----|------|-------------------|
| `generate-keeper-text` | KEEPER 收到订单后生成确认文本 | **KEEPER** |
| `generate-transport-text` | KEEPER 确认后生成运输通知文本 | **KEEPER** |

**结论**: `notification:create` 权限应分配给 **KEEPER** 角色

---

## Required References

1. `backend/services/rbac_service.py` - RBAC 权限配置
   - `_ensure_incremental_permission_defaults()` 函数 (L287-365)
   - 查找 `notification:create` 相关代码
2. `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵文档
3. `docs/RBAC_DESIGN.md` - RBAC 设计文档

---

## Core Task

为 KEEPER 角色分配 `notification:create` 权限，修复 generate-text API 的 403 问题。

### 需要修改的位置

1. `backend/services/rbac_service.py` 的 `_ensure_incremental_permission_defaults()` 函数中添加：
   - 确保 `notification:create` 权限存在
   - 将 `notification:create` 分配给 ROLE_KEEPER

### 预期结果

修改后 KEEPER 角色拥有以下权限：
- `notification:view` ✅ (刚修复)
- `notification:create` ✅ (本次修复)
- `notification:send_feishu` ✅

---

## Required Work

1. **检查 rbac_service.py** 中 `_ensure_incremental_permission_defaults()` 函数
2. **确认 `notification:create` 权限已定义**（如果不存在需要先创建）
3. **为 ROLE_KEEPER 添加** `notification:create` 权限关联
4. **验证** 修改后 KEEPER 可以访问 generate-text APIs
5. **更新 RBAC_PERMISSION_MATRIX.md** 同步权限矩阵

### 权限定义参考

```python
# 应该存在的权限定义
('notification:create', 'Create Notification', 'notification', 'create'),
```

### 需要添加的角色权限关联

```python
# 在 _ensure_role_permission_rel 调用中添加
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="notification:create",
)
```

---

## Constraints

1. **只修改必要的权限配置**，不要修改其他角色权限
2. **遵循现有代码模式** - 使用 `_ensure_permission_exists` 和 `_ensure_role_permission_rel` 函数
3. **同步更新文档** - 修改后更新 `docs/RBAC_PERMISSION_MATRIX.md`
4. **语法检查** - 修改后运行 `python -m py_compile backend/services/rbac_service.py`

---

## Completion Criteria

- [ ] KEEPER 角色可以成功访问 `GET /api/tool-io-orders/<order_no>/generate-keeper-text`
- [ ] KEEPER 角色可以成功访问 `GET /api/tool-io-orders/<order_no>/generate-transport-text`
- [ ] `docs/RBAC_PERMISSION_MATRIX.md` 中 notification:create 行已更新，标注 KEEPER 拥有此权限
- [ ] 语法检查通过: `python -m py_compile backend/services/rbac_service.py`
