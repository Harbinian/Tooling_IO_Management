Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 059
Goal: Implement feedback persistence to database
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端已实现反馈提交和查看功能 (`SettingsPage.vue`, `feedback.js`)，使用 localStorage 存储。现在需要将反馈数据持久化到 SQL Server 数据库。

## Required References / 必需参考

- `web_server.py` - Flask 路由定义
- `database.py` - 数据库操作
- `config/settings.py` - 配置
- `docs/API_SPEC.md` - API 规范文档
- `docs/DB_SCHEMA.md` - 数据库 Schema
- `frontend/src/api/feedback.js` - 前端反馈 API

## Core Task / 核心任务

将反馈功能从 localStorage 升级到数据库持久化：
1. 创建反馈数据表
2. 实现 CRUD API
3. 更新前端 API 调用

## Required Work / 必需工作

1. **创建数据库表**
   - `用户反馈表` 或类似名称
   - 字段：id, category, subject, content, login_name, user_name, status, created_at, updated_at

2. **实现 API 端点**
   - `GET /api/feedback` - 获取当前用户的反馈列表
   - `POST /api/feedback` - 提交新反馈
   - `DELETE /api/feedback/<id>` - 删除反馈

3. **更新前端 API**
   - 修改 `frontend/src/api/feedback.js`
   - 调用后端 API 替代 localStorage
   - 保留 localStorage 回退逻辑（可选）

4. **确保表创建逻辑**
   - 在 `ensure_*` 函数中添加表创建逻辑

## Constraints / 约束条件

- 反馈数据按用户隔离（只能查看自己的反馈）
- 遵循项目编码规范（英文变量名、snake_case）
- 不得破坏现有功能

## Completion Criteria / 完成标准

1. 反馈可以保存到数据库
2. 用户可以查看自己的反馈历史
3. 用户可以删除自己的反馈
4. 前端与后端 API 正确集成
5. 后端语法检查通过：`python -m py_compile web_server.py database.py`
6. 前端构建通过：`cd frontend && npm run build`
