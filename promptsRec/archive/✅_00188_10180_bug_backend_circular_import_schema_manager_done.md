# Bug Fix: Circular Import in backend/database/schema/schema_manager.py

Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: 10180
Goal: Fix circular import between schema_manager.py and database_manager.py
Dependencies: None
Execution: RUNPROMPT

---

## Context

后端服务无法启动，报错：
```
ImportError: cannot import name 'DatabaseManager' from partially initialized module 'backend.database.core.database_manager' (most likely due to a circular import)
```

**循环导入链**:
1. `backend/database/core/database_manager.py` (line 27) → imports `from backend.database.schema.column_names`
2. `backend/database/schema/__init__.py` (line 4) → imports `from backend.database.schema.schema_manager`
3. `backend/database/schema/schema_manager.py` (line 9) → imports `from backend.database.core.database_manager` → **循环回来**

---

## Required References

- `backend/database/schema/schema_manager.py` - 需要修改的文件
- `backend/database/core/database_manager.py` - 被导入的模块
- `.claude/rules/00_core.md` - 核心开发规则（编码规范）

---

## Core Task

修复 `schema_manager.py` 中的循环导入问题。

**根因**: `DatabaseManager` 在模块级别（第9行）被导入，但只在函数 `_execute_statements_in_transaction` 内部使用（第36行）。

**修复方案**: 将 `DatabaseManager` 的导入从模块级别改为函数内延迟导入（lazy import）。

---

## Required Work

1. 修改 `backend/database/schema/schema_manager.py`:
   - 删除第9行的模块级导入: `from backend.database.core.database_manager import DatabaseManager, ORDER_NO_SEQUENCE_TABLE`
   - 仅保留 `ORDER_NO_SEQUENCE_TABLE` 的导入（它不参与循环）
   - 在 `_execute_statements_in_transaction` 函数内部添加延迟导入

2. 验证修复:
   - 运行 `python -m py_compile backend/database/schema/schema_manager.py`
   - 尝试启动后端: `python web_server.py`

3. 确认修复后的代码逻辑不变

---

## Constraints

- 只修改 `backend/database/schema/schema_manager.py`
- 保持 `_execute_statements_in_transaction` 的逻辑不变
- 保持 `ORDER_NO_SEQUENCE_TABLE` 的导入
- UTF-8 编码

---

## Completion Criteria

- [ ] `schema_manager.py` 中 `DatabaseManager` 改为函数内导入
- [ ] `python -m py_compile backend/database/schema/schema_manager.py` 无错误
- [ ] `python web_server.py` 可以启动（可能因数据库连接失败，但不应有 ImportError）
- [ ] 循环导入错误消失
