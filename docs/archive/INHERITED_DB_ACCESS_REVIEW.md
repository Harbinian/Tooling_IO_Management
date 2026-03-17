# 继承数据库访问审查 / Inherited Database Access Review

---

## 概述 / Overview

本文档审查现有的数据库模块（database.py），描述连接策略、查询执行模式、现有 CRUD 函数和集成建议。 / This document reviews the existing database module (database.py), describing connection strategy, query execution patterns, existing CRUD functions, and integration recommendations.

---

## 1. 连接策略 / 1 Connection Strategy

### 1.1 DatabaseManager 单例 / 1.1 DatabaseManager Singleton

位置：database.py:119-220 / Location: database.py:119-220

```python
class DatabaseManager:
    """Database manager with connection pool"""
    _instance = None
    _pool: Optional[ConnectionPool] = None
```

**特性：** / **Features:**

- 单例模式，确保全局唯一数据库管理器 / Singleton pattern, ensuring globally unique database manager
- 线程安全（使用 threading.Lock） / Thread-safe (using threading.Lock)
- 支持从 config.settings 或环境变量读取配置 / Support reading config from config.settings or environment variables

### 1.2 配置来源 / 1.2 Configuration Source

**优先级：** / **Priority:**

1. `config/settings.py`（统一配置 / Unified configuration）
2. 环境变量（CESOFT_DB_* 系列 / Environment variables (CESOFT_DB_* series)）

**配置项：** / **Configuration Items:**

| 配置项 / Config Item | 环境变量 / Environment Variable | 默认值 / Default Value |
|--------|----------|--------|
| 服务器 / Server | CESOFT_DB_SERVER | 192.168.19.220,1433 |
| 数据库 / Database | CESOFT_DB_DATABASE | CXSYSYS |
| 用户名 / Username | CESOFT_DB_USERNAME | sa |
| 密码 / Password | CESOFT_DB_PASSWORD | (空 / empty) |
| 驱动 / Driver | CESOFT_DB_DRIVER | {SQL Server} |
| 连接池大小 / Pool Size | CESOFT_DB_POOL_SIZE | 5 |

---

## 2. 连接池行为 / 2 Connection Pool Behavior

### 2.1 ConnectionPool / 2.1 ConnectionPool

位置：database.py:31-113 / Location: database.py:31-113

**特性：** / **Features:**

- 固定大小连接池（默认5个连接）/ Fixed-size connection pool (default 5 connections)
- 自动连接验证（每60秒检查一次）/ Automatic connection validation (check every 60 seconds)
- 自动重连机制（最多3次重试）/ Automatic reconnection mechanism (max 3 retries)
- 连接超时控制（默认30秒）/ Connection timeout control (default 30 seconds)

**核心方法：** / **Core Methods:**

```python
def get_connection(self) -> pyodbc.Connection:
    """从连接池获取连接 / Get connection from pool"""

def release_connection(self, conn: pyodbc.Connection):
    """释放连接回池 / Release connection back to pool"""

def close_all(self):
    """关闭所有连接 / Close all connections"""
```

### 2.2 连接生命周期 / 2.2 Connection Lifecycle

```
请求进入 → get_connection() → 使用连接 → release_connection() → 归还池中
Request enters → get_connection() → Use connection → release_connection() → Return to pool
                                      ↓
                                连接失效检测 / Connection validity check
                                      ↓
                                关闭并重建 / Close and rebuild
```

---

## 3. 查询执行模式 / 3 Query Execution Pattern

### 3.1 核心方法 / 3.1 Core Methods

位置：database.py:221-259 / Location: database.py:221-259

```python
def execute_query(
    self,
    sql: str,
    params: Optional[Tuple] = None,
    fetch: bool = True
) -> List[Dict]:
```

**特性：** / **Features:**

- 参数化查询（防止 SQL 注入）/ Parameterized queries (prevent SQL injection)
- 自动列名映射 / Automatic column name mapping
- 支持查询和非查询（INSERT/UPDATE/DELETE）/ Support query and non-query (INSERT/UPDATE/DELETE)
- 自动提交事务（fetch=False 时）/ Auto-commit transaction (when fetch=False)

### 3.2 事务支持 / 3.2 Transaction Support

**当前实现：** / **Current Implementation:**

- 无显式事务支持 / No explicit transaction support
- 每条 SQL 自动提交 / Each SQL auto-commits
- 缺少 `transaction()` 上下文管理器 / Missing `transaction()` context manager

**局限性：** / **Limitations:**

- 多步操作无法原子性执行 / Multi-step operations cannot be executed atomically
- 需要手动处理错误回滚 / Need to manually handle error rollback

### 3.3 查询示例 / 3.3 Query Examples

```python
# 查询 / Query
result = db.execute_query(
    "SELECT * FROM 工装出入库单_主表 WHERE 出入库单号 = ?",
    (order_no,)
)

# 插入/更新 / Insert/Update
db.execute_query(
    "INSERT INTO 表名 (...) VALUES (...)",
    params,
    fetch=False  # 不返回结果，自动提交 / No return result, auto-commit
)
```

---

## 4. 现有 CRUD 函数 / 4 Existing CRUD Functions

### 4.1 表初始化 / 4.1 Table Initialization

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| ensure_tool_io_tables() | 创建5张表 / Create 5 tables | database.py:302-441 |

### 4.2 订单操作 / 4.2 Order Operations

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| generate_order_no() | 生成订单号 / Generate order number | database.py:444-464 |
| create_tool_io_order() | 创建订单 / Create order | database.py:467-537 |
| submit() | 提交订单 / Submit order | database.py:540-570 |
| get_tool_io_order() | 获取订单详情 / Get order details | database.py:573-589 |
| get_tool_io_orders() | 查询订单列表 / Query order list | database.py:592-658 |
| keeper_confirm_order() | 保管员确认 / Keeper confirm | database.py:721-815 |
| final_confirm_order() | 最终确认 / Final confirm | database.py:818-874 |
| reject_tool_io_order() | 拒绝订单 / Reject order | database.py:877-930 |
| cancel_tool_io_order() | 取消订单 / Cancel order | database.py:933-984 |

### 4.3 工装操作 / 4.3 Tool Operations

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| search_tools() | 搜索工装 / Search tools | database.py:661-718 |

### 4.4 日志操作 / 4.4 Log Operations

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| add_tool_io_log() | 添加操作日志 / Add operation log | database.py:987-1011 |
| get_tool_io_logs() | 获取操作日志 / Get operation logs | database.py:1014-1026 |

### 4.5 通知操作 / 4.5 Notification Operations

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| add_tool_io_notification() | 添加通知记录 / Add notification record | database.py:1029-1054 |
| update_notification_status() | 更新通知状态 / Update notification status | database.py:1057-1072 |

### 4.6 查询操作 / 4.6 Query Operations

| 函数名 / Function Name | 说明 / Description | 位置 / Location |
|--------|------|------|
| get_pending_keeper_orders() | 获取待确认订单 / Get pending keeper orders | database.py:1075-1093 |
| test_db_connection() | 测试数据库连接 / Test database connection | database.py:1105-1107 |

---

## 5. 可复用机会 / 5 Reuse Opportunities

### 5.1 直接复用的模块 / 5.1 Directly Reusable Modules

| 模块 / Module | 复用方式 / Reuse Method |
|------|----------|
| DatabaseManager | 直接导入使用 / Direct import and use |
| ConnectionPool | 通过 DatabaseManager使用 / Use through DatabaseManager |
| execute_query() | 所有数据库操作 / All database operations |
| ToolIOStatus | 状态常量定义 / Status constant definitions |
| ToolIOAction | 操作类型常量 / Action type constants |

### 5.2 可扩展的函数 / 5.2 Extensible Functions

| 函数 / Function | 扩展点 / Extension Points |
|------|--------|
| create_tool_io_order() | 可添加更多字段验证 / Can add more field validation |
| get_tool_io_orders() | 可添加更多过滤条件 / Can add more filter conditions |
| keeper_confirm_order() | 可添加更多业务逻辑 / Can add more business logic |
| search_tools() | 可添加更多搜索条件 / Can add more search conditions |

---

## 6. 缺失的抽象 / 6 Missing Abstractions

### 6.1 事务管理 / 6.1 Transaction Management

**当前：** 无显式事务支持 / **Current:** No explicit transaction support
**建议：** 添加事务上下文管理器 / **Recommendation:** Add transaction context manager

```python
@contextmanager
def transaction(self):
    conn = self.connect()
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        self.close(conn)
```

### 6.2 乐观锁 / 6.2 Optimistic Locking

**当前：** 无版本控制 / **Current:** No version control
**建议：** 添加 version 字段支持 / **Recommendation:** Add version field support

### 6.3 软删除 / 6.3 Soft Delete

**当前：** 使用 IS_DELETED 字段（部分实现）/ **Current:** Uses IS_DELETED field (partial implementation)
**建议：** 统一软删除逻辑 / **Recommendation:** Unify soft delete logic

### 6.4 审计字段自动填充 / 6.4 Audit Field Auto-population

**当前：** 需要手动传递创建人/修改人 / **Current:** Need to manually pass creator/modifier
**建议：** 添加自动填充逻辑 / **Recommendation:** Add auto-population logic

---

## 7. 识别的 Schema 不一致 / 7 Identified Schema Inconsistencies

### 7.1 主表缺失字段 / 7.1 Missing Fields in Main Table

| 字段 / Field | 类型 / Type | 代码引用 / Code Reference | 影响 / Impact |
|------|------|----------|------|
| 工装数量 / Tool Quantity | INT | database.py:519 | 创建订单更新失败 / Order creation update fails |
| 已确认数量 / Confirmed Quantity | INT | database.py:785 | 确认数量无法记录 / Cannot record confirmation quantity |
| 最终确认人 / Final Confirmer | VARCHAR(64) | database.py:842 | 确认人无法记录 / Cannot record confirmer |

### 7.2 明细表缺失字段 / 7.2 Missing Fields in Detail Table

| 字段 / Field | 类型 / Type | 代码引用 / Code Reference | 影响 / Impact |
|------|------|----------|------|
| 确认时间 / Confirmation Time | DATETIME | database.py:755 | 时间无法记录 / Cannot record time |
| 出入库完成时间 / IO Completion Time | DATETIME | database.py:853 | 完成时间无法记录 / Cannot record completion time |

### 7.3 修复建议 / 7.3 Fix Recommendations

```sql
-- 主表添加缺失字段 / Add missing fields to main table
ALTER TABLE 工装出入库单_主表 ADD 工装数量 INT;
ALTER TABLE 工装出入库单_主表 ADD 已确认数量 INT;
ALTER TABLE 工装出入库单_主表 ADD 最终确认人 VARCHAR(64);

-- 明细表添加缺失字段 / Add missing fields to detail table
ALTER TABLE 工装出入库单_明细 ADD 确认时间 DATETIME;
ALTER TABLE 工装出入库单_明细 ADD 出入库完成时间 DATETIME;
```

---

## 8. 集成建议 / 8 Integration Recommendations

### 8.1 API 层集成 / 8.1 API Layer Integration

```python
# 在 web_server.py 中复用 database.py / Reuse database.py in web_server.py
from database import (
    DatabaseManager,
    create_tool_io_order,
    get_tool_io_orders,
    # ...
)

@app.route('/api/tool-io-orders', methods=['POST'])
def create_order():
    db = DatabaseManager()
    # 直接调用现有函数 / Directly call existing functions
    result = create_tool_io_order(request.json)
    return jsonify(result)
```

### 8.2 服务层扩展 / 8.2 Service Layer Extension

在现有函数基础上添加业务逻辑层：/ Add business logic layer on existing functions:

```
API Route → Service Layer → Existing CRUD Functions → Database
```

### 8.3 注意事项 / 8.3 Notes

1. **不要替换现有模块** - 在现有基础上扩展 / **Do not replace existing modules** - Extend on existing basis
2. **保持参数化查询** - 继续使用 ? 占位符 / **Maintain parameterized queries** - Continue using ? placeholders
3. **遵循现有命名规范** - 中文表名/列名 / **Follow existing naming conventions** - Chinese table/column names
4. **处理异常一致** - 使用现有的错误处理模式 / **Handle exceptions consistently** - Use existing error handling patterns

---

## 9. 相关文档 / 9 Related Documents

- [数据库架构文档 / Database Schema Document](./DB_SCHEMA.md)
- [API规格文档 / API Specification Document](./API_SPEC.md)
- [产品需求文档 / Product Requirements Document](./PRD.md)
- [架构文档 / Architecture Document](./ARCHITECTURE.md)
