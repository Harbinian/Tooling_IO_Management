# Bug 修复: 订单详情 API 请求返回 404，订单号异常带有 `:1` 后缀

**提示词编号**: 10201
**任务类型**: Bug 修复 (8D)
**优先级**: P1
**执行器**: Codex

---

## D1 - 团队分工

| 角色 | 负责人 |
|------|--------|
| Reviewer | - |
| Coder | Codex |
| Architect | - |

---

## D2 - 问题描述 (5W2H)

### What (发生了什么)
- **错误现象**: 浏览器控制台显示 `GET /api/tool-io-orders/TO-OUT-20260403-001:1` 返回 404 NOT FOUND
- **请求端口**: 前端开发服务器 8150
- **问题订单号**: `TO-OUT-20260403-001:1`（异常格式，多了 `:1` 后缀）
- **正常订单号**: `TO-OUT-20260403-001`

### Where (在哪里发生)
- KeeperProcess.vue 页面加载待确认订单列表后，点击订单查看详情时

### When (什么时候发生)
- 保管员在 KeeperProcess 页面点击待确认订单时触发

### Who (谁受到影响)
- 保管员 (keeper) 角色用户无法查看订单详情

### Why (为什么是问题)
- 订单号格式非法，后端无法匹配到对应订单
- 可能导致正常订单也无法查看

### How (如何复现)
1. 使用 keeper 角色登录系统
2. 进入保管员处理页面 (`/tool-io/keeper`)
3. 页面加载待确认订单列表
4. 点击任意订单查看详情
5. 观察浏览器控制台网络请求

### 证据链
| 证据类型 | 内容 |
|----------|------|
| 错误日志 | `Failed to load resource: the server responded with a status of 404 (NOT FOUND)` |
| 请求 URL | `/api/tool-io-orders/TO-OUT-20260403-001:1` |
| 可疑点 | 订单号带有 `:1` 后缀，正常应为 `TO-OUT-20260403-001` |

---

## D3 - 临时遏制措施 (Containment)

**爆炸半径评估**:
- 影响范围: KeeperProcess.vue 订单选择功能
- 潜在风险: 保管员无法处理订单，影响出入库工作流

**临时措施**:
1. 检查数据库中是否存在订单号带有 `:1` 后缀的数据
2. 检查前端是否有地方错误地将数组索引附加到订单号

---

## D4 - 根因分析 (5 Whys)

待 D3 完成后填写

---

## D5 - 永久对策 + 防退化宣誓

待 D4 完成后填写

---

## D6 - 实施验证 (Implementation)

待 D5 完成后填写

---

## D7 - 预防复发 (Prevention)

待 D6 完成后填写

---

## D8 - 归档复盘 (Documentation)

待 D7 完成后填写

---

## Context / 上下文

KeeperProcess.vue 页面最近引入了 `keeperConfirmPayload.js` helper 函数，用于重构保管员确认逻辑。订单详情的 `getOrderDetail(row.orderNo)` 调用在 selectOrder 函数中使用。

### 最近代码变更
```diff
# KeeperProcess.vue
+ import {
+   buildKeeperConfirmPayload,
+   collectKeeperConfirmItemsMissingId
+ } from './keeperConfirmPayload'
```

---

## Required References / 必需参考

### 代码文件
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员处理页面
- `frontend/src/api/orders.js` - 订单 API 封装
- `frontend/src/composables/useKeeperOrderProcessing.js` - 保管员订单处理逻辑
- `backend/routes/order_routes.py` - 后端订单路由

### API 端点
- `GET /api/tool-io-orders/<order_no>` - 获取订单详情

### 数据库表
- `tool_io_order` - 订单主表

---

## Constraints / 约束条件

1. **禁止猜测**: 必须基于实际代码和数据库状态分析问题
2. **禁止临时补丁**: 必须找到真正根因并修复
3. **防退化**: 修复后不得影响现有功能
4. **UTF-8 编码**: 所有文件操作必须使用 UTF-8 编码

---

## Completion Criteria / 完成标准

- [ ] 找到 `:1` 后缀的来源（前端拼接错误或数据问题）
- [ ] 修复订单号格式问题
- [ ] 保管员可以正常查看订单详情（不出现 404）
- [ ] KeeperProcess.vue 其他功能不受影响
- [ ] 回归测试通过

---

## D3 执行要求

在进入 D4 之前，必须完成以下调查：

1. **检查前端代码**:
   - 搜索所有 `orderNo` 拼接逻辑，确认是否有地方附加了 `:` 或索引
   - 检查 `useKeeperOrderProcessing.js` 中的 `selectOrder` 函数
   - 检查 `getPendingKeeperOrders` 返回的数据结构

2. **检查后端路由**:
   - 确认 `/api/tool-io-orders/<order_no>` 的匹配逻辑
   - Flask 路由如何处理包含 `:` 的 order_no

3. **检查数据库**:
   - 查询是否存在订单号包含 `:1` 的记录
   - 确认正常订单 `TO-OUT-20260403-001` 是否存在

---

**注意**: D3、D5、D6 完成后必须通知 Reviewer 评分审核，通过后才能继续下一步。
