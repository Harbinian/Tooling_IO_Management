# 00085 - Feature Development

## Header

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P1
Stage: 00085
Goal: Implement GET /api/inspection/stats/summary API
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 `InspectionDashboard.vue` 调用 `GET /api/inspection/stats/summary` 获取检查统计数据，但后端该路由不存在，导致 404 错误。

**错误日志:**
```
InspectionDashboard.vue:216 加载统计数据失败: AxiosError: Request failed with status code 404
```

---

## Required References / 必需参考

- 后端路由文件: `backend/routes/inspection_routes.py`
- 服务实现: `backend/services/inspection_plan_service.py`
- Repository: `backend/database/repositories/inspection_plan_repository.py`
- 前端 API: `frontend/src/api/inspection.js::getStatsSummary`
- 前端组件: `frontend/src/pages/inspection/InspectionDashboard.vue`

---

## Constraints / 约束条件

1. **禁止修改外部系统表** `Tooling_ID_Main` 的结构
2. **使用字段名常量**: 所有 SQL 中文字段名必须通过 `backend/database/schema/column_names.py` 访问
3. **遵循现有架构**: 使用检查模块现有的 repository 和 service 层
4. **RBAC 权限**: 新路由需要 `@require_permission("inspection:list")`
5. **UTF-8 编码**: 所有文件操作使用 `encoding='utf-8'`

---

## Phase 1: PRD - 业务需求分析

### 业务场景
管理员或班组长需要查看检查计划的统计汇总数据，包括：待执行任务数、已完成任务数、逾期任务数等。

### 目标用户
- 管理员 (admin)
- 班组长 (team_leader)

### 核心痛点
前端 `InspectionDashboard.vue` 需要展示统计数据，但后端 API 未实现。

### 业务目标
实现 `/api/inspection/stats/summary` 返回检查统计数据，支撑仪表盘展示。

---

## Phase 2: Data - 数据流转审视

### 数据来源
- `tool_io_inspection_plan` 表 - 检查计划
- `tool_io_inspection_task` 表 - 检查任务
- `tool_io_inspection_report` 表 - 检查报告

### 主键校验
- `plan_no` - 检查计划编号 (如 `IP-20260401-001`)
- `task_no` - 检查任务编号 (如 `IT-20260410-002`)

### 生命周期防御
- 检查统计应基于当前状态实时计算，不缓存
- 考虑性能，大数据量时使用索引优化

---

## Phase 3: Architecture - 架构设计

### 交互链路
```
前端 InspectionDashboard
  → GET /api/inspection/stats/summary
  → inspection_routes.api_inspection_stats_summary
  → inspection_stats_service.get_summary()
  → inspection_plan_repository / inspection_task_repository
  → 数据库
```

### 风险识别
1. **性能风险**: 统计数据涉及多表聚合，大数据量时可能慢
2. **权限风险**: 需确认用户只能看到自己有权限访问的数据

### 熔断策略
- 统计查询超时设置合理阈值
- 失败时返回 500 并记录日志

---

## Phase 4: Execution - 精确执行

### 4.1 后端核心数据处理逻辑

1. **在 `backend/routes/inspection_routes.py` 添加路由**:
   ```python
   @inspection_bp.route("/api/inspection/stats/summary", methods=["GET"])
   @require_permission("inspection:list")
   def api_inspection_stats_summary():
       try:
           from backend.services.inspection_stats_service import get_summary
           result = get_summary(current_user=get_authenticated_user())
           return jsonify(result)
       except Exception as exc:
           logger.error("failed to get inspection stats: %s", exc)
           return jsonify({"success": False, "error": str(exc)}), 500
   ```

2. **新建 `backend/services/inspection_stats_service.py`**:
   - `get_summary(current_user)` - 获取统计汇总
   - 调用 repository 层聚合查询

3. **如需要，在 repository 层添加聚合方法**

### 4.2 前端确认

- `frontend/src/api/inspection.js` - 确认 `getStatsSummary` 函数存在

### 4.3 Headless TDD

不适用。

### 4.4 E2E 验证

**→ TESTER E2E 验证占位符 ←**

---

## Completion Criteria / 完成标准

- [ ] `/api/inspection/stats/summary` 返回 200 和统计数据
- [ ] 统计数据包含: 待执行任务数、进行中任务数、已完成任务数、逾期任务数
- [ ] RBAC 权限正确 - 无权限用户返回 403
- [ ] 前端 `InspectionDashboard.vue` 能正常加载统计数据
- [ ] `python -m py_compile` 语法检查通过
