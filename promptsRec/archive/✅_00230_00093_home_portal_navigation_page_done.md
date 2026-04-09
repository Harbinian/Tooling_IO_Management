Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00093
Goal: Create home portal navigation page at /home with role-based business domain entry cards
Dependencies: None
Execution: RUNPROMPT

---

## Phase 1: PRD - 业务需求分析

**业务场景**：用户登录系统后，需要一个清晰的门户入口来访问不同的业务域（工装出入库、定检管理、MPL管理、系统管理）。

**目标用户**：所有登录用户，根据权限显示不同的业务域入口。

**核心痛点**：当前登录后直接跳转到 Dashboard，Dashboard 主要展示数据统计，用户难以快速找到业务入口。

**业务目标**：创建一个门户式首页，作为系统的主入口，用户可以看到自己有权限访问的业务域卡片，点击后跳转到对应业务域。

---

## Phase 2: Data - 数据流转

**数据来源**：
- 用户权限：`session store` 中的 `roles` 和 `permissions`
- 业务域配置：前端静态配置（4个业务域卡片）

**数据流转**：
```
session.roles → checkPermission() → filter visible cards → render
```

**关键检查**：
- `session.hasPermission('order:list')`
- `session.hasPermission('inspection:list')`
- `session.hasPermission('mpl:write')`
- `session.hasPermission('admin:user_manage')`

---

## Phase 3: Architecture - 架构设计

**页面位置**：`frontend/src/pages/home/HomePage.vue`

**路由配置**：
- 路径：`/home`
- 需要登录权限
- 登录后默认跳转目标

**组件结构**：
```
HomePage.vue
├── PortalHeader (欢迎语 + 用户信息)
└── PortalGrid
    ├── OutboundPortalCard (工装出入库)
    ├── InspectionPortalCard (定检管理)
    ├── MplPortalCard (MPL管理)
    └── AdminPortalCard (系统管理)
```

**权限控制策略**：
- 路由守卫：未登录跳转到 `/login`
- 组件渲染：根据 `session.hasPermission()` 过滤卡片

**登录后跳转调整**：
- 修改 `LoginPage.vue` 中的 `redirectTarget` 逻辑
- 从 `route.query.redirect || '/dashboard'` 改为 `route.query.redirect || '/home'`

---

## Phase 4: Execution - 精确执行

### 4.1 创建 HomePage.vue

创建 `frontend/src/pages/home/HomePage.vue`，实现：

1. **PortalHeader**：
   - 欢迎语（动态显示用户名）
   - 当前日期时间

2. **PortalGrid**：
   - 响应式网格布局（4列 → 2列 → 1列）
   - 4个业务域卡片

3. **业务域卡片设计**：
   - 大图标（使用 Element Plus icons 或自定义 SVG）
   - 业务域名称（中文）
   - 卡片样式：大背景色、圆角、悬停效果

4. **权限控制**：
   ```javascript
   const visibleCards = computed(() => {
     return cards.filter(card => session.hasPermission(card.permission))
   })
   ```

### 4.2 路由配置

在 `frontend/src/router/index.js` 中：

1. 添加 `/home` 路由：
   ```javascript
   {
     path: 'home',
     name: 'home',
     component: () => import('@/pages/home/HomePage.vue'),
     meta: { title: '首页', permission: 'dashboard:view', group: 'personal' }
   }
   ```

2. 修改根路径重定向：
   ```javascript
   { path: '', redirect: '/home' }
   ```

### 4.3 登录跳转调整

修改 `LoginPage.vue` 中的登录成功后跳转逻辑：

```javascript
// 将默认跳转从 '/dashboard' 改为 '/home'
const redirect = route.query.redirect || '/home'
router.replace(redirect)
```

### 4.4 卡片配置

定义卡片数据：

```javascript
const cards = [
  {
    key: 'tool-io',
    title: '工装出入库',
    icon: 'Box',
    href: '/inventory',
    permission: 'order:list',
    description: '出入库订单管理'
  },
  {
    key: 'inspection',
    title: '定检管理',
    icon: 'Calendar',
    href: '/inspection/plans',
    permission: 'inspection:list',
    description: '工装定期检查任务'
  },
  {
    key: 'mpl',
    title: 'MPL管理',
    icon: 'Document',
    href: '/mpl',
    permission: 'mpl:write',
    description: '工装可拆卸件清单'
  },
  {
    key: 'admin',
    title: '系统管理',
    icon: 'Setting',
    href: '/admin/users',
    permission: 'admin:user_manage',
    description: '用户、角色、权限管理'
  }
]
```

---

## Required References

| 文件 | 用途 |
|------|------|
| `frontend/src/pages/auth/LoginPage.vue` | 登录跳转逻辑，需修改 |
| `frontend/src/router/index.js` | 路由配置，需添加 /home |
| `frontend/src/store/session.js` | session store，权限判断 |
| `frontend/src/layouts/MainLayout.vue` | 侧边栏，权限控制参考 |
| `.claude/rules/04_frontend.md` | 前端开发规范 |
| `docs/RBAC_PERMISSION_MATRIX.md` | 权限矩阵参考 |

---

## Constraints

1. 使用 CSS 变量，禁止硬编码颜色
2. 图标使用 Element Plus icons 或 SVG
3. 遵循现有代码风格和命名规范
4. 卡片悬停效果使用 CSS transition
5. 响应式布局适配不同屏幕尺寸

---

## Completion Criteria

1. [ ] `frontend/src/pages/home/HomePage.vue` 已创建
2. [ ] 路由 `/home` 已配置且需要登录权限
3. [ ] 4个业务域卡片正确渲染
4. [ ] 无权限的卡片被正确隐藏
5. [ ] 点击卡片能跳转到对应业务域
6. [ ] 登录后默认跳转到 `/home`
7. [ ] 前端构建 `cd frontend && npm run build` 无编译错误
8. [ ] 视觉风格与现有系统保持一致
