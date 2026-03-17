# Prompt Task: 20107 - Tool Search Location Parameter Type Mismatch

Primary Executor: Claude Code
Task Type: Refactoring
Priority: P2
Stage: 20107
Goal: Fix location parameter type mismatch between database.py and tool_repository.py
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

Code Review 报告 (2026-03-25) 识别出以下技术债问题：

`database.py` 中的 `search_tools` 函数将 `location: Optional[str]` 参数传递给 `tool_repository.py` 中的 `location_id: int` 参数。

**问题位置:**
- `database.py:368-389` - `search_tools` 函数定义和调用
- `tool_repository.py:63-69` - `ToolRepository.search_tools` 方法签名

**影响评估:**
- 当前功能正常（repository 层使用 `str(location_id).strip()` + LIKE 匹配）
- 但类型注解不一致可能导致代码阅读困惑和静态类型检查报警

---

## Required References / 必需参考

1. `database.py` - 第 368-389 行，`search_tools` 函数
2. `backend/database/repositories/tool_repository.py` - 第 63-153 行，`search_tools` 方法
3. `backend/database/schema/column_names.py` - 字段名常量定义
4. `docs/API_SPEC.md` - API 规范文档
5. `.claude/rules/20_codex_backend.md` - 后端实现规则

---

## Core Task / 核心任务

统一 `search_tools` 函数中 `location` 参数的类型注解和传递逻辑，消除类型不一致。

### 具体修改要求

1. **修改 `database.py` 中的 `search_tools` 函数**:
   - 将参数名 `location: Optional[str]` 改为 `location_id: Optional[str]`（保持 str 类型以支持 LIKE 匹配）
   - 更新 docstring 以反映参数用途
   - 确保传递给 repository 时注释清晰说明类型转换

2. **验证 `tool_repository.py` 中的 `search_tools` 方法**:
   - 检查 `location_id` 参数的实际使用方式
   - 如果需要，调整参数名为 `location_keyword` 以更准确反映其用途（模糊匹配）

3. **确保调用链一致性**:
   - 检查所有调用 `search_tools` 的地方
   - 确保参数传递正确

---

## Required Work / 必需工作

- [ ] 1. 读取并分析 `database.py` 中的 `search_tools` 函数实现
- [ ] 2. 读取并分析 `tool_repository.py` 中的 `search_tools` 方法实现
- [ ] 3. 确定最佳修复方案（统一命名或添加类型转换）
- [ ] 4. 修改 `database.py` 中的参数定义和 docstring
- [ ] 5. 如需要，修改 `tool_repository.py` 中的参数命名
- [ ] 6. 执行语法检查：`python -m py_compile database.py backend/database/repositories/tool_repository.py`
- [ ] 7. 更新相关文档（如需要）

---

## Constraints / 约束条件

1. **零退化原则**: 修改不得破坏现有功能
2. **向后兼容**: 如果修改函数签名，必须确保所有调用方不受影响
3. **类型一致性**: 参数类型注解必须与实际使用一致
4. **代码规范**: 使用英文变量名，4 空格缩进，snake_case 函数/变量
5. **文档更新**: 如果修改了 API 行为，需要更新 `docs/API_SPEC.md`

---

## Completion Criteria / 完成标准

1. `database.py` 和 `tool_repository.py` 中的 `location` 相关参数类型一致
2. Python 语法检查通过：`python -m py_compile database.py backend/database/repositories/tool_repository.py`
3. 所有调用 `search_tools` 的地方仍然正常工作
4. 如有 API 行为变更，更新 `docs/API_SPEC.md`
5. 生成执行报告到 `logs/prompt_task_runs/`

---

## 技术细节参考

### 当前代码状态

**database.py:368-389**
```python
def search_tools(
    keyword: str = "",
    status: Optional[str] = None,
    location: Optional[str] = None,  # 类型是 str
    page: int = 1,
    page_size: int = 20
) -> dict:
    repo = ToolRepository()
    return repo.search_tools(keyword, status, location, page_no=page, page_size=page_size)
    # location 传递给 location_id (int)
```

**tool_repository.py:63-69**
```python
def search_tools(
    self,
    keyword: str = None,
    status: str = None,
    location_id: int = None,  # 类型是 int，但实际用于 LIKE 模糊匹配
    page_no: int = 1,
    page_size: int = 20
) -> Dict:
```

**tool_repository.py:143-153 (实际使用)**
```python
if location_id not in (None, ''):
    location_like = f"%{str(location_id).strip()}%"
    # 使用 LIKE 进行模糊匹配
```

### 修复建议

方案 A（推荐）: 统一命名 + 保持 str 类型
- 将 `tool_repository.py` 中 `location_id: int` 改为 `location_keyword: str`
- 移除不必要的类型转换注释

方案 B: 添加类型转换层
- 在 `database.py` 中添加显式类型转换
- 保持 `tool_repository.py` 参数名不变
