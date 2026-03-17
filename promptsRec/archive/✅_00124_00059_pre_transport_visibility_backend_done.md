# 00059 准备工预知运输任务功能 - 后端实现

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00059
Goal: 实现准备工预知列表API（查看已提交但未审批的订单）
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
班组长可以看到订单执行进度。生产准备工（Production Prep）也希望能提前看到已提交但保管员未审批的申请，这样准备工们能有心理准备，知道有哪些运输任务即将到来。

### 目标用户
- 生产准备工：查看即将到来的运输任务

### 核心痛点
当前 Production Prep 无法提前获知即将到来的运输任务，只有在 Keeper 确认并指派后才能看到。

### 业务目标
1. Production Prep 可查看"预知列表"
2. 列表包含已提交(submitted)但 Keeper 还没确认的订单
3. 列表包含 Keeper 已确认、等待运输的订单
4. 按组织数据范围隔离

---

## Required References / 必需参考

- docs/RBAC_PERMISSION_MATRIX.md - 权限矩阵
- docs/RBAC_INIT_DATA.md - RBAC初始数据
- backend/database/schema/column_names.py - 中文字段名常量
- backend/database/repositories/order_repository.py - 订单仓库
- backend/routes/order_routes.py - 订单路由
- backend/services/rbac_service.py - RBAC服务

---

## Core Task / 核心任务

### 1. 权限设计

根据 RBAC_PERMISSION_MATRIX.md：
- `GET /api/tool-io-orders/pre-transport` → `order:transport_execute` (Production Prep)

### 2. 数据范围

- ORG: 本组织的订单
- 过滤条件: `status IN ('submitted', 'keeper_confirmed', 'transport_notified')`

### 3. API端点设计

#### 获取预知列表
```
GET /api/tool-io-orders/pre-transport
权限: order:transport_execute
角色: Production Prep
响应:
{
    "success": true,
    "orders": [
        {
            "order_no": "IO202603250001",
            "order_type": "outbound",
            "destination": "车间A3",
            "status": "submitted",
            "status_text": "已提交",
            "expected_tools": 5,
            "submit_time": "2026-03-25T10:00:00",
            "submitter_name": "李四",
            "estimated_transport_time": null,
            "keeper_confirmed_time": null
        },
        {
            "order_no": "IO202603250002",
            "order_type": "outbound",
            "destination": "车间B2",
            "status": "keeper_confirmed",
            "status_text": "保管员已确认",
            "expected_tools": 3,
            "submit_time": "2026-03-25T09:00:00",
            "submitter_name": "王五",
            "keeper_confirmed_time": "2026-03-25T09:30:00",
            "estimated_transport_time": "2026-03-25T14:00:00"
        }
    ]
}
```

**状态说明**:
| 状态值 | 显示文本 | 说明 |
|--------|---------|------|
| submitted | 已提交 | 等待 Keeper 确认 |
| keeper_confirmed | 保管员已确认 | 已批准，等待运输 |
| transport_notified | 运输已通知 | 已指派，准备执行 |

---

## Required Work / 必需工作

1. **Repository层**
   - 扩展 `order_repository.py`
   - 添加 `get_pre_transport_orders(user_id)` 方法
   - 使用 RBAC 数据范围过滤

2. **Service层**
   - 扩展 `tool_io_service.py`
   - 添加 `get_pre_transport_orders()` 方法
   - 数据格式转换

3. **Route层**
   - 在 `backend/routes/order_routes.py` 添加新端点
   - 使用 `@require_permission('order:transport_execute')` 注解

4. **数据范围**
   - 实现组织级数据隔离
   - Production Prep 只能看本组织的订单

5. **文档同步**
   - 更新 `docs/API_SPEC.md` 添加新API端点

---

## Constraints / 约束条件

1. **权限控制**: 严格基于 RBAC 矩阵实现权限校验
2. **数据隔离**: 按组织隔离，Production Prep 不能看到其他组织的订单
3. **字段名规范**: 所有 SQL 中的中文字段名必须使用 `column_names.py` 中的常量
4. **禁止占位符**: 所有代码必须完整可执行

---

## Completion Criteria / 完成标准

1. ✅ 实现 `GET /api/tool-io-orders/pre-transport` API
2. ✅ API 正确使用 `@require_permission` 权限注解
3. ✅ 实现组织级数据范围隔离
4. ✅ 返回数据包含所有必需字段
5. ✅ 更新 `docs/API_SPEC.md` 添加新API文档
6. ✅ 后端语法检查通过: `python -m py_compile <相关文件>`
