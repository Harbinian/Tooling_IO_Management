Primary Executor: Gemini
Task Type: Bug Fix
Priority: P1
Stage: 121
Goal: Fix frontend/backend mismatch causing 400 error on order detail load
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

管理员在订单详情页面查看订单时，控制台出现 400 BAD REQUEST 错误。错误发生在调用 `GET /api/tool-io-orders/{order_no}/generate-transport-text` 时。

错误日志：
```
DELETE /tool-io-orders/TO-OUT-20260313-003 Object
[API Response] DELETE /tool-io-orders/TO-OUT-20260313-003 Object
GET /tool-io-orders/TO-OUT-20260313-003/generate-transport-text
Failed to load resource: the server responded with a status of 400 (BAD REQUEST)
```

---

## Required References / 必需参考

1. `frontend/src/pages/tool-io/OrderDetail.vue` - 前端订单详情页面
2. `backend/services/tool_io_service.py` - 后端服务逻辑 (line 935-990)
3. `backend/routes/order_routes.py` - API 路由定义 (line 395-407)

---

## Core Task / 核心任务

**根本原因**：
- 前端 `canGenerateTransportPreview` 函数检查订单状态是否为 `keeper_confirmed` 时返回 true
- 但后端 `generate_transport_text` 函数检查的是每个明细项的 `item_status === 'approved'`
- 两者逻辑不一致导致：当订单状态是 `keeper_confirmed` 但明细项未完全确认时，前端会调用 API，后端返回 400 错误

**修复方向**：统一前后端检查逻辑

---

## Required Work / 必需工作

1. 检查前端 `canGenerateTransportPreview` 函数的当前逻辑 (OrderDetail.vue line 497-501)
2. 检查后端 `generate_transport_text` 函数的当前逻辑 (tool_io_service.py line 940-946)
3. 统一检查逻辑，确保前后端判断条件一致
4. 修复后验证：加载任意状态的订单详情不再出现 400 错误

---

## Constraints / 约束条件

- 不要破坏现有功能
- 保持代码风格一致
- 使用英文变量名和函数名
- 4空格缩进

---

## Completion Criteria / 完成标准

1. 加载任何状态订单的详情页面不再出现 400 错误
2. 运输通知预览功能在订单状态达到要求时仍能正常工作
3. 前端和后端的检查逻辑保持一致
