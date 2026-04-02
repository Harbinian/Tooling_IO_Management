# 00081 - 工装定检任务管理组件 - 后端服务+路由层（Service+Routes）

Primary Executor: Codex
Task Type: Feature Development
Priority: P0
Stage: 2 of 3
Goal: 实现工装定检任务管理后端服务层和API路由
Dependencies: 00080 (backend foundation must complete first)
Execution: RUNPROMPT

---

## Context

承接 Prompt 00080 的后端基础层（4张表 + 4个Repository），本阶段实现：
- 3 个 Service 类（业务逻辑 + 状态机）
- 1 个 Routes 文件（API 端点）
- Blueprint 注册到 web_server.py

**核心设计决策**：
- 状态机：pending→received→outbound_created→outbound_completed→in_progress→report_submitted→accepted/rejected→inbound_created→inbound_completed→closed
- 出入库复用现有 tool_io 订单，出库单必须标注定检任务号
- 质检驳回后任务退回 `report_submitted`
- 72 小时逾期提醒（飞书通知）
- 关键节点全通知

---

## Required References

| 文件 | 用途 |
|------|------|
| `backend/services/tool_io_service.py` | 状态机模式、通知模式 |
| `backend/services/feishu_notification_adapter.py` | 通知适配器复用 |
| `backend/services/rbac_service.py` | 权限检查复用 |
| `backend/routes/order_routes.py` | Routes 模式参考 |
| `backend/routes/common.py` | 通用辅助函数（require_permission, get_authenticated_user 等） |
| `web_server.py` | Blueprint 注册位置 |

---

## Core Task

实现工装定检任务管理后端服务层和 API 路由。

---

## Required Work

### 1. Service 层

创建 3 个 Service 文件：

**`backend/services/inspection_plan_service.py`** - 计划 Service：
- `create_plan(payload, current_user)` - 创建定检任务管理
- `get_plan(plan_no, current_user)` - 获取计划详情
- `list_plans(filters, current_user)` - 分页查询计划
- `update_plan(plan_no, payload, current_user)` - 更新计划（仅草稿状态）
- `publish_plan(plan_no, current_user)` - 发布计划（生成任务 + 发飞书通知）
- `preview_tasks(plan_no, current_user)` - 预览待发布的工装清单（调用 ToolInspectionStatusRepository.get_expiring_tools）
- `close_plan(plan_no, current_user)` - 关闭计划

**`backend/services/inspection_task_service.py`** - 任务 Service（核心状态机）：
- `get_task(task_no, current_user)` - 获取任务详情
- `list_tasks(filters, current_user)` - 分页查询任务（支持 task_status, plan_no 等过滤）
- `receive_task(task_no, current_user)` - 领取任务（pending→received，开启 72h 计时，发飞书通知 QUALITY_INSPECTOR）
- `start_inspection(task_no, current_user)` - 开始检验（received→in_progress）
- `submit_report(task_no, payload, current_user)` - 提交测量报告（in_progress→report_submitted，包含 Base64 附件，发飞书通知 QUALITY_INSPECTOR）
- `accept_report(task_no, current_user)` - 验收通过（report_submitted→accepted，发飞书通知 TEAM_LEADER 和 KEEPER）
- `reject_report(task_no, reject_reason, current_user)` - 驳回报告（report_submitted→rejected→report_submitted，驳回原因记录，发飞书通知 TEAM_LEADER）
- `create_outbound_link(task_no, order_no, current_user)` - 关联出库单（received→outbound_created）
- `create_inbound_link(task_no, order_no, current_user)` - 关联入库单（accepted→inbound_created）
- `advance_from_outbound_completed(task_no, current_user)` - 出库单完成自动推进（outbound_created→outbound_completed→in_progress）
- `advance_from_inbound_completed(task_no, current_user)` - 入库单完成自动推进（inbound_created→inbound_completed）
- `close_task(task_no, current_user)` - 关闭任务（inbound_completed→closed，更新 tool_io_tool_inspection_status 的 next_inspection_date，发飞书通知 PLANNER）
- `get_linked_orders(task_no)` - 查询关联的 tool_io 订单
- `link_order_to_task(order_no, task_no)` - 将订单关联到定检任务
- `check_and_advance_by_order_status(order_no)` - 根据订单状态自动推进任务（出库单 completed → outbound_completed→in_progress，入库单 completed → inbound_completed→closed）
- `get_overdue_tasks()` - 获取逾期任务列表（供定时任务调用）

**状态机转换规则**：
```
pending → received (receive_task)
received → outbound_created (create_outbound_link 或手动关联)
outbound_created → outbound_completed (advance_from_outbound_completed，由出库单 completed 触发)
outbound_completed → in_progress (advance_from_outbound_completed 或 start_inspection)
in_progress → report_submitted (submit_report)
report_submitted → accepted (accept_report)
report_submitted → rejected → report_submitted (reject_report)
report_submitted → accepted → inbound_created (create_inbound_link)
inbound_created → inbound_completed (advance_from_inbound_completed，由入库单 completed 触发)
inbound_completed → closed (close_task)
```

**`backend/services/inspection_notification_service.py`** - 通知 Service：
- `notify_task_received(task_no, user_name)` - 任务被领取通知质检检验员
- `notify_report_submitted(task_no)` - 报告提交通知质检检验员
- `notify_report_accepted(task_no)` - 报告验收通知班组长和保管员
- `notify_report_rejected(task_no, reason)` - 报告驳回通知班组长
- `notify_task_closed(task_no)` - 任务关闭通知计划员
- `notify_overdue(task_no, overdue_hours)` - 逾期提醒（72h）

参照 `notification_service.py` 和 `feishu_notification_adapter.py` 模式，调用 `deliver_notification_to_feishu` 发送飞书通知。

### 2. Routes 层

**`backend/routes/inspection_routes.py`**：

参照 `order_routes.py` 和 `mpl_routes.py` 模式，创建 Blueprint `inspection_bp`，实现以下端点：

| 方法 | 端点 | 权限 | 说明 |
|------|------|------|------|
| GET/POST | `/api/inspection/plans` | inspection:list/create | 计划列表/创建 |
| GET/PUT | `/api/inspection/plans/{plan_no}` | inspection:view/write | 计划详情/修改 |
| POST | `/api/inspection/plans/{plan_no}/publish` | inspection:publish | 发布计划 |
| GET | `/api/inspection/plans/{plan_no}/preview-tasks` | inspection:list | 预览待发布工装清单 |
| GET | `/api/inspection/tasks` | inspection:list | 任务列表 |
| GET | `/api/inspection/tasks/{task_no}` | inspection:view | 任务详情 |
| POST | `/api/inspection/tasks/{task_no}/receive` | inspection:execute | 领取任务 |
| POST | `/api/inspection/tasks/{task_no}/start-inspection` | inspection:execute | 开始检验 |
| POST | `/api/inspection/tasks/{task_no}/submit-report` | inspection:execute | 提交测量报告 |
| POST | `/api/inspection/tasks/{task_no}/accept` | inspection:accept | 验收通过 |
| POST | `/api/inspection/tasks/{task_no}/reject` | inspection:accept | 驳回报告 |
| POST | `/api/inspection/tasks/{task_no}/create-outbound` | inspection:execute | 关联出库单 |
| POST | `/api/inspection/tasks/{task_no}/create-inbound` | inspection:execute | 关联入库单 |
| POST | `/api/inspection/tasks/{task_no}/close` | inspection:close | 关闭任务 |
| GET | `/api/inspection/tasks/{task_no}/linked-orders` | inspection:view | 查询关联订单 |
| POST | `/api/inspection/orders/{order_no}/link-task` | inspection:execute | 关联订单到任务 |
| GET | `/api/inspection/status/{serial_no}` | inspection:list | 查询工装定检状态 |
| POST | `/api/inspection/advance-by-order/{order_no}` | inspection:execute | 根据订单状态推进任务 |

**权限字符串定义**（需在 `sys_permission` 表中预置）：
- `inspection:create`
- `inspection:list`
- `inspection:view`
- `inspection:write`
- `inspection:publish`
- `inspection:execute`
- `inspection:accept`
- `inspection:close`

### 3. Blueprint 注册

在 `web_server.py` 中：
1. 添加 `from backend.routes.inspection_routes import inspection_bp`
2. 在 `app.register_blueprint()` 区域添加 `app.register_blueprint(inspection_bp)`

---

## Constraints

1. **UTF-8 编码**：所有文件必须 `encoding='utf-8'`
2. **权限检查**：使用 `@require_permission('inspection:xxx')` 装饰器
3. **用户信息**：通过 `get_authenticated_user()` 获取当前用户
4. **错误处理**：所有端点必须有 try-except，返回规范化的错误 JSON
5. **状态机安全**：状态转换前必须验证当前状态，不允许跳步
6. **Base64 验证**：报告附件必须在 Service 层验证大小（2MB）
7. **不出库回退**：如果出库单创建后被取消，任务状态应回退

---

## Completion Criteria

1. 3 个 Service 文件已创建且包含所有指定方法
2. `inspection_routes.py` 已实现所有指定端点
3. `web_server.py` 已注册 `inspection_bp`
4. 状态机转换规则完整且安全
5. 所有新增 .py 文件通过 `python -m py_compile` 语法检查
6. RBAC 权限字符串已在代码中正确定义（对应 `sys_permission` 表）
