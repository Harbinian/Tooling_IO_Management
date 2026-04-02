# 00086 - Feature Development

## Header

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P1
Stage: 00086
Goal: Implement POST /api/inspection/tasks/{task_no}/reschedule API
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 `InspectionCalendar.vue` 调用 `POST /api/inspection/tasks/IT-20260410-002/reschedule` 更新检查任务时间，但后端该路由不存在，导致 404 错误。

**错误日志:**
```
InspectionCalendar.vue:211 更新计划时间失败: AxiosError: Request failed with status code 404
```

---

## Required References / 必需参考

- 后端路由文件: `backend/routes/inspection_routes.py`
- 服务实现: `backend/services/inspection_task_service.py`
- Repository: `backend/database/repositories/inspection_task_repository.py`
- 前端 API: `frontend/src/api/inspection.js::rescheduleTask`
- 前端组件: `frontend/src/pages/inspection/InspectionCalendar.vue`

---

## Constraints / 约束条件

1. **禁止修改外部系统表** `Tooling_ID_Main` 的结构
2. **使用字段名常量**: 所有 SQL 中文字段名必须通过 `backend/database/schema/column_names.py` 访问
3. **遵循现有架构**: 使用检查模块现有的 repository 和 service 层
4. **RBAC 权限**: 新路由需要 `@require_permission("inspection:execute")`
5. **UTF-8 编码**: 所有文件操作使用 `encoding='utf-8'`

---

## Phase 1: PRD - 业务需求分析

### 业务场景
用户需要在日历界面上拖拽或手动调整检查任务的计划时间，并保存到系统。

### 目标用户
- 班组长 (team_leader)
- 保管员 (keeper)
- 管理员 (admin)

### 核心痛点
前端 `InspectionCalendar.vue` 需要更新任务计划时间，但后端 API 未实现。

### 业务目标
实现 `POST /api/inspection/tasks/<task_no>/reschedule` 更新任务的 `plan_date` 或类似字段。

---

## Phase 2: Data - 数据流转审视

### 数据来源
- `tool_io_inspection_task` 表 - 检查任务

### 主键校验
- `task_no` - 检查任务编号 (如 `IT-20260410-002`)

### 生命周期防御
- 只能对"待执行"状态的任务进行重新计划
- 已完成/已取消的任务不能重新计划

---

## Phase 3: Architecture - 架构设计

### 交互链路
```
前端 InspectionCalendar
  → POST /api/inspection/tasks/{task_no}/reschedule
  → inspection_routes.api_inspection_task_reschedule
  → inspection_task_service.reschedule_task()
  → inspection_task_repository
  → 数据库
```

### 风险识别
1. **状态机风险**: 只能对特定状态的任务进行 reschedule
2. **权限风险**: 需确认用户有权限修改该任务

### 熔断策略
- 状态不允许时返回 400 并说明原因
- 数据库错误时返回 500

---

## Phase 4: Execution - 精确执行

### 4.1 后端核心数据处理逻辑

1. **在 `backend/services/inspection_task_service.py` 添加方法**:
   - `reschedule_task(task_no, new_plan_date, current_user)` - 重新计划任务
   - 检查任务状态必须是"待执行"才能修改

2. **在 `backend/routes/inspection_routes.py` 添加路由**:
   ```python
   @inspection_bp.route("/api/inspection/tasks/<task_no>/reschedule", methods=["POST"])
   @require_permission("inspection:execute")
   def api_inspection_task_reschedule(task_no):
       try:
           from backend.services.inspection_task_service import reschedule_task
           payload = get_json_dict(required=True)
           new_plan_date = payload.get("plan_date")
           result = reschedule_task(task_no, new_plan_date, current_user=get_authenticated_user())
           return jsonify(result) if result.get("success") else (jsonify(result), 400)
       except Exception as exc:
           logger.error("failed to reschedule inspection task %s: %s", task_no, exc)
           return jsonify({"success": False, "error": str(exc)}), 500
   ```

3. **Repository 层**: 如需要，添加 `update_task_plan_date` 方法

### 4.2 前端确认

- `frontend/src/api/inspection.js` - 确认 `rescheduleTask` 函数存在
- `frontend/src/pages/inspection/InspectionCalendar.vue` - 确认调用方式

### 4.3 Headless TDD

不适用。

### 4.4 E2E 验证

**→ TESTER E2E 验证占位符 ←**

---

## Completion Criteria / 完成标准

- [ ] `POST /api/inspection/tasks/{task_no}/reschedule` 返回 200 和更新结果
- [ ] 只能对"待执行"状态的任务进行重新计划，其他状态返回 400
- [ ] RBAC 权限正确 - 无权限用户返回 403
- [ ] 前端 `InspectionCalendar.vue` 能正常更新任务时间
- [ ] `python -m py_compile` 语法检查通过
