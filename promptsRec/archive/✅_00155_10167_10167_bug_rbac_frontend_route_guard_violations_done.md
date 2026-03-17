# RBAC 前端路由守卫权限违规修复

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10167
Goal: 修复前端路由守卫，允许 TEAM_LEADER 访问 /keeper 和 KEEPER 访问 /create
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在 Human E2E 测试中发现以下 RBAC 违规：

| 用户 | 角色 | 访问路径 | 预期 | 实际 | 严重性 |
|------|------|---------|------|------|--------|
| taidongxu | TEAM_LEADER | /keeper | DENY | ALLOW | HIGH |
| hutingting | KEEPER | /create | DENY | ALLOW | HIGH |

**根本原因**：前端路由守卫未正确检查角色权限。后端 API 权限是正确的（已通过 API 响应验证）。

**测试证据**：
- taidongxu (TEAM_LEADER) 登录后可直接访问 http://localhost:8150/keeper
- hutingting (KEEPER) 登录后可直接访问 http://localhost:8150/create

---

## Required References / 必需参考

1. `frontend/src/router/` - 路由守卫配置
2. `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵定义
3. `docs/RBAC_DESIGN.md` - RBAC 设计文档
4. `frontend/src/pages/auth/LoginPage.vue` - 登录页面

---

## Core Task / 核心任务

### 问题分析

1. 检查 `frontend/src/router/` 目录下的路由配置文件
2. 找到 `/keeper` 和 `/create` 路由的守卫逻辑
3. 确认守卫是否正确检查了角色权限

### 预期权限规则

根据 RBAC 矩阵：

| 路径 | TEAM_LEADER | KEEPER | PRODUCTION_PREP |
|------|-------------|--------|-----------------|
| /keeper | DENY | ALLOW | DENY |
| /create | ALLOW | DENY | DENY |

### 必须执行的修复

1. **修复 /keeper 路由守卫**：
   - 查找路由配置中的 `/keeper` 路由
   - 确保只有 KEEPER 角色可以访问
   - TEAM_LEADER 和 PRODUCTION_PREP 必须被拒绝

2. **修复 /create 路由守卫**：
   - 查找路由配置中的 `/create` 路由
   - 确保只有 TEAM_LEADER 和 PLANNER 角色可以访问
   - KEEPER 必须被拒绝

3. **验证修复**：
   - 使用 Playwright 或手动测试验证：
     - taidongxu 访问 /keeper 应被重定向
     - hutingting 访问 /create 应被重定向

---

## Required Work / 必需工作

- [ ] Step 1: 检查 `frontend/src/router/index.js` 或 `frontend/src/router/routes.js`
- [ ] Step 2: 找到 `/keeper` 和 `/create` 路由配置
- [ ] Step 3: 检查路由守卫逻辑（beforeEach 或 meta 字段）
- [ ] Step 4: 添加/修正角色检查逻辑
- [ ] Step 5: 运行语法检查：`cd frontend && npm run build`
- [ ] Step 6: 手动测试验证 RBAC 修复

---

## Constraints / 约束条件

- **零退化原则**：不得破坏其他路由的权限
- **不得修改后端**：后端 API 权限是正确的
- **使用现有角色常量**：不要硬编码角色名称，使用已有的角色常量
- **前端代码规范**：使用英文变量名，4空格缩进

---

## Completion Criteria / 完成标准

1. taidongxu (TEAM_LEADER) 访问 http://localhost:8150/keeper 被重定向到其他页面
2. hutingting (KEEPER) 访问 http://localhost:8150/create 被重定向到其他页面
3. 现有允许的访问路径不受影响（如 taidongxu 可以访问 /create）
4. 前端构建成功（npm run build 无错误）
