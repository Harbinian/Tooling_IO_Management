# Bug Fix: Keeper Cross-Organization Data Access Violation

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P0 (CRITICAL)
**Stage**: 10163
**Goal**: Fix RBAC data scope so KEEPER role can only see orders from their own organization
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context / 上下文

E2E 测试发现 KEEPER 角色（hutingting, DEPT_001）可以看到并操作 TEAM_LEADER（taidongxu, DEPT_005）创建的订单，这是跨组织数据访问违规。

测试场景：
- hutingting (KEEPER, DEPT_001) 调用 `GET /api/tool-io-orders` 可以看到 DEPT_005 的订单
- 这破坏了组织数据隔离 - 用户可以访问其他组织的数据

---

## Required References / 必需参考

1. `backend/services/rbac_data_scope_service.py` - 特别是 `order_matches_scope()` 函数
2. `backend/database/schema/column_names.py` - 中文字段名常量
3. `docs/RBAC_DESIGN.md` - RBAC 设计文档
4. `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵

---

## Core Task / 核心任务

修复 `order_matches_scope()` 函数中的数据隔离逻辑。

当前问题代码 (`rbac_data_scope_service.py` 第 262-265 行):
```python
# 3. KEEPER: Any keeper can see submitted/partially_confirmed orders
#    This enables CROSS-ORGANIZATION department auto-assignment
if order_status in {"submitted", "partially_confirmed"}:
    if is_keeper:
        # Any keeper can see submitted orders - enables cross-org department assignment
        return True
```

这个逻辑允许任何 keeper 看到任何组织的 submitted/partially_confirmed 订单，违反了 RBAC 数据隔离原则。

---

## Required Work / 必需工作

1. **调查根本原因**
   - 检查 `order_matches_scope()` 函数的完整逻辑
   - 确认 keeper 角色当前的 data scope 配置
   - 检查 `get_tool_io_orders` 如何应用 scope filtering

2. **修复方案选择**（选择其一）:
   - **方案A**: 移除跨组织 keeper 可见性逻辑，keeper 只能看到自己组织的订单
   - **方案B**: 为跨组织可见性添加明确的 scope_type (如 `CROSS_ORG_KEEPER`)，并在 RBAC 配置中显式启用

3. **实施修复**
   - 修改 `order_matches_scope()` 中的 keeper 可见性逻辑
   - 确保 keeper 只能看到 `org_ids` 范围内的订单
   - 确保测试验证修复有效

4. **验证**
   - 确认 hutingting (DEPT_001) 看不到 DEPT_005 的订单
   - 确认 keeper 仍然可以看到自己组织的订单

---

## Constraints / 约束条件

- 不得破坏现有的其他 RBAC 逻辑
- 不得移除 keeper 查看自己组织订单的能力
- 不得修改 API 路径或接口契约
- 使用 `column_names.py` 中的常量引用中文字段名
- 所有 SQL 必须使用参数化查询

---

## Completion Criteria / 完成标准

1. hutingting (KEEPER, DEPT_001) 调用 `GET /api/tool-io-orders` 只能看到 DEPT_001 的订单
2. taidongxu (TEAM_LEADER, DEPT_005) 的订单对 hutingting 不可见
3. keeper 仍然可以执行自己组织订单的 confirm/cancel 操作
4. 相关日志正确记录操作审计跟踪
