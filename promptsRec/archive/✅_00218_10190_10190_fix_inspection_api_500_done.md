# Bug Fix Prompt — Inspection API 500 Errors

## Header

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10190
Goal: Fix inspection stats summary and reschedule endpoints returning 500 instead of calling schema init
Dependencies: None
Execution: RUNPROMPT

---

## Context

`GET /api/inspection/stats/summary` and `PUT /api/inspection/tasks/{task_no}/reschedule` are both returning HTTP 500. These endpoints serve the Inspection Dashboard and Calendar Vue pages. The 500 errors indicate unhandled exceptions propagating to the Flask route layer.

---

## Required References

### Source Files

| File | Relevance |
|------|-----------|
| `backend/services/inspection_stats_service.py` | `get_summary()` — directly queries `tool_io_inspection_task` without schema init |
| `backend/services/inspection_task_service.py` | `reschedule_task()` — calls `_ensure_inspection_schema()` but query may still fail |
| `backend/database/repositories/inspection_task_repository.py` | `InspectionTaskRepository.get_task()` — underlying query |
| `backend/routes/inspection_routes.py` | Route handlers that catch exceptions and return 500 |
| `backend/database/schema/schema_manager.py` | `ensure_inspection_task_table()` — table creation |
| `backend/database/schema/__init__.py` | `_ensure_inspection_schema()` helper defined here |

### Key Code Snippets

**`backend/services/inspection_stats_service.py` (BUG)**:
```python
def get_summary(current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    db = DatabaseManager()  # ← No schema init before querying!
    today = date.today()
    pending_rows = db.execute_query(
        f"""SELECT COUNT(1) AS cnt
            FROM [{TABLE_NAMES['INSPECTION_TASK']}]
            WHERE [{INSPECTION_TASK_COLUMNS['task_status']}] = 'pending'"""
    )
    # ... more queries without schema init
```

**`backend/services/inspection_task_service.py` (line 40-48)**:
```python
def _ensure_inspection_schema() -> None:
    if not ensure_inspection_plan_table():
        raise RuntimeError("inspection plan table is not ready")
    if not ensure_inspection_task_table():
        raise RuntimeError("inspection task table is not ready")
    if not ensure_inspection_report_table():
        raise RuntimeError("inspection report table is not ready")
    if not ensure_tool_inspection_status_table():
        raise RuntimeError("tool inspection status table is not ready")
```

**`backend/routes/inspection_routes.py` (line 28-30)**:
```python
except Exception as exc:
    logger.error("failed to get inspection stats summary: %s", exc)
    return jsonify({"success": False, "error": str(exc)}), 500
```

---

## Core Task

### Bug Analysis

**Bug 1 — `get_summary()` missing schema init**
- `get_summary()` in `inspection_stats_service.py` directly calls `db.execute_query()` on `tool_io_inspection_task` without calling `_ensure_inspection_schema()` first
- If the table does not yet exist (first API call after deployment), pyodbc raises `ProgrammingError: Invalid object name 'tool_io_inspection_task'`
- The route catches this as a generic `Exception` and returns 500

**Bug 2 — `reschedule_task()` may fail even with schema init**
- `reschedule_task()` calls `_ensure_inspection_schema()` which raises `RuntimeError` on failure → 500
- Additionally, `_task_repo.get_task()` uses `SELECT *` and returns `rows[0] if rows else {}`
- If the table exists but the query fails for any other reason (e.g., connection issue), the exception propagates as 500

### Required Fixes

**Fix 1**: In `backend/services/inspection_stats_service.py`, add `_ensure_inspection_schema()` call at the beginning of `get_summary()`:

```python
def get_summary(current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from backend.services.inspection_task_service import _ensure_inspection_schema
    _ensure_inspection_schema()  # ← ADD THIS LINE
    # ... rest of function unchanged
```

**Fix 2**: In `backend/services/inspection_task_service.py`, wrap `reschedule_task()`'s core logic in proper error handling to distinguish 400 (business logic error) from 500 (system error):

```python
def reschedule_task(self, task_no: str, new_deadline: str, current_user: Optional[Dict]) -> Dict:
    try:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        current_status = str(task.get("task_status") or "").strip()
        if current_status not in {"pending"}:
            return {"success": False, "error": f"cannot reschedule task in status '{current_status}', only pending tasks can be rescheduled"}
        updated = self._update_task(
            task_no,
            {
                "deadline": new_deadline,
                "updated_by": _user_name(current_user),
            },
        )
        return {"success": True, "data": updated}
    except RuntimeError as exc:
        # Schema init failed — this is a system error, not a business logic error
        raise  # Let route return 500
    except ValueError as exc:
        # Task not found or business rule violation
        raise
    except Exception as exc:
        # Unexpected system error
        raise
```

**Fix 3**: The route already handles exceptions correctly — it returns 500 for any unhandled exception. Ensure no `except` clause swallows exceptions silently.

---

## Constraints

1. Do NOT modify the `InspectionTaskRepository.get_task()` method signature
2. Do NOT change the API response contract (200/400/404/500 status codes remain the same)
3. Do NOT add logging statements — only fix the schema init issue
4. Preserve all existing error handling in `inspection_routes.py`
5. UTF-8 encoding for all modified files

---

## Completion Criteria

- [ ] `get_summary()` calls `_ensure_inspection_schema()` before any database query
- [ ] `reschedule_task()` propagates `RuntimeError` (from failed schema init) as 500
- [ ] `reschedule_task()` propagates `ValueError` (task not found) as 400
- [ ] No changes to API contract or route handler logic
- [ ] Backend syntax check passes: `python -m py_compile backend/services/inspection_stats_service.py backend/services/inspection_task_service.py`
- [ ] Frontend syntax check passes: `cd frontend && npm run build` (if any frontend changes needed)

---

## 8D Problem Solving

### D1 - 团队分工
- **Reviewer**: Claude Code (self-review)
- **Coder**: Claude Code
- **Architect**: Claude Code

### D2 - 问题描述 (5W2H)

| 要素 | 内容 |
|------|------|
| What | Inspection Dashboard 和 Calendar 页面调用 API 返回 HTTP 500 |
| Where | `GET /api/inspection/stats/summary` 和 `PUT /api/inspection/tasks/{id}/reschedule` |
| When | 2026-04-02，用户打开 InspectionDashboard 和 InspectionCalendar 页面时 |
| Who | 所有使用 Inspection 模块的用户（班组长、保管员） |
| Why | `get_summary()` 直接查询数据库，未调用 schema 初始化确保表存在 |
| How | 浏览器发送 GET/PUT 请求，后端 pyodbc 抛出 Invalid object name 异常 |
| How Many | 2 个 API 端点受影响 |

### D3 - 临时遏制措施 (Containment)
**→ REVIEWER 评分审核占位符（需全部维度达标）←**

### D4 - 根因分析 (5 Whys)

#### 直接原因
`get_summary()` 函数在查询 `tool_io_inspection_task` 表之前，未调用 `_ensure_inspection_schema()` 确保表已创建。数据库首次访问时表不存在，pyodbc 抛出 `ProgrammingError`，被 Flask 路由层作为 `Exception` 捕获并返回 500。

#### 深层原因
`get_summary()` 是新加入的统计接口，其实现参考了其他 service（如 `InspectionTaskService`）的模式，但没有注意到 `_ensure_inspection_schema()` 是所有 inspection service 方法的前置要求。

#### 全部问题点
1. `inspection_stats_service.py` 的 `get_summary()` 缺少 schema init 调用
2. `reschedule_task()` 虽然调用了 `_ensure_inspection_schema()`，但如果 schema 创建失败（RuntimeError），异常直接冒泡到路由层返回 500，无降级处理

### D5 - 永久对策 + 防退化宣誓
**→ REVIEWER 评分审核占位符（需全部维度达标）←**

### D6 - 实施验证 (Implementation)
**→ REVIEWER 评分审核占位符（需全部维度达标）←**

### D7 - 预防复发

#### 短期（立即生效）
- 在 `get_summary()` 开头添加 `_ensure_inspection_schema()` 调用

#### 长期（机制保证）
- 在 `inspection_stats_service.py` 所有查询方法中添加 schema init
- 考虑在 `DatabaseManager` 层面统一处理表不存在的情况（超出本次修复范围）

### D8 - 归档复盘

#### 经验教训
新 inspection service 方法必须遵循已有的 `_ensure_inspection_schema()` 前置模式

#### 后续行动
- [x] 修复 `get_summary()` schema init
- [ ] 检查 `inspection_stats_service.py` 其他方法是否有同样问题
