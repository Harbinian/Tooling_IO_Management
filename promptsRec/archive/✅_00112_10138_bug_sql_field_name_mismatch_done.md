Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: 131
Goal: Fix SQL field name mismatches causing runtime errors in query interfaces
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在代码审查中发现多个 SQL 查询接口使用了错误的字段名，导致运行时 SQL 执行失败。主要问题有两类：

1. **英文字段名 vs 中文字段名**: 部分代码使用了英文（如 `order_no`, `transport_operator`），而数据库 Schema 定义的是中文（如 `出入库单号`, `运输人ID`）

2. **乱码字段名**: 部分 SQL 中的中文字段名显示为乱码字符（如 `搴忓垪鍙?`），这是文件编码问题导致的

这些错误会导致所有涉及的工作流（订单提交、保管员确认、运输通知等）执行失败。

---

## Required References / 必需参考

- `docs/DB_SCHEMA.md` - 数据库 Schema 定义（权威字段名来源）
- `docs/API_SPEC.md` - API 规范
- `backend/services/order_workflow_service.py` - 需要修复的文件
- `backend/services/tool_io_service.py` - 需要修复的文件
- `backend/services/tool_io_runtime.py` - 需要修复的文件
- `backend/database/repositories/tool_repository.py` - 需要修复的文件

---

## Core Task / 核心任务

修复所有 SQL 查询接口中的字段名错误，确保与数据库 Schema 一致。

---

## Required Work / 必需工作

### 1. 修复 `order_workflow_service.py`

需要修改的位置和字段映射：

| 行号 | 错误写法 | 正确字段名 |
|------|---------|-----------|
| 208-215 | `transport_operator` | `运输人ID` |
| 208-215 | `transport_operator_name` | `运输人姓名` |
| 208-215 | `order_no` | `出入库单号` |
| 208-215 | `updated_at` | `修改时间` |
| 264-269 | `order_status` | `单据状态` |
| 264-269 | `order_no` | `出入库单号` |
| 264-269 | `updated_at` | `修改时间` |
| 312-318 | `order_status` | `单据状态` |
| 312-318 | `order_no` | `出入库单号` |

### 2. 修复 `tool_io_service.py`

- 第896-919行: `batch_query_tools` 函数中所有字段名需要使用正确的中文列名
- 第1134-1146行: `notify_transport` 的 UPDATE 语句字段名修复

### 3. 修复 `tool_io_runtime.py`

- 第85-94行: `get_recent_operation_errors` 函数乱码字段名
- 第104-112行: `get_recent_notification_failures` 函数乱码字段名

### 4. 修复 `tool_repository.py`

- 第42-62行: 工装主表查询
- 第88-101行: 探测 SQL
- 第223-246行: `check_tools_available`
- 第292-306行: `check_tools_in_draft_orders`
- 第347-359行: `load_tool_master_map`

### 5. 验证修复

修复后必须执行语法检查：
```powershell
python -m py_compile backend/services/order_workflow_service.py
python -m py_compile backend/services/tool_io_service.py
python -m py_compile backend/services/tool_io_runtime.py
python -m py_compile backend/database/repositories/tool_repository.py
```

---

## Constraints / 约束条件

1. **禁止修改 Schema**: 只修复代码中的字段名，不修改数据库 Schema
2. **保持文件编码**: 修复时确保文件保持 UTF-8 编码
3. **保留业务逻辑**: 只修改字段名，不改变 SQL 的业务逻辑
4. **参数化查询**: 保持现有的参数化查询方式不变
5. **事务处理**: 关键操作的事务处理逻辑保持不变

---

## Completion Criteria / 完成标准

1. 所有 SQL 语句使用正确的字段名（与 DB_SCHEMA.md 一致）
2. 文件编码正确，中文字段名正常显示（非乱码）
3. `python -m py_compile` 所有修改的文件无语法错误
4. 现有的参数化查询方式未被破坏
5. 业务逻辑保持不变

---

## Acceptance Tests / 验收测试

1. 执行 `python -m py_compile` 验证所有修改的文件
2. 检查文件中无乱码字符（中文字段正常显示）
3. 确认所有 SQL UPDATE/SELECT 语句使用中文字段名
4. 确认 `order_workflow_service.py` 中 `update_transport_info` 函数能正确执行
5. 确认 `tool_io_service.py` 中 `batch_query_tools` 和 `notify_transport` 函数能正确执行
