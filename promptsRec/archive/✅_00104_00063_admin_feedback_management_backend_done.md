Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 063
Goal: Implement admin feedback management API and database schema
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

当前问题反馈模块存在设计漏洞：管理员和普通用户共用 SettingsPage.vue 的反馈标签页，管理员只能看到自己提交的反馈，无法履行管理职责。

需求：
1. 管理员需要查看所有用户提交的反馈
2. 管理员需要更新反馈状态（pending → reviewed → resolved）
3. 管理员需要回复功能

## Required References / 必需参考

- `backend/database/schema/schema_manager.py` - 数据库表创建逻辑
- `backend/services/feedback_service.py` - 反馈服务层
- `backend/routes/feedback_routes.py` - API 路由
- `docs/API_SPEC.md` - API 规范文档
- `docs/DB_SCHEMA.md` - 数据库 Schema
- `frontend/src/api/feedback.js` - 前端 API 封装（参考现有结构）

## Core Task / 核心任务

实现管理员反馈管理的后端能力：
1. 创建返信表 `tool_io_feedback_reply`
2. 新增管理员 API 端点（查看所有反馈、更新状态、添加回复）
3. 确保权限控制正确

## Required Work / 必需工作

### 1. 数据库层

在 `schema_manager.py` 中添加 `ensure_feedback_reply_table()` 函数：

```sql
CREATE TABLE [tool_io_feedback_reply] (
    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [feedback_id] BIGINT NOT NULL,
    [reply_content] NVARCHAR(1000) NOT NULL,
    [replier_login_name] VARCHAR(100) NOT NULL,
    [replier_user_name] NVARCHAR(100) NOT NULL,
    [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_feedback_reply FOREIGN KEY (feedback_id) REFERENCES [tool_io_feedback](id) ON DELETE CASCADE
);

CREATE INDEX IX_tool_io_feedback_reply_feedback_id ON [tool_io_feedback_reply](feedback_id);
```

### 2. 服务层 (feedback_service.py)

新增以下函数：

- `list_all_feedback(*, status, category, keyword, limit, offset)` - 获取所有反馈（管理员用），支持按 status/category/keyword 过滤
- `update_feedback_status(feedback_id, new_status, *, login_name, user_name)` - 更新反馈状态
- `add_feedback_reply(feedback_id, content, *, login_name, user_name)` - 添加回复，同时自动将 pending 状态改为 reviewed
- `get_feedback_replies(feedback_id)` - 获取某条反馈的所有回复

状态流转验证：
- pending → reviewed ✓
- pending → resolved ✓
- reviewed → resolved ✓
- resolved → reviewed (可重新打开)

### 3. 路由层 (feedback_routes.py)

新增端点（所有端点需要 admin:user_manage 权限）：

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/feedback/all` | 获取所有反馈（支持分页/过滤） |
| PUT | `/api/feedback/<id>/status` | 更新反馈状态 |
| POST | `/api/feedback/<id>/reply` | 添加回复 |
| GET | `/api/feedback/<id>/replies` | 获取回复列表 |

**GET /api/feedback/all 查询参数**：
- `status`: pending/reviewed/resolved
- `category`: bug/feature/ux/other
- `keyword`: 搜索主题或内容
- `limit`: 默认 50
- `offset`: 默认 0

**响应格式**：
```json
{
  "success": true,
  "data": [...],
  "total": 100
}
```

## Constraints / 约束条件

- 所有 admin 端点必须验证 `admin:user_manage` 权限
- 回复内容长度限制：1-1000 字符
- 使用事务确保数据一致性
- 遵循项目编码规范（英文变量名、snake_case）
- 不得破坏现有功能（普通用户仍只能看自己的反馈）

## Completion Criteria / 完成标准

1. 新返信表 `tool_io_feedback_reply` 可正常创建
2. 管理员可以调用 `/api/feedback/all` 查看所有用户反馈
3. 管理员可以调用 `/api/feedback/<id>/status` 更新状态
4. 管理员可以调用 `/api/feedback/<id>/reply` 添加回复
5. 回复添加后自动将 pending 状态改为 reviewed
6. 管理员可以调用 `/api/feedback/<id>/replies` 获取回复列表
7. 非 admin 用户无法访问这些端点（返回 403）
8. 后端语法检查通过：`python -m py_compile backend/services/feedback_service.py backend/routes/feedback_routes.py backend/database/schema/schema_manager.py`
