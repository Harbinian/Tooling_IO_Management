# 仓库上下文防火墙报告 / Repo Context Firewall Report

**生成时间**: 2026-04-01  
**仓库**: Tooling IO Management System

---

## 执行摘要 / Executive Summary

本报告分析了仓库的上下文热点，识别出 Token 消耗高风险区域，并提出优化建议。

---

## 1. 最大文件 / Largest Files

### 后端 Python 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `backend/services/tool_io_service.py` | 1408 | 组C | 建议拆分 |
| `backend/database/repositories/order_repository.py` | 1299 | 组C | 建议拆分 |
| `backend/routes/order_routes.py` | 605 | 组C | 建议拆分 |
| `backend/services/rbac_service.py` | 604 | 组C | 建议拆分 |
| `backend/database/repositories/tool_repository.py` | 582 | 组C | 建议拆分 |
| `backend/database/core/database_manager.py` | 542 | 组C | 建议拆分 |
| `backend/database/schema/column_names.py` | 506 | 组C | 建议拆分 |
| `backend/database/acceptance_queries.py` | 453 | 组C | 可选拆分 |
| `backend/services/feedback_service.py` | 434 | - | OK |
| `backend/services/admin_user_service.py` | 431 | - | OK |
| `backend/services/order_workflow_service.py` | 419 | - | OK |

### 前端 Vue 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `frontend/src/pages/tool-io/KeeperProcess.vue` | 858 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 726 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderList.vue` | 538 | 组C | 建议拆分 |
| `frontend/src/pages/settings/SettingsPage.vue` | 486 | - | OK |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 475 | - | OK |

### 根目录文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `dev_server_launcher.py` | 699 | 组C | 建议拆分 |
| `database.py` | 637 | 组C | 建议拆分 |
| `ChatGPT_Dev_Context.md` | 507 | 组B | 保留但避免频繁加载 |
| `Harness Engineering 架构应用指南.md` | 451 | 组B | 保留但避免频繁加载 |
| `AGENTS.md` | 378 | 组B | 保留但避免频繁加载 |
| `web_server.py` | 74 | - | OK |

---

## 2. 最耗费 Token 的目录 / Most Token-Expensive Directories

| 目录 | 文件数 | 估计 Token 消耗 | 分类 |
|------|--------|----------------|------|
| `logs/prompt_task_runs/` | ~80+ | 极高 | 组A (已忽略) |
| `logs/codex_rectification/` | ~60+ | 高 | 组A (已忽略) |
| `promptsRec/archive/` | ~186 | 高 | 组B (保留但少加载) |
| `frontend/node_modules/` | 1000+ | 极高 | 组A (已忽略) |
| `.venv/` | 大量 | 极高 | 组A (已忽略) |

---

## 3. 忽略的目录 / Ignored Directories

已在 `.trae/.ignore` 中配置忽略以下目录：

```
# GROUP A - Safe to Ignore
.venv/
frontend/node_modules/
frontend/dist/
build/, dist/, bin/, obj/
logs/
.vscode/, .idea/
.env

# GROUP B - Keep but Avoid Frequent Loading
promptsRec/archive/
docs/archive/
```

---

## 4. 建议拆分的文件 / Files Recommended for Splitting

### 4.1 `backend/services/tool_io_service.py` (1408 行)

**问题**: 超大 Service 层，包含订单、保管员、通知等多种业务逻辑

**建议拆分**:
```
backend/services/tool_io_service.py
  → backend/services/tool_io_order_service.py    # 订单核心业务
  → backend/services/tool_io_keeper_service.py   # 保管员确认逻辑
  → backend/services/tool_io_notification_service.py  # 通知相关
```

### 4.2 `backend/database/repositories/order_repository.py` (1299 行)

**问题**: 超大 Repository，包含大量 SQL 查询

**建议拆分**:
```
backend/database/repositories/order_repository.py
  → backend/database/repositories/order_query.py  # 查询相关
  → backend/database/repositories/order_command.py  # 命令相关
  → backend/database/repositories/order_criteria.py  # 条件构建
```

### 4.3 `frontend/src/pages/tool-io/KeeperProcess.vue` (858 行)

**问题**: 超大 Vue 组件，包含多个功能区域

**建议拆分**:
```
frontend/src/pages/tool-io/KeeperProcess.vue
  → frontend/src/components/keeper/OrderTable.vue
  → frontend/src/components/keeper/ConfirmDialog.vue
  → frontend/src/components/keeper/FilterPanel.vue
```

### 4.4 `frontend/src/pages/tool-io/OrderDetail.vue` (726 行)

**问题**: 超大 Vue 组件，包含详情、确认、操作等多个区块

**建议拆分**:
```
frontend/src/pages/tool-io/OrderDetail.vue
  → frontend/src/components/order/DetailHeader.vue
  → frontend/src/components/order/ItemTable.vue
  → frontend/src/components/order/ActionPanel.vue
  → frontend/src/components/order/LogTimeline.vue
```

### 4.5 `database.py` (637 行) 和 `dev_server_launcher.py` (699 行)

**问题**: 根目录超大文件

**建议拆分**:
```
database.py
  → backend/database/core/connection_pool.py
  → backend/database/core/query_builder.py
  → backend/database/core/transaction_manager.py

dev_server_launcher.py
  → backend/launcher/server_launcher.py
  → backend/launcher/process_manager.py
```

---

## 5. 安全的优化操作 / Safe Optimization Actions

### 已执行
- ✅ 创建 `.trae/.ignore` 忽略规则
- ✅ 识别并分类热点文件

### 可选优化 (不破坏代码)
1. **定期归档日志**: 将 `logs/prompt_task_runs/` 和 `logs/codex_rectification/` 定期压缩归档
2. **拆分超大文件**: 按上述建议拆分组C文件
3. **建立 API 快照**: 将 `docs/API_SPEC.md` 定期更新并独立存储

---

## 6. Trae Token 浪费的高风险区域 / High-Risk Areas for Token Waste

| 风险区域 | 原因 | 当前状态 |
|---------|------|---------|
| `logs/` | 258 个日志文件，累积 10000+ 行 | ✅ 已在 .trae/.ignore 中忽略 |
| `promptsRec/archive/` | 186 个归档提示词 | ⚠️ 保留但标记为少加载 |
| `frontend/node_modules/` | 1000+ npm 包文件 | ✅ 已在 .gitignore 中忽略 |
| `backend/services/tool_io_service.py` | 1408 行单文件 | ⚠️ 建议拆分 |
| `order_repository.py` | 1299 行单文件 | ⚠️ 建议拆分 |

---

## 7. 拆分建议总结 / Split Recommendations Summary

### 高优先级 (建议近期拆分)
1. `tool_io_service.py` - 业务逻辑最集中
2. `order_repository.py` - 数据访问最频繁
3. `KeeperProcess.vue` - 前端组件最大

### 中优先级 (可计划拆分)
4. `OrderDetail.vue` - 功能完整但过大
5. `database.py` - 根目录遗留代码

### 低优先级 (可选)
6. `dev_server_launcher.py` - 工具脚本，影响较小

---

## 8. 主动开发上下文保持可见 / Active Development Context

以下内容对 AI 开发保持可见：

| 类别 | 路径 |
|------|------|
| 后端源码 | `backend/` |
| 前端源码 | `frontend/src/` |
| 活跃提示词 | `promptsRec/active/` |
| 技能定义 | `.skills/` |
| 开发规则 | `.claude/rules/` |
| 架构文档 | `docs/PRD.md`, `docs/ARCHITECTURE.md`, 等 |

---

## 9. 相关文件 / Related Files

- **忽略规则**: `.trae/.ignore`
- **Git 忽略**: `.gitignore` (已包含 .venv, node_modules, logs)
- **Skills**: `.skills/repo-context-firewall/SKILL.md`

---

*本报告由 `repo-context-firewall` 技能自动生成*
