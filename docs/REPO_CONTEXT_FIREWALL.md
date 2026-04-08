# 仓库上下文防火墙报告 / Repo Context Firewall Report

**生成时间**: 2026-04-08
**仓库**: Tooling IO Management System
**扫描范围**: backend/, frontend/src/, test_runner/, logs/, promptsRec/, docs/

---

## 执行摘要 / Executive Summary

本次扫描确认 `.trae/.ignore` 已正确配置，但识别到多个新的上下文热点：
- `test_runner/` 下 3 个超大测试文件 (共 3843 行)
- `promptsRec/archive/` 增长至 169 个文件 (1.6MB)
- `logs/dev_server_launcher/` 突增至 2.3MB
- `tool_io_service.py` 已超过 1600 行

---

## 1. 最大源文件 / Largest Source Files

### 后端 Python 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `backend/services/tool_io_service.py` | 1636 | 组C | 建议拆分 |
| `backend/database/repositories/order_repository.py` | 1382 | 组C | 建议拆分 |
| `backend/services/rbac_service.py` | 805 | 组C | 建议拆分 |
| `backend/database/core/database_manager.py` | 626 | 组C | 建议拆分 |
| `backend/database/schema/column_names.py` | 693 | 组C | 建议拆分 |
| `backend/database/acceptance_queries.py` | 453 | - | OK |
| `backend/services/feedback_service.py` | 434 | - | OK |
| `backend/services/admin_user_service.py` | 431 | - | OK |
| `backend/services/order_workflow_service.py` | 419 | - | OK |
| `backend/database/repositories/tool_repository.py` | 582 | 组C | 建议拆分 |
| `backend/database/repositories/rbac_repository.py` | 547 | - | OK |
| `backend/services/inspection_task_service.py` | 573 | - | OK |

### 前端 Vue 文件 (>500 行)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `frontend/src/pages/tool-io/KeeperProcess.vue` | 1013 | 组C | 建议拆分 |
| `frontend/src/pages/settings/SettingsPage.vue` | 752 | - | OK |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 683 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderList.vue` | 538 | - | OK |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 497 | - | OK |
| `frontend/src/pages/admin/UserAdminPage.vue` | 413 | - | OK |
| `frontend/src/pages/inspection/TaskDetail.vue` | 386 | - | OK |
| `frontend/src/pages/admin/FeedbackAdminPage.vue` | 365 | - | OK |

### 测试文件 (新热点)

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `test_runner/api_e2e.py` | 2093 | 组C | 建议拆分 |
| `test_runner/test_runner_agent.py` | 932 | 组C | 建议拆分 |
| `test_runner/playwright_e2e.py` | 818 | 组C | 建议拆分 |

### 根目录文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `database.py` | 637 | 组C | 建议拆分 |
| `dev_server_launcher.py` | 811 | 组C | 建议拆分 |
| `backend/utils/response.py` | 120 | - | OK |

---

## 2. 最耗费 Token 的目录 / Most Token-Expensive Directories

| 目录 | 大小 | 文件数 | 估计 Token 消耗 | 分类 |
|------|------|--------|----------------|------|
| `logs/dev_server_launcher/` | 2.3MB | ~234 | 高 | 组A (已忽略) |
| `logs/prompt_task_runs/` | 1.2MB | ~80+ | 高 | 组A (已忽略) |
| `logs/codex_rectification/` | 410KB | ~60+ | 中 | 组A (已忽略) |
| `promptsRec/archive/` | 1.6MB | 169 | 高 | 组B (保留但少加载) |
| `frontend/node_modules/` | 极大 | 1000+ | 极高 | 组A (已忽略) |
| `.venv/` | 极大 | 大量 | 极高 | 组A (已忽略) |

---

## 3. 当前 `.trae/.ignore` 状态 / Current .trae/.ignore Status

**✅ 已正确配置，规则完整**

已在 `.trae/.ignore` 中配置忽略以下目录：

```
GROUP A - Safe to Ignore
  .venv/, frontend/node_modules/, frontend/dist/, build/, dist/
  logs/, .vscode/, .idea/, .env, __pycache__

GROUP B - Keep but Avoid Frequent Loading
  promptsRec/archive/, docs/archive/, AGENTS.md

NEVER IGNORE (否定规则)
  backend/, frontend/src/, promptsRec/active/, .skills/
  .claude/rules/, docs/PRD.md, docs/ARCHITECTURE.md, 等
```

---

## 4. 建议拆分的文件 / Files Recommended for Splitting

### 4.1 `backend/services/tool_io_service.py` (1636 行) — 高优先级

**问题**: 超大 Service 层，包含订单、保管员、通知等多种业务逻辑

**建议拆分**:
```
backend/services/tool_io_service.py
  → backend/services/tool_io_order_service.py    # 订单核心业务
  → backend/services/tool_io_keeper_service.py   # 保管员确认逻辑
  → backend/services/tool_io_notification_service.py  # 通知相关
```

### 4.2 `backend/database/repositories/order_repository.py` (1382 行) — 高优先级

**问题**: 超大 Repository，包含大量 SQL 查询

**建议拆分**:
```
backend/database/repositories/order_repository.py
  → backend/database/repositories/order_query.py  # 查询相关
  → backend/database/repositories/order_command.py  # 命令相关
  → backend/database/repositories/order_criteria.py  # 条件构建
```

### 4.3 `test_runner/api_e2e.py` (2093 行) — 高优先级

**问题**: 超大 E2E 测试文件

**建议拆分**:
```
test_runner/api_e2e.py
  → test_runner/api_e2e_orders.py  # 订单 API 测试
  → test_runner/api_e2e_tools.py  # 工装 API 测试
  → test_runner/api_e2e_auth.py   # 认证 API 测试
```

### 4.4 `frontend/src/pages/tool-io/KeeperProcess.vue` (1013 行) — 中优先级

**建议拆分**:
```
frontend/src/pages/tool-io/KeeperProcess.vue
  → frontend/src/components/keeper/OrderTable.vue
  → frontend/src/components/keeper/ConfirmDialog.vue
  → frontend/src/components/keeper/FilterPanel.vue
```

### 4.5 `backend/services/rbac_service.py` (805 行) — 中优先级

**建议拆分**:
```
backend/services/rbac_service.py
  → backend/services/rbac_permission_service.py  # 权限判断
  → backend/services/rbac_user_service.py       # 用户角色
```

### 4.6 `test_runner/test_runner_agent.py` (932 行) — 中优先级

**建议拆分**:
```
test_runner/test_runner_agent.py
  → test_runner/agent/base_agent.py
  → test_runner/agent/test_executor.py
  → test_runner/agent/report_generator.py
```

---

## 5. 安全优化操作 / Safe Optimization Actions

### 已执行
- ✅ `.trae/.ignore` 已配置完整的忽略规则
- ✅ `docs/REPO_CONTEXT_FIREWALL.md` 已维护最新热点报告
- ✅ 所有依赖目录已正确忽略

### 建议操作 (不破坏代码)
1. **定期归档 logs/**: 将 `logs/dev_server_launcher/` 和 `logs/prompt_task_runs/` 定期压缩或清理
2. **清理 promptsRec/archive/**: 169 个历史提示词已积累 1.6MB，建议年度归档
3. **拆分超大测试文件**: `api_e2e.py` 已达 2093 行，建议按功能域拆分
4. **拆分超大源文件**: 按上述建议拆分组C文件

---

## 6. Trae Token 浪费的高风险区域 / High-Risk Areas for Token Waste

| 风险区域 | 原因 | 当前状态 |
|---------|------|---------|
| `logs/dev_server_launcher/` | 234 个日志，2.3MB | ✅ 已在 .trae/.ignore 中忽略 |
| `logs/prompt_task_runs/` | ~80+ 个日志，1.2MB | ✅ 已在 .trae/.ignore 中忽略 |
| `promptsRec/archive/` | 169 个归档提示词，1.6MB | ⚠️ 组B，保留但少加载 |
| `frontend/node_modules/` | 1000+ npm 包文件 | ✅ 已在 .gitignore 中忽略 |
| `backend/services/tool_io_service.py` | 1636 行单文件 | ⚠️ 建议拆分 |
| `order_repository.py` | 1382 行单文件 | ⚠️ 建议拆分 |
| `api_e2e.py` | 2093 行单文件 | ⚠️ 建议拆分 |

---

## 7. 拆分建议总结 / Split Recommendations Summary

### 高优先级 (建议近期拆分)
1. **`api_e2e.py`** (2093行) - 最大测试文件，已影响加载速度
2. **`tool_io_service.py`** (1636行) - 核心业务逻辑集中
3. **`order_repository.py`** (1382行) - 数据访问最频繁

### 中优先级 (可计划拆分)
4. **`test_runner_agent.py`** (932行) - 工具脚本
5. **`rbac_service.py`** (805行) - 权限服务
6. **`KeeperProcess.vue`** (1013行) - 前端组件最大
7. **`OrderDetail.vue`** (683行) - 功能完整但过大

### 低优先级 (可选)
8. **`database.py`** (637行) - 根目录遗留代码
9. **`dev_server_launcher.py`** (811行) - 工具脚本

---

## 8. 新发现 / New Discoveries

### 8.1 新增未跟踪文件
以下文件在 git status 中显示为未跟踪，可能为新增开发文件：
- `backend/http_runtime.py` (122行)
- `backend/utils/response.py` (120行)
- `frontend/src/api/types/` (TypeScript 类型文件)
- `frontend/src/pages/HomePage.vue`

### 8.2 测试基础设施状态
- `tests/test_rbac_enforcement.py` (555行)
- `tests/test_workflow_state_machine.py` (358行)
- `tests/test_get_tool_io_orders.py` (541行)
- `tests/test_api_response_helpers.py` (新文件)
- `tests/test_http_runtime.py` (新文件)

这些测试文件也属于较大文件，应考虑拆分或整合。

---

## 9. 主动开发上下文保持可见 / Active Development Context

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

## 10. 相关文件 / Related Files

- **忽略规则**: `.trae/.ignore`
- **Git 忽略**: `.gitignore` (已包含 .venv, node_modules, logs)
- **Skills**: `.skills/repo-context-firewall/SKILL.md`

---

*本报告由 `repo-context-firewall` 技能自动生成，上次更新: 2026-04-08*
