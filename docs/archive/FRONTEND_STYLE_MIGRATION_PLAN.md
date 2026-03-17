# 前端样式迁移计划 (FRONTEND_STYLE_MIGRATION_PLAN)

## 1. 设计目标 (Design Goals)

本计划旨在将工装出入库管理系统从现有的 **Element Plus** 风格迁移至基于 **Tailwind CSS + shadcn/ui + Tailark Mist** 的现代设计语言。

- **视觉提升**：采用 Mist 套件的极简主义风格，提升系统专业感。
- **操作效率**：优化信息层级，减少视觉噪音，使核心业务流程（出入库申请与确认）更直观。
- **一致性**：建立统一的组件映射和布局规范，确保所有页面遵循相同的设计逻辑。

---

## 2. 视觉系统原则 (Visual System Principles)

遵循 Tailark Mist 的核心审美：

1.  **极简视觉噪音 (Minimal Visual Noise)**：去除不必要的背景色块和重阴影，使用细线条（Thin borders）区分区域。
2.  **呼吸感布局 (Large Whitespace)**：增加元素间的间距，避免信息过度拥挤，提升阅读舒适度。
3.  **文档化排版 (Content-Focused)**：列表和详情页应像文档一样清晰、易读，而非复杂的表格堆砌。
4.  **专业色调 (Calm Palette)**：以纯白、浅灰（Slate/Gray）为基调，仅在状态标签（Status Tags）和核心动作按钮（CTA）上使用品牌色。
5.  **清晰层级 (Strong Hierarchy)**：通过字号、字重和间距而非颜色块来区分信息主次。

---

## 3. 页面重构计划 (Page-by-Page Redesign)

### 3.1 仪表盘概览 (Dashboard Overview) - 新增
- **设计思路**：模仿 `mist-stats` 和 `mist-features`。
- **核心模块**：
    - **统计块 (Stats)**：展示“今日出库”、“待保管员确认”、“运输中”、“已完成”等关键数字。
    - **功能网格 (Feature Grid)**：提供“发起出库”、“发起入库”、“库存查询”、“订单列表”的快速入口。
- **布局**：采用宽大的卡片式布局，背景极简。

### 3.2 订单管理页 (Order Management)
- **设计思路**：模仿 `Documentation-style layout`。
- **布局重构**：
    - **侧边栏筛选**：将目前的顶部筛选器移至简洁的左侧边栏（Clean Sidebar），支持分类和多选。
    - **列表展示**：订单列表不再是密集的表格，而是带有状态图标、单号、发起人和摘要的结构化行。
- **交互**：点击行展开简要详情或跳转至详情页。

### 3.3 订单详情与工作流跟踪 (Order Detail & Workflow)
- **设计思路**：模仿 `mist-steps` 和 `Changelog-style` 时间轴。
- **布局重构**：
    - **工作流可视化**：顶部使用极简线条风格的步骤条展示当前状态。
    - **双栏结构**：左侧展示工装明细列表，右侧展示审计日志（Audit Trail）和通知记录。
    - **动作区**：底部或右上角固定简洁的操作按钮区。

### 3.4 身份认证页 (Authentication)
- **设计思路**：模仿 `mist-auth`。
- **布局重构**：
    - 居中的极简表单，纯白背景，细边框输入框。
    - 仅保留 Logo、欢迎语、账号/密码输入和登录按钮。

### 3.5 空状态与错误页 (Empty & Error States)
- **设计思路**：模仿 `mist-cta`。
- **设计规则**：
    - 统一的插图风格（极简线条）。
    - 明确的解释性文字（如“暂无待处理订单”）。
    - 单一的行动按钮（如“返回列表”或“重新搜索”）。

---

## 4. 技术栈推荐 (Tech Stack & Guidelines)

-   **布局与间距**：全面使用 Tailwind CSS 的 `gap`, `p`, `m`, `flex`, `grid` 工具类。
-   **基础组件**：
    -   使用 `shadcn-vue` (Vue 版本的 shadcn/ui) 作为基础组件库。
    -   **按钮 (Button)**: 默认采用 `outline` 或 `ghost` 变体，仅主要动作为 `default`。
    -   **输入框 (Input/Select)**: 统一使用无阴影、细边框样式。
    -   **卡片 (Card)**: 使用 `border-slate-200` 和极小圆角。
-   **排版**：使用 Tailwind 的 `text-slate-900` (标题) 和 `text-slate-500` (副标题/描述)。

---

## 5. 迁移优先级与顺序 (Migration Priorities)

1.  **全局布局 (Global Layout & Shell)**：首先重构侧边导航和顶部栏，建立基础视觉框架。
2.  **仪表盘 (Dashboard Overview)**：作为新风格的展示窗口，建立统计和卡片规范。
3.  **订单列表 (Order List)**：最常用的业务页面，重构筛选逻辑和列表样式。
4.  **订单详情 (Order Detail)**：重构工作流展示和信息展示。
5.  **保管员工作台 (Keeper Process)**：重构交互复杂的确认表格。
6.  **新建订单 (Order Create)**：重构搜索弹窗和批量选择逻辑。
7.  **认证页 (Auth Page)**：登录流程重构。
8.  **状态页 (Empty/Error States)**：最后统一空状态视觉。

---

## 6. 约束与守则 (Constraints & Guardrails)

-   **不改变业务流**：状态转换逻辑、权限检查、API 交互保持不变。
-   **不修改后端**：不依赖任何尚未实现的后端接口。
-   **渐进式替换**：在迁移过程中，允许局部页面保留 Element Plus，但应尽快完成全局替换以保持体验一致。
