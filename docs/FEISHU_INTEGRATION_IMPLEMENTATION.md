# 飞书集成实现 / Feishu Integration Implementation

## 概述 / Overview

本文档描述工装出入库管理系统的飞书 (Feishu) 通知集成实现。该集成允许系统通过飞书群机器人发送工装出入库工作流通知。

This document describes the Feishu notification integration implementation for the Tooling IO Management System. The integration allows the system to send workflow notifications via Feishu group bots.

## 架构 / Architecture

### 组件 / Components

- **后端服务层** (`backend/services/tool_io_service.py`): 业务逻辑，包含 `notify_transport` 和 `notify_keeper` 函数
- **飞书 API 模块** (`utils/feishu_api.py`): 飞书 webhook 发送实现
- **数据库层** (`database.py`): 通知记录存储
- **前端** (`frontend/src/pages/tool-io/OrderDetail.vue`): 用户界面，用于触发发送

Backend service layer: business logic with `notify_transport` and `notify_keeper` functions. Feishu API module: webhook sending implementation. Database layer: notification record storage. Frontend: user interface for triggering sends.

### 通知类型 / Notification Types

1. **保管员请求通知** (`keeper_request`): 发送给保管员的工装确认请求
2. **运输通知** (`transport_notice`): 发送给物流的运输任务通知

Keeper Request Notification: sent to keeper for tool confirmation requests. Transport Notification: sent to logistics for transport task notifications.

---

## Schema 检查摘要 / Schema Inspection Summary

### 通知记录表 / Notification Records Table

表名: `工装出入库单_通知记录`

Table name: `工装出入库单_通知记录`

| 字段 | 类型 | 说明 |
|------|------|------|
| 出入库单号 | varchar | 关联的订单号 |
| 通知类型 | varchar | 如 `keeper_request`, `transport_notice` |
| 通知渠道 | varchar | 如 `feishu`, `internal` |
| 接收人 | varchar | 接收人名称 |
| 通知标题 | varchar | 通知标题 |
| 通知内容 | varchar | 通知正文 |
| 复制文本 | varchar | 用于复制的简洁文本 |
| 发送状态 | varchar | `sent`, `failed`, `pending` |
| 发送时间 | datetime | 实际发送时间 |
| 发送结果 | varchar | 发送结果描述 |
| 创建时间 | datetime | 记录创建时间 |

| Field | Type | Description |
|-------|------|-------------|
| 出入库单号 | varchar | Associated order number |
| 通知类型 | varchar | e.g., `keeper_request`, `transport_notice` |
| 通知渠道 | varchar | e.g., `feishu`, `internal` |
| 接收人 | varchar | Receiver name |
| 通知标题 | varchar | Notification title |
| 通知内容 | varchar | Notification body |
| 复制文本 | varchar | Compact text for copying |
| 发送状态 | varchar | `sent`, `failed`, `pending` |
| 发送时间 | datetime | Actual send time |
| 发送结果 | varchar | Send result description |
| 创建时间 | datetime | Record creation time |

---

## 配置加载策略 / Configuration Loading Strategy

### 环境变量 / Environment Variables

飞书配置通过环境变量加载:

Feishu configuration is loaded via environment variables:

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | 是 (for token) |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 是 (for token) |
| `FEISHU_WEBHOOK_URL` | 通用飞书 Webhook URL | 推荐 |
| `FEISHU_WEBHOOK_TRANSPORT` | 运输通知专用 Webhook URL | 可选 |

| Variable | Description | Required |
|----------|-------------|----------|
| `FEISHU_APP_ID` | Feishu App ID | Yes (for token) |
| `FEISHU_APP_SECRET` | Feishu App Secret | Yes (for token) |
| `FEISHU_WEBHOOK_URL` | General Feishu Webhook URL | Recommended |
| `FEISHU_WEBHOOK_TRANSPORT` | Transport notification专用 Webhook URL | Optional |

### 配置文件 / Configuration File

配置也在 `config/settings.py` 中定义:

Configuration is also defined in `config/settings.py`:

```python
FEISHU_APP_ID: str
FEISHU_APP_SECRET: str
FEISHU_APP_TOKEN: str
FEISHU_WEBHOOK_URL: str
FEISHU_WEBHOOK_TRANSPORT: str
```

---

## 发送流程 / Send Flow

### 运输通知流程 / Transport Notification Flow

1. 用户在订单详情页面点击"发送飞书"按钮
2. 前端调用 `POST /api/tool-io-orders/{orderNo}/notify-transport`
3. 后端执行:
   - 获取订单详情
   - 生成运输通知文本
   - 创建通知记录 (初始状态: pending)
   - 调用飞书 webhook 发送通知
   - 更新通知记录状态 (sent/failed)
   - 更新订单状态为 `transport_notified`
   - 记录操作日志
4. 返回发送结果给前端
5. 前端显示成功/失败消息

User clicks "Send to Feishu" button on order detail page. Frontend calls `POST /api/tool-io-orders/{orderNo}/notify-transport`. Backend: fetches order details, generates transport notification text, creates notification record (initial status: pending), calls Feishu webhook to send notification, updates notification record status (sent/failed), updates order status to `transport_notified`, records operation log. Returns send result to frontend. Frontend displays success/failure message.

### 保管员通知流程 / Keeper Notification Flow

类似运输通知，但:
- 触发条件: 订单状态为 `submitted` 或 `keeper_confirmed`
- 使用通用 webhook URL

Similar to transport notification, but: trigger condition: order status is `submitted` or `keeper_confirmed`, uses general webhook URL.

---

## 通知记录映射 / Notification Record Mapping

### 发送成功 / Send Success

| 字段 | 值 |
|------|---|
| 通知渠道 | `feishu` |
| 发送状态 | `sent` |
| 发送结果 | `Feishu notification sent successfully` |
| 发送时间 | 实际发送时间 |

| Field | Value |
|-------|-------|
| 通知渠道 | `feishu` |
| 发送状态 | `sent` |
| 发送结果 | `Feishu notification sent successfully` |
| 发送时间 | Actual send time |

### 发送失败 / Send Failure

| 字段 | 值 |
|------|---|
| 通知渠道 | `feishu` |
| 发送状态 | `failed` |
| 发送结果 | `Feishu send failed: <error message>` |
| 发送时间 | 尝试发送时间 |

| Field | Value |
|-------|-------|
| 通知渠道 | `feishu` |
| 发送状态 | `failed` |
| 发送结果 | `Feishu send failed: <error message>` |
| 发送时间 | Attempt send time |

---

## 前端触发位置 / Frontend Trigger Placement

### 订单详情页面 / Order Detail Page

位置: `frontend/src/pages/tool-io/OrderDetail.vue`

Location: `frontend/src/pages/tool-io/OrderDetail.vue`

按钮显示条件:
- **保管员通知**: 订单状态为 `submitted` 或 `keeper_confirmed`
- **运输通知**: 订单状态为 `keeper_confirmed`、`partially_confirmed` 或 `transport_notified`

Button display conditions:
- Keeper Notification: order status is `submitted` or `keeper_confirmed`
- Transport Notification: order status is `keeper_confirmed`, `partially_confirmed`, or `transport_notified`

按钮位于对应的通知预览卡片右下角。

Buttons are located at the bottom-right corner of the corresponding notification preview cards.

---

## 失败处理策略 / Failure Handling Strategy

### 设计原则 / Design Principles

1. **工作流隔离**: 飞书发送失败不会影响核心订单工作流
2. **可重试**: 失败的通知记录保留，可以重新发送
3. **明确反馈**: 用户能看到失败原因
4. **完整日志**: 所有发送尝试都被记录

Workflow isolation: Feishu send failure does not affect core order workflow. Retryable: failed notification records are preserved and can be resent. Clear feedback: users can see failure reasons. Complete logging: all send attempts are logged.

### 失败场景 / Failure Scenarios

| 场景 | 处理 |
|------|------|
| Webhook URL 未配置 | 记录失败，返回明确错误消息 |
| 飞书 API 返回错误 | 记录错误码和消息，更新状态为 failed |
| 网络超时 | 捕获异常，记录错误，更新状态为 failed |
| Token 获取失败 | 记录失败，不尝试发送 |

| Scenario | Handling |
|----------|----------|
| Webhook URL not configured | Record failure, return clear error message |
| Feishu API returns error | Record error code and message, update status to failed |
| Network timeout | Catch exception, record error, update status to failed |
| Token acquisition fails | Record failure, do not attempt to send |

---

## API 端点 / API Endpoints

### 发送运输通知 / Send Transport Notification

```
POST /api/tool-io-orders/<order_no>/notify-transport
```

Request Body:
```json
{
  "operator_id": "user123",
  "operator_name": "John Doe",
  "operator_role": "keeper"
}
```

Response:
```json
{
  "success": true,
  "notify_id": 123,
  "send_status": "sent",
  "send_result": "Feishu notification sent successfully",
  "wechat_text": "..."
}
```

### 发送保管员通知 / Send Keeper Notification

```
POST /api/tool-io-orders/<order_no>/notify-keeper
```

Request Body: 同上 / Same as above

Response: 同上 / Same as above

---

## 验证结果 / Verification Results

### 测试场景 / Test Scenarios

1. ✅ 飞书 webhook 配置正确时，通知发送成功
2. ✅ 发送结果正确存储到通知记录
3. ✅ 发送失败时，状态正确更新为 failed
4. ✅ 前端正确显示发送结果
5. ✅ 核心订单工作流在发送失败时保持稳定

With correct Feishu webhook configuration, notification sent successfully. Send result correctly stored in notification records. On send failure, status correctly updated to failed. Frontend correctly displays send results. Core order workflow remains stable on send failure.

### 限制 / Limitations

- 当前仅支持文本消息格式
- 尚未支持卡片消息格式
- 尚未实现重试机制

Currently only supports text message format. Card message format not yet supported. Retry mechanism not yet implemented.

---

## 剩余假设 / Remaining Assumptions

1. 飞书 webhook URL 已在环境变量中配置
2. 飞书应用具有发送消息的权限
3. 用户具有触发通知的操作权限

Feishu webhook URL is configured in environment variables. Feishu app has permission to send messages. User has operation permission to trigger notifications.

---

## 微信集成说明 / WeChat Integration Note

根据任务要求，微信集成暂未实现。目前微信复制文本功能保留为纯复制模式。

According to task requirements, WeChat integration is not implemented yet. WeChat copy text feature remains as copy-only mode for now.
