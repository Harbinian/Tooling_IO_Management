# Gemini 前端设计协议 / Gemini Frontend Design Protocol

## 角色 / Role

UI/UX 设计师和前端架构师。 / UI/UX Designer and Frontend Architect.

Gemini 专注于： / Gemini focuses on:

- 页面布局 / page layout
- 交互流程 / interaction flow
- 组件结构 / component structure
- 用户体验 / user experience

Gemini 不定义后端逻辑。 / Gemini does not define backend logic.

---

## 必需页面 / Required Pages

系统必须包含： / The system must include:

1. 订单创建页面 / Order creation page
2. 保管员处理页面 / Keeper processing page
3. 订单列表页面 / Order list page
4. 订单详情页面 / Order detail page

---

## 关键 UX 要求 / Key UX Requirements

工装搜索必须支持： / Tool search must support:

- 工装编码 / tool code
- 工装名称 / tool name
- 规格 / specification
- 位置 / location
- 状态 / status

必须支持批量选择。 / Batch selection must be supported.

---

## 状态显示 / State Display

订单必须显示状态标签： / Orders must display state badges:

- 已提交 / Submitted
- 保管员已确认 / Keeper Confirmed
- 运输已通知 / Transport Notified
- 已完成 / Completed
- 已拒绝 / Rejected

---

## 文本生成 UX / Text Generation UX

用户必须能够： / Users must be able to:

- 预览飞书通知 / preview Feishu notification
- 复制微信消息 / copy WeChat message

---

## 字段映射 / Field Mapping

Gemini 必须输出字段映射表： / Gemini must output a field mapping table:

UI 字段 -> API 字段 / UI Field -> API Field

示例: / Example:

| UI 字段 | API 字段 |
|---------|----------|
| 订单号 / Order Number | order_no |
| 工装编码 / Tool Code | tool_code |
| 工装名称 / Tool Name | tool_name |

---

## 确认对话框规范 / Confirmation Dialog Specification

所有关键操作必须在涉及该操作的每个页面保持一致的确认对话框。/ All critical operations must maintain consistent confirmation dialogs across all pages that involve that operation.

### 必须一致的页面 / Pages That Must Be Consistent

| 操作 | OrderList.vue | OrderDetail.vue | OrderCreate.vue |
|------|--------------|-----------------|-----------------|
| 提交 Submit | ✅ 有确认 | ✅ 必须有确认 | N/A |
| 取消 Cancel | N/A | ✅ 有确认 | N/A |
| 最终确认 Final Confirm | N/A | ✅ 有确认 | N/A |
| 删除 Delete | N/A | ✅ 有确认 | N/A |

### 确认对话框模板 / Confirmation Dialog Template

```javascript
await ElMessageBox.confirm(
  '确认消息内容',
  '对话框标题',
  { confirmButtonText: '确认按钮文字', cancelButtonText: '取消按钮文字', type: 'warning' }
)
```

### 提交操作确认消息 / Submit Confirmation Message

- 消息: `确认提交单据 ${orderNo} 吗？提交后将进入保管员审核流程。`
- 标题: `提交单据`
- 按钮: `提交` / `取消`
- 类型: `warning`

---

## 主题系统规范 / Theme System Specification

### 初始加载 / Initial Load

SettingsPage.vue 必须:
1. 首先检查 `localStorage` 中的保存的主题
2. 如果没有保存，使用 `window.matchMedia('(prefers-color-scheme: dark)').matches` 检测系统偏好
3. 应用检测到的主题

### 运行时同步 / Runtime Sync

SettingsPage.vue 必须监听系统主题变化:

```javascript
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (!userManualOverride) { // 需要实现用户手动覆盖标志
    isDarkMode.value = e.matches
    applyTheme(isDarkMode.value)
  }
})
```

### CSS 变量使用 / CSS Variable Usage

严禁使用硬编码颜色，必须使用 CSS 变量: / Hardcoded colors are FORBIDDEN, CSS variables must be used:

| 禁止 / Forbidden | 必须使用 / Must Use |
|-----------------|-------------------|
| `bg-white`, `bg-black` | `var(--background)` |
| `text-white`, `text-black` | `var(--foreground)`, `var(--primary-foreground)` |
| `border-gray-xxx` | `var(--border)` |
| `bg-slate-xxx` | `var(--muted)`, `var(--accent)` |

### 对比度与配色规范 / Contrast & Color Specifications

为确保在明暗主题下均具有极佳的可读性和一致性，必须遵循以下配色规则: / To ensure excellent readability and consistency across light and dark themes, the following color rules must be followed:

#### 1. 首要颜色与对比色 / Primary & Contrast Colors

| 场景 / Scenario | 浅色模式 (Light) | 深色模式 (Dark) | 配合规则 / Contrast Rule |
| :--- | :--- | :--- | :--- |
| **Primary (品牌主色)** | `hsl(240 5.9% 10%)` | `hsl(240 5.9% 10%)` | 在此背景上必须使用 `text-primary-foreground` |
| **Background (基础背景)** | `hsl(0 0% 100%)` | `hsl(240 10% 3.9%)` | 承载正文文字 `text-foreground` |
| **Card (容器/卡片)** | `hsl(0 0% 100%)` | `hsl(240 10% 3.9%)` | 悬停态使用 `hover:bg-accent` |
| **Muted (次要文字)** | `hsl(240 3.8% 46.1%)` | `hsl(240 5% 84.9%)` | 用于标签、描述，确保深色模式下亮度足够 |

#### 2. 多元素配合原则 / Multi-element Coordination

- **Header / Hero 区域**: 通常使用 `bg-primary`。内部所有文字必须使用 `text-primary-foreground`（而非 `text-white`），边框使用 `border-primary-foreground/20`。
- **输入框与选择框 (Forms)**: 统一使用 `border-input` 和 `bg-background/50`。避免在页面调用处硬编码 `bg-background` 或 `bg-white` 覆盖组件默认样式。
- **状态标签 (Tags/Badges)**: 优先使用 `variant="outline"` 配合 `border-primary/20`。在深色背景上，使用 `text-primary-foreground`。

#### 3. 禁止行为 / Forbidden Actions

- **严禁**在全局或共享组件中使用 `text-white` 或 `text-black`。
- **严禁**在深色模式下将 `primary` 颜色反转为浅色（除非是纯文字点缀）。
- **严禁**在卡片容器内使用与卡片背景完全相同的背景色（如 `bg-background` 覆盖 `bg-card`），应使用透明度或 `bg-muted` 区分层级。

---

## 工作流预览规范 / Workflow Preview Specification

### OrderCreate.vue 必须显示 / OrderCreate.vue Must Display

订单创建页面必须包含工作流步骤预览，显示提交后的流程: / Order creation page must include workflow step preview showing the process after submission:

```vue
<WorkflowStepper
  :current-status="'draft'"
  :order-type="orderType"
  :show-header="true"
  :custom-labels="workflowPreviewLabels"
/>
```

### 工作流标签 / Workflow Labels

- 出库流程: `草稿` -> `已提交` -> `保管员已确认` -> `运输通知` -> `班组长最终确认` -> `已完成`
- 入库流程: `草稿` -> `已提交` -> `保管员已确认` -> `运输通知` -> `保管员最终确认` -> `已完成`

---

## RBAC 数据隔离说明 / RBAC Data Isolation Note

测试时注意: 不同组织的用户无法访问彼此的订单数据。E2E 测试需要使用同一组织的用户账户。/ Note for testing: Users from different organizations cannot access each other's order data. E2E testing requires user accounts from the same organization.
