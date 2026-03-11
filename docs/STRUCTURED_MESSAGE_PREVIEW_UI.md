# 结构化消息预览 UI 实现 / Structured Message Preview UI Implementation

## 概述 / Overview

结构化消息预览 UI 提供了一种专门的方式来显示和交互工装出入库工作流期间生成的业务导向文本消息。此实现专注于可读性、快速复制和专业演示，使用 **Tailwind CSS + shadcn/ui + Tailark Mist** 设计系统。

The structured message preview UI provides a specialized way to display and interact with business-oriented text messages generated during the Tooling IO workflow. This implementation focuses on readability, quick copying, and professional presentation using the **Tailwind CSS + shadcn/ui + Tailark Mist** design system.

## 组件 / Components

### NotificationPreview.vue

用于所有结构化消息预览的核心组件。

The core component used for all structured message previews.

- **基于类型的样式**：支持 `keeper`、`transport`、`wechat` 和 `generic` 类型，具有特定的图标和标题。 / Supports `keeper`, `transport`, `wechat`, and `generic` types with specific icons and titles.
- **Mist 设计**：使用简洁的卡片布局，带有微妙的等宽字体标题和充足的空白。 / Uses a clean card layout with a subtle header, monospaced typography, and generous whitespace.
- **复制到剪贴板**：集成复制按钮，带有视觉反馈。 / Integrated copy button with visual feedback.
- **加载/空状态**：内置支持加载叠加层和描述性空占位符。 / Built-in support for loading overlays and descriptive empty placeholders.
- **等宽字体排版**：针对扫描结构化数据（如工装列表和订单号）进行了优化。 / Optimized for scanning structured data like tool lists and order numbers.

## 放置策略 / Placement Strategy

预览集成到最相关的位置的工作流中：

Previews are integrated into the workflow where they are most relevant:

1.  **订单创建 (`OrderCreate.vue`)**：
    - 放置在固定侧边栏中。 / Placed in a sticky sidebar.
    - 实时显示随着表单填写而更新的"保管员请求"预览。 / Shows the "Keeper Request" preview in real-time as the form is filled.
    - 允许发起人在提交前后查看将发送给保管员的内容。 / Allows initiators to review what will be sent to keepers before/after submission.

2.  **保管员处理 (`KeeperProcess.vue`)**：
    - 放置在项目验证表格下方。 / Placed below the item verification table.
    - 显示"运输通知"和"微信复制"预览。 / Shows both "Transport Notice" and "WeChat Copy" previews.
    - 使保管员能够快速复制通知文本以供下游物流使用。 / Enables keepers to quickly copy notification text for downstream logistics.

3.  **订单详情 (`OrderDetail.vue`)**：
    - 放置在页面底部的 3 列网格中。 / Placed at the bottom of the page in a 3-column grid.
    - 提供所有生成消息的全面视图，用于历史参考或后续操作。 / Provides a comprehensive view of all generated messages for historical reference or follow-up actions.

## 用户交互 / User Interaction

- **视觉反馈**：复制按钮在成功复制操作后短暂更改其图标和文本。 / The copy button changes its icon and text briefly after a successful copy operation.
- **可读性**：等宽字体确保结构化文本中的列和对齐得以保留。 / Monospaced fonts ensure that columns and alignments in the structured text are preserved.
- **动画**：内容更新时使用微妙的淡入动画，以提供平滑过渡。 / Subtle fade-in animations are used when content updates to provide a smooth transition.

## 兼容性与未来集成 / Compatibility & Future Integration

- **API 驱动**：UI 直接从现有后端端点（`generateKeeperText`、`generateTransportText`）消费文本。 / The UI consumes text directly from existing backend endpoints (`generateKeeperText`, `generateTransportText`).
- **面向未来**：组件已准备好托管"发送"操作（例如，发送到飞书），一旦集成端点可用。 / The component is prepared to host "Send" actions (e.g., Send to Feishu) once integration endpoints are available.
- **布局一致性**：遵循与其他迁移页面相同的视觉节奏，确保统一的内置工具体验。 / Follows the same visual rhythm as other migrated pages, ensuring a unified internal tool experience.
