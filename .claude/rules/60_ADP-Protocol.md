# ADP Protocol - 工装出入库管理系统开发协议 V1.0

进入首席架构师与全栈开发专家角色。在开发工装出入库管理系统新功能时，请严格按照以下四个阶段（PRD -> Data -> Architecture -> Execution）进行连贯的思考与实施。

---

# Phase 1: 业务需求与场景 (PRD & Context)

- 【业务场景】：[填入业务场景，如：工人需要在指定时间内完成订单的工装出入库操作]
- 【目标用户】：[填入目标用户，如：班组长、保管员、管理员]
- 【核心痛点】：[填入当前遇到的问题，如：订单状态无法跟踪，或工装搜索结果不准确]
- 【业务目标】：[填入期望实现的功能，如：实现工装出入库的完整工作流]

---

# Phase 2: 数据流转与深度穿透防御 (Data Flow & Deep Penetration Defense)

在动手写任何代码前，必须强制审视底层数据 Schema 与框架生命周期！

- 【数据来源】：
  - 后端：`database.py` (SQL Server)
  - 前端：`frontend/src/api/` (API 调用)
- 【主键穿透校验 (PK Consistency)】：
  - 如果涉及数据的修改/合并/删除，后端逻辑 **必须严格基于 UUID/ID 进行比对和落盘**。
  - 绝对禁止使用 Label/名称进行业务匹配，防范静默失效！
- 【缓存与状态防御 (Lifecycle Trap)】：
  1. 涉及 Vue 前端状态管理（Pinia store）的重构，必须确保状态持久化与组件卸载后的清理。
  2. 交互组件（如 `el-table`、`el-select`）操作时，是否会引发页面刷新导致"搜索状态/上下文丢失"？若有，必须引入预筛选（Pre-filter）或 `sessionStorage` 代理机制。
  3. Flask 后端确保使用连接池管理 SQL Server 连接，避免连接泄漏。
- 【强制前置动作】：请先执行语法检查确认代码无错误：
  ```powershell
  python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py
  ```

---

# Phase 3: 架构设计与约束 (Architecture Design & Constraints)

- 【交互链路】：
  - 前端：`Vue 3 + Element Plus` -> `API 调用` -> `Flask REST API` -> `SQL Server`
  - 完整链路：前端组件动作 -> API 请求 -> 后端路由 -> Service 层 -> Repository 层 -> 数据库 -> 响应回传 -> 前端状态更新
- 【零退化原则 (Zero-Regression)】：
  - 本次代码切入绝不允许破坏现有的 UI 规范（深色主题 Element Plus）
  - 不得破坏已实现的 8D 工作流闭环
  - 不得破坏底层的主键映射机制
- 【代码规范】：
  - 使用英文变量名和函数名（禁止拼音）
  - 4 空格缩进，`snake_case` 函数/变量
  - 配置集中在 `config/settings.py`

---

# Phase 4: 精确执行与集成验证 (Execution & E2E Verification)

请根据以上严密的架构分析，连贯执行代码修改：

- [ ] Step 1: 编写/升级后端核心数据处理逻辑（严格遵守主键穿透与清洗机制）。
- [ ] Step 2: 注入前端 Vue 代码（包含状态管理与 API 调用层）。
- [ ] Step 3: 复杂后端逻辑必须先辅以"无头测试 (Headless TDD)"，确保脱离 UI 也能正确执行数据库操作。
- [ ] Step 4: 执行端到端自测：
  - 后端：`python -m py_compile <相关文件>`
  - 前端：`cd frontend && npm run build`
  - 启动服务并验证功能

---

## Phase 5: UI 一致性验证 (UI Consistency Verification)

新增修改涉及前端 UI 时，必须验证以下一致性：

### 确认对话框一致性检查 / Confirmation Dialog Consistency Check

如果修改涉及以下操作之一，必须检查所有相关页面：

| 操作 | 必须检查的页面 |
|------|--------------|
| 提交 / Submit | OrderList.vue, OrderDetail.vue |
| 取消 / Cancel | OrderDetail.vue |
| 最终确认 / Final Confirm | OrderDetail.vue |
| 删除 / Delete | OrderDetail.vue |

**验证方法**:
1. 搜索相关页面中的 `ElMessageBox.confirm` 调用
2. 确认消息格式与 `00_global.md` 中定义的模板一致
3. 确认按钮文本使用中文：`提交`、`取消`、`确认`、`删除`

### CSS 变量使用检查 / CSS Variable Usage Check

1. 全局搜索禁止的硬编码颜色：`bg-white`, `bg-black`, `text-white`, `text-black`
2. 如果存在，记录到 `logs/codex_rectification/` 作为需要修复的技术债
3. 优先使用语义化 CSS 变量

### 主题系统检查 / Theme System Check

如果修改涉及 `SettingsPage.vue` 或主题系统：
1. 确认初始加载逻辑正确检测系统偏好
2. 确认运行时监听 `window.matchMedia` 变化
3. 确认用户手动覆盖后不再响应系统变化

---

# 关键约束

1. **文档权威性**：代码不得偏离 `docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md`
2. **事务处理**：订单提交、保管员确认、最终确认等关键操作必须使用数据库事务
3. **日志记录**：每个关键操作必须记录操作人、时间戳、订单ID、之前状态、下一状态
4. **通知处理**：飞书通知必须记录成功/失败状态，允许重试
5. **RBAC 权限同步**：新增或修改 API 的 `@require_permission` 注解时，必须同步更新 `docs/RBAC_PERMISSION_MATRIX.md` 中的权限矩阵，并确保新权限已分配给所需角色

---

执行完毕后，挂起并输出详细的"架构实施与全链路穿透报告"。
