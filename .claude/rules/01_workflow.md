# ADP 四阶段开发协议 / ADP Protocol

严格按照四阶段顺序执行，禁止跳阶段。

---

## 原则 / Principles

- **严格顺序**: PRD → Data → Architecture → Execution（禁止跳阶段）
- **主键校验**: 数据修改/合并/删除必须基于 ID/Label，禁止用名称做业务匹配
- **零退化**: 不破坏现有 UI 规范、核心业务逻辑、底层映射机制
- **Headless TDD**: 复杂逻辑先写测试，脱离 UI 验证数据库操作

---

## Phase 1: PRD - 业务需求分析

明确以下内容：

- **业务场景**: 用户需要在 XXX 场景下完成 XXX 操作
- **目标用户**: 班组长 / 保管员 / 管理员 / 运输员
- **核心痛点**: 当前遇到什么问题
- **业务目标**: 期望实现什么功能

---

## Phase 2: Data - 数据流转（强制审视）

在动手写代码前，必须审视数据 Schema：

- **数据来源**: 后端 `database.py` (SQL Server) / 前端 `frontend/src/api/`
- **主键校验**: 如果涉及数据修改，必须严格基于 UUID/ID 进行比对和落盘
- **生命周期防御**:
  - Vue 前端：Pinia store 状态持久化 + 组件卸载清理
  - Flask 后端：连接池管理，避免连接泄漏
- **强制前置**: 执行语法检查 `python -m py_compile <files>`

---

## Phase 3: Architecture - 架构设计

- **交互链路**: 前端动作 → API → 后端路由 → Service → Repository → 数据库
- **风险识别**: 并发风险、数据不一致、状态机漏洞、错误处理缺失
- **熔断策略**: 定义核心逻辑的失败策略（Log & Skip / Fail Fast）

---

## Phase 4: Execution - 精确执行

按顺序执行：

1. 编写/升级后端核心数据处理逻辑（严格遵守主键穿透与清洗机制）
2. 注入前端 Vue 代码（包含状态管理与 API 调用层）
3. Headless TDD：复杂后端逻辑先写测试，脱离 UI 验证
4. **E2E 验证**: 通知 `tester` 执行完整验证

---

## 验证节点 / Verification

Phase 4 完成后，由 `tester` 执行 E2E 验证，通过后自动归档并输出报告。
