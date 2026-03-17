# 前端 UI 组件映射表 (FRONTEND_UI_COMPONENT_MAP)

本文件定义了从当前 **Element Plus** 组件到新 **Tailwind + shadcn/ui + Tailark Mist** 风格的映射策略。

## 1. 核心布局组件 (Layout Components)

| 当前 Element Plus 组件 | 迁移策略 / Mist 风格组件 | Tailwind 类 / 样式建议 |
|-----------------------|-------------------------|----------------------|
| `el-container` / `el-main` | `mist-layout-shell` | `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` |
| `el-header` | `mist-navbar` | `border-b border-slate-200 bg-white/80 backdrop-blur` |
| `el-aside` | `mist-sidebar` | `w-64 border-r border-slate-100 hidden md:block` |
| `el-card` (普通) | `mist-card` | `rounded-lg border border-slate-200 bg-white p-6 shadow-none` |

## 2. 状态与概览组件 (Stats & Status)

| 当前组件 | 迁移策略 | 样式建议 |
|---------|---------|---------|
| `OrderStatusTag.vue` | `mist-badge` | 极简背景，加重文字颜色。例如：`bg-slate-100 text-slate-700 font-medium` |
| (暂无) 首页统计 | `mist-stats-grid` | 采用大字号（`text-3xl font-semibold`）+ 浅灰色副标题（`text-slate-500`） |

## 3. 表格与列表组件 (Table & List)

| 当前组件 | 迁移策略 | 样式建议 |
|---------|---------|---------|
| `el-table` (订单列表) | `mist-structured-list` | 去除外边框，行间使用细线分割。悬停时背景轻微变灰（`hover:bg-slate-50`） |
| `el-pagination` | `mist-pagination-simple` | 采用“上一页/下一页”按钮，中间显示页码，极简风格 |
| `ToolSelectionTable.vue` | `mist-selection-list` | 点击行变色，使用 Checkbox 指示选中状态，保持列表轻盈感 |

## 4. 表单与交互组件 (Forms & Interaction)

| 当前组件 | 迁移策略 | 样式建议 |
|---------|---------|---------|
| `el-button` (Primary) | `mist-button-default` | `bg-slate-900 text-white hover:bg-slate-800 transition-colors` |
| `el-button` (Secondary) | `mist-button-outline` | `border border-slate-200 bg-transparent hover:bg-slate-50` |
| `el-input` / `el-select` | `mist-input-field` | `border-slate-200 focus:border-slate-400 focus:ring-0 rounded-md` |
| `ToolSearchDialog.vue` | `mist-command-palette` | 类似于全局搜索框的样式，支持键盘操作，极简设计 |

## 5. 工作流与审计组件 (Workflow & Audit)

| 当前组件 | 迁移策略 | 样式建议 |
|---------|---------|---------|
| `el-steps` | `mist-workflow-stepper` | 细线条连接圆圈，当前步骤加粗，已完成步骤显示 Checkmark |
| `LogTimeline.vue` | `mist-audit-timeline` | 侧边垂直线条，圆点指示动作，右侧显示“人 + 时间 + 动作”，极简排版 |
| `NotificationPreview.vue` | `mist-notification-card` | 采用类似 Slack/Feishu 的消息气泡或简洁的引用块样式 |

## 6. 空状态组件 (Feedback & Empty)

| 当前组件 | 迁移策略 | 样式建议 |
|---------|---------|---------|
| `el-empty` | `mist-cta-block` | 垂直居中，极简 Icon，下方配以说明文字和单一动作按钮 |
| `el-notification` | `mist-toast` | 位于屏幕角落的极简提示，无背景装饰，仅图标和文字 |

---

## 7. 映射原则 (Mapping Principles)

- **去卡片化**：如果信息层级可以通过间距区分，则不使用 `el-card`。
- **排版优先**：利用字重（`font-medium`, `font-semibold`）代替背景色来强调标题。
- **交互降噪**：减少过渡动画，保持响应速度，仅在关键交互（如按钮点击）上保留轻微反馈。
