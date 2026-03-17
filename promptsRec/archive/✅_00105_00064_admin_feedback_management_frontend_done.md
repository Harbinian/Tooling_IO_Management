Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 064
Goal: Implement admin feedback management frontend page
Dependencies: 063
Execution: RUNPROMPT

---

## Context / 上下文

后端已完成管理员反馈管理 API（提示词 063）。现在需要实现管理员前端的独立反馈管理页面。

需求：
1. 独立的反馈管理页面（不在 SettingsPage 内）
2. 管理员可查看所有用户反馈列表
3. 管理员可更新反馈状态
4. 管理员可添加回复

## Required References / 必需参考

- `frontend/src/api/feedback.js` - 前端 API 封装（需新增管理员 API 函数）
- `frontend/src/pages/admin/UserAdminPage.vue` - 参考模板
- `frontend/src/pages/settings/SettingsPage.vue` - 参考现有反馈 UI 样式
- `frontend/src/router/index.js` - 路由配置
- `frontend/src/layouts/MainLayout.vue` - 导航菜单
- `docs/PROMPT_TASK_CONVENTION.md` - UI 一致性要求
- `.claude/rules/00_global.md` - 确认对话框规范
- `.claude/rules/30_gemini_frontend.md` - 前端设计规范

## Core Task / 核心任务

创建独立的反馈管理页面，管理员可以在其中查看所有用户反馈、处理状态更新和添加回复。

## Required Work / 必需工作

### 1. API 层 (frontend/src/api/feedback.js)

新增以下函数：

```javascript
/**
 * 获取所有反馈（管理员用）
 * @param {Object} params - { status, category, keyword, limit, offset }
 * @returns {Object} { success, data: [...], total }
 */
export async function getAllFeedbackAdmin(params = {}) { ... }

/**
 * 更新反馈状态
 * @param {number} id - 反馈ID
 * @param {string} status - 新状态
 * @returns {Object} { success }
 */
export async function updateFeedbackStatus(id, status) { ... }

/**
 * 添加回复
 * @param {number} feedbackId - 反馈ID
 * @param {string} content - 回复内容
 * @returns {Object} { success, data: { reply } }
 */
export async function addFeedbackReply(feedbackId, content) { ... }

/**
 * 获取回复列表
 * @param {number} feedbackId - 反馈ID
 * @returns {Array} 回复列表
 */
export async function getFeedbackReplies(feedbackId) { ... }
```

### 2. 页面 (frontend/src/pages/admin/FeedbackAdminPage.vue)

创建独立的反馈管理页面，结构如下：

```
+--------------------------------------------------+
|  反馈管理                                         |
|  -------------------------------------------      |
|  [状态▼] [分类▼] [关键词搜索...] [查询]           |
|  -------------------------------------------      |
|  | 提交者 | 分类 | 主题 | 状态 | 时间 | 操作 |     |
|  |--------|------|------|------|------|------|     |
|  | 张三   | Bug  | ...  | 待处理| ...  | [处理] |    |
|  | 李四   | 建议 | ...  | 已查看| ...  | [查看] |    |
|  -------------------------------------------      |
|                                                   |
|  [反馈详情抽屉 / FeedbackDetailDrawer]            |
|  - 反馈内容（主题、详情、提交者、时间）            |
|  - 状态标签（待处理/已查看/已解决）               |
|  - 回复历史列表                                   |
|  - 添加回复表单 + 状态变更                        |
+--------------------------------------------------+
```

**组件结构**：
- `<FeedbackAdminPage>` - 主页面
- `<FeedbackFilterBar>` - 过滤工具栏
- `<FeedbackTable>` - 反馈列表
- `<FeedbackDetailDrawer>` - 详情抽屉

**过滤器**：
- 状态筛选：全部/待处理/已查看/已解决
- 分类筛选：全部/Bug报告/功能建议/用户体验/其他
- 关键词搜索：匹配主题或内容

**详情抽屉功能**：
- 显示完整反馈内容
- 显示状态（带颜色标签）
- 回复历史列表（显示回复者、时间、内容）
- 添加回复表单（Textarea + 提交按钮）
- 状态变更下拉选择

### 3. 路由配置

在 `frontend/src/router/index.js` 添加：
```javascript
{
  path: 'admin/feedback',
  name: 'admin-feedback',
  component: () => import('@/pages/admin/FeedbackAdminPage.vue'),
  meta: { title: '反馈管理', permission: 'admin:user_manage' }
}
```

### 4. 导航菜单

在 `MainLayout.vue` 管理员导航菜单添加"反馈管理"入口，仅对拥有 `admin:user_manage` 权限的用户可见。

## Constraints / 约束条件

- UI 必须与项目设计规范一致（深色主题、Element Plus）
- 分类标签颜色：bug=rose-500, feature=emerald-500, ux=amber-500, other=muted
- 状态标签颜色：pending=amber-500, reviewed=blue-500, resolved=emerald-500
- 严禁使用硬编码颜色，必须使用 CSS 变量
- 确认对话框必须使用 ElMessageBox.confirm
- 不得破坏现有功能（SettingsPage.vue 的反馈标签页仍正常工作）

## Completion Criteria / 完成标准

1. 管理员登录后可访问 `/admin/feedback` 页面
2. 页面显示所有用户提交的反馈列表
3. 过滤器可按状态/分类/关键词筛选
4. 点击"处理"按钮打开详情抽屉
5. 详情抽屉显示反馈内容和回复历史
6. 管理员可添加回复并提交
7. 管理员可变更反馈状态
8. 非 admin 用户访问 `/admin/feedback` 被拒绝
9. 前端构建通过：`cd frontend && npm run build`
