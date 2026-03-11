# 保管员工作台 UI 迁移 / Keeper Process UI Migration

## 布局重新设计摘要 / Layout redesign summary

保管员处理页面被重构为分体式操作工作区：

The keeper processing page was refactored into a split operational workspace:

- **左侧边栏**：待处理订单的可滚动队列（`Inventory Queue`），允许保管员快速扫描和选择任务。/ A scrollable queue of pending orders (`Inventory Queue`), allowing keepers to quickly scan and select tasks.
- **右侧工作区**：所选订单的专注 `Process Workbench`，包含摘要信息、运输配置和项目验证。/ A focused `Process Workbench` for the selected order, containing summary information, transport configuration, and item verification.

此布局通过在处理单个订单时保持任务列表可见来最大化操作效率。

This layout maximizes operational efficiency by keeping the task list visible while processing individual orders.

## 待处理订单列表设计 / Pending order list design

待处理订单列表使用卡片式设计，具有：

The pending order list uses a card-based design with:

- 清晰的订单标识和状态徽章。 / Clear order identifiers and status badges.
- 元数据指示器（发起人、工装数量、项目代号），用于快速了解上下文。 / Metadata indicators (initiator, tool count, project code) for quick context.
- 活动状态高亮，指示当前正在处理的订单。 / Active state highlighting to indicate which order is currently being processed.
- 刷新操作以手动拉取最新队列。 / A refresh action to manually pull the latest queue.

## 处理详情区域设计 / Processing detail area design

所选订单的工作区被组织成逻辑部分：

The workspace for the selected order is organized into logical sections:

- **订单摘要**：紧凑网格显示订单类型、发起人、项目和目标位置。 / A compact grid showing order type, initiator, project, and target location.
- **运输配置**：运输类型和负责人的清洁输入字段，以及用于保管员备注的专用文本区域。 / Clean input fields for transport type and 负责人, plus a dedicated textarea for keeper remarks.
- **操作头部**：主要操作（确认、拒绝、预览）固定在头部以便于立即访问。 / Primary actions (Confirm, Reject, Preview) are pinned to the header for immediate accessibility.

## 明细级确认 UI 策略 / Item-level confirmation UI strategy

工装项目以专为验证设计的结构化表格显示：

Tool items are displayed in a structured table designed for verification:

- **信息**：工装编码和名称。 / Tool code and name.
- **建议**：显示当前/建议位置以供参考。 / Displays the current/suggested location for reference.
- **输入**：用于确认实际位置、状态（批准/拒绝）和批准数量的内联输入。 / Inline inputs for confirming the actual location, status (Approved/Rejected), and approved quantity.
- **视觉反馈**：微妙的行分隔线和充足的填充，以在数据输入期间保持可读性。 / Subtle row dividers and generous padding to maintain readability during data entry.

## 操作区域设计 / Action area design

- **头部操作**：主要工作流操作位于工作台右上角。 / The main workflow actions are located in the top-right of the workbench.
- **通知操作**：确认完成后出现专用"通知"块，引导保管员发送飞书通知。 / A dedicated "Notify" block appears after confirmation is complete, guiding the keeper to send the Feishu notification.
- **移动端支持**：操作在底部重复，以便在较小屏幕上更好地访问。 / Actions are duplicated at the bottom for better accessibility on smaller screens.

## 空/错误/加载状态处理 / Empty/error/loading state handling

- **队列加载**：待处理列表获取时使用类似骨架的脉冲动画。 / Skeleton-like pulse animations are used when the pending list is being fetched.
- **空队列**：当没有订单需要操作时显示清晰的"收件箱"空状态。 / A clear "Inbox" empty state when no orders require action.
- **未选择**：显示"鼠标指针"空状态，提示用户从左侧选择订单。 / A "Mouse Pointer" empty state prompting the user to select an order from the left.
- **API 反馈**：提交期间使用 `ElMessage` 进行成功/警告反馈。 / Uses `ElMessage` for success/warning feedback during submissions.

## 与当前 API 的兼容性说明 / Compatibility notes with current APIs

迁移保留所有现有 API 契约和业务逻辑：

The migration preserves all existing API contracts and business logic:

- `getPendingKeeperOrders` / 获取保管员待处理订单
- `getOrderDetail` / 获取订单详情
- `keeperConfirmOrder` / 保管员确认订单
- `rejectOrder` / 拒绝订单
- `notifyTransport` / 通知运输
- `generateTransportText` / 生成运输文本

`confirmItems` 和 `confirmForm` 的数据结构保持不变，以确保与后端服务层的完全兼容。

The data structure for `confirmItems` and `confirmForm` remains identical to ensure full compatibility with the backend service layer.
