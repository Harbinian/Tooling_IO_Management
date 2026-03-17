Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 058
Goal: Implement password change backend API
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端已实现密码修改表单 (`SettingsPage.vue`)，但后端尚未实现密码修改 API。用户需要能够修改自己的登录密码。

当前前端已有 localStorage MVP 版本的反馈功能，但需要升级到数据库持久化。

## Required References / 必需参考

- `web_server.py` - Flask 路由定义
- `backend/services/rbac_service.py` - RBAC 服务
- `database.py` - 数据库操作
- `config/settings.py` - 配置
- `docs/API_SPEC.md` - API 规范文档
- `docs/DB_SCHEMA.md` - 数据库 Schema

## Core Task / 核心任务

实现用户修改密码的后端 API：
1. 验证当前密码
2. 更新用户密码（加密存储）
3. 记录操作日志

## Required Work / 必需工作

1. **创建数据库表或修改现有用户表**
   - 如果需要，创建密码历史表（可选，防止重复使用最近 N 次密码）

2. **实现 API 端点**
   - `POST /api/user/change-password`
   - 请求体：`{ old_password, new_password }`
   - 需验证当前密码
   - 需验证新密码复杂度

3. **更新 RBAC 服务**
   - 添加密码验证逻辑

4. **记录审计日志**
   - 密码修改时间、操作人、操作结果

## Constraints / 约束条件

- 不得使用明文存储密码
- 不得跳过当前密码验证
- 必须与现有用户认证系统集成
- 遵循项目编码规范（英文变量名、snake_case）

## Completion Criteria / 完成标准

1. API 可以正确验证旧密码
2. API 可以成功更新新密码（加密存储）
3. API 返回正确的错误信息（旧密码错误、密码不符合要求等）
4. 前端可以调用此 API（更新 `frontend/src/api/auth.js` 中的调用）
5. 后端语法检查通过：`python -m py_compile web_server.py backend/services/rbac_service.py database.py`
