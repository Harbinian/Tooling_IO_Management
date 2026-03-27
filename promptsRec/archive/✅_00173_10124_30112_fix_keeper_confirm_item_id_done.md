# BUG 修复: keeper-confirm API 参数不匹配

## 任务编号
- **执行顺序号**: 00173
- **类型编号**: 10124
- **任务类型**: Bug修复任务 (10101-19999)

## 问题描述

### 症状
```
'error': 'no items were updated - check item identifiers'
```

keeper-confirm API 调用失败，订单无法完成保管员确认步骤。

### 根本原因
`api_e2e.py` 的 `step_keeper_confirm` 函数传递的 items 缺少必需的 `item_id` 主键：

**api_e2e.py:758-765 (当前代码)**:
```python
"items": [{
    "tool_code": TEST_TOOL["serial_no"],
    "location_id": 1,
    "location_text": "仓库A-1",
    "check_result": "approved",
    "approved_qty": 1,
    "status": "approved"
}]
```

**order_repository.py:580-583 (要求的参数)**:
```python
item_id = item.get('item_id')
if not item_id:
    logger.warning(f"keeper_confirm: item_id missing for order {order_no}, skipping item update")
    continue
```

Repository 的 `keeper_confirm` 方法**必须使用 `item_id` 作为主键**来精确更新每一项。当 `item_id` 缺失时，所有 item 都被跳过，导致 `updated_items_count == 0` 从而返回错误。

### 数据流分析
1. `step_create_order` 调用 `POST /tool-io-orders` 创建订单
2. 创建响应只返回 `{"success": True, "order_no": "..."}`，不包含 `item_id`
3. `step_submit_order` 提交订单
4. `step_keeper_confirm` 尝试确认但传递的 items 没有 `item_id`
5. Repository 因缺少 `item_id` 而跳过所有 item 更新

## 修复方案

### 修改文件: `test_runner/api_e2e.py`

#### 方案: 在 keeper_confirm 前获取 order detail 以提取 item_id

**修改 `step_keeper_confirm` 函数**:

找到函数签名 (约第743行):
```python
def step_keeper_confirm(order_no: str, token: str, user_id: int,
                        transport_assignee_id: str, orchestrator=None) -> tuple:
```

修改为:
```python
def step_keeper_confirm(order_no: str, token: str, user_id: int,
                        transport_assignee_id: str, orchestrator=None,
                        order_items: list = None) -> tuple:
    """
    步骤: keeper_confirm - 保管员确认

    Args:
        order_no: 订单号
        token: 认证令牌
        user_id: 保管员用户ID
        transport_assignee_id: 运输接收人ID
        orchestrator: 感知编排器(可选)
        order_items: 订单明细列表(可选)，如果提供则使用其中的item_id

    Returns:
        (status_code, body)
    """
```

在 action 函数内部 (约第751行)，找到:
```python
    def action():
        return api_post(f"/tool-io-orders/{order_no}/keeper-confirm", {
            "keeper_id": user_id,
            "keeper_name": "胡婷婷",
            "transport_type": "self",
            "transport_assignee_id": transport_assignee_id,
            "transport_assignee_name": "冯亮",
            "items": [{
                "tool_code": TEST_TOOL["serial_no"],
                "location_id": 1,
                "location_text": "仓库A-1",
                "check_result": "approved",
                "approved_qty": 1,
                "status": "approved"
            }],
            "operator_id": user_id,
            "operator_name": "胡婷婷",
            "operator_role": "keeper"
        }, token=token)
```

修改为:
```python
    def action():
        # If order_items is provided, extract item_id from it
        items_payload = []
        if order_items:
            for item in order_items:
                items_payload.append({
                    "item_id": item.get("id"),  # Use the database item_id
                    "tool_code": item.get("tool_code"),
                    "location_id": item.get("location_id") or 1,
                    "location_text": item.get("location_text") or item.get("keeper_confirm_location_text") or "仓库A-1",
                    "check_result": "approved",
                    "approved_qty": item.get("confirmed_qty") or item.get("apply_qty") or 1,
                    "status": "approved"
                })
        else:
            # Fallback: try to get order detail to extract item_ids
            _, order_detail = api_get(f"/tool-io-orders/{order_no}", token=token)
            if order_detail and order_detail.get("items"):
                for item in order_detail.get("items", []):
                    items_payload.append({
                        "item_id": item.get("id"),
                        "tool_code": item.get("tool_code"),
                        "location_id": item.get("location_id") or 1,
                        "location_text": item.get("location_text") or item.get("keeper_confirm_location_text") or "仓库A-1",
                        "check_result": "approved",
                        "approved_qty": item.get("confirmed_qty") or item.get("apply_qty") or 1,
                        "status": "approved"
                    })
            else:
                # Last resort fallback (should not reach here normally)
                items_payload = [{
                    "tool_code": TEST_TOOL["serial_no"],
                    "location_id": 1,
                    "location_text": "仓库A-1",
                    "check_result": "approved",
                    "approved_qty": 1,
                    "status": "approved"
                }]

        return api_post(f"/tool-io-orders/{order_no}/keeper-confirm", {
            "keeper_id": user_id,
            "keeper_name": "胡婷婷",
            "transport_type": "self",
            "transport_assignee_id": transport_assignee_id,
            "transport_assignee_name": "冯亮",
            "items": items_payload,
            "operator_id": user_id,
            "operator_name": "胡婷婷",
            "operator_role": "keeper"
        }, token=token)
```

### 修改调用处

**修改 `run_full_workflow_test` 中的 keeper_confirm 调用 (约第1110行)**:

找到:
```python
    status_code, body = api_post(f"/tool-io-orders/{order_no}/keeper-confirm", {
        "keeper_id": user_id_ht,
        ...
    }, token=token_ht)
```

修改为:
```python
    # First get order detail to extract item_ids
    _, order_detail = api_get(f"/tool-io-orders/{order_no}", token=token_ht)
    order_items = order_detail.get("items", []) if order_detail else []

    status_code, body = api_post(f"/tool-io-orders/{order_no}/keeper-confirm", {
        "keeper_id": user_id_ht,
        ...
    }, token=token_ht)
```

或者修改为使用 `step_keeper_confirm` 函数并传入 `order_items`:
```python
    # First get order detail to extract item_ids
    _, order_detail = api_get(f"/tool-io-orders/{order_no}", token=token_ht)
    order_items = order_detail.get("items", []) if order_detail else []

    status_code, body = step_keeper_confirm(
        order_no,
        token_ht,
        user_id_ht,
        TEST_USERS["fengliang"]["user_id"],
        orchestrator=orchestrator,
        order_items=order_items
    )
```

## 修改范围

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `test_runner/api_e2e.py` | Bug修复 | 在 keeper_confirm 前获取 order detail 以提取 item_id |

## 前置条件

无（此修改不影响其他功能）

## 验证步骤

1. 修改代码后，确保后端服务运行在端口 8151
2. 运行一轮 API E2E 测试:
   ```bash
   cd E:/CA001/Tooling_IO_Management
   python test_runner/api_e2e.py
   ```

3. 检查输出中 keeper-confirm 步骤不再出现:
   - `'error': 'no items were updated - check item identifiers'`

4. 检查订单是否成功流转到 `keeper_confirmed` 状态

## 约束

- 只修改指定的文件
- 不添加新文件
- 不删除任何文件
- 保持向后兼容：即使 order_items 为空也要有合理的 fallback 行为
