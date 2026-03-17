Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10140
Goal: Fix keeper cannot see submitted order in pending-keeper list
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

**问题描述**：
- 胡婷婷（keeper 角色）在工作台（pending-keeper 列表）中无法找到太东旭（team_leader）刚提交的出库订单 TO-OUT-20260324-005
- 太东旭和胡婷婷可能属于不同组织（ORG_DEPT_005 vs ORG_DEPT_001）

**已知信息**：
- 太东旭属于 ORG_DEPT_005（复材车间）
- 胡婷婷属于 ORG_DEPT_001
- 订单 TO-OUT-20260324-005 已提交（order_status = 'submitted'）

---

## Required References / 必需参考

1. `docs/RBAC_DESIGN.md` - RBAC 设计文档
2. `docs/DB_SCHEMA.md` - 数据库 Schema
3. `backend/services/tool_io_service.py` - 待办列表查询逻辑
4. `backend/routes/order_routes.py` - pending-keeper API
5. `backend/database/schema/column_names.py` - 字段名常量

---

## Core Task / 核心任务

调查并修复 keeper 无法在 pending-keeper 列表中看到已提交订单的问题。

---

## Required Work / 必需工作

### 1. 调查阶段

1.1 检查 `pending-keeper` API 的数据过滤逻辑：
- 路径：`backend/routes/order_routes.py` 中的 `api_pending_keeper_orders`
- 检查是否按 `org_id` 过滤

1.2 检查数据库中订单 TO-OUT-20260324-005 的 org_id：
```sql
SELECT 出入库单号, org_id, 单据状态, 发起人ID FROM 工装出入库单_主表 WHERE 出入库单号 = 'TO-OUT-20260324-005';
```

1.3 检查胡婷婷用户的 org_id 和 keeper 分配

1.4 检查 keeper 的 pending-keeper 查询是否应该返回跨组织的订单

### 2. 修复阶段

如果问题是跨组织数据隔离：
- keeper 应该能看到所有组织的已提交订单（作为保管员职责）
- 修改查询逻辑，移除 org_id 过滤或使用不同的过滤策略

如果问题是其他：
- 根据实际原因修复

### 3. 验证

- 语法检查相关文件
- 确认 keeper 角色可以查询到所有已提交订单

---

## Constraints / 约束条件

1. 只修改必要的后端逻辑
2. 不破坏现有的 RBAC 数据隔离
3. 遵循字段名常量使用规范
4. 使用数据库事务处理关键操作

---

## Completion Criteria / 完成标准

1. 胡婷婷可以查询到 TO-OUT-20260324-005（如果该订单属于公共/跨组织职责）
2. 或确认该订单确实不应该对胡婷婷可见（如果是组织隔离设计）
3. keeper 角色的 pending-keeper API 返回正确的订单列表
