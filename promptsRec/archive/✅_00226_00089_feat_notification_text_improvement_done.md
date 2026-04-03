Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00089
Goal: 修改飞书/微信通知文本为分层策略（保管员短讯、生产准备工详情）
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

工装出入库管理系统的飞书/微信通知文本当前全部采用详细格式，保管员收到的消息冗长，且纯 MD 表格在部分客户端渲染异常。

需求文档：`docs/REQUIREMENTS/REQ-20260403-001_notification_text_improvement.md`

**分层策略**：
- **保管员** (`notify_keeper`)：短讯式，≤50字，含单号，无明细
- **生产准备工** (`notify_transport`)：详细式，含时间/地点/人物/序列号/图号/库位

---

## Required References / 必需参考

- `backend/services/tool_io_service.py` - 通知文本生成函数
- `backend/services/feishu_notification_adapter.py` - 飞书通知适配器
- `backend/database/schema/column_names.py` - 字段名常量
- `docs/REQUIREMENTS/REQ-20260403-001_notification_text_improvement.md` - 需求文档

---

## Core Task / 核心任务

修改 `tool_io_service.py` 中的文本生成函数，实现分层通知策略：

### 1. `_build_keeper_text()` → 改为短讯模板

当前：详细格式，包含所有明细
目标：短讯格式，≤50字，含单号

**目标模板**：
```
【工装管理系统】您有待处理订单，单号 {order_no}，请登录系统查看。
```

### 2. `preview_keeper_text()` → 同步更新

当前调用 `_build_keeper_text()` 生成预览
目标：同步使用新的短讯模板

**预览模板**（与正式通知一致）：
```
【工装管理系统】您有待处理订单，单号 {order_no}，请登录系统查看。
```

### 3. `generate_transport_text()` → 优化为结构化换行文本

当前：较详细，但格式可优化
目标：纯文本换行格式，明确字段标签，禁止 MD 表格

**目标模板**：
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

请根据确认的工装清单安排运输。
```

`wechat_text` 同步调整为结构化换行格式。

---

## Required Work / 必需工作

### Phase 1: 数据确认
1. 确认 `order_no`、`order_type`、`required_by` 等字段的访问路径（通过 `_pick_value` 或字典 key）
2. 确认工装明细中 `serial_no`、`tool_name`、`drawing_no`、`split_quantity`/`approved_qty`、`location_text` 的访问路径

### Phase 2: 实现
1. 修改 `_build_keeper_text()` 为短讯模板
2. 修改 `preview_keeper_text()` 中的 `return` 语句，直接构造短讯文本（不调用 `_build_keeper_text`）
3. 修改 `generate_transport_text()` 中的 `text` 和 `wechat_text` 构造逻辑，使用结构化换行格式

### Phase 3: 验证
1. 后端语法检查：`python -m py_compile backend/services/tool_io_service.py`
2. 人工 Review 生成的文本格式是否符合预期

---

## Constraints / 约束条件

1. **仅修改文本格式**，不修改触发逻辑、不增加 API
2. `notify_keeper` 文本 ≤ 50 字（不含换行）
3. 所有文本使用换行符分隔字段，**禁止 MD 表格格式**
4. 保持 `wechat_text` 与飞书文本风格一致
5. 字段名使用 `column_names.py` 中的常量
6. UTF-8 编码，无 BOM

---

## Completion Criteria / 完成标准

1. [ ] `_build_keeper_text()` 输出短讯格式（≤50字，含单号，无明细列表）
2. [ ] `preview_keeper_text()` 输出与正式通知一致的短讯格式
3. [ ] `generate_transport_text()` 输出结构化换行文本（包含：单号、运输类型、需求日期、取货地点、接收人、工装明细）
4. [ ] `wechat_text` 同步为结构化换行格式
5. [ ] 无 MD 表格格式（无 `|` 分隔符）
6. [ ] 后端语法检查通过：`python -m py_compile backend/services/tool_io_service.py`
7. [ ] 不破坏现有调用方（`notify_keeper`、`notify_transport` 的调用逻辑不变）
