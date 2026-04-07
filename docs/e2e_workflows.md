# E2E 工作流定义 / E2E Workflow Definitions

**用途**: `human-e2e-tester` 技能执行完整工作流测试
**权威来源**: `docs/RBAC_PERMISSION_MATRIX.md`, `backend/services/order_workflow_service.py`

---

## 完整出库工作流（含驳回重提）/ Full Outbound Workflow with Rejection & Resubmit

### 流程概览

```
[太东旭 - taidongxu 班组长]
       │
       ▼
1. 创建订单 (order:create)
   订单类型: 出库 / Outbound
   工装: T000001
       │
       ▼
2. 提交订单 (order:submit)
       │
       ▼
[胡婷婷 - 保管员]
       │
       ▼
3. 查看待确认订单列表 (order:list) — 状态: submitted
       │
       ▼
4. 驳回订单 (order:cancel/reject)
   填写驳回原因（测试用）
       │
       ▼
   状态变为: rejected

--- 第一轮：驳回重提 ---

[太东旭 - taidongxu 班组长]
       │
       ▼
5. 查看被驳回的订单
       │
       ▼
6. 修改订单（补充/调整工装数量）
       │
       ▼
7. 再次提交订单 (order:submit)
       │
       ▼
[胡婷婷 - 保管员]
       │
       ▼
8. 再次查看待确认订单列表
       │
       ▼
9. 确认工装明细 (order:keeper_confirm)
       │
       ▼
10. 选择运输接收方 (assign-transport)
       │
       ▼
11. 发送运输通知 (notification:send_feishu)
       │
       ▼
[冯亮 - 生产准备工]
       │
       ▼
12. 查看预知运输列表 (pre-transport) — 状态: keeper_confirmed
       │
       ▼
13. 开始运输 (transport-start) — 状态: transport_in_progress
       │
       ▼
14. 完成运输 (transport-complete) — 状态: transport_completed
       │
       ▼
[太东旭 - taidongxu 班组长]
       │
       ▼
15. 最终确认 (order:final_confirm) — 状态: completed
       │
       ▼
16. 验证工装位置更新

--- 清理：管理员删除订单 ---

[CA - 系统管理员]
       │
       ▼
17. 查看订单列表，找到已完成的订单
       │
       ▼
18. 删除订单 (order:delete) — 验证删除功能
```

### 测试目标 / Test Objectives

| 步骤 | 目标 | 期望结果 |
|------|------|---------|
| 1-2 | TEAM_LEADER 创建并提交出库订单 | 订单状态: submitted |
| 3-4 | KEEPER 驳回订单，填写原因 | 订单状态: rejected |
| 5-7 | TEAM_LEADER 查看驳回原因，修改后重新提交 | 订单状态恢复: submitted |
| 8-11 | KEEPER 再次确认、指派运输、发送通知 | 订单状态: transport_notified |
| 12-14 | PRODUCTION_PREP 执行运输开始和完成 | 订单状态: transport_completed |
| 15-16 | TEAM_LEADER 最终确认，验证工装位置变更 | 订单状态: completed |
| 17-18 | SYS_ADMIN 删除已完成的订单 | 订单从前端列表消失 |

### 驳回重提特定检查

1. **驳回原因可见性** — 保管员驳回后，班组长是否看到驳回原因？
2. **重提流程** — 班组长能否编辑并重提被驳回的订单？
3. **状态重置** — 重提后订单状态是否正确重置为 submitted？
4. **运输分配持久性** — 如果驳回前保管员已分配运输，重提时是否清除？

---

## 完整出库工作流（标准无驳回）/ Full Outbound Workflow (Standard)

```
[太东旭 - taidongxu 班组长]
       │
       ▼
1. 创建订单 (order:create)
       │
       ▼
2. 搜索工装 T000001 (tool:search)
       │
       ▼
3. 选择目的组织/车间
       │
       ▼
4. 提交订单 (order:submit)
       │
       ▼
[胡婷婷 - 保管员]
       │
       ▼
5. 查看待确认订单列表 (order:list) — 状态: submitted
       │
       ▼
6. 确认工装明细 (order:keeper_confirm)
       │
       ▼
7. 选择运输接收方 (assign-transport)
       │
       ▼
8. 发送运输通知 (notification:send_feishu)
       │
       ▼
[冯亮 - 生产准备工]
       │
       ▼
9. 查看预知运输列表 (pre-transport) — 状态: keeper_confirmed
       │
       ▼
10. 开始运输 (transport-start) — 状态: transport_in_progress
       │
       ▼
[可选] 11. 上报异常 (report-transport-issue)
       │
       ▼
12. 完成运输 (transport-complete) — 状态: transport_completed
       │
       ▼
[太东旭 - taidongxu 班组长]
       │
       ▼
13. 最终确认 (order:final_confirm) — 状态: completed
       │
       ▼
14. 验证工装位置更新
```

---

## 完整入库工作流 / Full Inbound Workflow

```
[太东旭 - taidongxu 班组长]
       │
       ▼
1. 创建订单 (order:create) — type: inbound
       │
       ▼
2. 选择源组织/车间
       │
       ▼
3. 提交订单 (order:submit)
       │
       ▼
[胡婷婷 - 保管员]
       │
       ▼
5. 确认工装明细 (order:keeper_confirm)
       │
       ▼
7. 选择运输接收方 (assign-transport)
       │
       ▼
8. 发送运输通知 (notification:send_feishu)
       │
       ▼
[冯亮 - 生产准备工]
       │
       ▼
10. 开始运输 (transport-start)
       │
       ▼
12. 完成运输 (transport-complete)
       │
       ▼
[胡婷婷 - 保管员]
       │
       ▼
13. 最终确认 (order:final_confirm) — 入库由 KEEPER 最终确认
       │
       ▼
14. 验证工装位置更新
```

### 入库 vs 出库关键差异

| 差异点 | 出库 | 入库 |
|--------|------|------|
| 创建者 | TEAM_LEADER | TEAM_LEADER |
| 方向 | 从仓库到车间 | 从车间到仓库 |
| 最终确认者 | TEAM_LEADER | KEEPER |

---

## 按工作流步骤的 API 端点 / API Endpoints by Workflow Step

| 步骤 | API | 方法 | 权限 | 角色 |
|------|-----|------|------|------|
| 创建订单 | `/api/tool-io-orders` | POST | order:create | TEAM_LEADER, PLANNER |
| 搜索工装 | `/api/tools/search` | GET | tool:search | TEAM_LEADER, KEEPER, PLANNER, PRODUCTION_PREP |
| 提交订单 | `/api/tool-io-orders/<order_no>/submit` | POST | order:submit | TEAM_LEADER, PLANNER |
| 查看待确认 | `/api/tool-io-orders` | GET | order:list | TEAM_LEADER, KEEPER, PLANNER |
| 保管员确认 | `/api/tool-io-orders/<order_no>/keeper-confirm` | POST | order:keeper_confirm | KEEPER |
| 指派运输 | `/api/tool-io-orders/<order_no>/assign-transport` | POST | order:keeper_confirm | KEEPER |
| 发送通知 | `/api/tool-io-orders/<order_no>/notify-transport` | POST | notification:send_feishu | KEEPER |
| 预知列表 | `/api/tool-io-orders/pre-transport` | GET | order:transport_execute | PRODUCTION_PREP |
| 开始运输 | `/api/tool-io-orders/<order_no>/transport-start` | POST | order:transport_execute | KEEPER, PRODUCTION_PREP |
| 上报异常 | `/api/tool-io-orders/<order_no>/report-transport-issue` | POST | order:transport_execute | PRODUCTION_PREP |
| 查看异常 | `/api/tool-io-orders/<order_no>/transport-issues` | GET | order:keeper_confirm | KEEPER |
| 处理异常 | `/api/tool-io-orders/<order_no>/resolve-transport-issue` | POST | order:keeper_confirm | KEEPER |
| 完成运输 | `/api/tool-io-orders/<order_no>/transport-complete` | POST | order:transport_execute | KEEPER, PRODUCTION_PREP |
| 最终确认 | `/api/tool-io-orders/<order_no>/final-confirm` | POST | order:final_confirm | TEAM_LEADER (出库), KEEPER (入库) |
| 取消订单 | `/api/tool-io-orders/<order_no>/cancel` | POST | order:cancel | TEAM_LEADER, KEEPER |
