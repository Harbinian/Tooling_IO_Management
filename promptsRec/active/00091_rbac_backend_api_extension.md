# RBAC 管理页面 - 后端 API 扩展

Primary Executor: Codex
Task Type: Feature Development
Priority: P0
Stage: Prompt 1/2
Goal: 扩展后端 RBAC API，支持角色 CRUD、权限 CRUD、角色-权限分配
Dependencies: None
Execution: RUNPROMPT

---

## Context

系统需要提供图形化的 RBAC 管理界面。当前系统已有完整的 RBAC 数据模型（6 张表：`sys_user`, `sys_role`, `sys_permission`, `sys_user_role_rel`, `sys_role_permission_rel`, `sys_role_data_scope_rel`）和 `rbac_service.py` 初始化逻辑，但缺少角色管理、权限管理的 API 端点。

本提示词负责完成后端 API 扩展，为前端页面提供 HTTP 接口。

**技术栈**: Flask REST API + SQL Server (pyodbc)
**端口**: 后端 8151
**工作目录**: `E:\CA001\Tooling_IO_Management`

---

## Required References

### 核心文件

| 文件 | 说明 |
|------|------|
| `backend/routes/admin_user_routes.py` | 现有管理员路由，需扩展 |
| `backend/routes/common.py` | `@require_permission` 装饰器定义 |
| `backend/services/rbac_service.py` | 现有 RBAC 服务，需扩展 |
| `backend/database/core/database_manager.py` | 数据库管理器（**必须使用**，不是 database.py 的 get_connection()） |
| `backend/database/repositories/order_repository.py` | 参考 repository 模式（使用 DatabaseManager + execute_with_transaction） |
| `backend/database/schema/column_names.py` | 字段名常量（**必须使用**） |

### 规则文件（强制遵守）

| 文件 | 关键规则 |
|------|---------|
| `00_core.md` | UTF-8 编码、字段名常量使用、禁止占位符代码 |
| `01_workflow.md` | ADP 四阶段开发流程 |

---

## Core Task

### 1. 扩展 `backend/routes/admin_user_routes.py`

在现有 `admin_user_routes.py` 中添加以下端点：

#### 1.1 角色 CRUD

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/admin/roles` | GET | 获取角色列表 | `admin:role_manage` |
| `/api/admin/roles` | POST | 创建角色 | `admin:role_manage` |
| `/api/admin/roles/<role_id>` | PUT | 更新角色 | `admin:role_manage` |
| `/api/admin/roles/<role_id>` | DELETE | 删除角色 | `admin:role_manage` |
| `/api/admin/roles/<role_id>/permissions` | GET | 获取角色已有权限 | `admin:role_manage` |
| `/api/admin/roles/<role_id>/permissions` | PUT | 分配权限给角色（覆盖式） | `admin:role_manage` |

#### 1.2 权限 CRUD

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/admin/permissions` | GET | 获取权限列表（支持分页/筛选） | `admin:role_manage` |
| `/api/admin/permissions` | POST | 创建权限 | `admin:role_manage` |
| `/api/admin/permissions/<permission_code>` | PUT | 更新权限 | `admin:role_manage` |
| `/api/admin/permissions/<permission_code>` | DELETE | 删除权限 | `admin:role_manage` |

> **注意**: 角色相关 API 使用 `admin:role_manage` 权限，用户管理继续使用 `admin:user_manage`。

### 2. 新建 `backend/database/repositories/rbac_repository.py`

**必须**: 参考 `order_repository.py` 的实现方式，使用 `DatabaseManager` 和 `execute_with_transaction()`，**不是** `database.py` 的 `get_connection()`。

```python
from backend.database.core.database_manager import DatabaseManager
# 注意: ROLE_COLUMNS 和 PERMISSION_COLUMNS 可能尚未在 column_names.py 中定义
# 实现前先检查 column_names.py，若无则先补充常量定义，再在 repository 中引用
# 参考现有常量定义模式（如 ORDER_COLUMNS）添加 ROLE_COLUMNS 和 PERMISSION_COLUMNS

class RbacRepository:
    def __init__(self):
        self.db = DatabaseManager()

    # 角色操作
    def get_roles(self, keyword=None, status=None, role_type=None) -> List[Dict]:
        # 使用 self.db.execute_query() 和 ? 占位符
        pass

    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        pass

    def create_role(self, role_data: Dict) -> Dict:
        # 使用 self.db.execute_with_transaction()
        pass

    def update_role(self, role_id: str, role_data: Dict) -> Optional[Dict]:
        pass

    def delete_role(self, role_id: str) -> Tuple[bool, str]:
        # 返回 (成功, 错误消息)
        # 检查是否有用户关联
        pass

    # 权限操作
    def get_permissions(self, keyword=None, status=None, page=1, page_size=20) -> Dict:
        pass

    def get_permission_by_code(self, permission_code: str) -> Optional[Dict]:
        pass

    def create_permission(self, permission_data: Dict) -> Dict:
        pass

    def update_permission(self, permission_code: str, permission_data: Dict) -> Optional[Dict]:
        pass

    def delete_permission(self, permission_code: str) -> Tuple[bool, str]:
        # 返回 (成功, 错误消息)
        # 检查是否被角色使用
        pass

    # 角色-权限关联
    def get_role_permissions(self, role_id: str) -> List[str]:
        # 返回 permission_code 列表
        pass

    def assign_permissions(self, role_id: str, permission_codes: List[str]) -> bool:
        # 使用事务：先删除旧关联，再插入新关联
        pass
```

### 3. 扩展 `backend/services/rbac_service.py`

添加角色/权限管理方法，调用 `RbacRepository`：

```python
def get_roles(keyword=None, status=None, role_type=None) -> List[Dict]
def create_role(role_data: Dict) -> Dict
def update_role(role_id: str, role_data: Dict) -> Dict
def delete_role(role_id: str) -> Tuple[bool, str]  # (成功, 错误消息)
def get_role_permissions(role_id: str) -> List[str]
def assign_role_permissions(role_id: str, permission_codes: List[str]) -> bool

def get_permissions(keyword=None, status=None, page=1, page_size=20) -> Dict
def create_permission(permission_data: Dict) -> Dict
def update_permission(permission_code: str, permission_data: Dict) -> Dict
def delete_permission(permission_code: str) -> Tuple[bool, str]
```

---

## Required Work

### Phase 2: Data - 数据审视

- RBAC 表已在 `rbac_service.py` 的 `ensure_rbac_tables()` 中定义
- 字段名常量：先检查 `column_names.py` 是否已有 `ROLE_COLUMNS`、`PERMISSION_COLUMNS`；若无，先补充定义再使用（参考 `ORDER_COLUMNS` 的定义模式）
- 现有表结构已在 `rbac_service.py` lines 16-121 定义

### Phase 3: Architecture - 架构设计

- Repository 模式：`RbacRepository` 使用 `DatabaseManager`
- Service 层：扩展 `rbac_service.py` 提供业务逻辑
- Route 层：扩展 `admin_user_routes.py` 提供 HTTP API

### Phase 4: Execution - 精确执行

#### Step 1: 创建 `backend/database/repositories/rbac_repository.py`

- 实现上述 `RbacRepository` 所有方法
- **使用 `DatabaseManager`**（`from backend.database.core.database_manager import DatabaseManager`）
- **使用 `?` 占位符**（pyodbc 兼容），**不是** `%s`
- 使用 `column_names.py` 中的常量访问字段
- 所有 SQL 使用参数化查询防止注入

#### Step 2: 扩展 `backend/services/rbac_service.py`

- 添加 `get_roles`, `create_role`, `update_role`, `delete_role`
- 添加 `get_role_permissions`, `assign_role_permissions`
- 添加 `get_permissions`, `create_permission`, `update_permission`, `delete_permission`
- 实现业务约束：
  - `role_type=system` 的角色（sys_admin, auditor）禁止删除
  - `role_code` 禁止重复
  - 删除角色前检查是否有用户关联
  - 删除权限前检查是否被角色使用

#### Step 3: 扩展 `backend/routes/admin_user_routes.py`

- 添加所有新端点
- 每个端点使用 `@require_auth` 和权限检查 `@require_permission('admin:role_manage')`
- 复用现有的错误处理和响应格式

#### Step 4: 语法检查

```bash
python -m py_compile backend/routes/admin_user_routes.py backend/services/rbac_service.py backend/database/repositories/rbac_repository.py
```

---

## Constraints

1. **UTF-8 编码**: 所有文件使用 `encoding='utf-8'`
2. **字段名常量**: 所有 SQL 中的中文字段必须使用 `column_names.py` 常量
3. **禁止占位符**: 所有代码必须完整可执行
4. **SQL 占位符**: 使用 `?`（pyodbc 兼容），**禁止** `%s`
5. **数据库管理器**: 使用 `DatabaseManager`（`backend.database.core.database_manager`），**不是** `database.py`
6. **事务处理**: 创建/更新/删除操作使用 `execute_with_transaction()`
7. **业务约束**:
   - system 类型角色不可删除
   - role_code 唯一性检查
   - 删除前检查关联数据

---

## Completion Criteria

- [ ] `backend/database/repositories/rbac_repository.py` 已创建并包含所有方法
- [ ] `rbac_service.py` 已扩展包含角色/权限管理方法
- [ ] `admin_user_routes.py` 已添加所有新端点
- [ ] `python -m py_compile` 语法检查通过
- [ ] 所有 API 端点返回正确的 HTTP 状态码和 JSON 响应
- [ ] 业务约束已实现（system 角色保护、唯一性检查、关联检查）
- [ ] 文档同步：更新 `docs/API_SPEC.md`（新增 API 端点）和 `docs/RBAC_PERMISSION_MATRIX.md`（新增权限说明）
