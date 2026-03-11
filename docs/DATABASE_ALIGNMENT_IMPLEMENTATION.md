# 数据库对齐实现 / Database Alignment Implementation

---

## 范围 / Scope

此更改将现有 SQL Server `database.py` 实现与 `docs/SQLSERVER_SCHEMA_REVISION.md` 对齐，而不替换当前的 `pyodbc` + `DatabaseManager` 访问模式。 / This change aligns the existing SQL Server `database.py` implementation with `docs/SQLSERVER_SCHEMA_REVISION.md` without replacing the current `pyodbc` + `DatabaseManager` access pattern.

## 修复的 Schema 不匹配 / Schema mismatches fixed

- 更新 `工装出入库单_主表` CREATE TABLE 定义以包含运行时代码已引用的字段: / Updated `工装出入库单_主表` CREATE TABLE definition to include fields already referenced by runtime code:
  - `工装数量` / Tool Quantity
  - `已确认数量` / Confirmed Quantity
  - `最终确认人` / Final Confirmer
  - `取消原因` / Cancel Reason
- 更新 `工装出入库单_明细` CREATE TABLE 定义以包含运行时代码已引用的字段: / Updated `工装出入库单_明细` CREATE TABLE definition to include fields already referenced by runtime code:
  - `确认时间` / Confirmation Time
  - `出入库完成时间` / IO Completion Time
- 在 `ensure_tool_io_tables()` 内添加幂等 Schema 对齐 SQL，以便现有数据库可以使用 `ALTER TABLE` 就地升级，而不仅依赖新建表。 / Added idempotent schema alignment SQL inside `ensure_tool_io_tables()` so existing databases can be upgraded in place with `ALTER TABLE` instead of relying on fresh table creation only.
- 为主工装出入库表添加非破坏性索引创建，以更紧密地匹配修订后的 SQL Server 设计，并从结构上支持常见订单/过滤查询。 / Added non-destructive index creation for the main Tool IO tables to match the revised SQL Server design more closely and keep common order/filter queries structurally supported.

## 函数对齐 / Function alignment

根据已纠正的 Schema 审查当前工装出入库 CRUD 函数，重点关注: / Reviewed the current Tool IO CRUD functions against the corrected schema, with focus on:

- `create_tool_io_order`
- `submit_tool_io_order`
- `get_tool_io_order`
- `get_tool_io_orders`
- `keeper_confirm_order`
- `final_confirm_order`
- `reject_tool_io_order`
- `cancel_tool_io_order`
- `add_tool_io_log`
- `add_tool_io_notification`
- `search_tools`

确认并在已经正确的位置保留现有可用逻辑: / Confirmed and preserved the existing usable logic where already correct:

- 数据库支持的原子订单号分配 / database-backed atomic order number allocation
- 保管员确认输入验证 / keeper confirmation input validation
- 通过 `OUTPUT INSERTED.id` 的同连接通知 ID 获取 / same-connection notification id retrieval through `OUTPUT INSERTED.id`
- SQL Server 兼容的 `GETDATE()`, `IDENTITY` 和 `pyodbc` 参数风格 / SQL Server compatible `GETDATE()`, `IDENTITY`, and `pyodbc` parameter style

## 添加或纠正的字段 / Fields added or corrected

### 工装出入库单_主表 / ToolIOOrder

- `工装数量` / Tool Quantity
- `已确认数量` / Confirmed Quantity
- `最终确认人` / Final Confirmer
- `取消原因` / Cancel Reason

### 工装出入库单_明细 / ToolIOOrderItem

- `确认时间` / Confirmation Time
- `出入库完成时间` / IO Completion Time

### 幂等添加的索引 / Indexes added idempotently

- `工装出入库单_主表`: `单据类型`, `单据状态`, `发起人ID`, `保管员ID`, `创建时间` / `工装出入库单_主表`: `单据类型`, `单据状态`, `发起人ID`, `保管员ID`, `创建时间`
- `工装出入库单_明细`: `出入库单号`, `工装编码`, `明细状态` / `工装出入库单_明细`: `出入库单号`, `工装编码`, `明细状态`
- `工装出入库单_操作日志`: `出入库单号`, `操作时间` / `工装出入库单_操作日志`: `出入库单号`, `操作时间`
- `工装出入库单_通知记录`: `出入库单号`, `发送状态`, `通知渠道` / `工装出入库单_通知记录`: `出入库单号`, `发送状态`, `通知渠道`

## 剩余风险 / Remaining risks

- 在此任务中未完成针对实时 SQL Server 实例的运行时验证，因此 Schema 迁移成功是通过结构和语法审查验证的，而不是通过端到端 DB 执行。 / Runtime validation against a live SQL Server instance was not completed in this task, so schema migration success is verified structurally and by syntax review, not by end-to-end DB execution.
- `cancel_tool_io_order` 当前仍不接受来自 API 层的取消原因参数。Schema 现在支持 `取消原因`，但该字段的完整填充取决于未来的 API/请求更改。 / `cancel_tool_io_order` still does not accept a cancel reason parameter from the current API layer. The schema now supports `取消原因`, but full population of that field depends on future API/request changes.
- `web_server.py` 中的运输通知路由仍包含超出此纯数据库模块对齐任务范围的字段名不一致问题。 / The transport notification route in `web_server.py` still contains field-name inconsistencies outside the scope of this database-module-only alignment task.

## 需要确认的假设 / Assumptions requiring confirmation

- `出入库完成时间` 是 `final_confirm_order` 引用的项目完成时间戳的预期物理 SQL Server 列名。 / `出入库完成时间` is the intended physical SQL Server column name for the item completion timestamp referenced by `final_confirm_order`.
- 修订后的 Schema 的附加索引可以安全地添加到目标 SQL Server 环境，并且与现有的手动 DBA 索引不冲突。 / The revised schema's additional indexes are safe to add in the target SQL Server environment and do not conflict with existing manually managed DBA indexes.
- 现有生产数据库使用与本仓库中当前备份恢复基准相同的中文表名和列名。 / Existing production databases use the same Chinese table and column names as the current backup-restored baseline in this repository.
