---
name: 20115_refactor_fix_assign_transport_direct_db_call
executor: Codex
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/00_core.md
version: 1.0.0
---

# 20115: 重构 - 修复 assign_transport 跨层调用问题

## Header / 头部信息

Primary Executor: Codex
Task Type: Refactoring
Priority: P0
Stage: 20115
Goal: 将 order_workflow_service.assign_transport 中的直接 db.execute_query 调用迁移到 Repository 层
Dependencies: "10203 (Bug修复 - SQL编码错误)"
Execution: RUNPROMPT

---

## Context / 上下文

架构评审发现 `backend/services/order_workflow_service.py` 的 `assign_transport` 函数直接调用 `DatabaseManager().execute_query()`，绕过了 Repository 层，违反分层原则。

**注意**：本任务**范围仅限于** `assign_transport` 函数中的直接 DB 调用修复，**不涉及**其他服务文件的跨层调用。

**真实文件结构（已验证）**：

| 文件 | 状态 | 备注 |
|------|------|------|
| `backend/services/order_workflow_service.py` | ✅ 存在 | line 186 `def assign_transport(...)` |
| `backend/database/repositories/order_repository.py` | ✅ 存在 | 有多种 update/keeper/final 方法可参考 |
| `backend/database/__init__.py` | ✅ 存在 | 导出 `DatabaseManager` |
| `backend/database/core/database_manager.py` | ✅ 存在 | 但不应直接引用，应通过 Repository |
| `backend/database/schema/column_names.py` | ✅ 存在 | 定义了 `ORDER_COLUMNS` 常量 |

**导入来源（已验证）**：
```python
from database import DatabaseManager  # 顶层导入，非 backend.database
```

---

## Phase 1 - PRD / 业务需求分析

**业务背景**：
- `assign_transport` 函数需要更新订单的运输信息
- 当前直接在 service 层调用 `DatabaseManager().execute_query()`
- 违反"服务层 → Repository层 → 数据库"的分层原则

**目标**：
- 将 `assign_transport` 中的 DB 访问迁移到 `OrderRepository`
- 保持函数外部行为不变
- 保持事务语义

**成功标准**：
- `assign_transport` 中无直接 `DatabaseManager` 调用
- 所有 DB 访问通过 `OrderRepository` 方法
- 审计日志仍正确记录

---

## Phase 2 - Data / 数据流转审视

**assign_transport 函数分析（已读取真实代码）**：

```python
def assign_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    # ... validation ...

    db = DatabaseManager()  # line 203 - 直接实例化
    try:
        update_sql = """
            UPDATE tool_io_order
            SET ææ­·æµæ¯'D = ?,        -- 乱码，10203 需修复
                ææ­·æµæå"˜éš? = ?,
                æ·‡æ¿ˆî…¸é�›æ¨¼'ç'‡ã†æ¤‚é—‚? = ?,
                æ·‡î†½æ•¼éƒƒå ã¤æ£¿ = SYSDATETIME()
            WHERE é"'å"„å†…æ'¬æ'³å´Ÿé™? = ?
        """
        db.execute_query(update_sql, (...), fetch=False)  # line 217
    except Exception as exc:
        ...

    write_order_audit_log(...)  # 审计日志
    _emit_internal_notification(...)  # 通知
```

**现有 OrderRepository 方法参考**（来自 `order_repository.py`）：
- `update_order(...)` - 更新订单
- `keeper_confirm(...)` - 保管员确认（包含事务）
- `final_confirm(...)` - 最终确认（包含事务）
- `add_tool_io_log(...)` - 添加审计日志

**关键风险（由 Plan Agent 发现）**：
- `ORDER_COLUMNS` 中**不存在** `transport_contact` 字段
- 需要在 `OrderRepository.assign_transport` 方法中确认实际字段名

---

## Phase 3 - Architecture / 架构设计

### 重构方案

**方案：在 OrderRepository 中新增 assign_transport 方法**

参考 `keeper_confirm` 的事务模式（使用 `execute_with_transaction` + 内部回调函数）：

```python
# backend/database/repositories/order_repository.py

def assign_transport(
    self,
    order_no: str,
    transport_operator: str,
    transport_operator_name: str,
    transport_contact: str,
    operator_id: str,
    operator_name: str,
    operator_role: str,
) -> dict:
    """分配运输人（包含事务：更新+审计日志）"""
    try:
        def _assign_transport_tx(conn):
            # 1. 检查订单是否存在
            check_sql = f"""
            SELECT [{ORDER_COLUMNS['order_status']}]
            FROM [{TABLE_NAMES['ORDER']}]
            WHERE [{ORDER_COLUMNS['order_no']}] = ? AND [{ORDER_COLUMNS['is_deleted']}] = 0
            """
            result = self._db.execute_query(check_sql, (order_no,), conn=conn)
            if not result:
                raise ValueError('单据不存在')

            current_status = result[0].get('order_status')

            # 2. 更新运输信息（字段名待 10203 修复后确认）
            update_sql = f"""
            UPDATE [{TABLE_NAMES['ORDER']}] SET
                [{ORDER_COLUMNS['transport_operator_id']}] = ?,
                [{ORDER_COLUMNS['transport_operator_name']}] = ?,
                [{ORDER_COLUMNS['transport_contact']}] = ?,
                [{ORDER_COLUMNS['transport_notify_time']}] = GETDATE()
            WHERE [{ORDER_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(update_sql, (...), fetch=False, conn=conn)

            # 3. 添加审计日志
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.TRANSPORT_ASSIGN,
                ...
            }, conn=conn)

        self._db.execute_with_transaction(_assign_transport_tx)
        return {'success': True, 'order_no': order_no}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 事务处理

```
Service Layer                      Repository Layer
-----------                        ---------------
assign_transport()         -->   repo.assign_transport()
  - 验证订单                      - execute_with_transaction()
  - 调用 repo.assign_transport()    - UPDATE
  - 发送通知                        - add_tool_io_log()
```

### 风险识别

| 风险 | 严重度 | 说明 |
|------|--------|------|
| `transport_contact` 字段不存在 | **HIGH** | `ORDER_COLUMNS` 中无此字段，10203 修复时需确认 |
| 乱码 SQL 字段名 | **HIGH** | 10203 需先修复字段名常量 |
| `ToolIOAction.TRANSPORT_ASSIGN` 不存在 | LOW | 需添加到 `ToolIOAction` 枚举 |

---

## Phase 4 - Execution / 精确执行

### 执行步骤

**重要**：本任务依赖 10203 乱码修复完成。10203 修复后，字段名将通过 `ORDER_COLUMNS` 常量访问。

**Step 1**: 确认字段名（等待 10203 完成后）
```
- 读取 10203 修复后的 order_workflow_service.py
- 确认乱码 SQL 被替换为 ORDER_COLUMNS 常量
- 确认 transport_contact 等字段的常量名
```

**Step 2**: 在 OrderRepository 添加 assign_transport 方法
```
- 读取 order_repository.py 了解现有方法结构
- 参考 keeper_confirm 的事务模式
- 添加 assign_transport 方法
- 添加 ToolIOAction.TRANSPORT_ASSIGN 常量（如不存在）
```

**Step 3**: 修改 order_workflow_service.py
```
- 移除 line 203 的 DatabaseManager 实例化
- 移除 line 209-220 的乱码 SQL
- 添加 OrderRepository 导入
- 调用 repo.assign_transport()
```

**Step 4**: 验证
```
- 语法检查：python -m py_compile backend/services/order_workflow_service.py backend/database/repositories/order_repository.py
- 导入测试：python -c "from backend.services.order_workflow_service import assign_transport"
```

**Step 5**: 文档同步
```
- 更新 docs/API_SPEC.md（如 assign-transport API 有变更）
- 更新 docs/ARCHITECTURE.md（Repository 层新增方法说明）
```

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| 服务层 | `backend/services/order_workflow_service.py` | 重构目标，line 186-234 |
| Repository | `backend/database/repositories/order_repository.py` | 添加方法目标 |
| 字段名常量 | `backend/database/schema/column_names.py` | 字段名常量 |
| 表名常量 | `backend/database/schema/column_names.py` | `TABLE_NAMES` 常量 |
| 乱码修复后 | 等待 10203 完成 | 确认修复后的字段名 |

---

## Constraints / 约束条件

1. **范围限定**：本任务**仅修复** `assign_transport` 的跨层调用，**不扩大范围**
2. **依赖 10203**：必须等待 10203 完成后再执行 Step 1
3. **禁止破坏业务逻辑**：函数外部行为（返回值、通知、审计日志）必须保持不变
4. **事务语义不变**：更新和审计日志必须在同一事务中
5. **UTF-8 编码**：所有文件必须 UTF-8 无 BOM

---

## Completion Criteria / 完成标准

- [ ] `OrderRepository.assign_transport` 方法已添加
- [ ] `assign_transport` 函数中无直接 `DatabaseManager` 调用
- [ ] 乱码 SQL 已被 `ORDER_COLUMNS` 常量替换（来自 10203）
- [ ] 事务语义保持正确（更新+审计日志在同一事务）
- [ ] 语法检查通过
- [ ] 导入测试通过
- [ ] docs/API_SPEC.md 已更新（如需要）
- [ ] docs/ARCHITECTURE.md 已更新（如需要）
- [ ] tester E2E 验证通过（Order IO 核心流程）
