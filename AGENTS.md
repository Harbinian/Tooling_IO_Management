# 仓库指南 / Repository Guidelines

## 项目结构与模块组织 / Project Structure & Module Organization

应用从 `web_server.py` 启动，它承载 Flask 应用、HTTP API、页面路由和健康检查。核心 SQL Server 访问、连接池、Schema 引导和工作流持久化保留在 `database.py`。共享环境配置集中在 `config/settings.py`，飞书通知辅助函数位于 `utils/feishu_api.py`。

The application starts from `web_server.py`, which hosts the Flask app, HTTP APIs, page routes, and health checks. Core SQL Server access, connection pooling, schema bootstrapping, and workflow persistence remain in `database.py`. Shared environment-driven configuration is centralized in `config/settings.py`, and Feishu notification helpers live in `utils/feishu_api.py`.

`backend/` 已启用，包含服务层包装器（如 `backend/services/tool_io_service.py`）以桥接 Flask 路由到数据库和通知流。`frontend/` 已启用，包含 `frontend/src/` 下的 Vite + Vue 3 应用及 `frontend/dist/` 构建输出。`templates/` 下的服务端渲染模板仍是运行时的一部分。

`backend/` is active and contains service-layer wrappers (for example `backend/services/tool_io_service.py`) that bridge Flask routes to database and notification flows. `frontend/` is active with a Vite + Vue 3 app in `frontend/src/` and build output in `frontend/dist/`. Server-rendered templates under `templates/` are still part of runtime.

`docs/`、`rules/`、`.skills/`、`promptsRec/` 和 `.claude/` 下的文档与工作流资产均为工作仓库的一部分；任务涉及架构、交付流程、提示执行或代理规则时要同步更新。

Documentation and workflow assets under `docs/`, `rules/`, `.skills/`, `promptsRec/`, and `.claude/` are part of the working repository. Update them when a task touches architecture, delivery workflow, prompt execution, or agent guidance.

---

## 提示执行规范 / Prompt Execution Discipline

执行 `promptsRec/` 任务时使用仓库的 `RUNPROMPT` 工作流（注意是 `RUNPROMPT`，不是 `RUMPROMPT`），并完成完整生命周期，不要只改代码。

When executing tasks from `promptsRec/`, use the repository `RUNPROMPT` workflow (note: `RUNPROMPT`, not `RUMPROMPT`) and complete the full lifecycle instead of code-only changes.

必需步骤 / Required steps:

1. 按编号归档提示文件：`✅_<archive-seq>_<original-prompt-name>.md`
2. 在 `logs/prompt_task_runs/` 下写运行报告
3. 若有真实修正，在 `logs/codex_rectification/` 下写纠正日志
4. 任务再小也不得跳过报告

工作流依据文档 / Source of truth:

- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`
- `docs/README_AI_SYSTEM.md`

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

- Python：4 空格缩进、模块级日志、简洁 docstring；函数/变量/路由处理器使用 `snake_case`，类使用 `PascalCase`
- Vue：遵循 `frontend/src/` 结构（`pages/`、`components/`、`api/`、`store/`）
- 配置读取统一通过 `config/settings.py`，避免散落 `os.getenv()`

---

## 测试指南 / Testing Guidelines

- 引入非平凡逻辑时，在 `tests/` 下补充测试，优先路由级 Flask 测试和纯逻辑单测
- 影响 `database.py` 的改动需验证代表性 SQL Server 场景（状态流转、通知副作用、分页/过滤、单号分配）
- 前端至少执行 `npm run build` 并手动验证受影响页面

---

## 提交与 PR 规范 / Commit & Pull Request Guidelines

- 提交信息使用简短祈使句（例如 `fix keeper confirmation flow`）
- PR 需说明行为变更、新增环境变量或 schema 假设
- 涉及 UI 变更时附截图
- 若同时改 Flask 模板和 Vite 页面，需明确权威运行路径

---

## 安全与配置提示 / Security & Configuration Tips

- 禁止提交真实 SQL Server 凭据、飞书密钥或 webhook URL
- 非本地调试保持 `FLASK_DEBUG=False`
- 除非任务明确要求，不要手改 `frontend/dist/` 产物

---

## 当前补充约定（2026-03-19）/ Current Addendum (2026-03-19)

- 反馈功能已从浏览器 localStorage 迁移为 SQL Server 持久化
- 后端反馈接口：`GET /api/feedback`、`POST /api/feedback`、`DELETE /api/feedback/<id>`
- 数据表：`tool_io_feedback`（由 schema 引导函数自动创建/对齐）
- 相关规范见：`docs/API_SPEC.md` 与 `docs/DB_SCHEMA.md`

---

## Encoding Enforcement (UTF-8) / 编码强制规则（UTF-8）

- All newly created or modified text files MUST be UTF-8 encoded without BOM.
- All CLI/file I/O operations MUST explicitly use UTF-8 where supported.
- Any detected mojibake/garbled text MUST be treated as a blocking issue and fixed before task completion.
- For PowerShell commands, prefer `-NoProfile` and explicit encoding parameters to avoid environment-dependent encoding drift.
