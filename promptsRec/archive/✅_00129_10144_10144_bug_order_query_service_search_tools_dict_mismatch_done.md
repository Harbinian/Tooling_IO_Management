# Prompt Task: 10144 - Bug Fix - order_query_service Search Tools Dict Mismatch

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10144
Goal: Fix search_tool_inventory calling search_tools with dict instead of keyword arguments
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

在执行重构任务 20107 时，发现 `backend/services/order_query_service.py` 中的 `search_tool_inventory` 函数存在 API 调用错误。

**问题位置**: `backend/services/order_query_service.py:115`

**错误代码**:
```python
def search_tool_inventory(filters: Dict) -> Dict:
    """Search tool inventory."""
    return search_tools(filters)  # ❌ 传递字典，但 search_tools() 期望关键字参数
```

**database.py 中 search_tools 的签名**:
```python
def search_tools(
    keyword: str = "",
    status: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> dict:
```

**问题分析**: `filters` 是一个 `Dict` 对象，但被传递给期望 `str` 类型的 `keyword` 参数。这会导致运行时类型错误。

---

## Observed Issue / 观察到的症状

运行时错误：字典对象被当作字符串处理，导致后续 SQL 查询或类型检查失败。

---

## Required Investigation / 需要调查的内容

1. 检查 `order_query_service.py` 中 `search_tool_inventory` 函数的所有调用方
2. 确认 `filters` 字典的结构和预期字段
3. 验证 `database.py` 中 `search_tools` 函数签名
4. 确定正确的修复方式（提取参数调用 vs 使用 `**filters` 解包）

---

## Required Fix Scope / 需要修复的范围

### 1. 修改 `backend/services/order_query_service.py`

**位置**: 第 113-115 行

**修改前**:
```python
def search_tool_inventory(filters: Dict) -> Dict:
    """Search tool inventory."""
    return search_tools(filters)
```

**修改后** (方案 A - 显式提取参数):
```python
def search_tool_inventory(filters: Dict) -> Dict:
    """Search tool inventory."""
    return search_tools(
        keyword=filters.get("keyword"),
        status=filters.get("status"),
        location=filters.get("location"),
        page=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
    )
```

**修改后** (方案 B - 使用解包):
```python
def search_tool_inventory(filters: Dict) -> Dict:
    """Search tool inventory."""
    return search_tools(**filters)
```

**选择标准**: 选择使调用链最清晰、错误处理最好的方案。

---

## Output Requirements / 输出要求

1. 修改后的 `backend/services/order_query_service.py` 文件
2. 修改后的调用代码必须保持与 `database.py` 中 `search_tools` 函数签名一致
3. 确保 `filters` 中的 `page_no` 映射到 `page` 参数（如果使用方案 A）

---

## Completion Criteria / 完成标准

1. `python -m py_compile backend/services/order_query_service.py` 通过
2. 函数调用逻辑正确：`filters` 字典中的值被正确提取并传递给 `search_tools`
3. 如果 `filters` 中没有 `page_no` 字段，默认值为 1
4. 如果 `filters` 中没有 `page_size` 字段，默认值为 20
5. 在 `logs/prompt_task_runs/` 中创建执行报告

---

## Constraints / 约束条件

1. **零退化原则**: 不得破坏现有功能
2. **最小修改**: 只修改必要的代码行
3. **向后兼容**: 确保调用方 (`tool_io_service.py:search_tool_inventory`) 不受影响
4. **遵循后端规则**: 使用英文变量名，4 空格缩进，snake_case 函数/变量

---

## References / 参考

- `backend/services/order_query_service.py:113-115`
- `database.py:368-389`
- `.claude/rules/20_codex_backend.md`
- `.claude/rules/40_debug_8d.md`
