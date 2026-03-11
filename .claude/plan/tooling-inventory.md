# Implementation Plan: 工装出入库管理模块 (Tooling In/Out Management)

## Task Type
- [ ] Frontend (→ Gemini)
- [x] Backend (→ Codex)
- [x] Fullstack (→ Parallel)

---

## 1. 业务需求分析 (Business Requirements)

### 1.1 核心使用场景

| 场景 | 发起人 | 确认人 | 结束条件 |
|------|--------|--------|----------|
| 出库 | 班组长 | 班组长确认 | 发起人确认 |
| 入库 | 班组长 | 工装保管员 | 保管员确认 |

### 1.2 流程描述

```
[班组长] 发起出入库 → [系统] 生成结构化需求文字 → [工装保管员] 确认位置和状态
    → [系统] 通知叉车工/吊车工（飞书/微信） → [班组长/保管员] 确认完成
```

### 1.3 结构化输出需求

1. **工装使用需求** (班组长 → 保管员):
   - 工装序列号、图号、名称
   - 用途/项目代号
   - 需求数量
   - 期望使用时间

2. **运输通知** (保管员 → 叉车工/吊车工):
   - 工装当前位置（货架/区域）
   - 目标位置
   - 工装信息摘要
   - 紧急程度

---

## 2. Technical Solution

### 2.1 数据库设计

需要新建 **工装出入库记录表**:

```sql
CREATE TABLE 工装出入库记录 (
    出入库ID INT IDENTITY(1,1) PRIMARY KEY,
    出入库类型 NVARCHAR(10) NOT NULL,  -- '出库' / '入库'
    派工号 NVARCHAR(50),
    工装序列号 NVARCHAR(50) NOT NULL,
    工装图号 NVARCHAR(50),
    工装名称 NVARCHAR(100),
    发起人 NVARCHAR(50) NOT NULL,
    发起时间 DATETIME DEFAULT GETDATE(),
    保管员确认 NVARCHAR(50),
    保管员确认时间 DATETIME,
    运输类型 NVARCHAR(20),  -- '叉车' / '吊车' / '人工'
    运输人 NVARCHAR(50),
    运输通知时间 DATETIME,
    当前状态 NVARCHAR(20) DEFAULT '待确认',  -- '待确认' / '运输中' / '已完成'
    原位置 NVARCHAR(100),
    目标位置 NVARCHAR(100),
    备注 NVARCHAR(500),
    -- 飞行区字段
    项目代号 NVARCHAR(50),
    用途描述 NVARCHAR(200),
    期望时间 DATETIME
);
```

### 2.2 API 端点设计

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/inventory/create` | 发起出入库 |
| GET | `/api/inventory/list` | 列表查询（支持筛选） |
| GET | `/api/inventory/<id>` | 详情 |
| POST | `/api/inventory/<id>/confirm-keeper` | 保管员确认 |
| POST | `/api/inventory/<id>/confirm-transport` | 运输人确认 |
| POST | `/api/inventory/<id>/complete` | 完成确认 |
| GET | `/api/inventory/pending-keeper` | 待保管员确认列表 |
| GET | `/api/inventory/pending-transport` | 待运输列表 |
| GET | `/api/inventory/search-tools` | 搜索工装（批量选择） |
| GET | `/api/inventory/generate-notification` | 生成通知文字 |

### 2.3 飞书通知集成

利用现有的 `FeishuBase.send_webhook_message()`:

```python
def send_transport_notification(transporter: str, tool_info: dict, from_loc: str, to_loc: str):
    message = f"""🚚 运输任务通知

接收人: {transporter}
━━━━━━━━━━━━━━━━━━━━━━
📦 工装信息:
   序列号: {tool_info['serial_no']}
   图号: {tool_info['drawing_no']}
   名称: {tool_info['tool_name']}

📍 运输路线:
   从: {from_loc}
   到: {to_loc}

⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    # 发送到叉车工/吊车工群
    webhook_url = os.getenv("FEISHU_WEBHOOK_TRANSPORT")
    return feishu.send_webhook_message(webhook_url, message, "text")
```

---

## 3. Implementation Steps

### Phase 1: 数据库层 (Database Layer)

#### Step 1.1: 新增数据库方法
- **File**: `database.py`
- **Operation**: Add new methods
- **Description**:
  - `create_inventory_record()` - 创建出入库记录
  - `get_inventory_records()` - 查询出入库记录
  - `update_inventory_status()` - 更新状态
  - `search_tools_for_inventory()` - 搜索可用工装

#### Step 1.2: 创建数据表
- **File**: `database.py`
- **Operation**: Add table creation logic
- **Description**: 首次启动时自动创建 `工装出入库记录` 表

---

### Phase 2: 业务逻辑层 (Business Logic Layer)

#### Step 2.1: 创建出入库服务
- **File**: `services/inventory_service.py` (New)
- **Description**:
  - `create_checkout()` - 发起出库
  - `create_checkin()` - 发起入库
  - `generate_tool_requirement_text()` - 生成工装需求文字
  - `generate_transport_notification()` - 生成运输通知文字
  - `notify_transporter()` - 发送飞书通知

#### Step 2.2: 保管员确认处理
- **File**: `services/inventory_service.py`
- **Description**:
  - `keeper_confirm()` - 保管员确认位置和状态
  - 自动触发运输通知

#### Step 2.3: 运输完成处理
- **File**: `services/inventory_service.py`
- **Description**:
  - `transport_complete()` - 运输完成
  - 根据出入库类型决定最终确认人

---

### Phase 3: API 层 (API Layer)

#### Step 3.1: 添加 Flask 路由
- **File**: `web_server.py`
- **Operation**: Add routes
- **Description**:
  - `/inventory` - 出入库管理首页
  - `/api/inventory/*` - REST API 端点

#### Step 3.2: 实现 API 端点
- **File**: `web_server.py`
- **Operation**: Add endpoint implementations
- **Description**: 实现所有 Step 2.1 设计的端点

---

### Phase 4: 前端层 (Frontend Layer)

#### Step 4.1: 工装选择组件
- **File**: `templates/inventory/` (New directory)
- **Description**:
  - 工装搜索框（支持模糊搜索）
  - 工装批量选择表格
  - 已选工装列表展示

#### Step 4.2: 出入库表单
- **File**: `templates/inventory/form.html` (New)
- **Description**:
  - 出库/入库类型选择
  - 工装选择（调用 Step 4.1）
  - 项目代号/用途输入
  - 期望时间选择

#### Step 4.3: 保管员确认页面
- **File**: `templates/inventory/keeper_confirm.html` (New)
- **Description**:
  - 展示待确认的出入库申请
  - 位置和状态输入
  - 运输类型选择（叉车/吊车/人工）

#### Step 4.4: 列表与详情页
- **File**: `templates/inventory/list.html` (New)
- **Description**:
  - 出入库记录列表
  - 筛选和搜索
  - 详情查看

---

## 4. Key Files

| File | Operation | Description |
|------|-----------|-------------|
| `database.py` | Modify | Add inventory-related query methods |
| `services/inventory_service.py` | Create | Business logic for in/out operations |
| `web_server.py` | Modify | Add inventory API endpoints |
| `templates/inventory/form.html` | Create | In/out request form |
| `templates/inventory/keeper_confirm.html` | Create | Keeper confirmation page |
| `templates/inventory/list.html` | Create | In/out records list |
| `utils/feishu_api.py` | Modify (if needed) | Add transport notification method |

---

## 5. Data Flow

### 5.1 出库流程

```
1. 班组长选择工装 → POST /api/inventory/create (type='出库')
2. 系统生成需求文字，状态='待确认'
3. 保管员收到通知 → GET /api/inventory/pending-keeper
4. 保管员确认位置/状态 → POST /api/inventory/<id>/confirm-keeper
5. 系统发送飞书通知给运输人
6. 运输人完成运输 → POST /api/inventory/<id>/complete
7. 班组长确认 → 状态='已完成'，出库流程结束
```

### 5.2 入库流程

```
1. 班组长选择工装 → POST /api/inventory/create (type='入库')
2. 系统生成需求文字，状态='待确认'
3. 保管员收到通知 → GET /api/inventory/pending-keeper
4. 保管员确认位置/状态 → POST /api/inventory/<id>/confirm-keeper
5. 系统发送飞书通知给运输人
6. 运输人完成运输 → POST /api/inventory/<id>/complete
7. 保管员最终确认 → 状态='已完成'，入库流程结束
```

---

## 6. Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| 工装位置信息不完整 | 在 `get_tool_basic_info()` 中扩展查询位置字段 |
| 飞书 Webhook 配置缺失 | 使用环境变量 `FEISHU_WEBHOOK_TRANSPORT`，无配置则跳过通知 |
| 并发出入库冲突 | 数据库层面使用事务锁，状态机校验 |
| 移动端适配 | 前端使用响应式设计 |

---

## 7. Next Steps (User Approval Required)

1. **批准计划**: 请确认以上方案是否符合业务需求
2. **启动开发**: 执行 `/ccg:execute` 开始后端开发
3. **并行开发**: Codex 实现后端，Gemini 设计前端

---

## SESSION_ID (for /ccg:execute use)
- CODEX_SESSION: N/A (manual planning)
- GEMINI_SESSION: N/A (manual planning)

---

*Generated: 2026-03-11*
*Planning Tool: Claude Code (Multi-Model Collaborative Planning fallback)*
