# 仓库指南 / Repository Guidelines

## 项目结构与模块组织 / Project Structure & Module Organization

应用仍从 `web_server.py` 启动，它承载 Flask 应用、HTTP API、页面路由和健康检查。核心 SQL Server 访问、连接池、Schema 引导和工作流持久化保留在 `database.py` 中。共享的环境驱动配置集中在 `config/settings.py`，飞书通知辅助函数位于 `utils/feishu_api.py`。

The application still starts from `web_server.py`, which hosts the Flask app, HTTP APIs, page routes, and health checks. Core SQL Server access, connection pooling, schema bootstrapping, and workflow persistence remain in `database.py`. Shared environment-driven configuration is centralized in `config/settings.py`, and Feishu notification helpers live in `utils/feishu_api.py`.

`backend/` 目前已激活，包含服务层包装器如 `backend/services/tool_io_service.py`，桥接 Flask 路由到数据库和通知流。`frontend/` 也已激活，包含 `frontend/src/` 下的 Vite + Vue 3 应用，以及 `frontend/dist/` 下的构建输出。`templates/` 下的服务端渲染模板仍是运行时的一部分，除非任务明确迁移或替换它们。

`backend/` is now active and contains service-layer wrappers such as `backend/services/tool_io_service.py`, which bridge Flask routes to the database and notification flows. `frontend/` is also active and contains a Vite + Vue 3 application under `frontend/src/`, plus the built output under `frontend/dist/`. Server-rendered templates under `templates/` are still part of the runtime.

`docs/`、`rules/`、`skills/`、`promptsRec/` 和 `.claude/` 下的文档和工作流资产是工作仓库的一部分而非占位符。当任务涉及架构、交付工作流、提示/任务执行或代理指导时，请更新它们。

Documentation and workflow assets under `docs/`, `rules/`, `skills/`, `promptsRec/`, and `.claude/` are part of the working repository. Update them when the task touches architecture, delivery workflow, prompt/task execution, or agent guidance.

---

## 提示执行规范 / Prompt Execution Discipline

通过仓库的 `RUNPROMPT` 工作流执行 `promptsRec/` 中的任务时，完成完整生命周期，而不仅仅是更改代码或文档。

When executing a task from `promptsRec/` via the repository's `RUNPROMPT` workflow, complete the full lifecycle instead of only changing code or docs.

必需完成步骤:

1. 使用仓库编号约定归档提示: `✅_<归档序列>_<原始提示名>.md`
2. 在 `logs/prompt_task_runs/` 下编写运行报告
3. 如果 Codex 实现了真正的修正而非仅验证工作，同时在 `logs/codex_rectification/` 下编写纠正日志
4. 即使任务很小也不要跳过报告步骤

Required completion steps:

1. Archive the prompt using the repository numbering convention: `✅_<archive-seq>_<original-prompt-name>.md`
2. Write a run report under `logs/prompt_task_runs/`
3. If Codex implemented a real correction, also write a rectification log under `logs/codex_rectification/`
4. Do not skip the reporting step even if the task was small

示例:

- `promptsRec/102_bug_vite_entry_compile_failure.md` -> `promptsRec/✅_00016_102_bug_vite_entry_compile_failure.md`
- `promptsRec/103_bug_order_list_api_500.md` -> `promptsRec/✅_00017_103_bug_order_list_api_500.md`

Examples:

- `promptsRec/102_bug_vite_entry_compile_failure.md` -> `promptsRec/✅_00016_102_bug_vite_entry_compile_failure.md`
- `promptsRec/103_bug_order_list_api_500.md` -> `promptsRec/✅_00017_103_bug_order_list_api_500.md`

使用现有仓库文档作为此工作流的依据:

Use the existing repository documents as the source of truth for this workflow:

- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`
- `docs/README_AI_SYSTEM.md`

---

## 构建、测试和开发命令 / Build, Test, and Development Commands

运行 Flask 应用前，创建隔离的 Python 环境并安装后端依赖:

Create an isolated Python environment and install backend dependencies before running the Flask app:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python web_server.py
```

前端工作使用 `frontend/` 中的 Vite 应用:

For frontend work, use the Vite app in `frontend/`:

```powershell
cd frontend
npm install
npm run dev
```

验证前端构建:

Build the frontend for verification with:

```powershell
cd frontend
npm run build
```

提交 Python 更改前使用快速后端语法检查:

Use a quick backend syntax check before submitting Python changes:

```powershell
python -m py_compile web_server.py database.py backend\services\tool_io_service.py config\settings.py utils\feishu_api.py
```

目前没有已提交的自动化测试套件。通过本地启动 Flask 服务器并测试受影响路由(如 `/api/tool-io-orders`、`/api/tools/search`、`/api/tool-io-orders/<order_no>/notify-transport` 和 `/api/health`)来验证后端更改。前端更改至少需要成功的 `npm run build` 并手动检查受影响屏幕来验证。

There is no committed automated test suite yet. Validate backend changes by starting the Flask server locally and exercising affected routes. Validate frontend changes with at least a successful `npm run build` and a manual check of impacted screens.

---

## 编码风格与命名约定 / Coding Style & Naming Conventions

遵循现有 Python 约定: 4空格缩进、模块级日志记录、公共函数和类的简洁文档字符串。函数、变量和路由处理程序使用 `snake_case`。类使用 `PascalCase`，如 `ConnectionPool`、`DatabaseManager` 和 `FeishuBase`。

Follow the existing Python conventions: 4-space indentation, module-level logging, and concise docstrings. Use `snake_case` for functions, variables, and route handlers. Use `PascalCase` for classes.

Vue 代码遵循既定 `frontend/src/` 结构: 页面组件位于 `pages/`、可复用 UI 位于 `components/`、API 包装器位于 `api/`、共享状态位于 `store/`。保持命名描述性且与现有文件一致，如 `OrderList.vue`、`OrderDetail.vue` 和 `NotificationPreview.vue`。

For Vue code, follow the established structure with page components under `pages/`, reusable UI under `components/`, API wrappers under `api/`, and shared state under `store/`. Keep naming descriptive and consistent.

将配置访问集中在 `config/settings.py`。添加新环境变量时，更新现有 `.env.example` 或在需要时引入，通过 settings 模块公开新设置，而不是在整个代码库中散布 `os.getenv()` 调用。

Keep configuration access centralized in `config/settings.py`. When adding new environment variables, update `.env.example` or introduce it if needed, and expose new settings through the settings module instead of scattering `os.getenv()` calls.

---

## 测试指南 / Testing Guidelines

如果引入非平凡逻辑，在新的 `tests/` 包下添加针对性测试。优先选择 API 行为的路由级 Flask 测试，以及纯辅助逻辑(如验证、格式化和状态转换)的隔离单元测试。测试文件命名为 `test_<功能>.py`。

If you introduce non-trivial logic, add focused tests under a new `tests/` package. Prefer route-level Flask tests for API behavior and isolated unit tests for pure helper logic. Name test files `test_<feature>.py`.

影响 `database.py` 的更改应针对代表性 SQL Server 场景进行验证，特别是状态更改、通知副作用、分页/过滤查询和订单号分配行为。影响 `backend/services/tool_io_service.py` 或 `web_server.py` 中路由处理程序的更改也应检查请求验证和响应结构一致性。

Changes that affect `database.py` should be verified against representative SQL Server scenarios, especially status changes, notification side effects, pagination/filtering queries, and order number allocation behavior. Changes to service layer or route handlers should also be checked for request validation and response-shape consistency.

对于前端行为，如果以后添加测试工具，优先选择轻量级组件或集成测试。在此之前，使用 `npm run build` 加上 `/inventory`、`/inventory/create`、`/inventory/<order_no>` 和 `/inventory/keeper` 的手动路由验证。

For frontend behavior, prefer lightweight component or integration tests if a test harness is added later. Until then, use `npm run build` plus manual route verification.

---

## 提交与拉取请求指南 / Commit & Pull Request Guidelines

无法从工作区可靠地推断 Git 历史约定，因此使用简短祈使句提交主题，如 `fix keeper confirmation flow`、`wire vue tool io pages` 或 `update health check response`。

Git history conventions cannot be inferred reliably from this workspace, so use short imperative commit subjects.

拉取请求应总结行为更改、列出任何新环境变量或 Schema 假设，并在模板渲染或 Vue 屏幕更改时包含截图。如果更改同时影响 Flask 渲染模板和 Vite 前端，请说明更改后哪个运行时路径是权威的。

Pull requests should summarize behavior changes, list any new environment variables or schema assumptions, and include screenshots when template rendering or Vue screens change. If a change affects both Flask-rendered templates and the Vite frontend, call out which runtime path is authoritative.

---

## 安全与配置提示 / Security & Configuration Tips

不要提交活动的 SQL Server 凭据、飞书应用密钥或 Webhook URL。在本地调试外保持 `FLASK_DEBUG=False`，并在测试更改工装出入库记录或发送通知的流程前验证数据库连接。

Do not commit live SQL Server credentials, Feishu app secrets, or webhook URLs. Keep `FLASK_DEBUG=False` outside local debugging, and verify database connectivity before testing flows that mutate tool IO records or send notifications.

除非任务明确针对构建输出，否则不要手动编辑生成的前端产物。优先修改 `frontend/src/` 下的源文件并通过正常构建重新生成 `frontend/dist/`。将 `frontend/node_modules/`、`__pycache__/` 和 `logs/` 下的日志输出视为生成/运行时产物，除非任务明确涉及它们。

Do not hand-edit generated frontend artifacts unless the task explicitly targets build output. Prefer modifying source files under `frontend/src/` and regenerating `frontend/dist/` through the normal build. Treat generated/runtime artifacts as such unless the task explicitly involves them.
