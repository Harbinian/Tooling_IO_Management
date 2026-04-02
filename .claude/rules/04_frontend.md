# 前端开发规范 / Frontend Development Rules

---

## 必需页面 / Required Pages

系统必须包含：

1. 订单创建页面 / Order creation page
2. 保管员处理页面 / Keeper processing page
3. 订单列表页面 / Order list page
4. 订单详情页面 / Order detail page

---

## 工装搜索要求 / Tool Search Requirements

工装搜索必须支持：

- 工装序列号 / serial number
- 工装名称 / tool name
- 规格 / specification
- 位置 / location
- 状态 / status

**必须支持批量选择。**

---

## 状态显示 / State Display

订单必须显示状态标签：

- 已提交 / Submitted
- 保管员已确认 / Keeper Confirmed
- 运输已通知 / Transport Notified
- 已完成 / Completed
- 已拒绝 / Rejected

---

## 文本生成 UX / Text Generation UX

用户必须能够：
- 预览飞书通知 / preview Feishu notification
- 复制微信消息 / copy WeChat message

---

## 字段映射 / Field Mapping

UI 字段 -> API 字段 / UI Field -> API Field

| UI 字段 | API 字段 |
|---------|----------|
| 订单号 / Order Number | order_no |
| 工装序列号 / Serial Number | serial_no |
| 工装名称 / Tool Name | tool_name |

---

## 主题系统 / Theme System

### 初始加载 / Initial Load

SettingsPage.vue 必须:
1. 首先检查 `localStorage` 中的保存的主题
2. 如果没有保存，使用 `window.matchMedia('(prefers-color-scheme: dark)')` 检测系统偏好
3. 应用检测到的主题

### 运行时同步 / Runtime Sync

SettingsPage.vue 必须监听系统主题变化:

```javascript
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (!userManualOverride) {
    isDarkMode.value = e.matches
    applyTheme(isDarkMode.value)
  }
})
```

---

## CSS 变量使用 / CSS Variable Usage

**严禁使用硬编码颜色，必须使用 CSS 变量:**

| 禁止 / Forbidden | 必须使用 / Must Use |
|-----------------|-------------------|
| `bg-white`, `bg-black` | `var(--background)` |
| `text-white`, `text-black` | `var(--foreground)`, `var(--primary-foreground)` |
| `border-gray-xxx` | `var(--border)` |
| `bg-slate-xxx` | `var(--muted)`, `var(--accent)` |

---

## 工作流预览 / Workflow Preview

订单创建页面必须包含工作流步骤预览：

```vue
<WorkflowStepper
  :current-status="'draft'"
  :order-type="orderType"
  :show-header="true"
  :custom-labels="workflowPreviewLabels"
/>
```

**工作流标签:**
- 出库流程: `草稿` -> `已提交` -> `保管员已确认` -> `运输通知` -> `班组长最终确认` -> `已完成`
- 入库流程: `草稿` -> `已提交` -> `保管员已确认` -> `运输通知` -> `保管员最终确认` -> `已完成`

---

## RBAC 数据隔离 / RBAC Data Isolation

**测试时注意**: 不同组织的用户无法访问彼此的订单数据。E2E 测试需要使用同一组织的用户账户。
