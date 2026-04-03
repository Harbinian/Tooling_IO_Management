# 00088 - 全面更新 DEBUG_IDS 和修复遗漏的 v-debug-id

## Context / 上下文

管理员 debug 徽章功能未完整覆盖所有页面。目前发现：

1. **DEBUG_IDS 缺失**：inspection、feedback、pre_transport 等新页面完全没有 DEBUG_IDS 定义
2. **Vue 文件缺失 v-debug-id**：OrderDetail.vue 的 `删除订单` 和 `上报异常` 按钮没有徽章

---

## Required References / 必需参考

- `frontend/src/debug/debugIds.js` - 当前 DEBUG_IDS 定义
- `frontend/src/directives/vDebugId.js` - debug 徽章指令实现
- `frontend/src/pages/tool-io/OrderDetail.vue` - 缺少 v-debug-id 的按钮
- `frontend/src/pages/tool-io/PreTransportList.vue` - 新页面无 debug 支持
- `frontend/src/pages/admin/FeedbackAdminPage.vue` - 新页面无 debug 支持
- `frontend/src/pages/inspection/*.vue` - inspection 页面群
- `.claude/rules/04_frontend.md` - 前端开发规范

---

## Core Task / 核心任务

### Part A: 在 debugIds.js 添加缺失的命名空间

#### 1. PRE_TRANSPORT (PT) - 运输前清单页面
```javascript
PRE_TRANSPORT: {
  PAGE_HEADER: 'PT-HEADER-001',
  REFRESH_BTN: 'PT-BTN-001',
  FILTER_SECTION: 'PT-SECTION-001',
  STATUS_FILTER: 'PT-FILTER-001',
  ORDER_TABLE: 'PT-TABLE-001',
  ORDER_CARD: 'PT-CARD-001',
  DETAIL_DRAWER: 'PT-PANEL-001'
}
```

#### 2. FEEDBACK (F) - 反馈管理页面
```javascript
FEEDBACK: {
  PAGE_HEADER: 'F-HEADER-001',
  FEEDBACK_LIST: 'F-LIST-001',
  REFRESH_BTN: 'F-BTN-001',
  FILTER_SECTION: 'F-SECTION-001',
  STATUS_FILTER: 'F-FILTER-001',
  QUERY_BTN: 'F-BTN-002'
}
```

#### 3. INSPECTION (I) - 巡检模块（复用 I 前缀避免冲突）
```javascript
INSPECTION: {
  DASHBOARD: {
    PAGE_HEADER: 'I-DASH-001',
    STATS_CARD: 'I-DASH-CARD-001',
    CALENDAR_PANEL: 'I-DASH-PANEL-001',
    RECENT_TASKS_TABLE: 'I-DASH-TABLE-001'
  },
  CALENDAR: {
    PAGE_HEADER: 'I-CAL-001',
    CALENDAR_GRID: 'I-CAL-GRID-001',
    DATE_CELL: 'I-CAL-CELL-001'
  },
  STATS: {
    PAGE_HEADER: 'I-STAT-001',
    METRIC_CARD: 'I-STAT-CARD-001',
    CHART_PANEL: 'I-STAT-PANEL-001'
  },
  STATUS: {
    PAGE_HEADER: 'I-STAT-001',
    STATUS_TAG: 'I-STAT-TAG-001'
  },
  TASK_LIST: {
    PAGE_HEADER: 'I-TASK-001',
    FILTER_SECTION: 'I-TASK-SECTION-001',
    TASK_TABLE: 'I-TASK-TABLE-001',
    REFRESH_BTN: 'I-TASK-BTN-001',
    CREATE_BTN: 'I-TASK-BTN-002'
  },
  TASK_DETAIL: {
    PAGE_HEADER: 'I-TASKD-001',
    INFO_PANEL: 'I-TASKD-PANEL-001',
    RECORD_LIST: 'I-TASKD-LIST-001',
    SUBMIT_BTN: 'I-TASKD-BTN-001',
    BACK_BTN: 'I-TASKD-BTN-002'
  },
  PLAN_LIST: {
    PAGE_HEADER: 'I-PLAN-001',
    PLAN_TABLE: 'I-PLAN-TABLE-001',
    CREATE_BTN: 'I-PLAN-BTN-001',
    REFRESH_BTN: 'I-PLAN-BTN-002'
  },
  PLAN_CREATE: {
    PAGE_HEADER: 'I-PLAN-C-001',
    FORM: 'I-PLAN-C-FORM-001',
    SUBMIT_BTN: 'I-PLAN-C-BTN-001',
    CANCEL_BTN: 'I-PLAN-C-BTN-002'
  },
  PLAN_DETAIL: {
    PAGE_HEADER: 'I-PLAN-D-001',
    INFO_PANEL: 'I-PLAN-D-PANEL-001',
    TOOL_LIST: 'I-PLAN-D-LIST-001',
    BACK_BTN: 'I-PLAN-D-BTN-001'
  },
  REPORT_SUBMIT: {
    PAGE_HEADER: 'I-REPORT-001',
    FORM: 'I-REPORT-FORM-001',
    SUBMIT_BTN: 'I-REPORT-BTN-001'
  }
}
```

#### 4. ORDER_DETAIL 补充
在 ORDER_DETAIL 部分添加：
```javascript
REPORT_ISSUE_BTN: 'OD-BTN-013'
```

### Part B: 在 Vue 文件添加缺失的 v-debug-id

#### 1. OrderDetail.vue
- 在 `删除订单` Button 添加 `v-debug-id="DEBUG_IDS.ORDER_DETAIL.DELETE_BTN"`
- 在 `上报异常` Button 添加 `v-debug-id="DEBUG_IDS.ORDER_DETAIL.REPORT_ISSUE_BTN"`

#### 2. PreTransportList.vue
- 导入 DEBUG_IDS: `import { DEBUG_IDS } from '@/debug/debugIds'`
- 在主要元素添加 v-debug-id（参考 debugIds.js PT-* 定义）

#### 3. FeedbackAdminPage.vue
- 已有 DEBUG_IDS 导入，确认是否需要添加 v-debug-id（已有 USER_LIST_CARD 等）

#### 4. Inspection 页面
- 在每个 inspection Vue 文件导入 DEBUG_IDS
- 在主要元素添加 v-debug-id（参考 debugIds.js I-* 定义）

---

## Required Work / 必需工作

1. **更新 debugIds.js**：
   - 添加 PRE_TRANSPORT (PT) 命名空间
   - 添加 FEEDBACK (F) 命名空间
   - 添加 INSPECTION (I) 命名空间（包含子模块）
   - 添加 ORDER_DETAIL.REPORT_ISSUE_BTN

2. **更新 OrderDetail.vue**：
   - 删除订单按钮添加 v-debug-id
   - 上报异常按钮添加 v-debug-id

3. **更新 PreTransportList.vue**：
   - 添加 DEBUG_IDS 导入
   - 在关键元素添加 v-debug-id

4. **更新 inspection 页面**（至少核心页面）：
   - InspectionDashboard.vue
   - TaskList.vue
   - PlanList.vue

5. **验证**：确保没有语法错误

---

## Constraints / 约束条件

- 只修改指定的文件
- 新增 ID 必须符合格式 `{PAGE}-{TYPE}-{NUMBER}`
- 保持 ID 编号连续性
- UTF-8 编码
- 不破坏现有功能

---

## Completion Criteria / 完成标准

1. [ ] debugIds.js 包含所有新命名空间（PT, F, I 及其子模块）
2. [ ] OrderDetail.vue 两个按钮都有 v-debug-id
3. [ ] PreTransportList.vue 导入 DEBUG_IDS 并使用
4. [ ] 至少 3 个 inspection 页面添加了 v-debug-id
5. [ ] 无语法错误
