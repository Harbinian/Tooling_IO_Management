# 仓库上下文防火墙报告 / Repo Context Firewall Report

**生成时间**: 2026-04-09
**仓库**: Tooling IO Management System
**扫描范围**: 全仓库扫描

---

## 执行摘要 / Executive Summary

本次扫描识别到多个上下文热点和优化机会：
- `.trae/.ignore` 已创建，统一上下文忽略规则
- `test_runner/` 下 3 个超大测试文件需要拆分
- `promptsRec/archive/` 增长至 247 个文件
- 核心后端 Service/Repository 文件超过 1000 行

**当前状态**: `.claudeignore` 和 `.trae/.ignore` 均已正确配置。

---

## 1. 最大文件 / Largest Files

| 排名 | 文件路径 | 大小 | 类型 |
|------|---------|------|------|
| 1 | `dist/dev_server_launcher.exe` | 15.6 MB | 构建产物 |
| 2 | `build/dev_server_launcher/dev_server_launcher.pkg` | 15.2 MB | 构建产物 |
| 3 | `.backend.stdout.log` | 2.0 MB | 日志 |
| 4 | `logs/dev_server_launcher/*/backend.log` | 1.4 MB | 日志 |
| 5 | `frontend/dist/assets/*.js` | 1.1 MB | 前端构建 |

---

## 2. 最耗费 Token 的目录 / Most Token-Expensive Directories

| 目录 | 大小 | 文件数 | 分类 |
|------|------|--------|------|
| `frontend/` (含 node_modules) | 295 MB | 1000+ | 组A (已忽略) |
| `build/` | 23 MB | ~100 | 组A (已忽略) |
| `dist/` | 15 MB | ~10 | 组A (已忽略) |
| `logs/` | 5.1 MB | ~400 | 组A (已忽略) |
| `promptsRec/archive/` | 1.8 MB | 247 | 组B (保留但少加载) |
| `promptsRec/active/` | ~100 KB | ~10 | 保留 |
| `backend/` | 2.6 MB | 79 | 保留 |

---

## 3. 超过 500 行的源文件 / Source Files > 500 Lines

### 后端 Python 文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `backend/database/repositories/order_repository.py` | 1382 | 组C | 建议拆分 |
| `backend/services/tool_io_service.py` | 1292 | 组C | 建议拆分 |
| `backend/services/rbac_service.py` | 818 | 组C | 建议拆分 |
| `backend/database/core/database_manager.py` | 626 | 组C | 建议拆分 |
| `backend/database/schema/column_names.py` | 693 | 组C | 建议拆分 |
| `backend/database/schema/schema_manager.py` | 709 | 组C | 建议拆分 |
| `backend/services/order_workflow_service.py` | 644 | 组C | 建议拆分 |
| `backend/launcher/server_launcher.py` | 641 | 组C | 建议拆分 |
| `database.py` | 637 | 组C | 建议拆分 |
| `backend/routes/order_routes.py` | 631 | 组C | 建议拆分 |
| `backend/database/repositories/tool_repository.py` | 582 | 组C | 建议拆分 |
| `backend/services/inspection_task_service.py` | 573 | - | OK |
| `backend/database/repositories/rbac_repository.py` | 547 | - | OK |

### 前端 Vue/JS 文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `frontend/src/pages/tool-io/KeeperProcess.vue` | 968 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 746 | 组C | 建议拆分 |
| `frontend/src/pages/tool-io/OrderList.vue` | 538 | - | OK |

### 测试文件

| 文件路径 | 行数 | 分类 | 建议 |
|---------|------|------|------|
| `test_runner/api_e2e.py` | 2111 | 组C | 建议拆分 |
| `test_runner/test_runner_agent.py` | 932 | 组C | 建议拆分 |
| `test_runner/playwright_e2e.py` | 818 | 组C | 建议拆分 |
| `tests/test_rbac_enforcement.py` | 555 | - | OK |
| `tests/test_get_tool_io_orders.py` | 546 | - | OK |
| `test_runner/api_e2e_base.py` | 583 | - | OK |

---

## 4. 当前忽略规则状态 / Current Ignore Rules Status

### `.trae/.ignore` ✅ 已创建

统一上下文忽略规则，包含：
- GROUP A: `.venv/`, `node_modules/`, `build/`, `dist/`, `logs/`, `.env`
- GROUP B: `promptsRec/archive/`, `docs/archive/`
- NEVER IGNORE: `backend/`, `frontend/src/`, `promptsRec/active/`, `.skills/`, `.claude/rules/`, 核心架构文档

### `.claudeignore` ✅ 已存在

与 `.trae/.ignore` 保持一致的忽略规则。

### `.gitignore` ✅ 已存在

已忽略：`logs/`, `.venv/`, `node_modules/`, `build/`, `dist/`

---

## 5. 建议拆分的文件 / Files Recommended for Splitting

### 高优先级 (建议近期拆分)

#### 5.1 `test_runner/api_e2e.py` (2111 行) — 最高优先级

**问题**: 超大 E2E 测试文件，影响加载速度

**建议拆分**:
```
test_runner/api_e2e.py
  → test_runner/api_e2e_orders.py    # 订单 API 测试
  → test_runner/api_e2e_tools.py     # 工装 API 测试
  → test_runner/api_e2e_auth.py      # 认证 API 测试
  → test_runner/api_e2e_mpl.py       # MPL API 测试
```

#### 5.2 `backend/database/repositories/order_repository.py` (1382 行)

**问题**: 超大 Repository，包含大量 SQL 查询

**建议拆分**:
```
backend/database/repositories/order_repository.py
  → backend/database/repositories/order_query.py     # 查询相关
  → backend/database/repositories/order_command.py   # 命令相关
```

#### 5.3 `backend/services/tool_io_service.py` (1292 行)

**问题**: 超大 Service 层，包含多种业务逻辑

**建议拆分**:
```
backend/services/tool_io_service.py
  → backend/services/tool_io_order_service.py       # 订单核心业务
  → backend/services/tool_io_keeper_service.py      # 保管员确认逻辑
```

### 中优先级 (可计划拆分)

#### 5.4 `test_runner/test_runner_agent.py` (932 行)

#### 5.5 `frontend/src/pages/tool-io/KeeperProcess.vue` (968 行)

#### 5.6 `backend/services/rbac_service.py` (818 行)

#### 5.7 `test_runner/playwright_e2e.py` (818 行)

### 低优先级 (可选)

#### 5.8 `database.py` (637 行) — 根目录遗留文件

#### 5.9 `backend/routes/order_routes.py` (631 行)

---

## 6. 安全优化操作 / Safe Optimization Actions

### ✅ 已执行
- `.trae/.ignore` 已创建
- `.claudeignore` 已验证完整
- `.gitignore` 已验证完整

### 建议操作 (不破坏代码)
1. **定期归档 logs/**: 将 `logs/dev_server_launcher/` 定期清理或压缩
2. **清理 promptsRec/archive/**: 247 个历史提示词已积累 1.8MB，建议年度归档
3. **拆分超大测试文件**: `api_e2e.py` 已达 2111 行
4. **拆分超大后端文件**: 按上述建议拆分组C文件

---

## 7. Trae Token 浪费的高风险区域 / High-Risk Areas

| 风险区域 | 原因 | 当前状态 |
|---------|------|---------|
| `logs/` | 400+ 文件，5.1MB | ✅ 已在 .trae/.ignore 中忽略 |
| `promptsRec/archive/` | 247 文件，1.8MB | ⚠️ 组B，保留但少加载 |
| `frontend/node_modules/` | 大量 npm 包 | ✅ 已在 .gitignore 中忽略 |
| `api_e2e.py` | 2111 行单文件 | ⚠️ 建议拆分 |
| `order_repository.py` | 1382 行单文件 | ⚠️ 建议拆分 |
| `tool_io_service.py` | 1292 行单文件 | ⚠️ 建议拆分 |

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

- **Trae 忽略规则**: `.trae/.ignore` (新建)
- **Claude 忽略规则**: `.claudeignore`
- **Git 忽略**: `.gitignore` (已包含 .venv, node_modules, logs, build)
- **Skills**: `.skills/repo-context-firewall/`

---

*本报告由 `repo-context-firewall` 技能自动生成，上次更新: 2026-04-09*
