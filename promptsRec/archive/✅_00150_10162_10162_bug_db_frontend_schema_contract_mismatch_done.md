# Bug Fix: 数据库脚本与前后端交互 Schema 契约不一致

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P0
Stage: 10162
Goal: 修复数据库 schema、后端响应结构与前端消费字段之间的关键契约断裂，恢复通知与运输异常链路可用性
Dependencies: 10161
Execution: RUNPROMPT

---

## Context / 上下文

最新审查发现多处“数据库定义 ↔ 后端接口 ↔ 前端消费”不一致，已影响核心流程：

1. 通知查询在英文表上仍使用中文列名过滤，存在 SQL 失败风险。
2. 运输异常接口返回字段为 `issues`，前端按 `data` 读取，导致异常记录列表为空。
3. 运输异常已处理字段命名不一致：后端 `handler_name/handle_time/handle_reply`，前端 `resolver_name/resolve_time/resolution`。
4. `generate_keeper_text` 依赖的 `ORDER_COLUMNS['keeper_demand_text']` 未在列常量中定义，存在运行时 KeyError 风险。
5. schema manager 中 `confirm_time` 类型存在冲突（建表 `VARCHAR(500)`，对齐逻辑为 `DATETIME`）。

---

## Required References / 必需参考

1. `backend/database/schema/schema_manager.py`
2. `backend/database/schema/column_names.py`
3. `backend/services/notification_service.py`
4. `backend/services/feishu_notification_adapter.py`
5. `backend/services/transport_issue_service.py`
6. `backend/database/repositories/transport_issue_repository.py`
7. `backend/services/tool_io_service.py`
8. `backend/routes/order_routes.py`
9. `frontend/src/api/orders.js`
10. `frontend/src/pages/tool-io/OrderDetail.vue`
11. `docs/API_SPEC.md`
12. `docs/DB_SCHEMA.md`
13. `migrations/001_rename_tables_to_english.sql`

---

## Core Task / 核心任务

以“契约一致性”为目标，完成后端响应模型、SQL 列名使用、前端字段消费和 schema 文档的统一修复。不得做临时绕过；必须通过可复现校验证明链路恢复。

---

## Required Work / 必需工作

1. **通知链路 SQL 修复**
- 修复 `notification_service.py` 中中文列名过滤条件，统一使用英文列名（`receiver/notify_channel/send_status/order_no`）。
- 修复 `feishu_notification_adapter.py` 重试查询中的列别名混用，确保与 `tool_io_notification` 英文 schema 一致。

2. **运输异常接口契约统一**
- 统一后端返回结构与前端消费结构（`issues` vs `data` 二选一并全链路一致）。
- 统一已处理异常字段命名，保证详情页可展示处理人/处理时间/处理回复。

3. **订单文本生成字段修复**
- 修复 `generate_keeper_text` 使用的字段常量缺失问题。
- 核对 `ORDER_COLUMNS` 与实际 `tool_io_order` 字段，清理无效或错误映射。

4. **Schema 类型冲突治理**
- 明确 `confirm_time` 的目标类型，并在 `schema_manager.py` 与对齐逻辑中统一。
- 避免同一字段“建表类型”和“schema alignment 类型”冲突。

5. **文档同步**
- 更新 `docs/API_SPEC.md` 中受影响接口的响应字段定义。
- 修复 `docs/DB_SCHEMA.md` 编码问题（UTF-8 无 BOM）并同步真实字段与类型。

6. **验证与测试**
- 后端语法检查：
```powershell
python -m py_compile backend/services/notification_service.py backend/services/feishu_notification_adapter.py backend/services/transport_issue_service.py backend/services/tool_io_service.py backend/database/schema/schema_manager.py backend/database/schema/column_names.py
```
- 前端构建检查：
```powershell
cd frontend
npm run build
```
- 最小 E2E 验证：
  - 订单详情页可加载运输异常列表。
  - 已处理异常字段可正确展示。
  - 通知列表与标记已读接口可正常读写。

---

## Constraints / 约束条件

- 不允许通过“前端兜底吞错”掩盖后端契约问题。
- 不允许新增与现有命名体系冲突的字段别名。
- 不允许破坏既有 RBAC 权限控制。
- 所有新增/修改文本文件必须 UTF-8 无 BOM。
- 变更必须最小化且可追踪，禁止无关重构。

---

## Completion Criteria / 完成标准

1. 通知相关接口不再依赖中文列名，SQL 可稳定执行。
2. 运输异常接口返回与前端消费字段完全一致，列表与已处理详情可见。
3. `generate_keeper_text` 路径不再触发字段常量 KeyError。
4. `confirm_time` 类型冲突被消除，schema 定义与对齐逻辑一致。
5. `python -m py_compile` 与 `npm run build` 全部通过。
6. API 与 DB 文档完成同步，且 `docs/DB_SCHEMA.md` 无乱码。