# 需求：飞书/微信通知文本格式优化 - 分层通知策略

## 基本信息 / Basic Information
- 需求编号：REQ-20260403-001
- 创建日期：2026-04-03
- 状态：已完善

## 5W2H 分析 / 5W2H Analysis

### What - 核心需求

**功能描述**：

对工装出入库管理系统的飞书/微信通知文本进行分层优化，采用不同的详细程度：

1. **保管员通知 (`notify_keeper`)**
   - 触发时机：订单提交后
   - 通知风格：**短讯式**
   - 内容：包含单号，告知"您有新订单需要处理，请登录系统查看"
   - 示例：`【工装管理系统】您有待处理订单，单号 TO-OUT-20260403-001，请登录系统查看。`
   - 不包含明细列表

2. **生产准备工通知 (`notify_transport`)**
   - 触发时机：保管员确认后（keeper_confirmed）
   - 通知风格：**详细式**
   - 必须包含字段：
     - 时间：订单需求日期（出库时间/入库时间）
     - 地点：库位信息（取货地点/送货地点）
     - 人物：申请人、保管员
     - 工装序列号
     - 图号
     - 运输类型
   - 格式：纯文本 + 换行符，禁止 MD 表格（防止渲染崩溃）

**输入**：
- 订单数据（来自 `tool_io_order` + `tool_io_order_item`）
- 工装主数据（来自 `Tooling_ID_Main`）
- 库位信息（来自 `tool_io_location`）

**输出**：
- 飞书通知文本（`notify_keeper` → 短讯）
- 飞书通知文本（`notify_transport` → 详情）
- 微信 copy 文本（同步调整）

---

### Why - 动机与价值

**业务背景**：
- 当前通知文本全部采用详细格式，保管员收到的消息冗长
- 纯 MD 格式（表格）在部分客户端渲染异常
- 保管员需要在移动端快速浏览，核心诉求是"有订单来了"，而非明细

**预期价值**：
- 保管员：快速知晓待处理，提升移动端体验
- 生产准备工：获得完整信息（时间地点人物工装），减少沟通成本

**成功标准**：
- 保管员通知文本 ≤ 50 字
- 生产准备工通知文本结构清晰，换行分隔字段
- 两种通知在飞书/微信均可正常显示，无渲染异常

---

### Who - 角色与用户

**主要用户**：
| 角色 | 接收通知类型 | 通知风格 |
|------|------------|---------|
| 保管员 (keeper) | `notify_keeper` | 短讯式 |
| 生产准备工/运输员 | `notify_transport` | 详细式 |

**开发负责人**：待定

**受影响者**：
- 保管员：减少信息噪音
- 生产准备工：获得更完整的任务信息

---

### When - 时间线

**期望完成时间**：本周内（2026-04-03 ~ 2026-04-09）

**使用频率**：实时（每次订单状态变更触发）

**优先级**：P1

---

### Where - 使用场景

**使用环境**：生产环境，移动端（飞书/微信）优先

**集成需求**：
- `backend/services/tool_io_service.py` 中的 `generate_keeper_text()` 和 `generate_transport_text()`
- 飞书通知适配器 `feishu_notification_adapter.py`

**约束条件**：
- 不修改通知触发逻辑（仅修改文本内容）
- 不增加新 API
- 保持 `wechat_text` 与飞书文本风格一致

---

### How - 实现方式

**建议实现方式**：

1. **修改 `_build_keeper_text()`**
   - 改为短讯模板
   - 示例：`【工装管理系统】您有待处理订单，单号 {order_no}，请登录系统查看。`

2. **修改 `generate_transport_text()`**
   - 优化格式，使用换行符而非表格
   - 明确字段标签（时间、地点、序列号、图号、库位）
   - 示例：
     ```
     【运输准备通知】
     单号：{order_no}
     运输类型：{transport_type}
     需求日期：{required_by}
     取货地点：{location}
     接收人：{receiver}

     工装明细：
     {serial_no} / {tool_name} / 图号 {drawing_no} / 数量 {qty}
     ...
     ```

**参考系统**：现有 `tool_io_service.py` 中的 `_build_keeper_text()` 和 `generate_transport_text()`

**技术栈**：Python（后端文本生成），不改前端

---

### How Much - 资源与范围

**范围**：

包含：
- [ ] `generate_keeper_text()` 改为短讯式模板
- [ ] `generate_transport_text()` 优化为结构化换行文本（字段名: 值）
- [ ] `wechat_text` 同步调整
- [ ] 预览功能 `preview_keeper_text()` 同步更新

不包含：
- [ ] 通知触发逻辑修改
- [ ] 新增通知渠道
- [ ] 前端界面修改

**资源需求**：
- 后端文本模板调整：约 1-2 小时
- 测试验证：约 1 小时

---

## 待确认问题 / Open Questions

- [x] 保管员短讯是否需要包含订单号（方便在系统中搜索）？→ ✅ 需要
- [x] 生产准备工详情的时间：使用订单的 `required_by`（需求日期）
- [x] 地点：使用库位 `location_text`
- [x] 序列号、图号、库位：来自订单明细项
- [x] `notify_keeper` 的预览功能（`preview_keeper_text`）是否也需要更新为短讯风格？→ ✅ 同步更新，保持一致

---

## 验收标准 / Acceptance Criteria

1. [ ] `notify_keeper` 通知文本 ≤ 50 字，包含单号，不包含明细列表
2. [ ] `notify_transport` 通知文本包含：单号、运输类型、需求日期、取货地点、接收人、工装明细（序列号/名称/图号/数量）
3. [ ] 所有文本使用换行符分隔字段，不使用 MD 表格格式
4. [ ] 飞书/微信显示正常，无渲染异常
5. [ ] 预览功能 `preview_keeper_text` 与实际发送文本风格一致
6. [ ] 后端语法检查通过：`python -m py_compile backend/services/tool_io_service.py`

---

## 关联文档 / Related Documents

- `docs/PRD.md` - 产品需求定义
- `docs/API_SPEC.md` - API 接口规范
- `backend/services/tool_io_service.py` - 通知文本生成函数
- `backend/services/feishu_notification_adapter.py` - 飞书通知适配器
