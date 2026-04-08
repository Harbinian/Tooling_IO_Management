# 仓库上下文防火墙报告 / Repo Context Firewall Report

**生成时间**: 2026-04-07
**仓库**: Tooling IO Management System
**上次更新**: 2026-04-01

---

## 执行摘要 / Executive Summary

本报告分析了仓库的上下文热点，识别出 Token 消耗高风险区域，并提出优化建议。

**关键发现**:
- `logs/prompt_task_runs/` 包含 1064 个历史运行记录 (1.1M)
- `docs/archive/` 包含 101 个归档文档 (848K)
- 多个源码文件超过 500 行，建议拆分
- `review-reports/` 现已加入 GROUP B

---

## 1. 最大文件 / Largest Files

### 后端 Python 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `backend/services/tool_io_service.py` | 1636 | 组C | 建议拆分 |
| `backend/database/repositories/order_repository.py` | 1382 | 组C | 建议拆分 |
| `backend/services/rbac_service.py` | 805 | 组C | 建议拆分 |
| `backend/database/schema/schema_manager.py` | 709 | 组C | 可选拆分 |
| `backend/database/schema/column_names.py` | 693 | 组C | 可选拆分 |
| `backend/database/core/database_manager.py` | 626 | 组C | 可选拆分 |
| `backend/routes/order_routes.py` | 626 | 组C | 可选拆分 |
| `backend/database/repositories/tool_repository.py` | 582 | 组C | 可选拆分 |

### 前端 Vue 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `frontend/src/pages/tool-io/KeeperProcess.vue` | 1013 | 组C | 建议拆分 |
| `frontend/src/pages/settings/SettingsPage.vue` | 752 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 683 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderList.vue` | 538 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 497 | - | OK |

### 测试文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `test_runner/api_e2e.py` | 2093 | 组C | 建议拆分 |
| `test_runner/test_runner_agent.py` | 932 | 组C | 可选拆分 |
| `test_runner/playwright_e2e.py` | 818 | 组C | 可选拆分 |

### 根目录文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `dev_server_launcher.py` | 811 | 组C | 建议拆分 |
| `database.py` | 637 | 组C | 建议拆分 |
| `AGENTS.md` | 410 | 组B | 保留但避免频繁加载 |

---

## 2. 最耗费 Token 的目录 / Most Token-Expensive Directories

| 目录 | 文件数 | 大小 | 分类 | 状态 |
|------|--------|------|------|------|
| `logs/prompt_task_runs/` | 1064 | 1.1M | 组B→组A | ✅ 改为精确忽略运行时日志 |
| `logs/codex_rectification/` | 89 | 382K | 组B→组A | ✅ 改为精确忽略运行时日志 |
| `promptsRec/archive/` | ~100 | - | 组B | ⚠️ 保留但少加载 |
| `docs/archive/` | 101 | 848K | 组B | ⚠️ 保留但少加载 |
| `review-reports/` | 9 | 76K | 组B | ⚠️ 新加入 GROUP B |
| `frontend/node_modules/` | 1000+ | - | 组A | ✅ 已忽略 |
| `.venv/` | 大量 | - | 组A | ✅ 已忽略 |

---

## 3. 当前忽略规则 / Current Ignore Rules

已在 `.trae/.ignore` 中配置：

```gitignore
# GROUP A - Safe to Ignore
.venv/
venv/
env/
frontend/node_modules/
frontend/dist/
build/
dist/
bin/
obj/
logs/dev_server_launcher/
logs/codex_rectification/      # Historical records
logs/prompt_task_runs/        # Historical records
.vscode/
.idea/
.env
*.tmp, *.temp
__pycache__/
*.py[cod], *$py.class

# GROUP B - Keep but Avoid Frequent Loading
promptsRec/archive/
docs/archive/
review-reports/
AGENTS.md

# NEVER IGNORE
!backend/
!frontend/src/
!promptsRec/active/
!.skills/
!.claude/rules/
```

---

## 4. 建议拆分的文件 / Files Recommended for Splitting

### 4.1 `backend/services/tool_io_service.py` (1636 行) 🔴 高优先级

**问题**: 超大 Service 层，包含订单、保管员、通知等多种业务逻辑

**建议拆分**:
```
backend/services/tool_io_service.py
  → backend/services/tool_io_order_service.py    # 订单核心业务
  → backend/services/tool_io_keeper_service.py   # 保管员确认逻辑
  → backend/services/tool_io_notification_service.py  # 通知相关
```

### 4.2 `backend/database/repositories/order_repository.py` (1382 行) 🔴 高优先级

**问题**: 超大 Repository，包含大量 SQL 查询

**建议拆分**:
```
backend/database/repositories/order_repository.py
  → backend/database/repositories/order_query.py  # 查询相关
  → backend/database/repositories/order_command.py  # 命令相关
```

### 4.3 `test_runner/api_e2e.py` (2093 行) 🔴 高优先级

**问题**: 超大测试文件，包含所有 API 测试用例

**建议拆分**:
```
test_runner/api_e2e.py
  → test_runner/api_e2e_base.py          # 基础测试类
  → test_runner/api_e2e_orders.py          # 订单 API 测试
  → test_runner/api_e2e_auth.py           # 认证 API 测试
  → test_runner/api_e2e_admin.py          # 管理员 API 测试
```

### 4.4 `frontend/src/pages/tool-io/KeeperProcess.vue` (1013 行) 🔴 高优先级

**问题**: 超大 Vue 组件

**建议拆分**:
```
frontend/src/pages/tool-io/KeeperProcess.vue
  → frontend/src/components/keeper/OrderTable.vue
  → frontend/src/components/keeper/ConfirmDialog.vue
  → frontend/src/components/keeper/FilterPanel.vue
```

### 4.5 `frontend/src/pages/settings/SettingsPage.vue` (752 行) 🟡 中优先级

**问题**: 设置页面包含多个功能区块

**建议拆分**:
```
frontend/src/pages/settings/SettingsPage.vue
  → frontend/src/components/settings/ThemeSettings.vue
  → frontend/src/components/settings/NotificationSettings.vue
  → frontend/src/components/settings/AccountSettings.vue
```

### 4.6 `dev_server_launcher.py` (811 行) 🟡 中优先级

**问题**: 根目录超大脚本

**建议拆分**:
```
dev_server_launcher.py
  → backend/launcher/server_launcher.py
  → backend/launcher/process_manager.py
```

### 4.7 `database.py` (637 行) 🟡 中优先级

**问题**: 根目录遗留代码

**建议拆分**:
```
database.py
  → backend/database/core/connection_pool.py
  → backend/database/core/query_builder.py
```

---

## 5. 已执行的优化 / Executed Optimizations

### 2026-04-07 更新

1. ✅ 更新 `.trae/.ignore`，将 `logs/prompt_task_runs/` 和 `logs/codex_rectification/` 从全面忽略改为精确忽略运行时日志
2. ✅ 添加 `review-reports/` 到 GROUP B
3. ✅ 更新行数统计（最新扫描结果）

---

## 6. Trae Token 浪费的高风险区域 / High-Risk Areas

| 风险区域 | 原因 | 当前状态 |
|---------|------|---------|
| `test_runner/api_e2e.py` | 2093 行单文件 | ⚠️ 建议拆分 |
| `tool_io_service.py` | 1636 行单文件 | ⚠️ 建议拆分 |
| `order_repository.py` | 1382 行单文件 | ⚠️ 建议拆分 |
| `KeeperProcess.vue` | 1013 行单文件 | ⚠️ 建议拆分 |
| `promptsRec/active/` | 当前活跃任务 | ⚠️ 注意体积控制 |

---

## 7. 拆分优先级总结 / Split Priority Summary

### 🔴 高优先级 (建议近期拆分)
1. `test_runner/api_e2e.py` - 测试文件最大
2. `tool_io_service.py` - 业务逻辑最集中
3. `order_repository.py` - 数据访问最频繁
4. `KeeperProcess.vue` - 前端组件最大

### 🟡 中优先级 (可计划拆分)
5. `SettingsPage.vue` - 设置页面过大
6. `dev_server_launcher.py` - 根目录遗留代码
7. `database.py` - 根目录遗留代码

### 🟢 低优先级 (可选)
8. `rbac_service.py` - 功能完整但较大
9. `schema_manager.py` - Schema 管理

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
| API 合约 | `docs/API_SPEC.md` |

---

## 9. 相关文件 / Related Files

- **忽略规则**: `.trae/.ignore`
- **Git 忽略**: `.gitignore`
- **Skills**: `.skills/repo-context-firewall/`

---

*本报告由 `repo-context-firewall` 技能自动生成*
