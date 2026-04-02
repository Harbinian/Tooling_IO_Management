# 00080 - 工装定检任务管理组件 - 后端基础层（数据库+Repository）

Primary Executor: Codex
Task Type: Feature Development
Priority: P0
Stage: 1 of 3
Goal: 实现工装定检任务管理后端基础层（4张表 + 4个Repository）
Dependencies: None
Execution: RUNPROMPT

---

## Context

工装出入库管理系统需要新增**工装定检任务管理**组件。需求背景：
- 物资保障部计划员需要发布和维护定检任务管理
- 运维安环部班组长需要执行定检（涉及 tool_io 出入库）
- 质量管理部检验员需要验收测量结果
- 测量报告需上传附件（Base64，2MB 限制）
- 保管员负责关闭任务，系统自动更新工装定检状态

**核心设计决策**：
- 4 张新表：plan、task、report、tool_inspection_status
- 状态机：pending→received→outbound_created→outbound_completed→in_progress→report_submitted→accepted→inbound_created→inbound_completed→closed
- 出入库复用现有 tool_io 订单，出库单必须标注定检任务号
- 工装定检状态表（`tool_io_tool_inspection_status`）本系统独立维护
- 72 小时逾期提醒机制

---

## Required References

| 文件 | 用途 |
|------|------|
| `backend/database/schema/column_names.py` | 字段名常量定义模式 |
| `backend/database/repositories/order_repository.py` | Repository 模式参考 |
| `backend/database/schema/schema_manager.py` | 建表语句注册模式 |
| `backend/database/repositories/mpl_repository.py` | MPL Repository 参考 |
| `backend/database/repositories/system_config_repository.py` | SystemConfig Repository 参考 |

---

## Core Task

实现工装定检任务管理后端基础层，包括：
1. 在 `column_names.py` 中追加 4 张表的字段常量
2. 在 `schema_manager.py` 中注册 4 张表的建表语句
3. 创建 4 个 Repository 类

---

## Required Work

### 1. 字段常量 - `backend/database/schema/column_names.py`

在 `TABLE_NAMES` 字典中追加：
```python
'INSPECTION_PLAN': 'tool_io_inspection_plan',
'INSPECTION_TASK': 'tool_io_inspection_task',
'INSPECTION_REPORT': 'tool_io_inspection_report',
'TOOL_INSPECTION_STATUS': 'tool_io_tool_inspection_status',
```

追加 `INSPECTION_PLAN_COLUMNS`、`INSPECTION_TASK_COLUMNS`、`INSPECTION_REPORT_COLUMNS`、`TOOL_INSPECTION_STATUS_COLUMNS` 四个字典，字段名全英文。

**定检任务管理表 (tool_io_inspection_plan)** 字段：
- `id`: int
- `plan_no`: varchar(50) - 主键，格式 `DJP-{YYYYMMDD}-{SEQ}`
- `plan_name`: varchar(200) - 计划名称
- `plan_year`: int - 计划年度
- `plan_month`: int - 计划月份
- `inspection_type`: varchar(50) - 定检类型（如：regular/annual/special）
- `status`: varchar(20) - 状态（draft/published/closed）
- `creator_id`: varchar(50) - 创建人ID
- `creator_name`: varchar(100) - 创建人姓名
- `publish_time`: datetime - 发布时间
- `remark`: varchar(500) - 备注
- `created_at`: datetime
- `updated_at`: datetime
- `created_by`: varchar(100)
- `updated_by`: varchar(100)

**定检任务表 (tool_io_inspection_task)** 字段：
- `id`: int
- `task_no`: varchar(50) - 主键，格式 `DJT-{YYYYMMDD}-{SEQ}`
- `plan_no`: varchar(50) - 关联计划号
- `serial_no`: varchar(100) - 工装序列号（关联外部表 Tooling_ID_Main）
- `tool_name`: varchar(200) - 工装名称
- `drawing_no`: varchar(100) - 工装图号
- `spec_model`: varchar(100) - 规格型号
- `task_status`: varchar(30) - 状态（pending/received/outbound_created/outbound_completed/in_progress/report_submitted/accepted/rejected/inbound_created/inbound_completed/closed）
- `assigned_to_id`: varchar(50) - 班组长ID
- `assigned_to_name`: varchar(100) - 班组长姓名
- `receive_time`: datetime - 领取时间
- `outbound_order_no`: varchar(50) - 关联出库单号
- `inbound_order_no`: varchar(50) - 关联入库单号
- `inspection_result`: varchar(20) - 检验结果（pass/fail）
- `reject_reason`: varchar(500) - 驳回原因
- `report_no`: varchar(50) - 关联报告号
- `next_inspection_date`: date - 下次定检日期（关闭时由保管员更新）
- `deadline`: datetime - 截止时间
- `actual_complete_time`: datetime - 实际完成时间
- `remark`: varchar(500)
- `created_at`: datetime
- `updated_at`: datetime
- `created_by`: varchar(100)
- `updated_by`: varchar(100)

**测量报告表 (tool_io_inspection_report)** 字段：
- `id`: int
- `report_no`: varchar(50) - 主键，格式 `RPT-{YYYYMMDD}-{SEQ}`
- `task_no`: varchar(50) - 关联任务号
- `inspector_id`: varchar(50) - 检验员ID
- `inspector_name`: varchar(100) - 检验员姓名
- `inspection_date`: date - 检验日期
- `inspection_result`: varchar(20) - 检验结果（pass/fail）
- `measurement_data`: text - 测量数据（JSON 格式）
- `attachment_data`: nvarchar(max) - 附件（Base64，2MB 限制）
- `attachment_name`: varchar(200) - 附件文件名
- `remark`: varchar(500)
- `created_at`: datetime
- `updated_at`: datetime
- `created_by`: varchar(100)
- `updated_by`: varchar(100)

**工装定检状态表 (tool_io_tool_inspection_status)** 字段：
- `id`: int
- `serial_no`: varchar(100) - 主键，工装序列号
- `tool_name`: varchar(200) - 工装名称
- `drawing_no`: varchar(100) - 工装图号
- `last_inspection_date`: date - 最近定检日期
- `next_inspection_date`: date - 下次定检日期
- `inspection_cycle_days`: int - 定检周期（天）
- `inspection_status`: varchar(20) - 状态（normal/overdue/pending）
- `remark`: varchar(500)
- `updated_at`: datetime
- `updated_by`: varchar(100)

### 2. 建表语句 - `backend/database/schema/schema_manager.py`

参照 `ensure_mpl_table()` 和 `ensure_transport_issue_table()` 模式，创建：
- `ensure_inspection_plan_table()`
- `ensure_inspection_task_table()`
- `ensure_inspection_report_table()`
- `ensure_tool_inspection_status_table()`

并在 `ensure_all_tables()` 中追加调用。

### 3. Repository 类

参照 `order_repository.py` 和 `mpl_repository.py` 模式，创建 4 个 Repository：

**`inspection_plan_repository.py`** - 定检任务管理 Repository：
- `create_plan(plan_data)` - 创建计划
- `get_plan(plan_no)` - 获取计划详情
- `get_plans(filters)` - 分页查询计划
- `update_plan(plan_no, plan_data)` - 更新计划
- `publish_plan(plan_no)` - 发布计划（生成任务）
- `preview_tasks(plan_no)` - 预览待发布的工装清单（查询 tool_io_tool_inspection_status 中到期的工装）

**`inspection_task_repository.py`** - 定检任务 Repository：
- `create_task(task_data)` - 创建任务
- `create_tasks_bulk(tasks)` - 批量创建任务
- `get_task(task_no)` - 获取任务详情
- `get_tasks(filters)` - 分页查询任务（支持 task_status, plan_no, assigned_to_id 等过滤）
- `update_task_status(task_no, new_status, operator_info)` - 更新任务状态
- `link_outbound_order(task_no, order_no)` - 关联出库单
- `link_inbound_order(task_no, order_no)` - 关联入库单
- `get_overdue_tasks(hours=72)` - 查询逾期任务（received 状态超过 N 小时未推进）

**`inspection_report_repository.py`** - 测量报告 Repository：
- `create_report(report_data)` - 创建报告（含 Base64 附件验证，2MB 限制）
- `get_report(report_no)` - 获取报告详情
- `get_reports_by_task(task_no)` - 查询任务的报告
- `update_report(report_no, report_data)` - 更新报告

**`tool_inspection_status_repository.py`** - 工装定检状态 Repository：
- `get_status(serial_no)` - 获取工装定检状态
- `upsert_status(serial_no, status_data)` - 创建或更新状态
- `update_next_inspection_date(serial_no, next_date, updated_by)` - 更新下次定检日期
- `get_expiring_tools(days_before=30)` - 查询即将到期的工装（用于计划员预览）
- `get_overdue_tools()` - 查询已到期工装

---

## Constraints

1. **UTF-8 编码**：所有文件必须 `encoding='utf-8'`
2. **字段名常量**：所有 SQL 中的中文字段名必须使用 `column_names.py` 中的常量
3. **主键格式**：
   - 计划号：`DJP-{YYYYMMDD}-{SEQ}`，SEQ 为当日顺序号（001-999）
   - 任务号：`DJT-{YYYYMMDD}-{SEQ}`
   - 报告号：`RPT-{YYYYMMDD}-{SEQ}`
4. **序号生成**：参照 `order_repository.py` 中 `generate_order_no_atomic` 模式，实现原子性序号生成
5. **Base64 限制**：报告附件大小不超过 2MB
6. **事务要求**：批量创建任务、出库/入库单关联必须使用事务
7. **不得修改外部系统表**：Tooling_ID_Main 保持只读

---

## Completion Criteria

1. `column_names.py` 已追加 4 张表的常量定义
2. `schema_manager.py` 已注册 4 张表的建表语句
3. 4 个 Repository 类已创建且包含所有指定方法
4. 所有新增 .py 文件通过 `python -m py_compile` 语法检查
5. Repository 方法的 SQL 使用字段常量，无中文字面量
