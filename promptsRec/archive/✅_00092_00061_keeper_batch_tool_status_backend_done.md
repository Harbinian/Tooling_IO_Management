Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 082
Goal: Implement keeper batch tool status update API and audit logging
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

保管员在日常工装管理中，需要不依赖订单流程直接设置工装状态（如工装送修、报废等），并要求所有变更可追溯。

当前系统工装状态只能通过订单工作流间接变更，没有直接更新工装状态的 API。

---

## Required References / 必需参考

- `backend/database/repositories/tool_repository.py` - 工装数据访问层，复用 `get_tool_by_serial`, `load_tool_master_map` 方法
- `backend/services/tool_io_service.py` - 服务层，复用现有业务逻辑模式
- `backend/routes/tool_routes.py` - API 路由，复用 `@require_permission` 装饰器
- `backend/services/rbac_service.py` - 权限系统，参考 `_ensure_permission_exists`, `_ensure_role_permission_rel` 方法
- `docs/ARCHITECTURE.md` 3.3 节 - 工装状态定义: `in_storage`(在库), `outbounded`(已出库), `maintain`(维修中), `scrapped`(已报废)

---

## Core Task / 核心任务

实现保管员批量设置工装出入库状态的 API 功能：

1. **数据库**：确保审计表 `工装状态变更记录` 存在
2. **Repository 层**：在 `tool_repository.py` 新增 `update_tool_status_batch` 和 `get_tool_status_history` 方法
3. **Service 层**：在 `tool_io_service.py` 新增 `batch_update_tool_status` 函数
4. **RBAC**：新增 `tool:status_update` 权限，为 `ROLE_KEEPER` 和 `ROLE_SYS_ADMIN` 授予该权限
5. **Route 层**：新增 `PATCH /api/tools/batch-status` 和 `GET /api/tools/status-history/<tool_code>` 端点

---

## Required Work / 必需工作

### 1. 数据库审计表

确保 `工装状态变更记录` 表存在（如果不存在则创建）：

```sql
CREATE TABLE 工装状态变更记录 (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    工装编码 NVARCHAR(100) NOT NULL,
    原状态 NVARCHAR(50) NOT NULL,
    新状态 NVARCHAR(50) NOT NULL,
    变更原因 NVARCHAR(500) NULL,
    操作人ID NVARCHAR(64) NOT NULL,
    操作人姓名 NVARCHAR(100) NOT NULL,
    变更时间 DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    客户端IP NVARCHAR(64) NULL
)
```

### 2. Repository 层新增方法

**文件**: `backend/database/repositories/tool_repository.py`

新增方法：

```python
def update_tool_status_batch(
    self,
    tool_codes: List[str],
    new_status: str,
    operator: Dict,
    remark: str = None,
    client_ip: str = None
) -> Dict:
    """
    批量更新工装出入库状态并记录审计日志。

    Args:
        tool_codes: 工装编码列表
        new_status: 新状态 (in_storage/outbounded/maintain/scrapped)
        operator: 操作人信息 {user_id, display_name}
        remark: 变更原因
        client_ip: 客户端IP

    Returns:
        {
            success: bool,
            updated_count: int,
            records: [{tool_code, old_status, new_status}, ...]
        }
    """
```

```python
def get_tool_status_history(self, tool_code: str, page_no: int = 1, page_size: int = 20) -> Dict:
    """
    查询工装状态变更历史。

    Args:
        tool_code: 工装编码
        page_no: 页码
        page_size: 每页条数

    Returns:
        {
            success: bool,
            data: [{old_status, new_status, remark, operator_id, operator_name, change_time, client_ip}, ...],
            total: int,
            page_no: int,
            page_size: int
        }
    """
```

### 3. Service 层新增函数

**文件**: `backend/services/tool_io_service.py`

新增函数：

```python
def batch_update_tool_status(
    tool_codes: List[str],
    new_status: str,
    remark: str,
    operator: Dict
) -> Dict:
    """
    批量更新工装状态并记录审计。

    1. 验证 new_status 是有效状态值
    2. 调用 repository 更新状态
    3. 记录审计日志
    4. 返回更新结果
    """
```

### 4. RBAC 权限新增

**文件**: `backend/services/rbac_service.py`

在 `_ensure_incremental_permission_defaults` 函数中新增：

```python
# 新增权限 tool:status_update
_ensure_permission_exists(
    db,
    permission_code="tool:status_update",
    permission_name="Update Tool Status",
    resource_name="tool",
    action_name="status_update",
)
# 为 ROLE_KEEPER 授予权限
_ensure_role_permission_rel(db, role_id="ROLE_KEEPER", permission_code="tool:status_update")
# 为 ROLE_SYS_ADMIN 授予权限
_ensure_role_permission_rel(db, role_id="ROLE_SYS_ADMIN", permission_code="tool:status_update")
```

### 5. API 路由新增

**文件**: `backend/routes/tool_routes.py`

新增端点：

```python
@tool_bp.route("/api/tools/batch-status", methods=["PATCH"])
@require_permission("tool:status_update")
def api_batch_update_tool_status():
    """
    批量更新工装状态。

    请求体:
    {
        "tool_codes": ["T001", "T002"],
        "new_status": "maintain",
        "remark": "送修保养"
    }

    响应:
    {
        "success": true,
        "updated_count": 2,
        "records": [
            {"tool_code": "T001", "old_status": "in_storage", "new_status": "maintain"},
            {"tool_code": "T002", "old_status": "outbounded", "new_status": "maintain"}
        ]
    }
    """
```

```python
@tool_bp.route("/api/tools/status-history/<tool_code>", methods=["GET"])
@require_permission("tool:view")
def api_tool_status_history(tool_code: str):
    """
    查询工装状态变更历史。

    查询参数: page_no, page_size

    响应:
    {
        "success": true,
        "data": [...],
        "total": 10,
        "page_no": 1,
        "page_size": 20
    }
    """
```

---

## Constraints / 约束条件

1. **主键穿透**：必须使用 `工装编码` (序列号) 进行业务匹配，禁止使用名称匹配
2. **状态值验证**：只接受 `in_storage`, `outbounded`, `maintain`, `scrapped` 四个状态值
3. **审计日志**：每次状态变更必须记录审计日志
4. **权限控制**：只有持有 `tool:status_update` 权限的用户才能调用批量更新接口
5. **事务处理**：批量更新使用数据库事务保证数据一致性
6. **编码规范**：使用英文变量名，4空格缩进，snake_case 命名
7. **更新字段**：直接更新 `工装身份卡_主表` 的 `出入库状态` 字段

---

## Completion Criteria / 完成标准

1. **语法检查通过**：
   ```powershell
   python -m py_compile backend/database/repositories/tool_repository.py backend/services/tool_io_service.py backend/routes/tool_routes.py backend/services/rbac_service.py
   ```

2. **API 功能验证**（使用 curl 或 Postman）：
   - 使用 keeper 角色 token 调用 `PATCH /api/tools/batch-status`，验证返回 `updated_count` 正确
   - 调用 `GET /api/tools/status-history/<tool_code>`，验证返回历史记录
   - 使用无权限角色调用，验证返回 403 Forbidden

3. **数据库验证**：
   - 查询 `工装状态变更记录` 表，确认审计记录已正确创建
   - 查询 `工装身份卡_主表`，确认 `出入库状态` 字段已更新

4. **权限验证**：
   - keeper 角色可以成功调用 batch-status API
   - team_leader 角色调用返回 403
