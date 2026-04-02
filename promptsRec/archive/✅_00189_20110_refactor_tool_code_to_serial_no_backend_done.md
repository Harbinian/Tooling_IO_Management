# 重构提示词：后端 tool_code → serial_no 字段重命名

## Header

Primary Executor: Codex
Task Type: Refactoring
Priority: P1
Stage: 1/2
Goal: 将后端和数据库中的 tool_code 字段重命名为 serial_no
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

**业务背景**：工装唯一标识的正确名称是"工装序列号"（serial_no），而非"工装编码"（tool_code）。需要将数据库字段 `tool_code` 重命名为 `serial_no`，并更新所有后端代码中的引用。

**影响范围**：
- 数据库：2张表（`tool_io_order_item`、`tool_status_change_history`）需要 DDL 变更
- 后端：11个文件需要修改
- 文档：API_SPEC.md、DB_SCHEMA.md 等

---

## Core Task / 核心任务

### 1. 数据库 Schema 变更

创建数据库迁移脚本，执行以下 DDL：

```sql
-- 1. 添加新列 serial_no
ALTER TABLE tool_io_order_item ADD serial_no VARCHAR(64) NULL;
ALTER TABLE tool_status_change_history ADD serial_no VARCHAR(64) NULL;

-- 2. 迁移数据
UPDATE tool_io_order_item SET serial_no = tool_code WHERE serial_no IS NULL;
UPDATE tool_status_change_history SET serial_no = tool_code WHERE serial_no IS NULL;

-- 3. 删除旧列（确认数据迁移成功后执行）
-- ALTER TABLE tool_io_order_item DROP COLUMN tool_code;
-- ALTER TABLE tool_status_change_history DROP COLUMN tool_code;
```

### 2. 修改 column_names.py

文件：`backend/database/schema/column_names.py`

修改以下常量中的 `tool_code` → `serial_no`：

- `ITEM_COLUMNS`（第132行）：`'tool_code': 'tool_code'` → `'serial_no': 'serial_no'`
- `ITEM_CHINESE_COLUMNS`（第166行）：`'tool_code': 'tool_code'` → `'serial_no': 'serial_no'`
- `TOOL_STATUS_HISTORY_COLUMNS`（第367行）：`'tool_code': 'tool_code'` → `'serial_no': 'serial_no'`
- `TOOL_MASTER_COLUMNS`（第295行）：保持 `'tool_code': '序列号'` 不变（因为这是外部系统表映射）

### 3. 修改后端文件

修改以下11个文件中所有引用 `tool_code` 的地方，改为 `serial_no`：

1. `backend/database/core/database_manager.py` - SQL 查询中的 tool_code 引用
2. `backend/database/repositories/order_repository.py` - Repository 层的 tool_code 引用
3. `backend/database/repositories/tool_repository.py` - Repository 层的 tool_code 引用
4. `backend/services/tool_io_service.py` - Service 层的 tool_code 引用
5. `backend/services/tool_location_service.py` - Service 层的 tool_code 引用
6. `backend/services/order_query_service.py` - Service 层的 tool_code 引用
7. `backend/routes/tool_routes.py` - 路由层的 tool_code 引用
8. `backend/database/services/order_service.py` - Service 层的 tool_code 引用
9. `backend/database/tool_io_queries.py` - SQL 查询的 tool_code 引用
10. `backend/database/schema/schema_manager.py` - Schema 管理的 tool_code 引用

**注意**：
- 使用 `grep -r "tool_code"` 搜索所有引用
- 确保 API 响应中的字段名从 `tool_code` 改为 `serial_no`
- 前端依赖此字段名进行数据解析

### 4. 更新 API SPEC 文档

文件：`docs/API_SPEC.md`

将所有 `tool_code` 相关描述更新为 `serial_no`：
- 请求参数中的 `items[].tool_code` → `items[].serial_no`
- 响应参数中的 `tool_code` → `serial_no`
- 描述文本中的"工装编码" → "工装序列号"

---

## Required Work / 必需工作

1. **数据库迁移脚本** - 创建可执行的 SQL 迁移脚本
2. **字段常量更新** - 修改 `column_names.py` 中的 3 处常量定义
3. **后端代码更新** - 修改 11 个文件中的所有 tool_code 引用
4. **API 文档更新** - 更新 docs/API_SPEC.md 中的字段说明
5. **DB_SCHEMA 文档更新** - 更新 docs/DB_SCHEMA.md 中的字段说明

---

## Constraints / 约束条件

1. **UTF-8 编码** - 所有文件操作必须使用 `encoding='utf-8'`
2. **字段名常量使用** - 所有 SQL 中的中文字段名必须通过 `column_names.py` 引用，禁止直接使用中文字面量
3. **API 字段一致性** - 确保 API 请求/响应中的字段名与数据库列名一致
4. **向后兼容** - 如果存在过渡期需求，可以同时支持新旧字段名

---

## Completion Criteria / 完成标准

1. ✅ 数据库成功添加 `serial_no` 列并迁移数据
2. ✅ `column_names.py` 中的 3 处常量已更新
3. ✅ 11 个后端文件中的 tool_code 引用已全部替换为 serial_no
4. ✅ API SPEC 文档已更新
5. ✅ DB_SCHEMA 文档已更新
6. ✅ 语法检查通过：`python -m py_compile <修改的后端文件>`
7. ✅ 后端服务可正常启动

---

## Verification / 验证

```powershell
# 语法检查
python -m py_compile backend/database/schema/column_names.py
python -m py_compile backend/database/core/database_manager.py
python -m py_compile backend/database/repositories/order_repository.py
python -m py_compile backend/services/tool_io_service.py

# 启动后端验证
python web_server.py
```
