# 飞书机器人配置指南 / Feishu Bot Configuration Guide

## 目录 / Contents

1. [概述](#概述)
2. [第一步：创建飞书群](#第一步创建飞书群)
3. [第二步：添加群机器人](#第二步添加群机器人)
4. [第三步：获取 Webhook 地址](#第三步获取-webhook-地址)
5. [第四步：配置项目（方式 A: API / 方式 B: 环境变量）](#第四步配置项目两种方式可选)
6. [第五步：验证配置](#第五步验证配置)
7. [配置项说明](#配置项说明)
8. [飞书通知触发时机](#飞书通知触发时机)
9. [故障排查](#故障排查)

---

## 概述

本系统通过飞书群机器人（Webhook）实现工装出入库工作流通知。支持的通知类型：

| 通知类型 | 说明 | 触发时机 |
|---------|------|---------|
| `ORDER_SUBMITTED` | 订单已提交 | 班组长提交订单后 |
| `KEEPER_CONFIRM_REQUIRED` | 需要保管员确认 | 提交后自动通知保管员 |
| `ORDER_SUBMITTED_TO_SUPPLY_TEAM` | 工装需求通知（物资保障部） | 提交后自动发送到物资保障部群 |
| `TRANSPORT_REQUIRED` | 需要运输 | 保管员确认后 |
| `TRANSPORT_STARTED` | 运输已开始 | 运输员开始运输 |
| `TRANSPORT_COMPLETED` | 运输已完成 | 运输员完成运输 |
| `ORDER_COMPLETED` | 订单已完成 | 最终确认后 |

---

## 第一步：创建飞书群

### 1.1 登录飞书

访问 [飞书官网](https://www.feishu.cn/) 并登录。

### 1.2 创建群聊

1. 点击左侧边栏的 **「消息」**
2. 点击左上角的 **「+」** 新建按钮
3. 选择 **「发起群聊」**
4. 输入群名称（如「工装物资保障部」）和群成员
5. 点击 **「创建」**

> **建议**：为物资保障部创建专用群，用于接收工装需求通知。

---

## 第二步：添加群机器人

### 2.1 选择正确的机器人类型

> **重要**：飞书有两种机器人，配置 Webhook 必须使用**自定义群机器人**：
> - **自定义群机器人** ✅ - 添加后直接显示 Webhook 地址
> - **应用机器人**（开放平台创建）❌ - 不显示 Webhook，需用 API

### 2.2 添加自定义群机器人

1. 打开目标群聊
2. 点击右上角 **「···」** → **「设置」**
3. 找到 **「群机器人」**
4. 点击 **「添加机器人」**
5. 选择 **「自定义机器人」**（不是应用机器人）
6. 设置机器人名称（如「工装管理系统」）
7. 点击 **「添加」**

### 2.3 验证机器人类型

添加成功后，机器人的「机器人详情」页面会显示：
- **开发者** 显示为「张广懿」（添加者）
- 有「仅群主和添加者可移除该机器人」选项

如果显示的是「飞书」或开放平台信息，说明添加的是应用机器人，需要删除后重新添加自定义机器人。

---

## 第三步：获取 Webhook 地址

### 3.1 复制 Webhook URL

添加机器人成功后，页面会显示 Webhook 地址，格式如下：

```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**请完整复制此地址**，后续配置需要使用。

### 3.2 创建多个群的 Webhook（如需要）

| 群名称 | 用途 | 对应配置项 |
|-------|------|-----------|
| 工装物资保障部 | 接收工装需求通知 | `FEISHU_WEBHOOK_SUPPLY_TEAM` |
| 工装运输组 | 接收运输任务通知 | `FEISHU_WEBHOOK_TRANSPORT` |
| 工装管理（通用） | 通用通知 | `FEISHU_WEBHOOK_URL` |

---

## 第四步：配置项目（两种方式可选）

### 方式 A：API 动态配置（推荐）

系统支持通过 API 动态配置飞书 Webhook，无需修改文件。配置后立即生效。

> **认证要求**：API 需要管理员权限，需先登录获取 token。

#### 4A.0 登录获取 Token

```bash
# 管理员账号密码为 admin/admin123
curl -s -X POST http://localhost:8151/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login_name": "admin", "password": "admin123"}'
```

响应中的 `token` 即为认证令牌。

#### 4A.1 启用飞书通知

```bash
# 替换 <YOUR_TOKEN> 为上一步获取的 token
curl -X PUT http://localhost:8151/api/admin/system-config/feishu_notification_enabled \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"config_value": "true"}'
```

#### 4A.2 配置物资保障部群 Webhook

```bash
# 替换 <YOUR_TOKEN> 和 <WEBHOOK_URL> 为实际值
curl -X PUT http://localhost:8151/api/admin/system-config/feishu_webhook_supply_team \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"config_value": "<WEBHOOK_URL>"}'
```

#### 4A.3 配置其他 Webhook（可选）

```bash
# 通用 Webhook
curl -X PUT http://localhost:8151/api/admin/system-config/feishu_webhook_url \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"config_value": "<WEBHOOK_URL>"}'

# 运输通知群 Webhook
curl -X PUT http://localhost:8151/api/admin/system-config/feishu_webhook_transport \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{"config_value": "<WEBHOOK_URL>"}'
```

#### 4A.4 验证配置

```bash
# 查看所有配置（需要带 token）
curl http://localhost:8151/api/admin/system-config \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

响应示例：
```json
{
  "success": true,
  "data": [
    {"config_key": "feishu_notification_enabled", "config_value": "true"},
    {"config_key": "feishu_webhook_supply_team", "config_value": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"},
    ...
  ]
}
```

---

### 方式 B：环境变量配置（传统方式）

#### 4B.1 创建或编辑 .env 文件

在项目根目录找到 `.env` 文件（如果不存在，则复制 `.env.example` 为 `.env`）：

```powershell
# 复制示例文件
copy .env.example .env
```

#### 4B.2 编辑 .env 文件

打开 `.env` 文件，添加或修改以下配置：

```env
# ===========================================
# 飞书机器人配置 / Feishu Bot Configuration
# ===========================================

# 飞书应用凭证（如果使用调用飞书 API 需要）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 通用 Webhook（用于其他通知）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# 物资保障部群 Webhook（工装需求通知）
FEISHU_WEBHOOK_SUPPLY_TEAM=https://open.feishu.cn/open-apis/bot/v2/hook/yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy

# 运输通知群 Webhook
FEISHU_WEBHOOK_TRANSPORT=https://open.feishu.cn/open-apis/bot/v2/hook/zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz

# 飞书通知总开关（true = 启用，false = 禁用）
FEISHU_NOTIFICATION_ENABLED=true

# 通知超时时间（秒）
FEISHU_NOTIFICATION_TIMEOUT_SECONDS=10
```

> **注意**：环境变量配置需要重启后端服务才能生效。

### 4.3 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `FEISHU_WEBHOOK_SUPPLY_TEAM` | **是** | 物资保障部群的 Webhook 地址 |
| `FEISHU_WEBHOOK_URL` | 推荐 | 通用 Webhook，备用 |
| `FEISHU_WEBHOOK_TRANSPORT` | 否 | 运输通知专用 |
| `FEISHU_NOTIFICATION_ENABLED` | 否 | 默认 `false`，设为 `true` 启用 |
| `FEISHU_APP_ID` | 否 | 如需调用飞书 API（卡片消息等） |
| `FEISHU_APP_SECRET` | 否 | 同上 |

---

## 第五步：验证配置

### 5.1 确认后端运行中

```bash
curl http://localhost:8151/api/health
```

正常响应：`{"database": "Connection successful", "status": "ok"}`

### 5.2 查看当前配置

```bash
curl -s http://localhost:8151/api/admin/system-config \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

确认 `feishu_notification_enabled = true` 且 `feishu_webhook_supply_team` 有值。

### 5.3 手动发送测试消息（可选）

直接用 curl 测试 Webhook 是否可用：

```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-here" \
  -H "Content-Type: application/json" \
  -d '{"msg_type": "text", "content": {"text": "测试消息"}}'
```

### 5.4 端到端测试

1. 使用**班组长账号**登录系统（账号：`taidongxu`，密码：`test1234`）
2. 创建并提交一个工装订单
3. 检查物资保障部群是否收到 Markdown 格式的工装需求通知

### 5.5 测试账号参考

| 角色 | 账号 | 密码 | 权限 |
|------|------|------|------|
| 班组长 | taidongxu | test1234 | 创建订单、提交订单 |
| 保管员 | hutingting | test1234 | 确认订单、发送通知 |
| 运输员 | fengliang | test1234 | 执行运输 |
| 系统管理员 | admin | admin123 | 全部权限 |

### 5.6 查看发送日志

如果未收到通知，检查后端输出：

```powershell
python web_server.py 2>&1 | Select-String -Pattern "Feishu", "notification"
```

---

## 飞书通知触发时机

### 自动触发（工作流事件）

| 订单状态变化 | 触发的通知 | 发送到 |
|------------|-----------|--------|
| 提交订单 | `ORDER_SUBMITTED` | 申请人（班组长） |
| 提交订单 | `ORDER_SUBMITTED_TO_SUPPLY_TEAM` | **物资保障部群** |
| 提交订单 | `KEEPER_CONFIRM_REQUIRED` | 该部门的保管员 |
| 保管员确认 | `TRANSPORT_REQUIRED` | 运输通知群 |
| 开始运输 | `TRANSPORT_STARTED` | 申请人/保管员 |
| 完成运输 | `TRANSPORT_COMPLETED` | 申请人/保管员 |
| 最终确认 | `ORDER_COMPLETED` | 申请人/保管员 |
| 拒绝订单 | `ORDER_REJECTED` | 申请人 |
| 取消订单 | `ORDER_CANCELLED` | 申请人 |

### 手动触发

| 操作 | API 端点 | 权限 |
|------|---------|------|
| 发送运输通知 | `POST /api/tool-io-orders/<order_no>/notify-transport` | keeper |
| 发送保管员确认请求 | `POST /api/tool-io-orders/<order_no>/notify-keeper` | keeper |

---

## 故障排查

### 问题 1：添加机器人后看不到 Webhook 地址

**原因**：添加的是「应用机器人」而不是「自定义群机器人」

**解决方法**：
1. 群设置 → 群机器人 → 找到机器人 → **从群组中移除**
2. 重新添加，选择 **「自定义机器人」**（不是应用机器人）
3. 添加成功后，页面会直接显示 Webhook 地址

### 问题 2：API 返回认证错误

**错误信息**：`{"error": {"code": "AUTHENTICATION_REQUIRED", "message": "authentication required"}}`

**解决方法**：
API 需要带 token 请求，先登录获取：
```bash
curl -s -X POST http://localhost:8151/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login_name": "admin", "password": "admin123"}'
```

然后在请求头中加入：`Authorization: Bearer <token>`

### 问题 3：群没有收到通知

**检查项**：

1. 确认 `feishu_notification_enabled = true`
2. 确认 Webhook URL 正确（没有多余空格或换行）
3. 确认 `feishu_webhook_supply_team` 已配置

**解决方法**：

```bash
# 检查数据库配置
curl -s http://localhost:8151/api/admin/system-config \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 问题 4：Webhook URL 无效

**错误信息**：`Feishu error 99991672: webhook is invalid`

**解决方法**：
1. 重新在飞书群中添加自定义机器人
2. 复制新的 Webhook 地址
3. 重新配置到系统

### 问题 5：消息发送成功但群里看不到

**检查项**：
1. 群机器人是否被移除
2. Webhook 是否被禁用
3. 群是否设置了发言权限（联系群管理员）

---

## 高级配置

### 使用飞书应用（可选）

如需发送卡片消息或更丰富的交互，可配置飞书应用：

1. 在 [飞书开放平台](https://open.feishu.cn/) 创建应用
2. 获取 `App ID` 和 `App Secret`
3. 填入 `.env`：

```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 消息卡片模板

目前支持的 Markdown 格式：

```markdown
## 工装需求通知

**单号**: IO-20260402-001
**类型**: 出库
**申请人**: 张三
**部门**: 生产部

**用途**: 生产使用
**目标位置**: A06
**计划使用时间**: 2026-04-03 09:00:00

---

**工装明细**:

| 序号 | 序列号 | 名称 | 图号/机型 | 分体数量 |
|------|--------|------|-----------|----------|
| 1 | TK-001 | 钻头A | DWG-001 / Φ10 | 3 |

---

**备注**: 紧急
**时间**: 2026-04-02 10:30:00
```

---

## 快速参考

### 最小配置（只需物资保障部通知）

```env
FEISHU_NOTIFICATION_ENABLED=true
FEISHU_WEBHOOK_SUPPLY_TEAM=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-here
```

### 完整配置

```env
FEISHU_NOTIFICATION_ENABLED=true
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/general-webhook
FEISHU_WEBHOOK_SUPPLY_TEAM=https://open.feishu.cn/open-apis/bot/v2/hook/supply-team-webhook
FEISHU_WEBHOOK_TRANSPORT=https://open.feishu.cn/open-apis/bot/v2/hook/transport-webhook
FEISHU_NOTIFICATION_TIMEOUT_SECONDS=10
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `config/settings.py` | 配置定义 |
| `backend/services/feishu_notification_adapter.py` | 飞书通知适配器 |
| `backend/services/notification_service.py` | 通知类型常量 |
| `backend/services/tool_io_service.py` | 通知触发逻辑 |
| `utils/feishu_api.py` | 飞书 API 封装 |
