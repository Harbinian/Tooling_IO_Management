# 00082 - 前端基础层 - 主导航结构调整 + 风格规范

Primary Executor: Gemini
Task Type: Feature Development
Priority: P0
Stage: 1 of 2（前端层，第1部分）
Goal: 实现前端主导航的两级菜单结构和风格规范基座
Dependencies: None（独立可执行，但须先于 00083/00084 执行）
Execution: RUNPROMPT

---

## Context

本提示词是**前端基础层**，为工装定检任务管理组件（00082、00083）提供：
1. **主导航结构调整**：从扁平菜单升级为两级菜单结构
2. **风格规范基座**：统一所有页面的 UI 风格

**当前状态**：
- 侧边栏菜单是扁平结构，每个菜单项都是一级入口
- 工装出入库页面：`/inventory/*`
- 定检任务管理页面：`/inspection/*`

**目标状态**：
```
工装管理系统（一级入口）
├── 出入库（二级菜单）
│   ├── 订单列表 (/inventory)
│   ├── 创建申请 (/inventory/create)
│   ├── 保管员工作台 (/inventory/keeper)
│   ├── 预知运输 (/inventory/pre-transport)
│   └── 订单详情 (/inventory/:orderNo)
└── 定检任务管理（二级菜单）
    ├── 计划列表 (/inspection/plans)
    ├── 创建计划 (/inspection/plans/create)
    ├── 计划详情 (/inspection/plans/:planNo)
    ├── 任务列表 (/inspection/tasks)
    ├── 任务详情 (/inspection/tasks/:taskNo)
    ├── 定检看板 (/inspection/dashboard)
    ├── 定检统计 (/inspection/stats)
    ├── 定检日历 (/inspection/calendar)
    └── 工装定检状态 (/inspection/status)
```

**风格规范**：
- 所有页面必须与现有工装出入库界面（OrderCreate.vue、OrderList.vue）保持一致
- 使用 Element Plus + Tailwind CSS 变量
- Card 布局、Badge 标签、Header 区域统一风格

---

## Required References

| 文件 | 用途 |
|------|------|
| `frontend/src/layouts/MainLayout.vue` | 当前侧边栏实现，需改造 |
| `frontend/src/router/index.js` | 路由配置，需添加 group meta |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 风格参考（Card 布局、Header 区域） |
| `frontend/src/pages/tool-io/OrderList.vue` | 风格参考（列表页模式） |
| `frontend/src/pages/tool-io/OrderDetail.vue` | 风格参考（详情页模式、WorkflowStepper） |
| `frontend/src/pages/settings/SettingsPage.vue` | 风格参考（设置页布局） |
| `.claude/rules/04_frontend.md` | 前端开发规范 |

---

## Core Task

改造 MainLayout.vue 实现两级菜单结构，并建立前端风格规范。

---

## Required Work

### 1. MainLayout 改造 - `frontend/src/layouts/MainLayout.vue`

**改造要点**：

将扁平的 `navigation` 数组改造为两级结构：

```javascript
// 当前：一维数组
const navigation = [
  { name: '订单列表', href: '/inventory', icon: ClipboardList, permission: 'order:list' },
  // ...
]

// 目标：两级结构
const navigation = [
  {
    group: '工装管理系统',  // 一级分组名称
    items: [
      {
        label: '出入库',    // 二级菜单名
        icon: ClipboardList,
        children: [
          { name: '订单列表', href: '/inventory', permission: 'order:list' },
          { name: '创建申请', href: '/inventory/create', permission: 'order:create' },
          { name: '保管员工作台', href: '/inventory/keeper', permission: 'order:keeper_confirm' },
          { name: '预知运输', href: '/inventory/pre-transport', permission: 'order:transport_execute' },
        ]
      },
      {
        label: '定检任务管理',    // 二级菜单名
        icon: ClipboardList,
        children: [
          { name: '计划列表', href: '/inspection/plans', permission: 'inspection:list' },
          { name: '任务列表', href: '/inspection/tasks', permission: 'inspection:list' },
          { name: '定检看板', href: '/inspection/dashboard', permission: 'inspection:list' },
          { name: '定检统计', href: '/inspection/stats', permission: 'inspection:list' },
          { name: '定检日历', href: '/inspection/calendar', permission: 'inspection:list' },
          { name: '定检状态', href: '/inspection/status', permission: 'inspection:list' },
        ]
      }
    ]
  },
  // 其他一级分组...
]
```

**UI 实现要求**：
1. 侧边栏宽度保持 72（展开）和 16（收起）
2. 一级分组标题：只显示分组名，不显示图标，不可点击
3. 二级菜单：与现有扁平菜单样式一致，支持折叠/展开
4. 展开/收起行为：
   - 展开时：显示一级分组标题 + 二级菜单列表
   - 收起时：只显示图标，二级菜单通过 hover popover 显示
5. 当前激活状态高亮：检测 route.path 是否以二级菜单的 href 开头
6. 顶部 `Tooling IO` 文字改为 `工装管理系统`（翻译后）

**权限控制**：
- 一级分组：如果该分组下所有二级菜单都无权限，则隐藏整个分组
- 二级菜单：按原有 permission 过滤

### 2. 风格规范建立 - `frontend/src/styles/inspection-theme.css`（新建）

建立统一的前端风格规范，所有定检相关页面必须遵循：

```css
/* 工装管理系统 - 前端风格规范 */

/* === Card 布局 === */
.card-header {
  @apply border-b border-border bg-muted/30 py-4;
}
.card-header-inner {
  @apply flex items-center gap-2;
}
.card-header-accent {
  @apply h-8 w-1 rounded-full bg-primary;
}
.card-title {
  @apply text-base font-bold text-foreground;
}

/* === Header 区域 === */
.page-header {
  @apply relative overflow-hidden rounded-3xl bg-primary px-8 py-12 text-primary-foreground shadow-2xl;
}
.page-header-title {
  @apply text-3xl font-bold tracking-tight md:text-4xl text-primary-foreground;
}
.page-header-desc {
  @apply mt-2 max-w-lg text-primary-foreground/80;
}
.page-header-actions {
  @apply flex items-center gap-3;
}
.page-header-blur {
  @apply absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary-foreground/10 blur-3xl;
}

/* === Badge 标签 === */
.badge-outline {
  @apply border border-primary-foreground/20 bg-primary-foreground/10 text-primary-foreground backdrop-blur-sm;
}

/* === 状态标签 === */
.status-badge {
  @apply inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold;
}
.status-pending {
  @apply bg-gray-100 text-gray-800;
}
.status-active {
  @apply bg-blue-100 text-blue-800;
}
.status-overdue {
  @apply bg-red-100 text-red-800;
}
.status-completed {
  @apply bg-green-100 text-green-800;
}
.status-warning {
  @apply bg-yellow-100 text-yellow-800;
}

/* === 按钮 === */
.btn-primary {
  @apply bg-white font-bold text-slate-900 shadow-lg hover:bg-slate-100 border-none;
}
.btn-ghost {
  @apply border border-primary-foreground/20 text-primary-foreground hover:bg-white/10;
}

/* === 表单 === */
.form-label {
  @apply text-sm font-semibold text-foreground;
}
.form-required {
  @apply text-red-500 ml-1;
}

/* === 表格 === */
.table-header {
  @apply bg-muted/50 text-muted-foreground text-xs font-bold uppercase tracking-wider;
}

/* === 空状态 === */
.empty-state {
  @apply flex flex-col items-center justify-center py-12 text-center;
}
.empty-state-icon {
  @apply h-12 w-12 text-muted-foreground/50;
}
.empty-state-title {
  @apply mt-4 text-lg font-semibold text-foreground;
}
.empty-state-desc {
  @apply mt-2 text-sm text-muted-foreground;
}
```

### 3. 路由 Group Meta - `frontend/src/router/index.js`

在路由的 meta 中添加 group 字段，用于菜单渲染：

```javascript
// 在 MainLayout children 的各路由 meta 中添加：
meta: {
  title: '订单列表',
  permission: 'order:list',
  group: 'tooling',      // 工装管理系统
  subgroup: 'io',         // 出入库
}

// 定检相关路由：
meta: {
  title: '计划列表',
  permission: 'inspection:list',
  group: 'tooling',      // 工装管理系统
  subgroup: 'inspection', // 定检任务管理
}
```

### 4. 通用工作流组件 - `frontend/src/components/inspection/WorkflowStepper.vue`（新建）

参照 `OrderDetail.vue` 中的工作流展示，建立通用的工作流步骤预览组件：

```vue
<!-- Props -->
<!-- - currentStatus: string -->
<!-- - orderType: 'outbound' | 'inbound' -->
<!-- - showHeader: boolean -->
<!-- - customLabels: object (可选) -->

<!-- 步骤 -->
出库流程: 草稿 → 已提交 → 保管员已确认 → 运输通知 → 班组长最终确认 → 已完成
入库流程: 草稿 → 已提交 → 保管员已确认 → 运输通知 → 保管员最终确认 → 已完成

<!-- 定检流程: -->
pending → received → outbound_created → outbound_completed → in_progress → report_submitted → accepted → inbound_created → inbound_completed → closed
```

---

## Constraints

1. **CSS 变量强制使用**：严禁硬编码颜色，必须使用 CSS 变量（参照 `04_frontend.md`）
2. **MainLayout 兼容现有功能**：改造后现有功能（dashboard、settings、admin）必须正常运作
3. **权限过滤正确**：二级菜单按 permission 过滤后，如果分组下无可见菜单，整个分组隐藏
4. **折叠状态保持**：侧边栏折叠/展开状态在页面切换时保持
5. **Active 状态检测**：当前路由激活高亮必须正确匹配二级菜单的 href 前缀
6. **响应式行为**：侧边栏收起时，二级菜单通过 hover popover 显示（图标 + 文字）

---

## Completion Criteria

1. [ ] MainLayout.vue 已改造为两级菜单结构，`工装管理系统` 作为一级入口
2. [ ] 出入库：`订单列表`、`创建申请`、`保管员工作台`、`预知运输` 作为二级菜单正确挂载
3. [ ] 定检任务管理：6 个定检页面（计划列表、任务列表等）作为二级菜单正确挂载
4. [ ] 侧边栏收起时，二级菜单通过 hover popover 显示
5. [ ] `frontend/src/styles/inspection-theme.css` 已创建，包含所有风格规范
6. [ ] `WorkflowStepper.vue` 组件已创建，支持出库/入库/定检三种工作流
7. [ ] 路由 meta 已添加 group/subgroup 字段
8. [ ] 权限过滤正确：一级分组根据二级菜单权限自动显示/隐藏
9. [ ] 前端构建 `cd frontend && npm run build` 无编译错误
10. [ ] 现有功能（dashboard、settings、admin）功能正常，不受改造影响
