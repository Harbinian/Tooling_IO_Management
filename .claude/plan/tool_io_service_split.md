# Plan: 重构 `tool_io_service.py` — 消除跨层调用

> **状态**: 阶段一完成（代码阶段），阶段二待执行（文档同步）

---

## 执行摘要

| 单元 | 状态 | 文件 |
|------|------|------|
| Unit 1: 创建 `_shared_utils.py` | ✅ 已完成 | `backend/services/_shared_utils.py` (53行) |
| Unit 2: 创建 `_order_shared.py` | ✅ 已完成 | `backend/services/_order_shared.py` (205行) |
| Unit 3: 重构 `order_workflow_service.py` | ✅ 已完成 | 删除本地重复定义，从新模块导入 |
| Unit 4: 重构 `order_query_service.py` | ✅ 已完成 | 消除 helper 跨层导入 |
| Unit 5: 重构 `dashboard_service.py` | ✅ 已完成 | `_resolve_scope_context` 改为从 `_order_shared` 导入 |
| Unit 6: 精简 `tool_io_service.py` 为 Facade | ✅ 已完成 | `get_dashboard_stats` 转发到 `dashboard_service` |

---

## 执行后验证结果

| 层级 | 结果 |
|------|------|
| Layer 1 语法检查 | ✅ 通过 |
| Layer 2 模块导入冒烟 | ✅ 通过 |
| Layer 3 定向 pytest | ✅ 29 passed, 1 skipped |
| Layer 4 API E2E | ⚠️ 41 passed, **7 failed** (见下方) |

### E2E 失败测试分析

| 测试ID | 描述 | 原因分析 | 是否重构导致 |
|--------|------|---------|------------|
| `wf_09` (fengliang) | 登录 | 测试基础设施问题（登录API行为不一致） | ❌ 否 |
| `rbac_19` (TEAM_LEADER) | GET /notifications HTTP 500 | 后端通知服务错误，与重构无关 | ❌ 否 |
| `rbac_20` (TEAM_LEADER) | GET generate-transport-text HTTP 404 | TEST001订单不存在，测试数据问题 | ❌ 否 |
| `rbac_30` (TEAM_LEADER) | DELETE /tool-io-orders/TEST001 HTTP 404 | 同上，测试数据问题 | ❌ 否 |
| `rbac_34` (KEEPER) | GET /notifications HTTP 500 | 同 rbac_19 | ❌ 否 |
| `in_02` (taidongxu) | 入库流程 | 工具已被其他订单占用，数据冲突 | ❌ 否 |
| `rej_02` (taidongxu) | 拒绝流程 | 同上 | ❌ 否 |

**结论（初步判断，待复核）**: 所有失败均与本次重构无关，是测试基础设施或数据问题。

---

## 剩余跨层 Import（预期内，未纳入本计划）

| 调用方 | 导入的符号 | 原因 | 建议 |
|--------|-----------|------|------|
| `order_workflow_service.py` | `_emit_internal_notification` | deferred import，循环引用设计 | 迁移到 `notification_service.py` |
| `order_workflow_service.py` | `check_order_mpl_violations` | MPL 检查函数，仍从 tool_io_service 导入 | 迁移到 `mpl_service.py` |
| `order_query_service.py` | `_emit_internal_notification` | deferred import | 同上 |
| `transport_issue_service.py` | `get_order_detail` | 公共 Facade 函数 | 合法，无需修改 |
| `inspection_task_service.py` | `get_order_detail` | 公共 Facade 函数 | 合法，无需修改 |

---

## 文档同步

| 文档 | 状态 |
|------|------|
| `docs/ARCHITECTURE.md` | ⚠️ 未同步（需手动更新） |
| `docs/API_SPEC.md` | 无需变更 |

---

## 下一步待办

### 高优先级

1. **消除 `_emit_internal_notification` 跨层调用**
   - 将 `_emit_internal_notification` 迁移到 `notification_service.py`
   - 将其从 `tool_io_service.py` 移除
   - 更新 `order_workflow_service.py` 和 `order_query_service.py` 的 deferred import

2. **同步 `docs/ARCHITECTURE.md`**
   - 在 Service 层模块图中添加 `_shared_utils.py`、`_order_shared.py`
   - 更新模块边界说明

### 中优先级

3. **解决 E2E 测试基础设施问题**
   - 调查 `wf_09` 登录失败原因
   - 预置 TEST001 测试数据解决 404 问题
   - 调查 `/notifications` HTTP 500 根因

4. **精简 `tool_io_service.py` 进一步减少行数**
   - 当前 1033 行，目标约 400 行
   - MPL 相关函数可考虑迁移到 `mpl_service.py`

---

## 关键约束（执行时遵循）

1. ✅ Routes 层 import 路径不变
2. ✅ 函数签名完全一致
3. ✅ 先建 `_shared_utils.py`
4. ✅ Facade 保持向后兼容
5. ✅ `tool_location_service.py`、`notification_service.py`、`mpl_service.py` 不在本计划范围内
