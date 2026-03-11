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
