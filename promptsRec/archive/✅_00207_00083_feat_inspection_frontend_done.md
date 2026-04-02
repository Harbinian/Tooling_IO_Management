# 00083 - 工装定检任务管理组件 - 前端核心（API + 页面 + 路由）

Primary Executor: Gemini
Task Type: Feature Development
Priority: P0
Stage: 2 of 2（前端层，第2部分）
Goal: 实现工装定检任务管理前端（API + 7个页面 + 路由注册）
Dependencies: 00081, 00082 (backend and frontend foundation must complete first)
Execution: RUNPROMPT

---

## Context

承接 Prompt 00080 和 00081 的后端实现，本阶段实现前端：
- 1 个 API 模块（`frontend/src/api/inspection.js`）
- 7 个页面组件（`frontend/src/pages/inspection/`）
- 前端路由注册

**核心 UX 决策**：
- 工装搜索支持：序列号、名称、图号、状态
- 批量选择支持
- Base64 附件上传（2MB 限制，参考 MPL 设计）
- 工作流步骤预览（状态机可视化）

---

## Required References

| 文件 | 用途 |
|------|------|
| `frontend/src/api/orders.js` | API 封装模式参考 |
| `frontend/src/api/mpl.js` | MPL API 参考（含 Base64 附件模式） |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 页面结构模式 |
| `frontend/src/pages/tool-io/OrderList.vue` | 列表页面模式 |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 详情页面模式 |
| `frontend/src/router/index.js` | 路由注册位置 |
| `frontend/src/layouts/MainLayout.vue` | 布局组件参考 |
| `.claude/rules/04_frontend.md` | 前端开发规范 |

---

## Core Task

实现工装定检任务管理前端，包含 API 模块、7 个页面组件、前端路由注册。

---

## Required Work

### 1. API 模块 - `frontend/src/api/inspection.js`

参照 `orders.js` 和 `mpl.js` 模式，创建 `inspection.js`，导出：

```javascript
// 计划 API
export async function createPlan(payload)  // POST /api/inspection/plans
export async function getPlanList(params)  // GET /api/inspection/plans
export async function getPlanDetail(planNo)  // GET /api/inspection/plans/{plan_no}
export async function updatePlan(planNo, payload)  // PUT /api/inspection/plans/{plan_no}
export async function publishPlan(planNo)  // POST /api/inspection/plans/{plan_no}/publish
export async function previewTasks(planNo)  // GET /api/inspection/plans/{plan_no}/preview-tasks

// 任务 API
export async function getTaskList(params)  // GET /api/inspection/tasks
export async function getTaskDetail(taskNo)  // GET /api/inspection/tasks/{task_no}
export async function receiveTask(taskNo)  // POST /api/inspection/tasks/{task_no}/receive
export async function startInspection(taskNo)  // POST /api/inspection/tasks/{task_no}/start-inspection
export async function submitReport(taskNo, payload)  // POST /api/inspection/tasks/{task_no}/submit-report（含附件）
export async function acceptReport(taskNo)  // POST /api/inspection/tasks/{task_no}/accept
export async function rejectReport(taskNo, reason)  // POST /api/inspection/tasks/{task_no}/reject
export async function createOutbound(taskNo)  // POST /api/inspection/tasks/{task_no}/create-outbound（跳转页面）
export async function createInbound(taskNo)  // POST /api/inspection/tasks/{task_no}/create-inbound（跳转页面）
export async function closeTask(taskNo)  // POST /api/inspection/tasks/{task_no}/close
export async function getLinkedOrders(taskNo)  // GET /api/inspection/tasks/{task_no}/linked-orders
export async function linkOrderToTask(orderNo, taskNo)  // POST /api/inspection/orders/{order_no}/link-task

// 工装定检状态 API
export async function getInspectionStatus(serialNo)  // GET /api/inspection/status/{serial_no}

// 订单推进 API
export async function advanceByOrder(orderNo)  // POST /api/inspection/advance-by-order/{order_no}
```

**Base64 附件处理**（参照 `mpl.js`）：
- 前端使用 `FileReader.readAsDataURL()` 读取文件为 Base64
- 限制单文件 2MB（2 * 1024 * 1024 bytes）
- 上传前检查文件大小，超限提示用户

### 2. 页面组件 - `frontend/src/pages/inspection/`

创建以下 7 个 Vue 组件：

**`PlanList.vue`** - 计划列表页：
- 页面标题：定检任务管理管理
- 顶部操作栏：创建计划按钮（PLANNER 角色可见）
- 列表展示：计划号、计划名称、年度/月份、状态、创建人、发布时间
- 状态标签：draft（草稿）/ published（已发布）/ closed（已关闭）
- 操作列：查看详情 / 编辑（仅草稿）/ 发布（仅草稿）/ 删除（仅草稿）
- 分页组件
- 状态筛选 tabs 或下拉框

**`PlanCreate.vue`** - 创建/编辑计划页：
- 顶部 Badge：创建定检任务管理
- 表单字段：计划名称、年度、月份、定检类型（下拉：regular/annual/special）、备注
- 底部操作栏：保存草稿 / 发布计划
- 发布前显示确认对话框，提示将生成任务

**`PlanDetail.vue`** - 计划详情页：
- 页面标题：计划详情 + 计划号
- 基本信息卡片：计划名称、年度/月份、状态、创建人、发布时间
- 关联任务列表：展示该计划下的所有任务（任务号、工装序列号、状态、执行人）
- 操作栏：发布（仅草稿）、关闭（仅已发布）

**`TaskList.vue`** - 任务列表页：
- 顶部 Badge：定检任务
- 状态筛选 tabs：全部 / pending / received / in_progress / report_submitted / accepted / closed
- 列表展示：任务号、关联计划、序列号、工装名称、状态、执行人、领取时间
- 操作列：查看详情
- 支持按任务状态筛选

**`TaskDetail.vue`** - 任务详情+操作页（核心页面）：
- 顶部 Badge：任务详情 + 任务号
- 基本信息卡片：计划号、序列号、工装名称、图号、状态、执行人、截止时间
- 工作流步骤预览（参照 OrderDetail.vue 的 WorkflowStepper）：
  - pending → received → outbound_created → outbound_completed → in_progress → report_submitted → accepted → inbound_created → inbound_completed → closed
- 当前状态高亮，已完成状态打勾
- 操作按钮区（根据当前状态显示可执行操作）：
  - `pending` → 领取任务（receiveTask）
  - `received` → 创建出库单（跳转 OrderCreate，传递 task_no）/ 开始检验（startInspection）
  - `in_progress` → 提交测量报告（submitReport，打开附件上传对话框）
  - `report_submitted` → 验收通过 / 驳回（acceptReport / rejectReport，仅 QUALITY_INSPECTOR）
  - `accepted` → 创建入库单（跳转 OrderCreate，传递 task_no）
  - `inbound_completed` → 关闭任务（closeTask，仅 KEEPER）
- 关联订单信息区：显示 linked_orders
- 测量报告区（如有）：附件预览（Base64 转图片）

**`ReportSubmit.vue`** - 测量报告提交对话框或页面：
- 检验日期选择器
- 检验结果单选：合格 / 不合格
- 测量数据文本框（JSON 或自由文本）
- 附件上传区：
  - el-upload 设置 `:auto-upload="false"`
  - FileReader.readAsDataURL() 获取 Base64
  - 2MB 大小限制校验
- 提交按钮

**`InspectionStatus.vue`** - 工装定检状态查询页：
- 页面标题：工装定检状态
- 查询表单：输入序列号，查询该工装的定检状态
- 结果展示：序列号、工装名称、最近定检日期、下次定检日期、定检周期、状态（normal/overdue/pending）
- 状态标签颜色：normal（绿色）、overdue（红色）、pending（黄色）

### 3. 路由注册 - `frontend/src/router/index.js`

在 MainLayout 的 children 中添加：

```javascript
// 定检任务管理
{
  path: 'inspection/plans',
  name: 'inspection-plans',
  component: () => import('@/pages/inspection/PlanList.vue'),
  meta: { title: '定检任务管理', permission: 'inspection:list' }
},
{
  path: 'inspection/plans/create',
  name: 'inspection-plan-create',
  component: () => import('@/pages/inspection/PlanCreate.vue'),
  meta: { title: '创建定检任务管理', permission: 'inspection:create' }
},
{
  path: 'inspection/plans/:planNo',
  name: 'inspection-plan-detail',
  component: () => import('@/pages/inspection/PlanDetail.vue'),
  props: true,
  meta: { title: '计划详情', permission: 'inspection:view' }
},
{
  path: 'inspection/tasks',
  name: 'inspection-tasks',
  component: () => import('@/pages/inspection/TaskList.vue'),
  meta: { title: '定检任务', permission: 'inspection:list' }
},
{
  path: 'inspection/tasks/:taskNo',
  name: 'inspection-task-detail',
  component: () => import('@/pages/inspection/TaskDetail.vue'),
  props: true,
  meta: { title: '任务详情', permission: 'inspection:view' }
},
{
  path: 'inspection/status',
  name: 'inspection-status',
  component: () => import('@/pages/inspection/InspectionStatus.vue'),
  meta: { title: '工装定检状态', permission: 'inspection:list' }
},
```

### 4. 主导航入口 - `frontend/src/layouts/MainLayout.vue`

在侧边栏菜单中添加定检任务管理入口（参照现有菜单结构），包含：
- 定检任务管理（PlanList）
- 定检任务（TaskList）
- 工装定检状态（InspectionStatus）

权限：`inspection:list`

---

## Constraints

1. **CSS 变量**：严禁硬编码颜色，必须使用 CSS 变量（参照 `.claude/rules/04_frontend.md`）
2. **UI 一致性**：操作按钮的确认消息格式参照 `00_core.md` 的 UI 一致性规则
3. **状态显示**：必须显示状态标签（参照 `04_frontend.md` 的状态显示要求）
4. **Base64 限制**：前端必须验证附件大小不超过 2MB
5. **批量选择**：工装搜索必须支持批量选择
6. **WorkflowStepper**：TaskDetail 必须包含工作流步骤预览
7. **RBAC 数据隔离**：列表查询必须带上当前用户的 org_id 过滤

---

## Completion Criteria

1. `frontend/src/api/inspection.js` 已创建且包含所有指定方法
2. 7 个页面组件已创建且功能完整
3. 路由已正确注册
4. 主导航已添加定检任务管理入口
5. 前端构建 `cd frontend && npm run build` 无编译错误
6. 所有页面使用 CSS 变量，无硬编码颜色
7. Base64 附件上传有 2MB 限制校验
