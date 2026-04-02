# 10183: 修复系统配置 API 返回 500 错误

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10183
Goal: 修复 `/api/admin/system-config/*` 返回 HTTP 500 的问题
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 SettingsPage.vue 调用系统配置 API 获取 MPL 相关设置时返回 HTTP 500 错误：

```
api/admin/system-config:1  Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)
api/admin/system-config/mpl_enabled:1  Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)
api/admin/system-config/mpl_strict_mode:1  Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)
```

受影响的文件：
- `backend/routes/system_config_routes.py` - API 路由（已实现）
- `backend/services/tool_io_service.py` - Service 层（已实现）
- `backend/database/repositories/system_config_repository.py` - Repository 层（已实现）
- `backend/database/schema/schema_manager.py` - 表创建逻辑（已实现）
- `frontend/src/api/systemConfig.js` - 前端 API 调用
- `frontend/src/pages/SettingsPage.vue` - 前端设置页面

---

## Required References / 必需参考

1. **数据库 Schema**: `docs/DB_SCHEMA.md` - 确认 `sys_system_config` 表结构
2. **权限设计**: `docs/RBAC_DESIGN.md` - 确认 `admin:user_manage` 权限定义
3. **字段常量**: `backend/database/schema/column_names.py` - 使用 `SYSTEM_CONFIG_COLUMNS` 常量
4. **表名常量**: `backend/database/schema/column_names.py` - 使用 `TABLE_NAMES['SYSTEM_CONFIG']`

---

## Core Task / 核心任务

### Bug 调查要求

**在修改任何代码之前，必须完成以下调查：**

1. **检查后端日志**
   - 启动后端服务器：`python web_server.py`
   - 复现请求：`curl http://localhost:8151/api/admin/system-config`
   - 检查控制台输出的错误堆栈

2. **检查数据库表是否存在**
   ```sql
   SELECT * FROM sys_system_config
   ```
   - 如果表不存在，检查 `ensure_system_config_table()` 是否被正确调用
   - 如果表存在但查询失败，检查 Schema 是否匹配

3. **检查权限问题**
   - 确认 `require_permission("admin:user_manage")` 是否导致 500 错误
   - 检查 `sys_permission` 表中是否存在该权限记录

4. **检查函数返回值**
   - 在 `system_config_routes.py` 的 GET 路由中添加调试日志
   - 确认 `list_system_configs()` 返回的数据结构

### 根本原因分析

完成调查后，记录发现的**根本原因**，然后再进行修复。

可能的根因：
- 表创建失败但被静默忽略
- `MERGE` 语句在 `sys_system_config` 表上有问题
- 权限检查返回 403 但被映射为 500
- `ensure_tool_io_tables()` 中的某个前置表创建失败

---

## Required Work / 必需工作

1. **根因确认**: 确定 500 错误的准确原因
2. **修复实施**: 根据根因实施修复
3. **验证测试**: 修复后验证 API 正常工作
   ```bash
   curl http://localhost:8151/api/admin/system-config
   curl http://localhost:8151/api/admin/system-config/mpl_enabled
   ```
4. **回归测试**: 确认其他 API 端点未受影响

---

## Constraints / 约束条件

- **禁止盲目猜测根因** - 必须先调查再修复
- **使用字段常量** - 所有 SQL 必须使用 `column_names.py` 中的常量
- **保持事务完整性** - 表创建使用 `_execute_statements_in_transaction`
- **UTF-8 编码** - 所有文件操作使用 `encoding='utf-8'`

---

## Completion Criteria / 完成标准

1. `GET /api/admin/system-config` 返回 200 和配置列表
2. `GET /api/admin/system-config/mpl_enabled` 返回 200
3. SettingsPage.vue 能正常加载和显示系统配置
4. 后端无 500 错误日志
