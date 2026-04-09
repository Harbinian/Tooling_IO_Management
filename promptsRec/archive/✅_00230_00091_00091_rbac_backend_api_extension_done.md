---
name: rbac-backend-api-extension
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/00_core.md
  - .claude/rules/01_workflow.md
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# RBAC 管理页面 - 后端 API 扩展

## 目的 / Purpose

系统需要提供图形化的 RBAC 管理界面。当前系统已有完整的 RBAC 数据模型和 `rbac_service.py` 初始化逻辑，但缺少角色管理、权限管理的 API 端点。本任务完成后端 API 扩展，为前端 `PermissionManagementPage.vue` 等页面提供完整的 HTTP 接口。

**执行器**: Claude Code
**任务类型**: Feature Development (00001-09999)
**优先级**: P0
**工作目录**: `E:\CA001\Tooling_IO_Management`

---

## Phase 1: PRD - 业务需求分析

### 业务场景

管理员需要在后台管理界面完成以下操作：
- 创建、编辑、删除角色
- 分配权限给角色
- 创建、编辑、删除权限
- 查看角色已有的权限列表

### 目标用户

- **admin**: 需要完整管理所有角色和权限
- **未来扩展**: 其他需要角色管理能力的管理员

### 核心痛点

当前系统 RBAC 数据模型已存在，但缺乏管理接口。管理员无法通过 UI 管理角色和权限。

### 业务目标

- 提供完整的角色 CRUD API
- 提供完整的权限 CRUD API
- 提供角色-权限关联 API（GET/PUT）
- 实现业务约束：system 角色不可删除、role_code 唯一性、删除前检查关联

---

## Phase 2: Data - 数据审视

### 现有 RBAC 表结构

表已在 `rbac_service.py` 的 `ensure_rbac_tables()` 中定义（lines 16-121）：

- `sys_role` - 角色表
- `sys_permission` - 权限表
- `sys_user_role_rel` - 用户-角色关联
- `sys_role_permission_rel` - 角色-权限关联
- `sys_role_data_scope_rel` - 角色数据范围关联

### 字段名常量检查

实现前检查 `backend/database/schema/column_names.py`：
- 是否已有 `ROLE_COLUMNS`、`PERMISSION_COLUMNS`
- 若无，先在 `column_names.py` 中补充定义（参考 `ORDER_COLUMNS` 模式）

### 数据约束

- `role_type=system` 的角色（sys_admin, auditor）禁止删除
- `role_code` 必须唯一
- 删除角色前检查是否有用户关联
- 删除权限前检查是否被角色使用

---

## Phase 3: Architecture - 架构设计

### 交互链路

```
Route (admin_user_routes.py)
    ↓
Service (rbac_service.py)
    ↓
Repository (rbac_repository.py) [新建]
    ↓
DatabaseManager (database_manager.py)
```

### 风险识别

1. **并发风险**: 角色权限分配使用事务防止不一致
2. **业务约束**: system 类型角色保护、唯一性检查
3. **错误处理**: 统一异常捕获和错误响应

### 熔断策略

- 数据库操作失败：返回 500 + 错误消息
- 业务约束冲突：返回 400 + 明确错误原因

---

## Phase 4: Execution - 精确执行

### Step 1: 检查并补充字段名常量

文件: `backend/database/schema/column_names.py`

检查是否已有 `ROLE_COLUMNS`、`PERMISSION_COLUMNS` 常量。

若没有，添加类似以下定义：

```python
ROLE_COLUMNS = {
    "role_id": "角色ID",
    "role_code": "角色代码",
    "role_name": "角色名称",
    "role_type": "角色类型",
    "role_desc": "角色描述",
    "status": "状态",
    "org_id": "组织ID",
    "create_time": "创建时间",
    "update_time": "更新时间"
}

PERMISSION_COLUMNS = {
    "permission_code": "权限代码",
    "permission_name": "权限名称",
    "resource_name": "资源名称",
    "action_name": "操作名称",
    "permission_desc": "权限描述",
    "status": "状态",
    "create_time": "创建时间",
    "update_time": "更新时间"
}
```

### Step 2: 创建 `backend/database/repositories/rbac_repository.py`

**必须使用**: `DatabaseManager` (`from backend.database.core.database_manager import DatabaseManager`)
**必须使用**: `?` 占位符（pyodbc 兼容）
**必须使用**: `column_names.py` 中的常量

```python
# backend/database/repositories/rbac_repository.py
from typing import List, Dict, Optional, Tuple
import logging
from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import ROLE_COLUMNS, PERMISSION_COLUMNS

logger = logging.getLogger(__name__)


class RbacRepository:
    def __init__(self):
        self.db = DatabaseManager()

    # ========== 角色操作 ==========

    def get_roles(self, keyword=None, status=None, role_type=None) -> List[Dict]:
        sql = f"""
            SELECT {ROLE_COLUMNS['role_id']}, {ROLE_COLUMNS['role_code']},
                   {ROLE_COLUMNS['role_name']}, {ROLE_COLUMNS['role_type']},
                   {ROLE_COLUMNS['role_desc']}, {ROLE_COLUMNS['status']},
                   {ROLE_COLUMNS['org_id']}, {ROLE_COLUMNS['create_time']}
            FROM sys_role
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += f" AND ({ROLE_COLUMNS['role_code']} LIKE ? OR {ROLE_COLUMNS['role_name']} LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if status:
            sql += f" AND {ROLE_COLUMNS['status']} = ?"
            params.append(status)
        if role_type:
            sql += f" AND {ROLE_COLUMNS['role_type']} = ?"
            params.append(role_type)
        sql += f" ORDER BY {ROLE_COLUMNS['create_time']} DESC"
        return self.db.execute_query(sql, params)

    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        sql = f"""
            SELECT {ROLE_COLUMNS['role_id']}, {ROLE_COLUMNS['role_code']},
                   {ROLE_COLUMNS['role_name']}, {ROLE_COLUMNS['role_type']},
                   {ROLE_COLUMNS['role_desc']}, {ROLE_COLUMNS['status']},
                   {ROLE_COLUMNS['org_id']}, {ROLE_COLUMNS['create_time']},
                   {ROLE_COLUMNS['update_time']}
            FROM sys_role
            WHERE {ROLE_COLUMNS['role_id']} = ?
        """
        results = self.db.execute_query(sql, [role_id])
        return results[0] if results else None

    def create_role(self, role_data: Dict) -> Dict:
        role_id = role_data.get("role_id") or self._generate_role_id()
        sql = f"""
            INSERT INTO sys_role (
                {ROLE_COLUMNS['role_id']}, {ROLE_COLUMNS['role_code']},
                {ROLE_COLUMNS['role_name']}, {ROLE_COLUMNS['role_type']},
                {ROLE_COLUMNS['role_desc']}, {ROLE_COLUMNS['status']},
                {ROLE_COLUMNS['org_id']}, {ROLE_COLUMNS['create_time']}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        params = [
            role_id,
            role_data.get("role_code"),
            role_data.get("role_name"),
            role_data.get("role_type", "custom"),
            role_data.get("role_desc", ""),
            role_data.get("status", "active"),
            role_data.get("org_id", "")
        ]
        self.db.execute_update(sql, params)
        return self.get_role_by_id(role_id)

    def update_role(self, role_id: str, role_data: Dict) -> Optional[Dict]:
        existing = self.get_role_by_id(role_id)
        if not existing:
            return None
        sql = f"""
            UPDATE sys_role SET
                {ROLE_COLUMNS['role_name']} = ?,
                {ROLE_COLUMNS['role_type']} = ?,
                {ROLE_COLUMNS['role_desc']} = ?,
                {ROLE_COLUMNS['status']} = ?,
                {ROLE_COLUMNS['update_time']} = GETDATE()
            WHERE {ROLE_COLUMNS['role_id']} = ?
        """
        params = [
            role_data.get("role_name", existing["role_name"]),
            role_data.get("role_type", existing["role_type"]),
            role_data.get("role_desc", existing["role_desc"]),
            role_data.get("status", existing["status"]),
            role_id
        ]
        self.db.execute_update(sql, params)
        return self.get_role_by_id(role_id)

    def delete_role(self, role_id: str) -> Tuple[bool, str]:
        role = self.get_role_by_id(role_id)
        if not role:
            return False, "角色不存在"
        if role.get(ROLE_COLUMNS['role_type']) == "system":
            return False, "系统角色不可删除"
        check_sql = f"SELECT 1 FROM sys_user_role_rel WHERE {ROLE_COLUMNS['role_id']} = ?"
        if self.db.execute_query(check_sql, [role_id]):
            return False, "该角色已有用户关联，无法删除"
        delete_sql = f"DELETE FROM sys_role WHERE {ROLE_COLUMNS['role_id']} = ?"
        self.db.execute_update(delete_sql, [role_id])
        return True, ""

    def _generate_role_id(self) -> str:
        import uuid
        return f"role_{uuid.uuid4().hex[:12]}"

    # ========== 权限操作 ==========

    def get_permissions(self, keyword=None, status=None, page=1, page_size=20) -> Dict:
        count_sql = f"SELECT COUNT(*) as cnt FROM sys_permission WHERE 1=1"
        sql = f"""
            SELECT {PERMISSION_COLUMNS['permission_code']},
                   {PERMISSION_COLUMNS['permission_name']},
                   {PERMISSION_COLUMNS['resource_name']},
                   {PERMISSION_COLUMNS['action_name']},
                   {PERMISSION_COLUMNS['permission_desc']},
                   {PERMISSION_COLUMNS['status']},
                   {PERMISSION_COLUMNS['create_time']}
            FROM sys_permission
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += f" AND ({PERMISSION_COLUMNS['permission_code']} LIKE ? OR {PERMISSION_COLUMNS['permission_name']} LIKE ?)"
            count_sql += f" AND ({PERMISSION_COLUMNS['permission_code']} LIKE ? OR {PERMISSION_COLUMNS['permission_name']} LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if status:
            sql += f" AND {PERMISSION_COLUMNS['status']} = ?"
            count_sql += f" AND {PERMISSION_COLUMNS['status']} = ?"
            params.append(status)
        total_list = self.db.execute_query(count_sql, params)
        total = total_list[0]["cnt"] if total_list else 0
        offset = (page - 1) * page_size
        sql += f" ORDER BY {PERMISSION_COLUMNS['create_time']} DESC OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
        items = self.db.execute_query(sql, params)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_permission_by_code(self, permission_code: str) -> Optional[Dict]:
        sql = f"""
            SELECT {PERMISSION_COLUMNS['permission_code']},
                   {PERMISSION_COLUMNS['permission_name']},
                   {PERMISSION_COLUMNS['resource_name']},
                   {PERMISSION_COLUMNS['action_name']},
                   {PERMISSION_COLUMNS['permission_desc']},
                   {PERMISSION_COLUMNS['status']},
                   {PERMISSION_COLUMNS['create_time']},
                   {PERMISSION_COLUMNS['update_time']}
            FROM sys_permission
            WHERE {PERMISSION_COLUMNS['permission_code']} = ?
        """
        results = self.db.execute_query(sql, [permission_code])
        return results[0] if results else None

    def create_permission(self, permission_data: Dict) -> Dict:
        sql = f"""
            INSERT INTO sys_permission (
                {PERMISSION_COLUMNS['permission_code']},
                {PERMISSION_COLUMNS['permission_name']},
                {PERMISSION_COLUMNS['resource_name']},
                {PERMISSION_COLUMNS['action_name']},
                {PERMISSION_COLUMNS['permission_desc']},
                {PERMISSION_COLUMNS['status']},
                {PERMISSION_COLUMNS['create_time']}
            ) VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """
        params = [
            permission_data.get("permission_code"),
            permission_data.get("permission_name"),
            permission_data.get("resource_name", ""),
            permission_data.get("action_name", ""),
            permission_data.get("permission_desc", ""),
            permission_data.get("status", "active")
        ]
        self.db.execute_update(sql, params)
        return self.get_permission_by_code(permission_data.get("permission_code"))

    def update_permission(self, permission_code: str, permission_data: Dict) -> Optional[Dict]:
        existing = self.get_permission_by_code(permission_code)
        if not existing:
            return None
        sql = f"""
            UPDATE sys_permission SET
                {PERMISSION_COLUMNS['permission_name']} = ?,
                {PERMISSION_COLUMNS['resource_name']} = ?,
                {PERMISSION_COLUMNS['action_name']} = ?,
                {PERMISSION_COLUMNS['permission_desc']} = ?,
                {PERMISSION_COLUMNS['status']} = ?,
                {PERMISSION_COLUMNS['update_time']} = GETDATE()
            WHERE {PERMISSION_COLUMNS['permission_code']} = ?
        """
        params = [
            permission_data.get("permission_name", existing["permission_name"]),
            permission_data.get("resource_name", existing["resource_name"]),
            permission_data.get("action_name", existing["action_name"]),
            permission_data.get("permission_desc", existing["permission_desc"]),
            permission_data.get("status", existing["status"]),
            permission_code
        ]
        self.db.execute_update(sql, params)
        return self.get_permission_by_code(permission_code)

    def delete_permission(self, permission_code: str) -> Tuple[bool, str]:
        perm = self.get_permission_by_code(permission_code)
        if not perm:
            return False, "权限不存在"
        check_sql = f"SELECT 1 FROM sys_role_permission_rel WHERE {PERMISSION_COLUMNS['permission_code']} = ?"
        if self.db.execute_query(check_sql, [permission_code]):
            return False, "该权限已被角色使用，无法删除"
        delete_sql = f"DELETE FROM sys_permission WHERE {PERMISSION_COLUMNS['permission_code']} = ?"
        self.db.execute_update(delete_sql, [permission_code])
        return True, ""

    # ========== 角色-权限关联 ==========

    def get_role_permissions(self, role_id: str) -> List[str]:
        sql = f"""
            SELECT {PERMISSION_COLUMNS['permission_code']}
            FROM sys_role_permission_rel
            WHERE {ROLE_COLUMNS['role_id']} = ?
        """
        results = self.db.execute_query(sql, [role_id])
        return [r[PERMISSION_COLUMNS['permission_code']] for r in results]

    def assign_permissions(self, role_id: str, permission_codes: List[str]) -> bool:
        def _tx(conn):
            cursor = conn.cursor()
            delete_sql = f"DELETE FROM sys_role_permission_rel WHERE {ROLE_COLUMNS['role_id']} = ?"
            cursor.execute(delete_sql, [role_id])
            for code in permission_codes:
                insert_sql = f"""
                    INSERT INTO sys_role_permission_rel ({ROLE_COLUMNS['role_id']}, {PERMISSION_COLUMNS['permission_code']})
                    VALUES (?, ?)
                """
                cursor.execute(insert_sql, [role_id, code])
            conn.commit()
        self.db.execute_with_transaction(_tx)
        return True
```

### Step 3: 扩展 `backend/services/rbac_service.py`

在现有 `rbac_service.py` 中添加以下方法（不修改现有代码）：

```python
# ========== 角色管理 ==========

def get_roles(keyword=None, status=None, role_type=None) -> List[Dict]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.get_roles(keyword, status, role_type)


def get_role_by_id(role_id: str) -> Optional[Dict]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.get_role_by_id(role_id)


def create_role(role_data: Dict, actor: str = "") -> Dict:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    existing = repo.get_roles()
    for r in existing:
        if r.get(ROLE_COLUMNS['role_code']) == role_data.get("role_code"):
            raise ValueError(f"角色代码 {role_data.get('role_code')} 已存在")
    return repo.create_role(role_data)


def update_role(role_id: str, role_data: Dict) -> Dict:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    existing = repo.get_role_by_id(role_id)
    if not existing:
        raise ValueError("角色不存在")
    if existing.get(ROLE_COLUMNS['role_type']) == "system" and role_data.get("role_type") != "system":
        raise ValueError("系统角色类型不可修改")
    return repo.update_role(role_id, role_data)


def delete_role(role_id: str) -> Tuple[bool, str]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.delete_role(role_id)


# ========== 权限管理 ==========

def get_permissions(keyword=None, status=None, page=1, page_size=20) -> Dict:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.get_permissions(keyword, status, page, page_size)


def get_permission_by_code(permission_code: str) -> Optional[Dict]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.get_permission_by_code(permission_code)


def create_permission(permission_data: Dict, actor: str = "") -> Dict:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    existing = repo.get_permission_by_code(permission_data.get("permission_code"))
    if existing:
        raise ValueError(f"权限代码 {permission_data.get('permission_code')} 已存在")
    return repo.create_permission(permission_data)


def update_permission(permission_code: str, permission_data: Dict) -> Dict:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    existing = repo.get_permission_by_code(permission_code)
    if not existing:
        raise ValueError("权限不存在")
    return repo.update_permission(permission_code, permission_data)


def delete_permission(permission_code: str) -> Tuple[bool, str]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.delete_permission(permission_code)


# ========== 角色-权限关联 ==========

def get_role_permissions(role_id: str) -> List[str]:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    return repo.get_role_permissions(role_id)


def assign_role_permissions(role_id: str, permission_codes: List[str]) -> bool:
    from backend.database.repositories.rbac_repository import RbacRepository
    repo = RbacRepository()
    role = repo.get_role_by_id(role_id)
    if not role:
        raise ValueError("角色不存在")
    return repo.assign_permissions(role_id, permission_codes)
```

### Step 4: 扩展 `backend/routes/admin_user_routes.py`

在现有 `admin_user_routes.py` 中添加以下端点（在文件末尾添加新路由）：

```python
# ========== 角色管理 API ==========

@admin_user_bp.route("/api/admin/roles", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_list_roles():
    try:
        data = get_roles(
            keyword=request.args.get("keyword", ""),
            status=request.args.get("status", ""),
            role_type=request.args.get("role_type", "")
        )
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        logger.error("failed to list roles: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles", methods=["POST"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_create_role():
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = create_role(payload, actor.get("user_id", ""))
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create role: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_update_role(role_id):
    try:
        payload = get_json_dict(required=True)
        data = update_role(role_id, payload)
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update role %s: %s", role_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>", methods=["DELETE"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_delete_role(role_id):
    try:
        success, error = delete_role(role_id)
        if not success:
            return jsonify({"success": False, "error": error}), 400
        return jsonify({"success": True})
    except Exception as exc:
        logger.error("failed to delete role %s: %s", role_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>/permissions", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_get_role_permissions(role_id):
    try:
        data = get_role_permissions(role_id)
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        logger.error("failed to get role permissions %s: %s", role_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>/permissions", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_assign_role_permissions(role_id):
    try:
        payload = get_json_dict(required=True)
        permission_codes = payload.get("permission_codes", [])
        assign_role_permissions(role_id, permission_codes)
        return jsonify({"success": True})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to assign role permissions %s: %s", role_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ========== 权限管理 API ==========

@admin_user_bp.route("/api/admin/permissions", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_list_permissions():
    try:
        data = get_permissions(
            keyword=request.args.get("keyword", ""),
            status=request.args.get("status", ""),
            page=parse_positive_int_arg("page", 1),
            page_size=parse_positive_int_arg("page_size", 20)
        )
        return jsonify({
            "success": True,
            "data": data.get("items", []),
            "total": data.get("total", 0),
            "page": data.get("page", 1),
            "page_size": data.get("page_size", 20)
        })
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list permissions: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions", methods=["POST"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_create_permission():
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = create_permission(payload, actor.get("user_id", ""))
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create permission: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions/<permission_code>", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_update_permission(permission_code):
    try:
        payload = get_json_dict(required=True)
        data = update_permission(permission_code, payload)
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update permission %s: %s", permission_code, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions/<permission_code>", methods=["DELETE"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_delete_permission(permission_code):
    try:
        success, error = delete_permission(permission_code)
        if not success:
            return jsonify({"success": False, "error": error}), 400
        return jsonify({"success": True})
    except Exception as exc:
        logger.error("failed to delete permission %s: %s", permission_code, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
```

### Step 5: 语法检查

```bash
python -m py_compile backend/database/repositories/rbac_repository.py backend/services/rbac_service.py backend/routes/admin_user_routes.py backend/database/schema/column_names.py
```

### Step 6: E2E 验证

执行 API E2E 测试：

```bash
python test_runner/api_e2e.py
```

验证以下 API 端点：

| 端点 | 方法 | 验证内容 |
|------|------|---------|
| `/api/admin/roles` | GET | 返回角色列表 |
| `/api/admin/roles` | POST | 创建角色成功 |
| `/api/admin/roles/<role_id>` | PUT | 更新角色成功 |
| `/api/admin/roles/<role_id>` | DELETE | system 角色返回 400，普通角色删除成功 |
| `/api/admin/roles/<role_id>/permissions` | GET | 返回角色权限列表 |
| `/api/admin/roles/<role_id>/permissions` | PUT | 分配权限成功 |
| `/api/admin/permissions` | GET | 返回权限列表（分页） |
| `/api/admin/permissions` | POST | 创建权限成功 |
| `/api/admin/permissions/<code>` | PUT | 更新权限成功 |
| `/api/admin/permissions/<code>` | DELETE | 被使用返回 400，未使用删除成功 |

---

## 约束 / Constraints

1. **UTF-8 编码**: 所有文件使用 `encoding='utf-8'`
2. **字段名常量**: 所有 SQL 中的中文字段必须使用 `column_names.py` 常量
3. **禁止占位符**: 所有代码完整可执行，无 `pass`、`TODO`、`...`
4. **SQL 占位符**: 使用 `?`（pyodbc 兼容），**禁止** `%s`
5. **数据库管理器**: 使用 `DatabaseManager`（`backend.database.core.database_manager`）
6. **事务处理**: 角色权限分配使用 `execute_with_transaction()`
7. **业务约束**:
   - `system` 类型角色不可删除
   - `role_code` 唯一性检查
   - 删除前检查关联数据

---

## 完成标准 / Completion Criteria

- [ ] `backend/database/schema/column_names.py` 已补充 `ROLE_COLUMNS`、`PERMISSION_COLUMNS` 常量
- [ ] `backend/database/repositories/rbac_repository.py` 已创建并包含所有方法
- [ ] `backend/services/rbac_service.py` 已扩展包含角色/权限管理方法
- [ ] `backend/routes/admin_user_routes.py` 已添加所有新端点
- [ ] `python -m py_compile` 语法检查通过
- [ ] 所有 API 端点返回正确的 HTTP 状态码和 JSON 响应
- [ ] 业务约束已实现（system 角色保护、唯一性检查、关联检查）
- [ ] **E2E 验证通过**（使用 `python test_runner/api_e2e.py`）
- [ ] 文档同步：更新 `docs/API_SPEC.md`（新增 API 端点）
