# 00077_fix_preview_creates_orphan_draft_order

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00077
Goal: Fix handlePreview creating orphan draft orders; add non-persistent preview API
Dependencies: None
Execution: RUNPROMPT

---

## Context

### Business Scenario
用户在工作台创建工装出入库单据时，点击"生成预览"按钮本应仅生成通知文本预览，但实际上该操作**副作用性地**创建了一个 draft 订单。用户不知情地得到了两个订单：一个是点击"生成预览"产生的 orphan draft（008），另一个是点击"提交单据"产生的已提交订单（009）。

### Root Cause (Frontend Analysis)
`OrderCreate.vue` 的 `handlePreview()` 函数实现为：
```javascript
async function handlePreview() {
  const created = await createOrder(buildPayload())  // ❌ 创建了 draft 订单
  const preview = await generateKeeperText(created.order_no)
  keeperText.value = preview.text
}
```
当用户点击"生成预览"时，`createOrder()` 实际上在数据库中创建了一个 draft 订单，但该订单永远不会被提交，最终成为 orphan draft。

### Expected Behavior
- 点击"生成预览"：仅生成预览文本，**不创建任何订单**
- 点击"提交单据"：创建一个订单并立即提交

### Target Files
- Backend: `backend/routes/order_routes.py`, `backend/services/tool_io_service.py`
- Frontend: `frontend/src/pages/tool-io/OrderCreate.vue`

---

## Required References

### Backend
- `backend/routes/order_routes.py` line 51-64: 现有的 `api_tool_io_orders_create` 创建订单逻辑
- `backend/routes/order_routes.py` line 529-541: 现有的 `api_generate_keeper_text` 基于已有订单生成文本
- `backend/services/tool_io_service.py` line 1385: `generate_keeper_text()` 函数
- `backend/database/schema/column_names.py`: 字段名常量
- `config/settings.py`: 配置集中地

### Frontend
- `frontend/src/pages/tool-io/OrderCreate.vue` line 378-397: `handlePreview()` 函数
- `frontend/src/api/orders.js` line 12-14: `createOrder()` API 封装
- `frontend/src/api/orders.js` line 197-199: `generateKeeperText()` API 封装

### Documentation
- `docs/API_SPEC.md`: API 规范
- `docs/RBAC_PERMISSION_MATRIX.md`: 权限矩阵

---

## Core Task

### Backend
新增一个 **非持久化** 的预览生成 API：

**Endpoint**: `POST /api/tool-io-orders/preview-keeper-text`

该 API 接收与 `createOrder` 相同的 payload，但不创建订单，直接返回保管员通知文本。

**返回格式**:
```json
{
  "success": true,
  "text": "【工装领用申请】\n单号：TO-OUT-20260402-XXX\n申请人：..."
}
```

**权限**: `notification:create` (KEEPER) 或 `order:create` (TEAM_LEADER) - 与现有 `generate-keeper-text` 权限一致

### Frontend
修改 `OrderCreate.vue` 的 `handlePreview()` 函数：
- 改用新的 `previewKeeperText()` API 替代 `createOrder() + generateKeeperText()`
- 不再创建 draft 订单

**新增 API 函数** `previewKeeperText(payload)`:
```javascript
export async function previewKeeperText(payload) {
  return unwrap(await client.post('/tool-io-orders/preview-keeper-text', payload))
}
```

---

## Required Work

### Backend (Codex)

1. **新增 API 路由** `backend/routes/order_routes.py`:
   - 在合适位置（建议在 `api_generate_keeper_text` 之后）新增 `POST /api/tool-io-orders/preview-keeper-text`
   - 权限decorator: `@require_permission("notification:create")`
   - 复用现有的 `generate_keeper_text` service 函数逻辑，但不依赖已有订单

2. **新增 Service 函数** `backend/services/tool_io_service.py`:
   - 新增 `preview_keeper_text(payload, current_user)` 函数
   - 接收 order payload，直接构造通知文本字符串（不落库）
   - 参考 `generate_keeper_text()` 的文本生成逻辑，但改为从 payload 而非数据库读取

3. **数据 Schema**:
   - payload 结构与 `createOrder` 完全一致：`order_type`, `initiator_id`, `initiator_name`, `initiator_role`, `items[]` 等
   - 无新增数据库表或字段

4. **语法检查**:
   ```powershell
   python -m py_compile backend/routes/order_routes.py backend/services/tool_io_service.py
   ```

### Frontend (Codex)

1. **新增 API 封装** `frontend/src/api/orders.js`:
   ```javascript
   export async function previewKeeperText(payload) {
     return unwrap(await client.post('/tool-io-orders/preview-keeper-text', payload))
   }
   ```

2. **修改 `handlePreview()`** `frontend/src/pages/tool-io/OrderCreate.vue`:
   ```javascript
   import { previewKeeperText } from '@/api/orders'  // 新增导入

   async function handlePreview() {
     if (!validateBeforeSubmit()) return

     const result = await previewKeeperText(buildPayload())
     if (!result.success) {
       ElMessage.error(result.error || '生成预览失败')
       return
     }
     if (result.warning) {
       ElMessage.warning(result.warning)
     }
     keeperText.value = result.text
   }
   ```

3. **保留 `createOrder` + `submitOrder` 逻辑不变**：`saveDraft()` 和 `submitCreatedOrder()` 行为不变

4. **前端构建验证**:
   ```bash
   cd frontend && npm run build
   ```

---

## Constraints

1. **不破坏现有功能**：
   - `saveDraft()` 和 `submitCreatedOrder()` 必须继续正常工作
   - `generateKeeperText()` API（基于已有订单的预览）必须继续正常工作
   - 不修改现有数据库 schema

2. **权限要求**：
   - 新 API 需要与 `generate-keeper-text` 相同的权限（`notification:create`）
   - 前端调用新 API 时应使用当前用户的 session token

3. **代码规范**：
   - 使用英文变量名/函数名（禁止拼音）
   - 4 空格缩进，snake_case 函数/变量
   - UTF-8 编码

4. **事务要求**：
   - 新 API 不涉及数据库事务（纯计算，不持久化）

5. **UI 一致性**：
   - 预览文本格式必须与 `generateKeeperText()` 生成的完全一致

---

## Completion Criteria

1. **后端**：
   - `POST /api/tool-io-orders/preview-keeper-text` 正确返回预览文本（不创建订单）
   - 权限控制正常工作
   - `python -m py_compile` 无错误

2. **前端**：
   - 点击"生成预览"不再创建 orphan draft 订单
   - 预览文本内容与原逻辑一致
   - `npm run build` 构建成功

3. **集成验证**：
   - 使用同一账号，先点击"生成预览"，再点击"提交单据"
   - 最终只存在一个已提交的订单（不再有 orphan draft）
