# Prompt 10197: 修复重复提交通知与重试提交使用过期草稿

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10197
Goal: 修复订单重复提交时的通知副作用，以及创建页提交失败后重试仍使用旧草稿数据的问题
Dependencies: None
Execution: RUNPROMPT

---

## D1 - 团队分工 / Team Assignment

| 角色 | 职责 |
|------|------|
| Reviewer | 审核 D3/D5/D6 输出，确认根因、方案完整性与回归覆盖 |
| Coder | 在真实代码基础上完成后端与前端修复，并补充回归测试 |

---

## D2 - 问题描述 / Problem Description

### What

本次代码审查确认存在两个 P1 缺陷：

1. 订单已处于 `submitted` 状态时，仓储层将重复提交视为幂等成功，但服务层仍会继续发送 `ORDER_SUBMITTED` 与保管员分配通知，导致重复通知副作用。
2. 创建页首次 `createOrder` 成功后缓存 `createdOrderNo`，若后续 `submitOrder` 失败，用户修改表单再重试时，页面会继续提交第一次创建出来的旧草稿，导致最新编辑被静默丢弃。

### Where

- 后端：
  - `backend/database/repositories/order_repository.py`
  - `backend/services/tool_io_service.py`
- 前端：
  - `frontend/src/pages/tool-io/OrderCreate.vue`
- 相关测试：
  - `tests/test_order_repository.py`
  - 如需要可补充前端交互或 API 层回归验证

### When

- 用户双击提交、网络重试、浏览器重发请求时
- 首次创建成功但提交失败，随后用户继续编辑并再次点击“提交”时

### Who

- 订单创建人 / 班组长
- 被重复通知的保管员与发起人

### Why

- 后端把“幂等成功”和“真正发生状态迁移的成功”混为一类
- 前端引入了 `createdOrderNo` 缓存，但没有保证重试前把当前表单再次持久化到该草稿

### How

1. 创建一个新订单并提交，使其进入 `submitted`
2. 再次调用 `/api/tool-io-orders/<order_no>/submit`
3. 观察是否重复写入通知/重复触发保管员提醒
4. 在创建页首次创建成功后让提交失败
5. 修改工装、备注或日期，再次点击提交
6. 检查最终提交的订单内容是否仍是第一次创建时的旧数据

---

## D3 - 临时遏制措施 / Containment

- 在修复完成前，不得把幂等成功路径继续当作“新提交成功”处理
- 创建页重试逻辑未修复前，不允许仅依赖 `createdOrderNo` 直接提交旧草稿
- D3 完成后通知 reviewer 做节点审查，确认临时遏制不会扩大 blast radius

---

## D4 - 根因分析 / Root Cause Analysis

必须基于真实代码完成以下分析，不允许凭印象修补：

1. 核查 `order_repository.submit_order()` 的幂等返回结构，确认哪些字段可用于区分“真正提交成功”与“已提交幂等返回”。
2. 核查 `tool_io_service.submit_order()` 的通知触发条件，确认为什么在 `result.success == True` 时无条件发通知。
3. 核查 `OrderCreate.vue` 中 `createdOrderNo` 的生命周期，确认用户在首次创建成功、提交失败、修改表单、再次提交的路径上，哪些变更没有被回写到草稿。
4. 如需继续复用既有草稿，核查是否已有安全的草稿更新接口；若没有，评估是取消缓存复用还是先更新草稿后再提交。
5. 明确修复后不会破坏以下既有语义：
   - `submitted` 的重复提交仍可按幂等成功返回
   - 非 `draft` 且非 `submitted` 的状态仍返回冲突
   - 现有权限与状态流转规则不被放宽

---

## D5 - 永久对策 / Permanent Corrective Actions

必须完成以下修复：

1. 后端区分“状态真实变化”和“幂等命中”两类成功结果。
   - 服务层仅在订单从 `draft` 真实迁移到 `submitted` 时发送内部通知。
   - 幂等命中时返回成功，但不得重复发送通知、不得重复写副作用记录。
2. 前端修复创建页重试提交逻辑。
   - 若继续使用已创建草稿，必须保证重试前把当前表单同步到该草稿。
   - 若仓库没有可靠草稿更新路径，则改为避免提交旧草稿内容，并明确失败后用户路径。
3. 补充回归测试，覆盖：
   - 已 `submitted` 订单再次提交时不重复触发通知副作用
   - 创建页首次创建成功、首次提交失败、用户修改内容后重试时，最终提交内容与当前表单一致

### Anti-Regression / 防退化要求

- 不得用“直接屏蔽成功返回”方式回退幂等能力
- 不得删除已有状态冲突判断
- 不得修改 RBAC 权限设计
- 不得绕过真实接口约定伪造前端本地状态

D5 完成后通知 reviewer 做节点审查，确认方案完整且没有新的状态机回归。

---

## D6 - 实施与验证 / Implementation and Validation

至少完成以下验证：

1. Python 语法检查：
   - `python -m py_compile backend/services/tool_io_service.py backend/database/repositories/order_repository.py`
2. 后端测试：
   - 运行受影响测试，至少覆盖 `tests/test_order_repository.py`
   - 如新增服务层测试，需一并执行
3. 前端验证：
   - 至少执行 `frontend` 下 `npm run build`
   - 手动验证创建页失败重试路径
4. 回归点确认：
   - 首次提交草稿成功后仍能正常跳转到详情页
   - 重复提交已提交订单返回成功但无重复通知副作用
   - 修改表单后重试提交，不再提交旧草稿内容

D6 完成后通知 reviewer 做节点审查，确认测试覆盖与验证证据充分。

---

## D7 - 预防复发 / Prevention

- 为“幂等成功但无副作用”建立明确返回约定，并在调用层按字段区分处理
- 为创建页“创建成功 + 提交失败 + 编辑重试”路径补充回归测试
- 如本次修复引入新的响应字段或前端处理约定，同步更新 `docs/API_SPEC.md`

---

## D8 - 归档复盘 / Documentation

执行完成后必须补齐：

- `logs/prompt_task_runs/` 运行报告
- 若产生真实修复，写入 `logs/codex_rectification/` 纠正日志
- 若接口语义有变化，更新：
  - `docs/API_SPEC.md`
  - 必要时补充 `docs/ARCHITECTURE.md` 中的状态/副作用说明

---

## Context / 上下文

当前补丁把重复提交 `submitted` 订单改成幂等成功，并把部分状态冲突改为 `409`。但这次 review 发现：

- 服务层没有对幂等成功做副作用隔离
- 创建页缓存 `createdOrderNo` 后缺少“编辑后重试”的数据同步机制

这两个问题都属于真实行为回归，不是样式或文案问题，必须修复后才能视为补丁正确。

---

## Required References / 必需参考

- `.claude/rules/02_debug.md`
- `.claude/rules/05_task_convention.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`
- `backend/database/repositories/order_repository.py`
- `backend/services/tool_io_service.py`
- `backend/routes/order_routes.py`
- `frontend/src/pages/tool-io/OrderCreate.vue`
- `frontend/src/api/orders.js`
- `tests/test_order_repository.py`

---

## Core Task / 核心任务

基于这次 review finding，完成订单提交幂等路径与创建页失败重试路径的根因修复，避免重复通知和旧草稿被错误提交，同时保留现有状态机与权限边界。

---

## Required Work / 必需工作

1. 审查并修正后端提交幂等成功路径的副作用触发条件
2. 审查并修正创建页失败后重试的草稿复用策略
3. 补充或更新后端/前端回归测试
4. 执行语法检查与受影响测试
5. 同步更新 API 文档或架构说明（如语义变化）

---

## Constraints / 约束条件

- 全部文件必须保持 UTF-8
- 禁止直接修改 `frontend/dist/`
- 禁止删除 `promptsRec` 中任何提示词文件
- 禁止用临时补丁掩盖问题，必须解释根因
- 不得硬编码未经确认的新状态值或字段名
- 涉及 SQL 中文字段名时必须继续使用字段常量

---

## Completion Criteria / 完成标准

- [ ] 已 `submitted` 订单再次提交时，接口仍可幂等成功返回，但不会重复发送内部通知
- [ ] 创建页首次创建成功、首次提交失败、用户修改后再次提交时，最终订单内容与最新表单一致
- [ ] 相关自动化测试已覆盖上述两个回归点
- [ ] Python 语法检查通过
- [ ] 前端构建通过
- [ ] 运行报告、纠正日志、必要文档同步已完成
