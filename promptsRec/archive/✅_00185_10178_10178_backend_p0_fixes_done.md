# Prompt: 后端P0缺陷修复

Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: Prompt Number
Goal: 修复代码审查发现的4个P0后端问题
Dependencies: None
Execution: RUNPROMPT

---

## Context

代码审查报告 `review-reports/CODE_REVIEW_REPORT_20260401.md` 发现4个P0(必须立即修复)后端问题：

| # | 问题 | 位置 |
|---|------|------|
| 1 | 外部表访问绕过 `column_names.py` 常量 | `database_manager.py` |
| 2 | 复合操作无事务包装 | `order_repository.py` |
| 3 | SECRET_KEY 默认值风险 | `settings.py`, `web_server.py` |
| 4 | 缺少速率限制 | 全局 |

---

## Required References

- `backend/database/schema/column_names.py` - 字段名常量定义
- `backend/database/core/database_manager.py` - 需要修复的文件
- `backend/database/repositories/order_repository.py` - 需要添加事务的文件
- `config/settings.py` - 配置检查
- `web_server.py` - 速率限制和 SECRET_KEY
- `.claude/rules/00_core.md` - 核心规则（字段名常量规范）
- `.claude/rules/02_debug.md` - 8D问题解决协议

---

## Core Task

### 修复1: database_manager.py 外部表访问 (P0)

**问题**: 多处直接使用中文字段名而非 `column_names.py` 常量，违反架构规范。

**受影响方法**:
- `get_tool_basic_info()` - 使用 `m.序列号` 而非 `TOOL_MASTER_COLUMNS['tool_code']`
- `get_dispatch_info()` - 使用 `d.序列号`, `d.工装图号` 等
- `get_all_tpitr_info()` - 使用 `工装图号`, `版次` 等
- `get_acceptance_info()` - 使用 `m.派工号`, `m.表编号` 等

**修复要求**:
```python
# 在文件顶部导入
from backend.database.schema.column_names import TOOL_MASTER_COLUMNS, TOOL_MASTER_TABLE

# 将所有中文字段名替换为常量
# 错误示例
SELECT m.序列号, m.工装图号, m.工装名称

# 正确示例
SELECT m.{TOOL_MASTER_COLUMNS['tool_code']}, m.{TOOL_MASTER_COLUMNS['drawing_no']}, m.{TOOL_MASTER_COLUMNS['tool_name']}
```

### 修复2: order_repository.py 添加事务 (P0)

**问题**: `create_order`, `keeper_confirm`, `submit_order`, `final_confirm` 等复合操作缺少事务包装。

**修复要求**:
```python
# 使用已有的 execute_with_transaction 方法
def create_order(self, order_data, items):
    def _create_order_tx(conn):
        # 插入订单头
        self._db.execute_query(insert_order_sql, ..., conn=conn)
        # 插入明细
        for item in items:
            self._db.execute_query(insert_item_sql, ..., conn=conn)
        # 记录日志
        self.add_tool_io_log(..., conn=conn)
        return True

    return self._db.execute_with_transaction(_create_order_tx)
```

对以下方法应用相同模式：
- `create_order`
- `submit_order`
- `keeper_confirm`
- `final_confirm`

### 修复3: SECRET_KEY 配置 (P0)

**问题**: `settings.py:102` 和 `web_server.py:47` 使用默认值风险。

**修复要求**:
```python
# settings.py / web_server.py
import os
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")
```

### 修复4: 添加速率限制 (P0)

**问题**: 完全没有速率限制机制。

**修复要求**:
```python
# web_server.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# 登录接口更严格的限制
@auth_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    ...
```

---

## Required Work

1. **修复 `database_manager.py`**
   - 导入 `column_names` 中的常量
   - 将所有中文字段名替换为常量引用
   - 确保使用 `TOOL_MASTER_COLUMNS`, `TOOL_MASTER_TABLE` 等

2. **修复 `order_repository.py`**
   - 为 `create_order` 添加事务包装
   - 为 `submit_order` 添加事务包装
   - 为 `keeper_confirm` 添加事务包装
   - 为 `final_confirm` 添加事务包装

3. **修复 `settings.py` 和 `web_server.py`**
   - 移除 SECRET_KEY 默认值
   - 添加生产环境必须设置检查

4. **添加速率限制**
   - 在 `web_server.py` 添加 Flask-Limiter
   - 配置默认限制 100/minute
   - 登录接口限制 5/minute

---

## Constraints

- **必须使用 `column_names.py` 常量** - 禁止直接使用中文字段名
- **事务必须原子** - 失败时必须回滚
- **禁止修改外部系统表结构** - 只读访问 `Tooling_ID_Main`
- **UTF-8 编码** - 所有文件操作使用 `encoding='utf-8'`
- **参数化查询** - 继续使用 `?` 占位符

---

## Completion Criteria

1. `database_manager.py` 中无中文字段名字面量
2. `order_repository.py` 中所有复合操作使用事务
3. `SECRET_KEY` 无默认值，启动时必须设置
4. Flask-Limiter 正确配置并生效
5. `python -m py_compile backend/database/core/database_manager.py backend/database/repositories/order_repository.py config/settings.py web_server.py` 无语法错误
