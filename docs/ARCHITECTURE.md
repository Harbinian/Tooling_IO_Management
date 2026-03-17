# 工装出入库管理系统 - 架构文档

## 1. 系统架构概述

### 1.1 整体架构

本系统采用单体应用架构（Monolithic Architecture），分为以下层次：

```
┌─────────────────────────────────────────┐
│            Presentation Layer           │
│         (Vue3 + Element Plus)           │
├─────────────────────────────────────────┤
│             API Layer                   │
│            (Flask)                       │
├─────────────────────────────────────────┤
│           Service Layer                  │
│     (Business Logic Processing)         │
├─────────────────────────────────────────┤
│          Data Access Layer               │
│           (pyodbc)                       │
├─────────────────────────────────────────┤
│            Database                      │
│          (SQL Server)                    │
└─────────────────────────────────────────┘
```

### 1.2 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python + Flask | 轻量级Web框架 |
| 数据库访问 | pyodbc | Python SQL Server数据库访问 |
| 数据库 | SQL Server | 企业级关系型数据库 |
| 前端 | Vue3 + Element Plus | 渐进式前端框架 + UI组件库 |
| 通知 | 飞书Webhook | 企业即时通讯通知 |

### 1.3 项目规模约束

- < 100 并发用户
- < 100,000 工装记录
- 单数据库实例
- 无分布式系统
- 无消息队列

---

## 2. 模块边界

### 2.1 核心模块

```
┌─────────────────────────────────────────────────────────────┐
│                      API Router Layer                       │
│  /api/tool-io-orders  |  /api/tools  |  /api/notifications │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
│  OrderService  |  ToolService  |  NotificationService      │
│  TextGeneratorService  |  AuditService                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                         │
│  OrderRepository  |  ToolRepository  |  LogRepository       │
│  NotificationRepository                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                         │
│                   pyodbc + SQL Server                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

#### OrderService（订单服务）

- 创建、提交、确认、拒绝、取消订单
- 维护订单状态机
- 管理订单与工装的关联

#### ToolService（工装服务）

- 工装搜索和查询
- 工装状态管理
- 工装快照记录

#### NotificationService（通知服务）

- 飞书消息发送
- 通知记录持久化
- 通知重试机制

#### TextGeneratorService（文本生成服务）

- 生成保管员需求文本
- 生成运输通知文本
- 生成微信复制文本

#### AuditService（审计服务）

- 操作日志记录
- 状态变更追踪
- 审计查询

---

## 3. 状态机设计

### 3.1 订单状态 (order_status)

```
        ┌─────────┐
        │  draft  │
        └────┬────┘
             │ submit
             ↓
   ┌───────────────┐
   │   submitted   │←────────────┐
   └───────┬───────┘             │
           │                     │
           │ keeper_confirm      │
           ↓                     │
   ┌───────────────┐      ┌──────────┐
   │partially_      │     │ rejected │
   │confirmed       │     └────┬─────┘
   └───────┬───────┘          │ cancel
           │                   ↓
           │ keeper_confirm    ┌──────────┐
           ↓              ┌──────────┐
   ┌───────────────┐      │ cancelled │
   │keeper_confirmed│     └──────────┘
   └───────┬───────┘
           │
           │ notify_transport
           ↓
   ┌───────────────┐
   │transport_notified│
   └───────┬───────┘
           │
           │ transport_start
           ↓
   ┌───────────────┐
   │transport_in_progress│
   └───────┬───────┘
           │
           │ transport_complete
           ↓
   ┌───────────────┐
   │final_confirm_│
   │pending        │
   └───────┬───────┘
           │
           │ final_confirm
           ↓
   ┌─────────────┐
   │ completed   │
   └─────────────┘
```

| 状态 | 中文 | 说明 |
|------|------|------|
| draft | 草稿 | 订单刚创建，未提交 |
| submitted | 已提交 | 已提交给保管员 |
| partially_confirmed | 部分确认 | 部分明细已确认 |
| keeper_confirmed | 保管员已确认 | 保管员已确认工装状态 |
| transport_notified | 已通知运输 | 已发送运输通知 |
| transport_in_progress | 运输中 | 运输进行中 |
| final_confirmation_pending | 待最终确认 | 等待最终确认 |
| completed | 已完成 | 订单流程结束 |
| rejected | 已拒绝 | 保管员拒绝 |
| cancelled | 已取消 | 已取消 |

### 3.2 明细状态 (item_status)

| 状态 | 中文 | 说明 |
|------|------|------|
| pending | 待确认 | 等待确认 |
| confirmed | 已确认 | 保管员已确认 |
| rejected | 已拒绝 | 拒绝该项目 |
| completed | 已完成 | 项目完成 |

### 3.3 工装状态 (tool_status)

| 状态 | 中文 | 说明 |
|------|------|------|
| in_storage | 在库 | 工装在仓库中 |
| outbounded | 已出库 | 工装已被借出 |
| maintain | 维修中 | 工装需要维修 |
| scrapped | 已报废 | 工装已报废 |

---

## 4. 数据流

### 4.1 订单创建数据流

```
用户操作 (创建订单)
       ↓
API接收请求 (POST /api/tool-io-orders)
       ↓
参数校验
       ↓
OrderService 创建订单
       ↓
OrderRepository 保存订单
       ↓
OrderRepository 保存订单明细
       ↓
AuditService 记录操作日志
       ↓
返回响应
```

### 4.2 订单提交流数据流

```
用户操作 (提交订单)
       ↓
API接收请求 (POST /api/tool-io-orders/{order_no}/submit)
       ↓
校验订单状态
       ↓
OrderService 更新订单状态
       ↓
OrderRepository 更新状态
       ↓
AuditService 记录日志 (draft → submitted)
       ↓
返回响应
```

### 4.3 通知数据流

```
用户操作 (发送通知)
       ↓
API接收请求 (POST /api/tool-io-orders/{order_no}/notify)
       ↓
生成通知文本 (TextGeneratorService)
       ↓
发送飞书消息 (NotificationService)
       ↓
保存通知记录 (NotificationRepository)
       ↓
AuditService 记录日志
       ↓
返回响应
```

### 4.4 完整数据流视图

```
┌─────────┐
│  User   │
└────┬────┘
     │ HTTP Request
     ↓
┌─────────────┐
│   Flask     │
│  (API层)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Service   │
│   Layer     │
└──────┬──────┘
       │
       ├──────────────────┬──────────────────┐
       ↓                  ↓                  ↓
┌───────────┐    ┌───────────┐    ┌───────────────┐
│ Repository│    │  Text     │    │ Notification  │
│  Layer    │    │ Generator │    │   Service     │
└─────┬─────┘    └───────────┘    └───────┬───────┘
      │                                  │
      ↓                                  ↓
┌───────────┐                    ┌───────────────┐
│ SQL Server│                    │  飞书Webhook  │
└───────────┘                    └───────────────┘
```

---

## 5. 审计设计

### 5.1 审计原则

所有操作必须可追溯，记录以下信息：

- 操作人（ID、姓名、角色）
- 操作时间（精确到毫秒）
- 操作类型
- 订单ID
- 明细ID（可选）
- 变更前状态
- 变更后状态
- 操作内容

### 5.2 审计日志表结构

```
tool_io_operation_log
├── order_no (FK)
├── item_id (可选, FK)
├── operation_type
├── operator_id
├── operator_name
├── operator_role
├── from_status
├── to_status
├── operation_content
└── operation_time
```

### 5.3 审计场景

| 操作 | 日志记录 |
|------|----------|
| 创建订单 | 记录创建人和创建时间 |
| 提交订单 | 记录状态变更 draft → submitted |
| 保管员确认 | 记录状态变更 submitted → keeper_confirmed |
| 发送通知 | 记录通知内容和发送结果 |
| 最终确认 | 记录状态变更 notified → completed |
| 拒绝订单 | 记录状态变更 submitted → rejected + 拒绝原因 |
| 取消订单 | 记录状态变更 rejected/cancelled → cancelled |

---

## 6. 通知设计

### 6.1 通知类型

| 类型 | 接收人 | 触发时机 |
|------|--------|----------|
| 保管员确认请求 | 保管员 | 订单提交后 |
| 运输通知 | 运输操作员 | 保管员确认后 |
| 订单状态变更 | 申请人 | 状态变更时 |

### 6.2 通知记录

所有通知必须持久化存储：

```
tool_io_notification
├── order_no (FK)
├── notify_type
├── notify_channel (飞书/微信/邮件)
├── receiver
├── send_status (成功/失败)
├── send_time
└── response_content
```

### 6.3 飞书通知格式

```json
{
  "msg_type": "text",
  "content": {
    "text": "【工装出库通知】\n单号：IO202403150001\n工装：扳手×2、螺丝刀×1\n目的地：车间A3\n运输人：张三"
  }
}
```

---

## 7. 并发考虑

### 7.1 并发场景

- 多个班组长同时创建订单
- 班组长和保管员同时操作同一订单
- 同一工装同时被多个订单引用

### 7.2 并发控制策略

1. **数据库事务**
   - 所有状态变更使用事务保证原子性
   - 使用行级锁（SELECT FOR UPDATE）防止并发更新

2. **乐观锁**
   - 订单表添加 version 字段
   - 更新时检查版本号

3. **工装锁定**
   - 出库时锁定工装
   - 订单完成后释放锁定

### 7.3 示例代码

```python
# 伪代码示例
def update_order_status(order_no: str, new_status: str):
    with db.transaction():
        # 锁定订单行
        order = db.query("SELECT * FROM orders WHERE order_no = ? FOR UPDATE", order_no)

        # 检查当前状态
        if not can_transition(order.status, new_status):
            raise InvalidStatusTransition()

        # 更新状态
        db.execute("UPDATE orders SET status = ?, version = version + 1 WHERE order_no = ?",
                   new_status, order_no)

        # 记录日志
        audit_log(order_no, order.status, new_status)
```

---

## 8. 错误处理策略

### 8.1 错误分类

| 类别 | 示例 | 处理方式 |
|------|------|----------|
| 参数错误 | 缺少必填字段 | 返回400，提示具体错误 |
| 权限错误 | 无权限操作 | 返回403，提示权限不足 |
| 状态错误 | 非法状态转换 | 返回400，提示当前状态 |
| 业务错误 | 工装不存在 | 返回400，提示具体错误 |
| 系统错误 | 数据库连接失败 | 返回500，记录日志 |

### 8.2 响应格式

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATUS",
    "message": "当前订单状态不允许此操作",
    "details": {
      "current_status": "completed",
      "attempted_status": "submitted"
    }
  }
}
```

### 8.3 异常处理原则

1. 不暴露内部实现细节
2. 记录完整错误日志
3. 返回友好的错误信息
4. 关键操作使用事务回滚

---

## 9. 数据模型

### 9.1 核心实体关系

```
┌─────────────────────┐       ┌─────────────────────┐
│    tool_io_order    │       │      工装基本信息    │
├─────────────────────┤       ├─────────────────────┤
│ order_no (PK)      │       │ 工装ID (PK)         │
│ order_type          │       │ 工装编码             │
│ order_status        │──────→│ 工装名称             │
│ initiator_info      │       │ 工装图号             │
│ keeper_info         │       │ 工装状态             │
│ transport_info      │       │ 位置信息             │
└─────────────────────┘       └─────────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────────┐
│  tool_io_order_item │
├─────────────────────┤
│ order_no (FK)       │
│ item_id (PK)        │
│ tool_id (FK)        │
│ tool_snapshot        │
│ item_status         │
└─────────────────────┘
         │
         │ N:1
         ↓
┌─────────────────────┐
│tool_io_operation_log│
├─────────────────────┤
│ 操作ID (PK)         │
│ 出入库单号 (FK)     │
│ 明细ID (FK)        │
│ 操作类型            │
│ 操作人信息          │
│ 变更前后状态        │
│ 操作时间            │
└─────────────────────┘
```

---

## 10. API设计原则

### 10.1 RESTful规范

- 使用标准HTTP方法
- 资源命名使用名词
- 使用标准状态码

### 10.2 接口版本

- URL路径包含版本号：`/api/v1/`
- 保持向后兼容

### 10.3 安全考虑

- 参数化查询防止SQL注入
- 敏感信息加密存储
- 操作权限校验

---

## 11. 继承数据库访问约束

### 11.1 继承的CRUD模式

本项目继承自内部其他系统的数据库访问脚本，遵循以下约束：

1. **复用现有数据库模式**
   - 使用已有的 SQL Server 连接池管理
   - 复用已有的数据访问工具类
   - 不重新设计新的持久层

2. **增量集成策略**
   - 在现有数据库工具基础上扩展新表
   - 使用已有的参数化查询模式
   - 遵循现有系统的命名规范

3. **技术实现**
   - 使用 pyodbc 进行 SQL Server 数据库访问
   - 使用已有的 ConnectionPool 管理数据库连接
   - 直接使用 SQL 语句而非 ORM

### 11.2 数据访问层设计

```
┌─────────────────────────────────────┐
│          Service Layer              │
│      (业务逻辑处理)                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        DB CRUD Layer                │
│   (继承的数据库访问工具)              │
│   - ConnectionPool                  │
│   - Parameterized queries           │
│   - Transaction management           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           SQL Server                │
└─────────────────────────────────────┘
```

---

## 12. 相关文档

- [产品需求文档](./PRD.md)
