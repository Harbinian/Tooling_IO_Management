# 飞书通知中文化改进

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00076
Goal: 飞书通知预览文本中文化，添加缺失字段，使用分体数量
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

当前飞书通知功能存在以下问题：
1. **英文输出可读性差**：同事们英文水平一般，需要中文输出
2. **缺失字段**：运输通知缺少部门(`department`)、需求日期(`required_by`)
3. **工装数量 vs 分体数量**：需将工装数量改为分体数量(`split_quantity`)

核心文件：
- `backend/services/tool_io_service.py` - 通知文本生成函数
- `backend/services/notification_service.py` - 通知服务模板

---

## Required References / 必需参考

- `.claude/rules/00_core.md` - 核心开发规则（UTF-8编码、字段名常量）
- `.claude/rules/01_workflow.md` - ADP四阶段开发流程
- `backend/database/schema/column_names.py` - 字段名常量定义
- `backend/database/repositories/order_repository.py` 第399-410行 - split_quantity SQL查询

---

## Core Task / 核心任务

### 1. 修改 `_extract_item_values` 函数

**文件**: `backend/services/tool_io_service.py` 第1362-1371行

在返回字典中添加 `split_quantity` 字段提取：
```python
def _extract_item_values(item: Dict) -> Dict:
    return {
        "serial_no": _pick_value(item, ["serial_no", "tool_code"], ""),
        "tool_name": _pick_value(item, ["tool_name"], ""),
        "drawing_no": _pick_value(item, ["drawing_no"], ""),
        "location_text": _pick_value(item, ["location_text"], ""),
        "apply_qty": _pick_value(item, ["apply_qty"], 1),
        "approved_qty": _pick_value(item, ["approved_qty"], 0),
        "split_quantity": _pick_value(item, ["split_quantity"], 0),  # 新增
        "item_status": _pick_value(item, ["item_status", "status"], ""),
    }
```

### 2. 修改 `generate_keeper_text` 函数

**文件**: `backend/services/tool_io_service.py` 第1373-1408行

**修改 items_text 格式**（使用分体数量，中文标签）：
```python
items_text = "\n".join(
    [
        f"{idx + 1}. {item['serial_no']} / {item['tool_name'] or '-'} / 图号 {item['drawing_no'] or '-'} / 数量 {item['split_quantity'] or item['apply_qty'] or 1}"
        for idx, item in enumerate(items)
    ]
) or "- 无明细"
```

**修改 text 整体为中文**：
```python
text = (
    f"出库保管员确认请求\n"
    f"单号：{summary['order_no'] or order_no}\n"
    f"申请人：{summary['initiator_name'] or '-'}（{summary['initiator_id'] or '-'}）\n"
    f"部门：{summary['department'] or '-'}\n"
    f"需求日期：{summary['required_by'] or '-'}\n"
    f"备注：{summary['remark'] or '-'}\n"
    f"创建时间：{_format_order_datetime(summary['created_at'])}\n"
    f"提交时间：{_format_order_datetime(summary['submitted_at'])}\n\n"
    f"申请明细：\n{items_text}\n\n"
    "请确认订单明细并完成保管员审核。"
)
```

**order_label 改为中文**：
```python
order_label = "出库" if summary["order_type"] == "outbound" else "入库"
```

**修改通知标题为中文**：
```python
title="保管员确认请求",
```

### 3. 修改 `generate_transport_text` 函数

**文件**: `backend/services/tool_io_service.py` 第1411-1459行

**添加 department 和 required_by**：
```python
department = summary.get("department", "-")
required_by = summary.get("required_by", "-")
```

**修改 items_text**（使用分体数量）：
```python
items_text = "\n".join(
    [
        f"{idx + 1}. {item['location_text'] or '-'} / {item['tool_name'] or '-'} / {item['serial_no']} / 数量 {item['split_quantity'] or item['approved_qty'] or 1}"
        for idx, item in enumerate(approved_items)
    ]
)
```

**修改 text 整体为中文**：
```python
text = (
    f"运输准备通知\n"
    f"单号：{summary['order_no'] or order_no}\n"
    f"运输类型：{transport_type}\n"
    f"申请人：{summary['initiator_name'] or '-'}\n"
    f"部门：{department}\n"
    f"需求日期：{required_by}\n"
    f"运输接收人：{summary['transport_assignee_name'] or '-'}\n\n"
    f"确认明细：\n{items_text}\n\n"
    "请根据确认的工装清单安排运输。"
)
```

**修改 wechat_text 整体为中文**：
```python
wechat_text = (
    f"工装运输通知\n"
    f"单号：{summary['order_no'] or order_no}\n"
    f"运输类型：{transport_type}\n\n"
    f"取货地点：{approved_items[0]['location_text'] or '-'}\n"
    f"接收人：{summary['transport_assignee_name'] or '-'}\n\n"
    + "\n".join([f"- {item['serial_no']} ({item['tool_name'] or '-'})" for item in approved_items])
    + f"\n\n申请人：{summary['initiator_name'] or '-'} / 保管员：{summary['keeper_name'] or '-'}"
)
```

**修改通知标题为中文**：
```python
title="运输预览通知",
```

### 4. 修改 `notification_service.py` 模板

**文件**: `backend/services/notification_service.py` 第32-54行

**修改 _TITLE_TEMPLATES 为中文**：
```python
_TITLE_TEMPLATES = {
    ORDER_CREATED: "出入库单 {order_no} 已创建",
    ORDER_SUBMITTED: "出入库单 {order_no} 已提交",
    KEEPER_CONFIRM_REQUIRED: "出入库单 {order_no} 需要保管员确认",
    TRANSPORT_REQUIRED: "出入库单 {order_no} 需要运输处理",
    TRANSPORT_STARTED: "出入库单 {order_no} 运输已开始",
    TRANSPORT_COMPLETED: "出入库单 {order_no} 运输已完成",
    ORDER_COMPLETED: "出入库单 {order_no} 已完成",
    ORDER_CANCELLED: "出入库单 {order_no} 已取消",
    ORDER_REJECTED: "出入库单 {order_no} 已驳回",
}
```

**修改 _BODY_TEMPLATES 为中文**：
```python
_BODY_TEMPLATES = {
    ORDER_CREATED: "出入库单 {order_no} 已由 {actor_name} 创建为草稿。",
    ORDER_SUBMITTED: "出入库单 {order_no} 已由 {actor_name} 提交。",
    KEEPER_CONFIRM_REQUIRED: "出入库单 {order_no} 已提交，需要保管员确认。",
    TRANSPORT_REQUIRED: "出入库单 {order_no} 已通过保管员确认，需要运输处理。",
    TRANSPORT_STARTED: "出入库单 {order_no} 的运输已开始，工装正在搬运中。",
    TRANSPORT_COMPLETED: "出入库单 {order_no} 的运输已完成，订单可以进行最终确认。",
    ORDER_COMPLETED: "出入库单 {order_no} 已由 {actor_name} 完成。",
    ORDER_CANCELLED: "出入库单 {order_no} 已由 {actor_name} 取消。",
    ORDER_REJECTED: "出入库单 {order_no} 已由 {actor_name} 驳回。",
}
```

---

## Required Work / 必需工作

1. 修改 `_extract_item_values` 添加 `split_quantity` 提取
2. 修改 `generate_keeper_text` 中文化并使用分体数量
3. 修改 `generate_transport_text` 中文化，添加 department/required_by，使用分体数量
4. 修改 `notification_service.py` 的标题和正文模板中文化
5. 语法检查所有修改的文件
6. 启动后端服务验证 API 返回正确中文

---

## Constraints / 约束条件

1. **UTF-8 编码**：所有文件使用 `encoding='utf-8'`
2. **字段名常量**：使用 `column_names.py` 中定义的常量
3. **split_quantity fallback**：使用 `split_quantity or apply_qty` 保证空值安全
4. **不回退已有字段**：仅修改文本输出，不改变 API 返回字段结构
5. **中文标点**：使用中文冒号 `：` 和句号 `。`

---

## Completion Criteria / 完成标准

1. `generate_keeper_text` 返回的 `text` 字段全部为中文
2. `generate_transport_text` 返回的 `text` 和 `wechat_text` 字段全部为中文
3. `generate_transport_text` 输出包含 `部门：` 和 `需求日期：` 字段
4. items 列表中使用分体数量（`split_quantity`）替代工装数量
5. `notification_service.py` 的模板全部为中文
6. 语法检查通过：`python -m py_compile backend/services/tool_io_service.py backend/services/notification_service.py`
