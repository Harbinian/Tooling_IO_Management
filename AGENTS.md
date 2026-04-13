# 仓库指南 / Repository Guidelines

## 项目结构与模块组织 / Project Structure & Module Organization

应用从 `web_server.py` 启动，它承载 Flask 应用、HTTP API、页面路由和健康检查。核心 SQL Server 访问、连接池、Schema 引导和工作流持久化保留在 `database.py`。共享环境配置集中在 `config/settings.py`，飞书通知辅助函数位于 `utils/feishu_api.py`。

The application starts from `web_server.py`, which hosts the Flask app, HTTP APIs, page routes, and health checks. Core SQL Server access, connection pooling, schema bootstrapping, and workflow persistence remain in `database.py`. Shared environment-driven configuration is centralized in `config/settings.py`, and Feishu notification helpers live in `utils/feishu_api.py`.

`backend/` 已启用，包含服务层包装器（如 `backend/services/tool_io_service.py`）以桥接 Flask 路由到数据库和通知流。`frontend/` 已启用，包含 `frontend/src/` 下的 Vite + Vue 3 应用及 `frontend/dist/` 构建输出。页面运行路径当前以 `backend/routes/page_routes.py` 与前端路由为准，仓库当前没有独立的 `templates/` 目录。

`backend/` is active and contains service-layer wrappers (for example `backend/services/tool_io_service.py`) that bridge Flask routes to database and notification flows. `frontend/` is active with a Vite + Vue 3 app in `frontend/src/` and build output in `frontend/dist/`. Runtime page entry currently lives in `backend/routes/page_routes.py` plus frontend routing; there is no standalone `templates/` directory in the current workspace.

`docs/`、`promptsRec/`、`.claude/`、`.trae/`、`logs/`、`scripts/` 与 `test_runner/` 下的文档和流程资产都属于工作仓库的一部分。任务涉及架构、流程、提示词执行、代理分工、自动化脚本或上下文治理时，必须同步更新对应文档。

Documentation and workflow assets under `docs/`, `promptsRec/`, `.claude/`, `.trae/`, `logs/`, `scripts/`, and `test_runner/` are part of the working repository. Update them whenever a task touches architecture, delivery workflow, prompt execution, agent governance, automation scripts, or context-optimization rules.

---

## 核心规则映射 / Core Rules Mapping

`.claude/rules/` 是代理执行规则的主来源：

- `00_core.md`: 核心开发规则，包括 UTF-8、字段名常量、命名、文档权威性、表范围、事务与通知要求
- `01_workflow.md`: ADP 四阶段流程，适用于功能、重构、测试类任务
- `02_debug.md`: 8D 调试/回归协议，适用于 Bug 修复
- `03_hotfix.md`: 生产热修复 SOP
- `04_frontend.md`: 前端页面、状态、主题、工作流预览与 RBAC 规则
- `05_task_convention.md`: 提示词编号、归档命名和执行器分配规则
- `06_testing.md`: 测试任务和验证分层规则
- `07_ci_gates.md`: CI 自动化门禁与 G1-G6 评分规则
- `08_skill_convention.md`: 技能文件的结构、引用方式与瘦身约束

Rules in `.claude/rules/` are the source of truth for agent workflow:

- `00_core.md`: core development rules covering UTF-8, field-name constants, naming, documentation authority, table scope, transactions, and notifications
- `01_workflow.md`: ADP four-phase workflow for feature, refactor, and test work
- `02_debug.md`: 8D debugging and regression protocol for bug fixes
- `03_hotfix.md`: production hotfix SOP
- `04_frontend.md`: frontend requirements for pages, states, theming, workflow preview, and RBAC isolation
- `05_task_convention.md`: prompt numbering, archive naming, and executor assignment
- `06_testing.md`: testing-task and verification-layer rules
- `07_ci_gates.md`: CI automation gates and G1-G6 scoring rules
- `08_skill_convention.md`: skill-file structure, reference style, and slimming constraints

历史上 `.skills/` 承载过技能编排层，但当前工作区已不保留该目录。凡遇到旧文档提及 `.skills/`，一律以 `.claude/rules/` 为真源，并以 `docs/SKILLS_CLAUDE_RULES_CONSOLIDATION.md` 作为迁移与冲突整改说明。

---

## 提示执行规范 / Prompt Execution Discipline

执行 `promptsRec/` 任务时使用仓库 `RUNPROMPT` 工作流，注意是 `RUNPROMPT`，不是 `RUMPROMPT`。执行时必须走完整生命周期，不能只改代码不补流程资产。

When executing tasks from `promptsRec/`, use the repository `RUNPROMPT` workflow. Note the command is `RUNPROMPT`, not `RUMPROMPT`. Complete the full lifecycle instead of code-only changes.

必需步骤 / Required steps:

1. 从 `promptsRec/active/` 选择一个未被 `.lock` 占用的 `.md` 提示词
2. 在执行前创建对应 `.lock` 文件，避免并发重复执行
3. 按任务类型加载对应规则文件：
   - 功能/重构/测试 -> `.claude/rules/01_workflow.md`
   - Bug 修复 -> `.claude/rules/02_debug.md`
   - 生产热修复 -> `.claude/rules/03_hotfix.md`
4. 在 `logs/prompt_task_runs/` 下写运行报告
5. 若有真实修正，在 `logs/codex_rectification/` 下写纠正日志；目录不存在时先创建
6. 归档原提示词，禁止删除提示词文件
7. 成功归档后删除 `.lock`

归档约束 / Archive requirements:

- 任务再小也不得跳过报告
- `promptsRec/active/` 和 `promptsRec/archive/` 中的提示词文件严禁直接删除
- 完成动作必须是重命名/归档，不是移除
- 编号来自 `promptsRec/.sequence`，禁止通过扫描目录推断

工作流依据文档 / Source of truth:

- `.claude/rules/05_task_convention.md`
- `docs/SKILLS_CLAUDE_RULES_CONSOLIDATION.md`
- `docs/archive/PROMPT_TASK_CONVENTION.md`（历史参考）
- `docs/archive/AI_PIPELINE.md`（历史参考）
- `docs/archive/README_AI_SYSTEM.md`（历史参考）

---

## 任务编号与执行器 / Task Numbering & Executors

提示词统一使用 5 位类型编号，覆盖 active 和 archive 全流程。

Prompt tasks must use a 5-digit type number across active and archive flows.

类型范围 / Type ranges:

- `00001-09999`: 功能任务 / Feature development
- `10101-19999`: Bug 修复 / Bug fix
- `20101-29999`: 重构任务 / Refactoring
- `30101-39999`: 测试任务 / Testing

计数器来源 / Counter source:

- `promptsRec/.sequence`
- `feature_next`, `bugfix_next`, `refactor_next`, `test_next`, `exec_next`

禁止事项 / Prohibitions:

- 禁止扫描 `archive/` 或 `active/` 推断新编号
- 禁止使用 3 位编号
- 禁止重复使用执行顺序号

执行器分配 / Executor assignment:

- `Claude Code`: 架构、重构、测试、P0/P1 恶性 Bug、复杂跨模块任务、简单文档/单点修正
- `Codex`: 常规后端实现、常规前后端实现、非架构级普通 Bug
- `Gemini`: 大改版前端设计/UI 创意任务

简化任务默认由 `Claude Code` 直接执行，包括参数错误、调用签名修正、docstring/注释同步、单文件单函数修复、纯文档同步等。

Malignant bugs are P0/P1 issues such as system outage, data corruption risk, core workflow blockage, or unavailable APIs, and default to `Claude Code`.

### Codex Output Rules Only / 仅对 Codex 生效的输出规则

The following response-format rules apply only when the executor is `Codex`. They do not override executor assignment, workflow ownership, or output styles for `Claude Code`, `Gemini`, or other agents.

- 全程使用中文
- 优先输出结论，不要先输出过程
- 不要展示大段代码
- 不要展示完整 diff
- 除非用户明确要求，否则不要粘贴超过 15 行的代码
- 只汇报必要信息，适合人类快速阅读

Codex must use the following response structure unless the user explicitly requests a different format:

1. `【任务结论】`
2. `【根因判断】`
3. `【执行计划】`
4. `【实际变更】`
5. `【验证结果】`
6. `【后续建议】`

Additional constraints for `Codex`:

- `【任务结论】`: use 1 to 3 sentences to summarize the issue and handling direction
- `【根因判断】`: at most 3 items
- `【执行计划】`: at most 5 ordered items
- `【实际变更】`: list only changed files and what changed in each file, without pasting code
- `【验证结果】`: state what was verified and the result
- `【后续建议】`: provide 1 to 3 items only when helpful
- 若任务未修改文件，也必须在 `【实际变更】` 中明确说明
- 若未执行测试或验证受限，必须在 `【验证结果】` 中明确说明
- 除非用户明确要求，否则不要输出完整命令回显、长日志或大段实现细节

---

## ADP 与 8D 规则 / ADP and 8D Rules

功能、重构、测试类任务必须遵守 ADP 四阶段顺序，禁止跳阶段：

1. `PRD`
2. `Data`
3. `Architecture`
4. `Execution`

关键要求 / Key ADP requirements:

- 数据修改/合并/删除必须基于 ID 或 Label，而不是名称匹配
- 复杂逻辑优先 Headless TDD
- 编码前先审视 schema、连接池、状态生命周期与风险
- 执行前先做语法检查，如 `python -m py_compile <files>`

Bug 修复必须遵守 8D：

- D1 团队分工
- D2 问题描述
- D3 临时遏制
- D4 根因分析
- D5 永久对策
- D6 实施验证
- D7 预防复发
- D8 归档复盘

8D 补充要求 / 8D additions:

- 禁止临时补丁
- 必须给出根因解释、测试用例、回归预防
- D3、D5、D6 完成后需要 reviewer 节点评审思维

---

## 热修复规则 / Hotfix Rules

生产热修复必须遵守 `.claude/rules/03_hotfix.md`：

- 一次只执行一个原子变更，禁止并行热修
- 每一步后都要做冒烟验证
- 先写 RFC，包含 blast radius 和 rollback plan
- 所有文件操作强制 UTF-8
- 批量文件读取每次不超过 10 个，避免上下文和 I/O 失控

Hotfix principles:

- minimal blast radius
- atomic changes
- immediate verification

---

## 构建、测试与开发命令 / Build, Test, and Development Commands

后端：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python web_server.py
```

前端：

```powershell
cd frontend
npm install
npm run dev
npm run build
```

Python 语法检查：

```powershell
python -m py_compile web_server.py database.py backend\services\tool_io_service.py config\settings.py utils\feishu_api.py
```

---

## 编码风格与命名 / Coding Style & Naming Conventions

- Python：4 空格缩进、模块级日志、简洁 docstring；函数、变量、路由处理器使用 `snake_case`，类使用 `PascalCase`
- Vue：遵循 `frontend/src/` 结构（`pages/`、`components/`、`api/`、`store/`）
- 配置读取统一通过 `config/settings.py`，避免散落 `os.getenv()`
- 代码、注释、变量名、提交信息必须使用英文；CLI 面向仓库操作者的说明可用中文
- 变量和函数禁止使用拼音
- 所有关键 I/O 或网络操作必须有异常处理
- AI 生成的代码不得包含占位符，必须完整且可执行

字段名常量规则 / Field name constant rule:

- 所有 SQL 中的中文字段名必须通过 `backend/database/schema/column_names.py` 引用
- 禁止在 SQL 中直接硬编码中文字段名
- 禁止使用 Unicode 转义代替字段常量

---

## 数据库与业务约束 / Database and Business Constraints

外部系统表访问 / External system table access:

- 严禁对外部系统表执行 `CREATE TABLE`、`ALTER TABLE`、`DROP TABLE`
- `Tooling_ID_Main` 仅允许只读查询和受控字段更新，且必须使用字段常量

数据库表范围 / Database table scope:

- 核心业务表：`tool_io_order`、`tool_io_order_item`、`tool_io_operation_log`、`tool_io_notification`、`tool_io_location`、`tool_io_transport_issue`
- 系统表：`sys_org`、`sys_user`、`sys_role`、`sys_permission`、`tool_io_order_no_sequence`

事务要求 / Transaction requirements:

- 订单提交
- 保管员确认
- 最终确认

并发控制 / Concurrency control:

- 防止重复预约
- 防止并行订单冲突
- 使用行级锁或乐观锁

通知要求 / Notification handling:

- 发送成功要记录
- 发送失败要记录
- 支持重试
- 对应表为 `tool_io_notification`

可追溯性 / Traceability:

每个仓库业务操作必须记录：

- `operator`
- `timestamp`
- `order_id`
- `previous_state`
- `next_state`

---

## 前端规则 / Frontend Rules

前端开发必须遵守 `.claude/rules/04_frontend.md`。

Required pages:

1. Order creation page
2. Keeper processing page
3. Order list page
4. Order detail page

关键要求 / Key frontend requirements:

- 工装搜索必须支持编码、名称、规格、位置、状态，并支持批量选择
- 订单状态标签至少覆盖 Submitted、Keeper Confirmed、Transport Notified、Completed、Rejected
- 用户必须能预览飞书通知并复制微信消息
- UI 字段与 API 字段保持固定映射，如 `order_no`、`tool_code`、`tool_name`
- `SettingsPage.vue` 主题初始化要先读 `localStorage`，再读系统主题
- 运行时要监听 `prefers-color-scheme` 变化
- 严禁硬编码颜色值，必须使用 CSS 变量
- 订单创建页必须提供工作流预览
- E2E 测试需注意 RBAC 组织隔离，同组织账号才能互相看到订单

UI 一致性 / UI consistency:

提交、取消、确认、删除等关键操作在相关页面上必须保持一致的确认行为与文案风格。

---

## 测试指南 / Testing Guidelines

- 引入非平凡逻辑时，在 `tests/` 下补充测试，优先路由级 Flask 测试和纯逻辑单测
- 影响 `database.py` 的改动需验证代表性 SQL Server 场景（状态流转、通知副作用、分页/过滤、单号分配）
- 前端至少执行 `npm run build` 并手动验证受影响页面
- 复杂后端逻辑优先先写 headless tests 再接 UI
- Bug 修复必须附带回归验证

---

## 文档权威性 / Documentation Source of Truth

代码实现必须遵循 `docs/` 下的权威文档，并在实现变化前同步更新：

- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/API_SPEC.md`
- `docs/SCHEMA_SNAPSHOT_20260325.md`（当前仓库可见的 schema 快照）
- `docs/RBAC_PERMISSION_MATRIX.md`
- `backend/database/schema/column_names.py`

禁止事项 / Prohibitions:

- 禁止在文档未更新前先提交实现
- 禁止跳过文档同步直接交付代码

实现后至少检查：

- 功能变更后 `PRD.md`
- API 变更后 `API_SPEC.md`
- 权限变更后 `RBAC_PERMISSION_MATRIX.md`
- Schema 变更后至少同步 `docs/SCHEMA_SNAPSHOT_20260325.md`（或补回正式 `DB_SCHEMA.md`）与 `column_names.py`

---

## 上下文防火墙 / Repo Context Firewall

仓库已引入 `repo-context-firewall` 技能，用于控制上下文膨胀并减少无效扫描。

Use the repo context firewall rules when the repository becomes context-heavy.

原则 / Principles:

- 大于 200 KB 的文件、超过 500 行的源码、日志、构建产物、归档报告、旧评审文档都属于上下文热点
- `build/`、`dist/`、日志、生成报告、临时文件通常可忽略或减少频繁加载
- 大型但仍需保留可见性的源码文件应给出拆分建议，而不是盲目重构
- 不要忽略 `backend/`、`frontend/src/`、`promptsRec/active/`、`promptsRec/archive/`、`.claude/rules/` 与关键架构文档
- 如进行仓库上下文治理，应同步维护 `docs/REPO_CONTEXT_FIREWALL.md` 和 `.trae/.ignore`

---

## 提交与 PR 规范 / Commit & Pull Request Guidelines

- 提交信息使用简短祈使句，例如 `fix keeper confirmation flow`
- 重大功能建议对应单独提交
- PR 需说明行为变更、新增环境变量、schema 假设与验证方式
- 涉及 UI 变更时附截图
- 若同时改 Flask 页面路由和 Vite 页面，需明确权威运行路径

---

## 安全与配置提示 / Security & Configuration Tips

- 禁止提交真实 SQL Server 凭据、飞书密钥或 webhook URL
- 非本地调试保持 `FLASK_DEBUG=False`
- 除非任务明确要求，不要手改 `frontend/dist/` 产物
- 所有修复必须基于真实日志、真实接口和真实 schema，禁止盲猜
- 自愈流程或任务生成流程不得直接修改生产数据，不得绕过 `RUNPROMPT`

---

## 当前补充约定（2026-03-19）/ Current Addendum (2026-03-19)

- 反馈功能已从浏览器 localStorage 迁移为 SQL Server 持久化
- 后端反馈接口：`GET /api/feedback`、`POST /api/feedback`、`DELETE /api/feedback/<id>`，管理侧还包括 `GET /api/feedback/all`、`PUT /api/feedback/<id>/status`、`POST /api/feedback/<id>/reply`、`GET /api/feedback/<id>/replies`
- 数据表：`tool_io_feedback`（由 schema 引导函数自动创建/对齐）
- 相关规范见：`docs/API_SPEC.md`、`backend/database/schema/`，以及当前可见的 schema 快照 `docs/SCHEMA_SNAPSHOT_20260325.md`

---

## Encoding Enforcement (UTF-8) / 编码强制规则（UTF-8）

- All newly created or modified text files MUST be UTF-8 encoded without BOM.
- All CLI/file I/O operations MUST explicitly use UTF-8 where supported.
- Any detected mojibake or garbled text is a blocking issue and must be fixed before task completion.
- For PowerShell commands, prefer `-NoProfile` and explicit encoding controls where possible.
- In this repository, encoding mistakes in `AGENTS.md`, prompt files, reports, or rules are considered process violations, not cosmetic issues.
