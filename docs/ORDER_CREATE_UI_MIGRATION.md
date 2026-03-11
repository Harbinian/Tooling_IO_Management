# 订单创建 UI 迁移 / Order Create UI Migration

## 布局重新设计摘要 / Layout redesign summary

订单创建页面被重构为现代、结构化的表单布局：

The order creation page was refactored into a modern, structured form layout:

- **分节布局**：使用简洁的卡片分为"基本信息"和"已选工装项目"两部分。 / Divided into "Basic Information" and "Selected Tool Items" using clean cards.
- **操作侧边栏**：右侧固定的列，用于实时文本预览和主要提交操作。 / A sticky right-hand column for real-time text preview and primary submission actions.
- **增强的层次结构**：使用清晰的排版、微妙的背景和状态指示器来引导用户完成创建过程。 / Uses clear typography, subtle backgrounds, and status indicators to guide the user through the creation process.

## 订单表单重新设计 / Order form redesign

输入区域被重新组织以提高可扫描性：

The input area was reorganized for better scannability:

- **类型选择器**：用集成的 `TabsList` 替换标准单选按钮，用于出库/入库选择。 / Replaced standard radio buttons with an integrated `TabsList` for outbound/inbound selection.
- **网格布局**：字段采用 2 列响应式网格排列。 / Fields are arranged in a 2-column responsive grid.
- **现代输入**：使用新的自定义 `Input` 和 `Textarea` 原语，具有一致的板岩色边框和焦点状态。 / Uses the new custom `Input` and `Textarea` primitives with consistent slate-based borders and focus states.
- **日期选择器集成**：使用深度 CSS 覆盖样式化 `el-date-picker` 以匹配 Tailwind 主题。 / Styled `el-date-picker` to match the Tailwind theme using deep CSS overrides.

## 工装搜索入口重新设计 / Tool search entry redesign

搜索入口点移至页面标题以便于立即访问：

The search entry point was moved to the page header for immediate access:

- **主要操作**：标题中的突出"搜索并添加工装"按钮。 / A prominent "Search and Add Tools" button in the header.
- **对话框大修**：[ToolSearchDialog.vue](file:///e%3A/CA001/Tooling_IO_Management/frontend/src/components/tool-io/ToolSearchDialog.vue) 经过完全重新设计，具有 6 列过滤器网格、现代结果表格和增强的加载/空状态。 / Was completely redesigned with a 6-column filter grid, a modern results table, and enhanced loading/empty states.

## 已选工装区域重新设计 / Selected tool area redesign

选择表格直接集成到主卡片流程中：

The selection table was integrated directly into the main card flow:

- **紧凑行**：详细的工装信息（编码、名称、图号、规格）在表格单元格内以简洁的垂直排列呈现。 / Detailed tool info (Code, Name, Drawing, Spec) is presented in a clean, vertical arrangement within table cells.
- **内联编辑**：用户可以直接在表格中调整申请数量。 / Users can adjust the application quantity directly in the table.
- **操作空状态**：当未选择项目时，描述性块引导用户使用搜索工具。 / A descriptive block guides the user to the search tool when no items are selected.

## 提交区域策略 / Submission area strategy

提交工作流移至专注的固定侧边栏：

The submission workflow was moved to a focused sticky sidebar:

- **实时预览**：随着用户与表单交互，"保管员请求消息"预览会更新。 / The "Keeper Request Message" preview updates as the user interacts with the form.
- **分层操作**：高对比度的"提交订单"按钮，后跟次要的"保存草稿"选项。 / High-contrast "Submit Order" button followed by a secondary "Save Draft" option.
- **即时反馈**：加载微标和订单号成功消息（通过标准 API 流程路由）。 / Loading spinners and order number success messages (routed via standard API flow).

## 空/错误/加载状态处理 / Empty/error/loading state handling

- **对话框加载**：为工装搜索添加了背景模糊叠加层和旋转图标。 / Added a backdrop-blur overlay with a spinning icon for tool searches.
- **空状态**：为选择列表和搜索结果定制"盒子"和"收件箱"插图。 / Custom "Box" and "Inbox" illustrations for both the selection list and the search results.
- **验证**：保留现有的 `ElMessage` 验证逻辑，用于必填字段（目标位置、工装选择）。 / Retained existing `ElMessage` validation logic for mandatory fields (Target Location, Tool Selection).

## 与当前 API 的兼容性说明 / Compatibility notes with current APIs

迁移与后端服务层完全向后兼容：

The migration is fully backward-compatible with the backend service layer:

- **API 契约**：继续使用 `createOrder`、`submitOrder` 和 `generateKeeperText`。 / Continues to use `createOrder`, `submitOrder`, and `generateKeeperText`.
- **载荷结构**：`buildPayload` 函数保持不变，以保留所需的 JSON schema。 / The `buildPayload` function remains identical to preserve the required JSON schema.
- **路由**：更新重定向逻辑以使用新的 `/inventory/` 前缀，以与全局导航计划保持一致。 / Updated redirect logic to use the new `/inventory/` prefix for consistency with the global navigation plan.
