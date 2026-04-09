# Primary Executor: Claude Code
Task Type: Feature Development
Priority: P2
Stage: 00093
Goal: Optimize OrderDetail.vue loadOrder to avoid redundant API calls when order doesn't exist
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述
`OrderDetail.vue` 的 `loadOrder` 函数使用 `Promise.all` 并行发送三个请求：

```javascript
const [detailResult, logResult, issueResult] = await Promise.all([
  getOrderDetail(props.orderNo),       // GET /api/tool-io-orders/<order_no>
  getOrderLogs(props.orderNo),         // GET /api/tool-io-orders/<order_no>/logs
  getTransportIssues(props.orderNo)     // GET /api/tool-io-orders/<order_no>/transport-issues
])
```

当订单不存在时，三个请求都返回 404，导致浏览器控制台出现三个连续错误。这既浪费网络资源，也给调试带来干扰。

### 当前行为
1. 订单详情 404 ❌
2. 操作日志 404 ❌ （没必要查）
3. 运输异常 404 ❌ （没必要查，且有 `.catch` 兜底）

### 期望行为
- 只有订单存在时才发送后续请求（日志、运输异常）
- 订单不存在时只产生一个 404 错误

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/OrderDetail.vue` — 目标文件
- `frontend/src/api/orders.js` — API 封装（getOrderDetail, getOrderLogs, getTransportIssues）
- `.claude/rules/04_frontend.md` — 前端开发规范

---

## Core Task / 核心任务

修改 `OrderDetail.vue` 的 `loadOrder` 函数，实现以下逻辑：

1. **先查订单详情** — 串行第一步
2. **订单不存在则终止** — 只显示错误，不发后续请求
3. **订单存在才查日志和运输异常** — 用 Promise.all 并行

### 修改后的伪代码

```javascript
async function loadOrder() {
  loading.value = true
  errorMessage.value = ''

  // Step 1: 先查订单详情
  const detailResult = await getOrderDetail(props.orderNo)

  if (!detailResult.success) {
    errorMessage.value = detailResult.error || '单据详情加载失败。'
    order.value = { items: [] }
    logs.value = []
    issues.value = []
    finalConfirmState.value = { available: false, reason: '', expected_role: '' }
    keeperText.value = ''
    transportText.value = ''
    wechatText.value = ''
    loading.value = false
    return
  }

  // Step 2: 订单存在，并行查日志和运输异常
  order.value = detailResult.data

  const [logResult, issueResult] = await Promise.all([
    getOrderLogs(props.orderNo),
    getTransportIssues(props.orderNo).catch(() => ({ success: false, data: [] }))
  ])

  logs.value = logResult.success ? logResult.data : []
  issues.value = issueResult.success ? issueResult.data : []

  // Step 3: 后续操作（finalConfirmState, keeperText, transportText, wechatText）...
}
```

---

## Required Work / 必需工作

1. **读取当前 `loadOrder` 函数** — 确认完整的函数结构和所有变量初始化
2. **修改 `loadOrder` 函数** — 实现串行查询逻辑
3. **确保所有状态正确重置** — 当订单不存在时，清空 logs、issues 等相关状态
4. **保持现有错误处理** — 不要移除任何 try-catch 或 .catch
5. **验证修改正确性** — 确保 Promise.all 的 .catch 仍然有效

---

## Constraints / 约束条件

- 不修改 API 封装（`orders.js`）
- 不修改其他页面或组件
- 不引入新的网络请求
- 不改变任何业务逻辑，只优化请求策略
- 使用与现有代码一致的编码风格

---

## Completion Criteria / 完成标准

- [ ] `loadOrder` 函数先查订单详情，订单不存在时直接返回
- [ ] 只有订单存在时才发送 `getOrderLogs` 和 `getTransportIssues` 请求
- [ ] 当订单不存在时，控制台只出现 1 个 404 错误（而非 3 个）
- [ ] 订单不存在时，相关状态（logs、issues 等）正确清空
- [ ] `getTransportIssues` 的 `.catch` 兜底仍然有效
- [ ] 函数内所有状态初始化完整，不产生 undefined 错误
