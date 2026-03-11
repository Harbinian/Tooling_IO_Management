# Implementation Plan: 工装出入库管理系统 (Tooling Inventory Management v2.0)

> Version: 2.0 (Production-Ready)
> Generated: 2026-03-11
> Planning: Claude Code (Manual Mode)

---

## 1. 业务需求升级 (Business Requirements v2.0)

### 1.1 核心使用场景 (保留)

| 场景 | 发起人 | 确认人 | 结束条件 |
|------|--------|--------|----------|
| 出库 | 班组长/计划员 | 班组长确认 | 发起人确认 |
| 入库 | 班组长/计划员 | 保管员确认 | 保管员确认 |

### 1.2 流程图 (升级版)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         工装出入库完整流程                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐  │
│  │ 发起出入库 │ -> │  保管员确认  │ -> │ 通知运输人  │ -> │  确认完成   │  │
│  │ (批量工装) │    │ (位置/状态)  │    │  (可选)     │    │             │  │
│  └──────────┘    └──────────────┘    └─────────────┘    └──────────────┘  │
│       │               │                   │                  │              │
│       v               v                   v                  v              │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │                     异常流程                                 │           │
│  │  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────────┐     │           │
│  │  │  驳回   │  │  取消  │  │ 部分可用  │  │ 通知失败   │     │           │
│  │  └────────┘  └────────┘  └──────────┘  └────────────┘     │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据模型设计 (Data Model v2.0)

### 2.1 核心表结构

#### 2.1.1 出入库单主表 (`工装出入库单_主表`)

```sql
CREATE TABLE 工装出入库单_主表 (
    -- 主键
    出入库单号 NVARCHAR(50) PRIMARY KEY,
    序列号 INT IDENTITY(1,1),

    -- 单据基本信息
    单据类型 NVARCHAR(10) NOT NULL,           -- '出库' / '入库'
    单据状态 NVARCHAR(20) NOT NULL DEFAULT '待确认',
    项目代号 NVARCHAR(50),
    用途描述 NVARCHAR(200),
    期望时间 DATETIME,
    备注 NVARCHAR(500),

    -- 发起人信息
    发起人 NVARCHAR(50) NOT NULL,
    发起人角色 NVARCHAR(20) NOT NULL,          -- '班组长' / '计划员'
    发起时间 DATETIME DEFAULT GETDATE(),

    -- 保管员信息
    保管员 NVARCHAR(50),
    保管员确认时间 DATETIME,
    保管员备注 NVARCHAR(200),

    -- 运输信息 (可选)
    运输类型 NVARCHAR(20),                     -- '叉车' / '吊车' / '人工' / NULL
    运输人 NVARCHAR(50),
    运输通知时间 DATETIME,
    运输完成时间 DATETIME,

    -- 最终确认人
    最终确认人 NVARCHAR(50),
    最终确认时间 DATETIME,

    -- 统计字段
    工装数量 INT DEFAULT 0,
    已确认数量 INT DEFAULT 0,

    -- 元数据
    创建时间 DATETIME DEFAULT GETDATE(),
    修改时间 DATETIME DEFAULT GETDATE(),
    操作人 NVARCHAR(50)
);
```

#### 2.1.2 出入库单明细表 (`工装出入库单_明细`)

```sql
CREATE TABLE 工装出入库单_明细 (
    明细ID INT IDENTITY(1,1) PRIMARY KEY,
    出入库单号 NVARCHAR(50) NOT NULL,
    工装序列号 NVARCHAR(50) NOT NULL,
    工装图号 NVARCHAR(50),
    工装名称 NVARCHAR(100),

    -- 工装状态 (独立于单据状态)
    工装状态 NVARCHAR(20) DEFAULT '待确认',    -- '待确认' / '已确认' / '已出库' / '已入库' / '已驳回' / '已取消'
    工装原位置 NVARCHAR(100),
    工装目标位置 NVARCHAR(100),
    工装备注 NVARCHAR(200),

    -- 物流信息
    运输类型 NVARCHAR(20),
    运输人 NVARCHAR(50),

    -- 时间戳
    确认时间 DATETIME,
    出入库完成时间 DATETIME,

    -- 外键
    CONSTRAINT FK_出入库单_明细 FOREIGN KEY (出入库单号)
        REFERENCES 工装出入库单_主表(出入库单号)
);
```

#### 2.1.3 操作日志表 (`工装出入库单_操作日志`)

```sql
CREATE TABLE 工装出入库单_操作日志 (
    日志ID INT IDENTITY(1,1) PRIMARY KEY,
    出入库单号 NVARCHAR(50) NOT NULL,
    明细ID INT,                                  -- NULL 表示整单操作

    操作类型 NVARCHAR(20) NOT NULL,              -- '创建' / '确认' / '驳回' / '取消' / '完成' / '修改'
    操作内容 NVARCHAR(500),

    操作人 NVARCHAR(50) NOT NULL,
    操作人角色 NVARCHAR(20) NOT NULL,
    操作时间 DATETIME DEFAULT GETDATE(),

    -- 变更前后状态
    变更前状态 NVARCHAR(50),
    变更后状态 NVARCHAR(50),

    -- 扩展信息
    客户端IP NVARCHAR(50),
    用户代理 NVARCHAR(200),

    CONSTRAINT FK_日志_出入库单 FOREIGN KEY (出入库单号)
        REFERENCES 工装出入库单_主表(出入库单号)
);
```

#### 2.1.4 通知记录表 (`工装出入库单_通知记录`)

```sql
CREATE TABLE 工装出入库单_通知记录 (
    通知ID INT IDENTITY(1,1) PRIMARY KEY,
    出入库单号 NVARCHAR(50) NOT NULL,

    通知类型 NVARCHAR(20) NOT NULL,             -- '保管员确认' / '运输通知' / '完成通知'
    通知渠道 NVARCHAR(20) NOT NULL,              -- '飞书' / '微信' / '系统'
    接收人 NVARCHAR(50) NOT NULL,
    接收人联系方式 NVARCHAR(100),

    通知标题 NVARCHAR(100),
    通知内容 NVARCHAR(2000),
    复制文本 NVARCHAR(2000),                    -- 微信可复制文本

    发送状态 NVARCHAR(20) DEFAULT '待发送',      -- '待发送' / '已发送' / '发送失败'
    发送时间 DATETIME,
    发送结果 NVARCHAR(500),
    重试次数 INT DEFAULT 0,

    创建时间 DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_通知_出入库单 FOREIGN KEY (出入库单号)
        REFERENCES 工装出入库单_主表(出入库单号)
);
```

---

## 3. 状态机设计 (State Machine v2.0)

### 3.1 单据状态

```
单据状态流转:
                    ┌──────────┐
                    │ 待确认   │ (初始状态)
                    └─────┬────┘
                          │ 保管员确认
                          v
                    ┌──────────┐
              ┌───>│ 已确认   │<───┐
              │    └─────┬────┘    │
              │          │         │ 驳回
              │          │完成     └──────────┐
              │          v                      │
              │    ┌──────────┐                 │
              │    │ 进行中   │                 │
              │    └─────┬────┘                 │
              │          │                      │
              │          │部分可用               │取消
              │          v                      │
              │    ┌──────────┐    ┌──────────┐  │
              └───<│ 已完成   │───>│  已取消  │  │
                   └──────────┘    └──────────┘  │
                         ▲                       │
                         │驳回                   │
                         └───────────────────────┘
```

### 3.2 工装状态

```
工装状态流转:
                    ┌──────────┐
                    │ 待确认   │
                    └─────┬────┘
                          │ 确认
                          v
                    ┌──────────┐
              ┌───>│ 已确认   │<───┐
              │    └─────┬────┘    │
              │          │         │ 驳回
              │          │         └──────────┐
              │          │完成                  │
              │          v                      │
              │    ┌──────────┐    ┌──────────┐│
              └───<│ 已出库   │───>│  已取消  ││
                   │ 或已入库  │    └──────────┘│
                   └──────────┘                 │
```

### 3.3 状态常量定义

```python
class InventoryStatus:
    # 单据状态
    DOC_PENDING = "待确认"        # 初始状态
    DOC_CONFIRMED = "已确认"      # 保管员已确认
    DOC_IN_PROGRESS = "进行中"    # 运输中或处理中
    DOC_COMPLETED = "已完成"      # 正常完成
    DOC_CANCELLED = "已取消"      # 被取消
    DOC_REJECTED = "已驳回"       # 被驳回

    # 工装状态
    TOOL_PENDING = "待确认"
    TOOL_CONFIRMED = "已确认"
    TOOL_CHECKOUT = "已出库"      # 出库单专用
    TOOL_CHECKIN = "已入库"       # 入库单专用
    TOOL_REJECTED = "已驳回"
    TOOL_CANCELLED = "已取消"

class OperationType:
    CREATE = "创建"
    CONFIRM = "确认"
    REJECT = "驳回"
    CANCEL = "取消"
    COMPLETE = "完成"
    MODIFY = "修改"
    NOTIFY = "通知"

class Role:
    TEAM_LEADER = "班组长"        # 可发起、确认完成
    PLANNER = "计划员"            # 可发起（未来）
    KEEPER = "保管员"             # 可确认、入库最终确认
    ADMIN = "管理员"              # 全部权限
```

---

## 4. 角色权限矩阵 (Role Permissions)

| 操作 | 班组长 | 计划员 | 保管员 | 管理员 |
|------|:------:|:------:|:------:|:------:|
| 发起出入库 | ✅ | ✅ | ❌ | ✅ |
| 查看自己发起的单据 | ✅ | ✅ | ❌ | ✅ |
| 查看全部单据 | ❌ | ❌ | ✅ | ✅ |
| 保管员确认 | ❌ | ❌ | ✅ | ✅ |
| 驳回单据 | ❌ | ❌ | ✅ | ✅ |
| 发起运输通知 | ❌ | ❌ | ✅ | ✅ |
| 确认运输完成 | ✅* | ❌ | ✅ | ✅ |
| 最终确认完成 | ✅ | ❌ | ✅* | ✅ |
| 取消单据 | ✅ | ✅ | ❌ | ✅ |
| 查看操作日志 | ❌ | ❌ | ✅ | ✅ |
| 重发通知 | ❌ | ❌ | ❌ | ✅ |

> *注: 出库单由发起人(班组长)最终确认，入库单由保管员最终确认

---

## 5. API 接口设计ful API)

 (REST### 5.1 资源化设计

| Method | Endpoint | Description | 权限 |
|--------|----------|-------------|------|
| **单据管理** | | | |
| POST | `/api/v1/inventory/orders` | 创建出入库单 | 班组长/计划员 |
| GET | `/api/v1/inventory/orders` | 查询单据列表 | 角色相关 |
| GET | `/api/v1/inventory/orders/<order_no>` | 单据详情(含明细) | 角色相关 |
| PUT | `/api/v1/inventory/orders/<order_no>` | 修改单据(待确认状态) | 发起人 |
| DELETE | `/api/v1/inventory/orders/<order_no>` | 取消单据 | 发起人/管理员 |
| **流程操作** | | | |
| POST | `/api/v1/inventory/orders/<order_no>/confirm-keeper` | 保管员确认 | 保管员 |
| POST | `/api/v1/inventory/orders/<order_no>/reject` | 驳回单据 | 保管员 |
| POST | `/api/v1/inventory/orders/<order_no>/notify-transport` | 发起运输通知 | 保管员 |
| POST | `/api/v1/inventory/orders/<order_no>/complete` | 完成确认 | 发起人/保管员 |
| **工装操作** | | | |
| PUT | `/api/v1/inventory/orders/<order_no>/items/<item_id>/confirm` | 确认单个工装 | 保管员 |
| PUT | `/api/v1/inventory/orders/<order_no>/items/<item_id>/reject` | 驳回单个工装 | 保管员 |
| **辅助接口** | | | |
| GET | `/api/v1/inventory/orders/pending-keeper` | 待保管员确认列表 | 保管员 |
| GET | `/api/v1/inventory/orders/pending-transport` | 待运输列表 | 运输人 |
| GET | `/api/v1/inventory/tools/search` | 搜索可用工装 | 班组长/计划员 |
| GET | `/api/v1/inventory/orders/<order_no>/notification-draft` | 预览通知文案 | 保管员 |
| **日志与统计** | | | |
| GET | `/api/v1/inventory/orders/<order_no>/logs` | 操作日志 | 保管员/管理员 |
| GET | `/api/v1/inventory/notifications/<notification_id>/retry` | 重发通知 | 管理员 |
| GET | `/api/v1/inventory/stats` | 统计看板 | 管理员 |

### 5.2 请求/响应示例

#### 创建出入库单

```json
// POST /api/v1/inventory/orders
Request:
{
    "type": "出库",
    "project_code": "C2026-001",
    "purpose": "某项目测试使用",
    "expected_time": "2026-03-20T10:00:00",
    "remark": "急用",
    "items": [
        {"serial_no": "TZ-001", "target_location": "车间A-工位1"},
        {"serial_no": "TZ-002", "target_location": "车间A-工位2"}
    ]
}

Response:
{
    "success": true,
    "data": {
        "order_no": "CK-20260311-001",
        "status": "待确认",
        "created_at": "2026-03-11T09:30:00",
        "items_count": 2
    }
}
```

#### 保管员确认

```json
// POST /api/v1/inventory/orders/CK-20260311-001/confirm-keeper
Request:
{
    "keeper": "张三",
    "remark": "工装状态良好",
    "items": [
        {"serial_no": "TZ-001", "current_location": "货架A-3", "status": "已确认"},
        {"serial_no": "TZ-002", "current_location": "货架A-4", "status": "已确认"}
    ]
}
```

---

## 6. 异常流程设计 (Exception Flows)

### 6.1 驳回 (Reject)

- **触发者**: 保管员
- **原因**: 工装位置不对、状态异常、数量不足
- **影响**:
  - 单据状态 → "已驳回"
  - 被驳回工装状态 → "已驳回"
  - 记录操作日志
  - 通知发起人

### 6.2 取消 (Cancel)

- **触发者**: 发起人、管理员
- **前提**: 单据状态为 "待确认" 或 "已确认"
- **影响**:
  - 单据状态 → "已取消"
  - 所有工装状态 → "已取消"
  - 记录操作日志

### 6.3 部分可用 (Partial Available)

- **场景**: 部分工装无法出库/入库
- **处理**:
  - 正常工装状态 → "已确认"
  - 异常工装状态 → "已驳回" + 备注原因
  - 单据状态 → "进行中" (部分完成)
  - 记录操作日志

### 6.4 通知失败 (Notification Failed)

- **场景**: 飞书Webhook调用失败
- **处理**:
  - 通知状态 → "发送失败"
  - 记录错误信息
  - 提供重试机制（管理员手动重试）
  - 自动重试3次后标记

---

## 7. 通知文案模板 (Notification Templates)

### 7.1 飞书通知 (Markdown格式)

#### 保管员确认通知

```markdown
## 📋 工装出入库申请

**单号**: CK-20260311-001
**类型**: 出库
**发起人**: 班组长A (班组长)
**项目**: C2026-001
**期望时间**: 2026-03-20

### 工装明细
| 序列号 | 图号 | 名称 | 目标位置 |
|--------|------|------|----------|
| TZ-001 | GZ-001 | 焊接夹具 | 车间A-工位1 |
| TZ-002 | GZ-002 | 定位器   | 车间A-工位2 |

**请确认工装位置和状态**
```

#### 运输通知

```markdown
## 🚚 运输任务

**单号**: CK-20260311-001
**运输类型**: 叉车

### 工装信息
- 序列号: TZ-001, TZ-002
- 当前位置: 立体库A区
- 目标位置: 车间A

### 联系人
- 发起人: 班组长A
- 保管员: 张三
```

### 7.2 微信复制文本 (纯文本)

#### 保管员确认请求

```
【工装出库申请】
单号：CK-20260311-001
类型：出库
发起人：班组长A (班组长)
项目代号：C2026-001
期望时间：2026-03-20 10:00

工装明细：
1. TZ-001 - 焊接夹具 - 目标位置：车间A-工位1
2. TZ-002 - 定位器 - 目标位置：车间A-工位2

请确认工装位置和状态，谢谢！
```

#### 运输任务通知

```
【运输任务通知】
单号：CK-20260311-001
运输类型：叉车

工装：
- TZ-001 (焊接夹具)
- TZ-002 (定位器)

从：立体库A区
到：车间A

联系人：
- 发起人：班组长A (电话: 138xxxx)
- 保管员：张三 (电话: 139xxxx)

请前往运输，谢谢！
```

---

## 8. 文件变更清单 (File Changes)

### 8.1 新建文件

| File | Description |
|------|-------------|
| `services/inventory_service.py` | 出入库业务逻辑服务 |
| `models/inventory_models.py` | 数据模型和状态常量 |
| `templates/inventory/order_form.html` | 创建/编辑单据页面 |
| `templates/inventory/order_list.html` | 单据列表页面 |
| `templates/inventory/order_detail.html` | 单据详情页面 |
| `templates/inventory/keeper_confirm.html` | 保管员确认页面 |
| `templates/inventory/notification_preview.html` | 通知预览页面 |
| `static/js/inventory/*.js` | 前端交互脚本 |

### 8.2 修改文件

| File | Changes |
|------|---------|
| `database.py` | 新增出入库相关查询方法 |
| `web_server.py` | 新增 RESTful API 路由 |
| `utils/feishu_api.py` | 新增通知发送方法 |
| `config/settings.py` | 新增配置项 |

---

## 9. 实施步骤 (Implementation Steps)

### Phase 1: 数据层 (1-2天)
- [ ] 1.1 创建数据库表 (主表+明细表+日志表+通知表)
- [ ] 1.2 实现 database.py 中的 CRUD 方法
- [ ] 1.3 实现状态流转校验逻辑

### Phase 2: 业务层 (2-3天)
- [ ] 2.1 创建 inventory_service.py 服务类
- [ ] 2.2 实现各角色权限校验
- [ ] 2.3 实现通知文案生成器
- [ ] 2.4 实现飞书/微信通知发送

### Phase 3: API层 (2-3天)
- [ ] 3.1 实现 RESTful API 端点
- [ ] 3.2 实现异常处理和参数校验
- [ ] 3.3 实现操作日志记录中间件

### Phase 4: 前端层 (3-5天)
- [ ] 4.1 工装搜索和批量选择组件
- [ ] 4.2 出入库单创建/编辑页面
- [ ] 4.3 单据列表和详情页面
- [ ] 4.4 保管员确认工作台
- [ ] 4.5 通知预览和复制功能

### Phase 5: 测试与优化 (1-2天)
- [ ] 5.1 接口测试
- [ ] 5.2 异常流程测试
- [ ] 5.3 性能优化
- [ ] 5.4 文档编写

---

## 10. 风险与缓解 (Risks & Mitigation)

| 风险 | 缓解措施 |
|------|----------|
| 批量操作事务一致性 | 使用数据库事务，失败自动回滚 |
| 并发修改冲突 | 乐观锁 + 状态校验 |
| 通知失败丢失 | 通知记录表 + 重试机制 |
| 权限绕过 | API层 + 服务层双重校验 |
| 工装状态不一致 | 状态机强制约束 |

---

## SESSION_ID
- CODEX_SESSION: N/A (Manual Planning)
- GEMINI_SESSION: N/A (Manual Planning)

---

*End of Plan v2.0*
