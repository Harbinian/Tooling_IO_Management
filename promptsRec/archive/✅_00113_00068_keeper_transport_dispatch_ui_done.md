Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 098
Goal: Add transport task dispatch UI in KeeperProcess.vue for keeper to assign transport tasks to production preparation workers
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

**业务场景：**
保管员在完成工装确认后，需要向生产准备工（运输操作员）派遣运输任务。当前系统后端已有 `/api/tool-io-orders/{order_no}/assign-transport` API，前端已有 `assignTransport()` API 函数，但 KeeperProcess.vue 页面缺少触发该 API 的 UI 入口。

**目标用户：**
- 保管员 (keeper) - 发起运输任务派遣
- 运输操作员 (transport_operator) - 接收运输任务通知

**核心痛点：**
当前 KeeperProcess.vue 中没有"派遣运输"按钮，保管员完成确认后无法直接在界面上下发运输任务给生产准备工。用户需要通过其他途径（如口头通知）进行协调。

---

## Required References / 必需参考

### 代码文件
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员处理页面（主要修改）
- `frontend/src/api/orders.js` - 订单 API 封装（已有 `assignTransport`）
- `backend/routes/order_routes.py:165-185` - assign-transport API 路由
- `backend/services/tool_io_service.py` - assign_transport 服务函数

### 数据库 Schema
- `工装出入库单_主表` - 已有 `transport_type`, `transport_operator_id`, `transport_operator_name` 字段

### API 契约
- `POST /api/tool-io-orders/{order_no}/assign-transport`
- 请求参数：`transport_type`, `transport_assignee_id`, `transport_assignee_name`, `operator_id`, `operator_name`, `operator_role`

### 状态机
- 派遣运输任务后订单状态不变，仍为 `keeper_confirmed`
- 运输任务状态独立管理：待派遣 → 已派遣 → 运输中 → 运输完成

---

## Core Task / 核心任务

在 KeeperProcess.vue 的"订单处理"标签页中，为保管员添加"派遣运输任务"功能，具体包括：

1. **添加派遣运输按钮**：在现有操作按钮区域（"预览通知"、"驳回"、"确认通过"旁边）添加"派遣运输"按钮
2. **派遣运输表单/对话框**：点击按钮后，弹出或展开运输任务派遣表单，允许输入：
   - 运输类型（已有字段，支持手动输入或下拉选择）
   - 运输负责人姓名（用于查找/选择生产准备工）
   - 运输负责人ID（根据姓名自动填充或手动输入）
3. **调用 assignTransport API**：使用 `confirmForm` 中的运输信息调用 `assignTransport(selectedOrder.value.orderNo, payload)`
4. **结果反馈**：成功/失败消息提示
5. **状态刷新**：派遣成功后刷新订单详情和待处理列表

---

## Required Work / 必需工作

### Frontend (Gemini)

#### 1. 添加派遣运输按钮
在 KeeperProcess.vue 的 CardHeader 操作按钮区域（约第 91-111 行），在"预览通知"按钮后添加"派遣运输"按钮：

```vue
<Button
  v-if="canDispatchTransport"
  v-debug-id="DEBUG_IDS.KEEPER.DISPATCH_TRANSPORT_BTN"
  variant="outline"
  size="sm"
  class="font-bold text-primary border-primary/50 hover:bg-primary/10"
  @click="openDispatchTransportDialog"
>
  <Truck class="h-4 w-4 mr-1" />
  派遣运输
</Button>
```

#### 2. 添加 canDispatchTransport 计算属性
```javascript
const canDispatchTransport = computed(
  () =>
    session.hasPermission('order:keeper_confirm') &&
    ['keeper_confirmed', 'partially_confirmed'].includes(selectedOrder.value.orderStatus) &&
    !selectedOrder.value.transportOperatorId  // 尚未派遣运输
)
```

#### 3. 添加派遣运输对话框
使用 ElMessageBox 或自定义对话框组件：

```javascript
async function openDispatchTransportDialog() {
  const action = await ElMessageBox.confirm(
    `确认派遣运输任务给 ${confirmForm.transportAssigneeName || '指定运输负责人'} 吗？`,
    '派遣运输任务',
    {
      confirmButtonText: '确认派遣',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => 'confirm').catch(() => 'cancel')

  if (action !== 'confirm') return

  await dispatchTransport()
}
```

#### 4. 实现 dispatchTransport 函数
```javascript
async function dispatchTransport() {
  const payload = {
    transport_type: confirmForm.transportType,
    transport_assignee_id: confirmForm.transportAssigneeId,
    transport_assignee_name: confirmForm.transportAssigneeName,
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }

  const result = await assignTransport(selectedOrder.value.orderNo, payload)
  if (!result.success) return

  ElMessage.success('运输任务已派遣')
  await selectOrder(selectedOrder.value)
  await loadPendingOrders()
}
```

#### 5. 更新 confirmForm 添加 transportAssigneeId 字段
```javascript
const confirmForm = reactive({
  transportType: '',
  transportAssigneeId: '',
  transportAssigneeName: '',
  keeperRemark: ''
})
```

#### 6. 在订单详情加载时回填 transportAssigneeId
在 `selectOrder` 函数中：
```javascript
confirmForm.transportAssigneeId = result.data.transportOperatorId || ''
```

#### 7. 导入 Truck 图标
```javascript
import { Truck } from 'lucide-vue-next'
```

#### 8. 添加 DEBUG_IDS
```javascript
DISPATCH_TRANSPORT_BTN: 'keeper.dispatch_transport_btn',
```

### 后端验证 (Codex - 如需)

检查 `backend/services/tool_io_service.py` 中的 `assign_transport` 函数确保：
- 正确处理 `transport_type`, `transport_assignee_id`, `transport_assignee_name`
- 正确记录操作日志
- 正确更新数据库

---

## Constraints / 约束条件

1. **UI 一致性**：
   - 使用项目统一的按钮样式（variant="outline" + primary 配色）
   - 保持与现有"预览通知"、"驳回"按钮的视觉一致性
   - 遵循 00_global.md 中的确认对话框规范

2. **状态控制**：
   - 仅在订单状态为 `keeper_confirmed` 或 `partially_confirmed` 时显示派遣按钮
   - 已派遣运输的订单不应重复显示派遣按钮（通过 `transportOperatorId` 判断）

3. **字段名规范**：
   - 使用 `backend/database/schema/column_names.py` 中的常量（如有 SQL 操作）
   - 前端变量使用英文命名（snake_case）

4. **权限控制**：
   - 需要 `order:keeper_confirm` 权限

5. **无破坏性修改**：
   - 不修改现有功能的任何行为
   - 不修改后端 API 契约

---

## Completion Criteria / 完成标准

### 功能验收

1. **按钮可见性**：
   - [ ] 保管员登录后，在 KeeperProcess.vue 的订单处理工作台，当订单状态为 `keeper_confirmed` 且未派遣运输时，应显示"派遣运输"按钮
   - [ ] 订单状态为 `submitted` 或 `transport_notified` 时，不应显示该按钮
   - [ ] 已派遣运输的订单不应重复显示该按钮

2. **派遣流程**：
   - [ ] 点击"派遣运输"按钮后，弹出确认对话框
   - [ ] 确认后调用 `assignTransport` API
   - [ ] 派遣成功后显示成功消息"运输任务已派遣"
   - [ ] 派遣成功后刷新订单详情，显示更新的运输负责人信息

3. **数据一致性**：
   - [ ] 派遣时使用的 `transport_type`, `transport_assignee_id`, `transport_assignee_name` 正确传递到后端
   - [ ] 派遣后 `selectedOrder.transportOperatorId` 和 `selectedOrder.transportOperatorName` 正确更新

4. **错误处理**：
   - [ ] API 调用失败时显示错误消息
   - [ ] 网络错误时给出友好提示

### 代码质量验收

1. [ ] 新增按钮使用项目统一的 UI 组件和样式
2. [ ] 新增函数/变量使用英文命名
3. [ ] 新增计算属性 `canDispatchTransport` 逻辑正确
4. [ ] 正确导入并使用 Truck 图标
5. [ ] DEBUG_IDS 已添加
6. [ ] `confirmForm` 已添加 `transportAssigneeId` 字段
7. [ ] `selectOrder` 中正确回填 `transportAssigneeId`

### 集成验收

1. [ ] `npm run build` 前端构建成功
2. [ ] 后端 `python -m py_compile backend/routes/order_routes.py backend/services/tool_io_service.py` 编译成功

---

## Acceptance Tests / 验收测试（手动）

### 测试场景 1：派遣运输按钮显示条件

**前置条件**：以 keeper 角色登录，选择一个状态为 `keeper_confirmed` 且 `transportOperatorId` 为空的订单

**步骤**：
1. 进入"订单处理"标签页
2. 从左侧待处理列表选择一个订单
3. 观察右侧操作按钮区域

**预期结果**：
- "派遣运输"按钮可见且可点击
- 按钮位于"预览通知"按钮旁边

### 测试场景 2：派遣运输成功流程

**前置条件**：同上

**步骤**：
1. 确保 `confirmForm.transportAssigneeName` 有值（如"张三"）
2. 点击"派遣运输"按钮
3. 在确认对话框中点击"确认派遣"
4. 观察系统响应

**预期结果**：
- 显示成功消息"运输任务已派遣"
- 订单详情中 `transportOperatorName` 更新为"张三"
- "派遣运输"按钮不再显示（因为已派遣）

### 测试场景 3：重复派遣防护

**前置条件**：选择一个已派遣运输的订单（`transportOperatorId` 有值）

**步骤**：
1. 进入订单处理工作台
2. 观察"派遣运输"按钮是否显示

**预期结果**：
- "派遣运输"按钮不显示（因为已派遣）
