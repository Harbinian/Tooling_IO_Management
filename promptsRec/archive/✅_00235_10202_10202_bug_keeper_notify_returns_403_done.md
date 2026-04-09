# Bug 修复任务 / Bug Fix Task

**Prompt Number**: 10202
**Task Type**: Bug Fix (8D)
**Priority**: P1
**Executor**: Codex
**Stage**: D1-D8 (Full 8D Protocol)

---

## D1 团队分工 / Team Assignment

| 角色 | 负责人 |
|------|--------|
| Reviewer | reviewer |
| Coder | Codex |
| Architect | Codex |

---

## D2 问题描述 / Problem Description (5W2H)

### What（发生了什么）
用户调用 `POST /api/tool-io-orders/{order_no}/notify-keeper` 接口时，收到 HTTP 403 Forbidden 响应。请求被服务器拒绝。

### Where（在哪里）
- **前端**: `OrderDetail.vue:652` → `orders.js:108` → `notifyKeeper`
- **后端**: `order_routes.py:606` → `@require_permission("notification:send_feishu")`
- **API 端点**: `/api/tool-io-orders/<order_no>/notify-keeper`

### When（何时发生）
用户尝试在订单详情页面发送保管员通知时。

### Impact（影响范围）
- 订单 `TO-OUT-20260403-001` 无法发送保管员通知
- 阻塞出库工作流：草稿 → 保管员确认 → 运输通知
- 影响需要发送 keeper 通知的用户（当前用户角色缺少所需权限）

### 可疑层
**后端 RBAC 层**（基于 HTTP 403 响应：路由存在但权限不足）

---

## D3 临时遏制措施 / Temporary Containment

**爆炸半径评估**:
- 影响范围：仅 `notify-keeper` API 调用
- 潜在风险：若权限漏加，可能影响其他需要此权限的功能

**临时措施**:
- 确认触发 403 的用户角色和账号信息
- 记录当前 `sys_permission` 表中是否存在 `notification:send_feishu` 权限记录
- 记录 `sys_user_role_rel` 和 `sys_role_permission_rel` 中的权限关联

---

## D4 根因分析 / Root Cause Analysis (5 Whys)

**待 D3 数据收集完成后填写**

初步假设（需验证）：
1. `notification:send_feishu` 权限在 `sys_permission` 表中不存在？
2. Keeper 角色未被分配此权限？
3. 调用者的角色不是 Keeper？

---

## D5 永久对策 + 防退化宣誓 / Permanent Fix & Regression Prevention

**待 D4 分析完成后填写**

---

## D6 实施验证 / Implementation Verification

**待 D5 审核完成后填写**

---

## D7 预防复发 / Prevention

**待 D6 完成后填写**

---

## D8 归档复盘 / Documentation

**待 D7 完成后填写**

---

## Context / 上下文

用户调用 `/notify-keeper` 接口返回 403。RBAC 权限装饰器 `@require_permission("notification:send_feishu")` 正确拒绝了未授权请求。

**关键代码位置**:
- `backend/routes/order_routes.py:606-626` — `api_notify_keeper` 路由
- `backend/services/rbac_service.py` — `require_permission` 装饰器实现
- `backend/database/schema/column_names.py` — 字段名常量

**权限相关表**:
- `sys_permission` — 权限定义表
- `sys_role_permission_rel` — 角色-权限关联
- `sys_user_role_rel` — 用户-角色关联

---

## Required References / 必需参考

| 文件 | 说明 |
|------|------|
| `backend/routes/order_routes.py:606-626` | notify-keeper 路由及权限要求 |
| `backend/services/rbac_service.py` | RBAC 装饰器和权限校验逻辑 |
| `backend/database/schema/column_names.py` | 字段名常量 |
| `docs/RBAC_DESIGN.md` | RBAC 设计文档 |
| `docs/RBAC_PERMISSION_MATRIX.md` | 权限矩阵 |

---

## Constraints / 约束条件

1. **只读外部系统表**: `Tooling_ID_Main` 外部表禁止修改
2. **字段名常量**: SQL 查询必须使用 `column_names.py` 中的常量
3. **零假设**: 必须检查真实数据库数据，不假设权限配置存在
4. **原子事务**: 权限修改必须使用事务

---

## Completion Criteria / 完成标准

- [ ] 确认 `sys_permission` 表中存在 `notification:send_feishu` 记录
- [ ] 确认 Keeper 角色（`keeper`）在 `sys_role_permission_rel` 中有此权限
- [ ] 确认调用者账号在 `sys_user_role_rel` 中关联了 Keeper 角色
- [ ] 若权限/角色缺失，按正确路径修复（不可硬编码绕过）
- [ ] 修复后验证用户可正常调用 `/notify-keeper` 接口
- [ ] 更新 `docs/RBAC_PERMISSION_MATRIX.md`（如有变更）

---

## Execution / 执行

```
RUNPROMPT promptsRec/active/10202_bug_keeper_notify_returns_403.md
```
