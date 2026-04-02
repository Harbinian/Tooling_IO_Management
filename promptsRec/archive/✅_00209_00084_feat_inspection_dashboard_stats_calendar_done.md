# 00084 - 工装定检任务管理前端增强 - 看板/统计/日历

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 前端增强（第3部分）
Goal: 实现工装定检任务管理的三个前端增强功能：状态看板、统计面板、日历视图
Dependencies: 00083 (inspection frontend core must complete first)
Execution: RUNPROMPT

---

## Context

本提示词在工装定检任务管理组件（00080/00081/00082）基础上，实现配套的前端增强功能：

1. **工装定检状态看板** - 全局视图，四宫格统计 + 表格 + 筛选 + 导出
2. **定检任务统计面板** - 图表统计，任务分布 + 逾期率 + 周期对比
3. **定检日历视图** - 可视化，月/周切换 + 拖拽调整计划时间

**目标用户**：全员可用（PLANNER/KEEPER/TEAM_LEADER/ADMIN），数据范围按 org_id 和角色权限过滤

**技术选型**：
- 图表库：ECharts
- 日历组件：FullCalendar（Vue 3 版本）
- 拖拽：VueDraggable

---

## Required References

| 文件 | 用途 |
|------|------|
| `frontend/src/api/inspection.js` | 定检 API（来自 00082） |
| `frontend/src/pages/dashboard/DashboardOverview.vue` | 看板布局模式 |
| `frontend/src/pages/tool-io/OrderList.vue` | 表格筛选模式 |
| `.claude/rules/04_frontend.md` | 前端开发规范 |
| `backend/routes/inspection_routes.py` | 现有 API 端点（来自 00081） |

---

## Core Task

实现工装定检任务管理前端增强功能的三个页面组件。

---

## Required Work

### 1. 后端 API 扩展（如需要）

在 `backend/routes/inspection_routes.py` 中新增统计相关端点（由 Codex 执行，但 Gemini 需在提示词中说明）：

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/inspection/stats/summary` | 四宫格统计（待检/进行中/已逾期/已完成数量） |
| GET | `/api/inspection/stats/task-distribution` | 任务状态分布（各状态数量） |
| GET | `/api/inspection/stats/overdue-rate` | 逾期率统计（逾期任务数/总任务数、平均处理时长） |
| GET | `/api/inspection/stats/monthly-comparison` | 月度对比（本月 vs 上月任务数量和逾期率） |
| GET | `/api/inspection/plans/calendar` | 日历视图数据（指定月份/周的计划任务列表） |
| PUT | `/api/inspection/tasks/{task_no}/reschedule` | 拖拽调整任务时间（更新 deadline） |

### 2. 前端 API 模块扩展 - `frontend/src/api/inspection.js`

追加以下方法：

```javascript
// 统计 API
export async function getStatsSummary(params)  // GET /api/inspection/stats/summary
export async function getTaskDistribution(params)  // GET /api/inspection/stats/task-distribution
export async function getOverdueRate(params)  // GET /api/inspection/stats/overdue-rate
export async function getMonthlyComparison(params)  // GET /api/inspection/stats/monthly-comparison

// 日历 API
export async function getCalendarData(params)  // GET /api/inspection/plans/calendar
export async function rescheduleTask(taskNo, payload)  // PUT /api/inspection/tasks/{task_no}/reschedule

// 导出 API
export async function exportInspectionStatus(params)  // GET /api/inspection/status/export (Excel)
```

### 3. 页面组件 - `frontend/src/pages/inspection/`

**`InspectionDashboard.vue`** - 工装定检状态看板：

```
[路由] /inspection/dashboard
[布局]
├── 四宫格统计卡片（Row + 4 Col）
│   ├── 待检数量（pending 状态工装）
│   ├── 进行中数量（in_progress 状态任务）
│   ├── 已逾期数量（deadline 过期且未 closed）
│   └── 已完成数量（closed 状态任务）
├── 工具栏（筛选条件）
│   ├── 状态选择器（normal/overdue/pending/all）
│   ├── 日期范围选择器（到期时间筛选）
│   └── 导出按钮
└── 数据表格
    ├── 列：序列号、工装名称、图号、最近定检日期、下次定检日期、定检周期、状态
    ├── 分页组件
    └── 状态标签（normal=绿色，overdue=红色，pending=黄色）
```

**`InspectionStats.vue`** - 定检任务统计面板：

```
[路由] /inspection/stats
[布局]
├── 时间范围选择器
│   └── 默认最近30天，支持自定义日期范围
├── 统计卡片 Row
│   ├── 任务总数
│   ├── 逾期率（百分比）
│   ├── 平均处理时长（小时）
│   └── 本月完成数 vs 上月完成数
├── 图表区
│   ├── 左侧：柱状图 - 任务状态分布（pending/received/in_progress/report_submitted/accepted/closed）
│   └── 右侧：折线图 - 逾期趋势（最近6个月）
└── 详情表格
    └── 各班组长任务完成率排名
```

**`InspectionCalendar.vue`** - 定检日历视图：

```
[路由] /inspection/calendar
[布局]
├── 视图切换 Tabs
│   └── 月视图 / 周视图
├── 日历组件（FullCalendar）
│   ├── 每月/周第一天显示任务数量
│   ├── 点击日期弹出任务卡片 Popover
│   └── 任务卡片支持拖拽（仅 PLANNER 角色）
├── 任务卡片 Popover
│   ├── 显示：任务号、工装名称、状态、截止时间
│   └── 操作：查看详情（跳转 TaskDetail）
└── 日历 Legend（颜色说明）
    └── pending=灰，in_progress=蓝，report_submitted=橙，overdue=红，closed=绿
```

### 4. 路由注册 - `frontend/src/router/index.js`

在 MainLayout 的 children 中添加：

```javascript
{
  path: 'inspection/dashboard',
  name: 'inspection-dashboard',
  component: () => import('@/pages/inspection/InspectionDashboard.vue'),
  meta: { title: '定检看板', permission: 'inspection:list' }
},
{
  path: 'inspection/stats',
  name: 'inspection-stats',
  component: () => import('@/pages/inspection/InspectionStats.vue'),
  meta: { title: '定检统计', permission: 'inspection:list' }
},
{
  path: 'inspection/calendar',
  name: 'inspection-calendar',
  component: () => import('@/pages/inspection/InspectionCalendar.vue'),
  meta: { title: '定检日历', permission: 'inspection:list' }
},
```

### 5. 主导航入口更新 - `frontend/src/layouts/MainLayout.vue`

在侧边栏菜单中，在定检任务管理入口组下新增：

```
定检看板（InspectionDashboard）
定检统计（InspectionStats）
定检日历（InspectionCalendar）
```

---

## Constraints

1. **CSS 变量**：严禁硬编码颜色，必须使用 CSS 变量
2. **ECharts 主题**：使用 Element Plus 配套的暗色/亮色主题，与系统主题同步
3. **FullCalendar 配置**：语言设置为中文，weekNumbers 显示
4. **拖拽防抖**：拖拽操作后 300ms 防抖再调用 API
5. **数据权限**：所有 API 调用必须带上 org_id 过滤参数（由前端从 session 获取）
6. **导出限制**：Excel 导出限制 10000 条，超出提示用户
7. **图表响应式**：ECharts 图表支持窗口 resize 自动调整
8. **无新后端依赖**：优先复用 00081/00082 的已有 API，新建 API 需在完成标准中说明

---

## Completion Criteria

1. [ ] `frontend/src/api/inspection.js` 已追加统计和日历 API 方法
2. [ ] `InspectionDashboard.vue` 已实现四宫格 + 表格 + 筛选 + 导出功能
3. [ ] `InspectionStats.vue` 已实现图表（柱状图 + 折线图）+ 时间范围筛选
4. [ ] `InspectionCalendar.vue` 已实现月/周切换 + 任务卡片 + 拖拽调整
5. [ ] 路由已正确注册
6. [ ] 主导航已添加三个入口
7. [ ] 前端构建 `cd frontend && npm run build` 无编译错误
8. [ ] 所有页面使用 CSS 变量，无硬编码颜色
9. [ ] 拖拽调整后任务 deadline 同步更新到后端
10. [ ] 新建的后端统计 API（如有）已注册并通过语法检查
