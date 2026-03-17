# 00060 工装搜索有效性标注功能 - 后端实现

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00060
Goal: 扩展工装搜索API，标注异常状态工装（返修/封存/定检超期等）
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
保管员批准申请的标准需要班组长在选择工装时就知晓。班组长需要能看到工装的状态（返修/封存/定检超期/无合格证等），以便判断是否应该申请。当前工装搜索没有标注这些状态。

### 目标用户
- 班组长 (Team Leader): 搜索工装时看到异常状态
- 保管员 (Keeper): 审核时参考

### 核心痛点
班组长搜索工装时，无法知道哪些工装是异常状态（返修中、封存、定检超期等），只能尝试选择后发现不可选。

### 业务目标
1. 工装搜索结果标注 `disabled` 和 `disabled_reason`
2. 异常工装显示但不可选择
3. 鼠标悬停显示禁用原因

---

## Required References / 必需参考

- backend/database/repositories/tool_repository.py - 工装仓库
- backend/database/core/database_manager.py - 数据库管理
- backend/database/schema/column_names.py - 中文字段名常量
- backend/routes/tool_routes.py - 工装路由

---

## Core Task / 核心任务

### 1. 字段来源分析

工装有效性判断基于 `工装身份卡_主表`：

| 状态判断 | 字段 | 判断逻辑 |
|---------|------|---------|
| 有效工装 | `序列号` IS NOT NULL | 工装存在 = 有合格证 |
| 定检超期 | `定检有效截止` | `定检有效截止` < 当前日期 |
| 定检中 | `定检派工状态` | 值 = "定检中" |
| 返修 | `应用历史` | 包含"返修"字样 |
| 封存 | `应用历史` | 包含"封存"字样 |

### 2. API响应扩展

扩展 `GET /api/tools/search` 响应：

```json
{
    "success": true,
    "data": [
        {
            "tool_code": "T001",
            "tool_name": "扳手",
            "spec": "规格A",
            "current_location_text": "仓库A-1",
            "status_text": "在库",
            "disabled": false,
            "disabled_reason": null
        },
        {
            "tool_code": "T002",
            "tool_name": "螺丝刀",
            "spec": "规格B",
            "current_location_text": "维修区",
            "status_text": "返修中",
            "disabled": true,
            "disabled_reason": "工装处于返修状态，不可使用"
        },
        {
            "tool_code": "T003",
            "tool_name": "钻头",
            "spec": "规格C",
            "current_location_text": "仓库B-2",
            "status_text": "定检超期",
            "disabled": true,
            "disabled_reason": "定检超期，工装不具备使用条件"
        }
    ]
}
```

### 3. disabled_reason 枚举值

| 值 | 说明 |
|----|------|
| `null` | 可用 |
| `"工装处于返修状态，不可使用"` | 返修中 |
| `"工装处于封存状态，不可使用"` | 封存 |
| `"定检超期，工装不具备使用条件"` | 定检超期 |
| `"工装正在定检中，不可使用"` | 定检中 |
| `"工装无合格证，不具备验收条件"` | 无合格证（序列号为null） |

### 4. 判断优先级

1. 序列号为 NULL → 无合格证
2. 定检有效截止 < 当前日期 → 定检超期
3. 定检派工状态 = "定检中" → 定检中
4. 应用历史包含"返修" → 返修中
5. 应用历史包含"封存" → 封存中
6. 否则 → 正常

---

## Required Work / 必需工作

1. **Repository层**
   - 扩展 `tool_repository.py` 的 `search_tools()` 方法
   - 添加 disabled 字段计算逻辑

2. **Service层**
   - 扩展 `tool_service.py` 处理字段映射

3. **Route层**
   - 确保 `GET /api/tools/search` 返回新字段

4. **字段名规范**
   - 所有 SQL 中的中文字段名必须使用 `column_names.py` 中的常量

5. **文档同步**
   - 更新 `docs/API_SPEC.md` 添加新响应字段说明

---

## Constraints / 约束条件

1. **向后兼容**: `disabled` 字段必须添加，但现有调用方不受影响
2. **判断准确性**: 严格按照判断优先级实现
3. **字段名规范**: 所有 SQL 中的中文字段名必须使用常量
4. **禁止占位符**: 所有代码必须完整可执行

---

## Completion Criteria / 完成标准

1. ✅ `GET /api/tools/search` 返回 `disabled` 和 `disabled_reason` 字段
2. ✅ 所有异常状态正确判断并返回对应 `disabled_reason`
3. ✅ 正常工装返回 `disabled: false`
4. ✅ 后端语法检查通过: `python -m py_compile <相关文件>`
5. ✅ 更新 `docs/API_SPEC.md` 添加新字段说明
