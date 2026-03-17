# fengliang 登录成功后端返回成功但前端未重定向

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10168
Goal: 修复 fengliang (PRODUCTION_PREP) 登录成功后端返回成功但前端停留在登录页
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在 Human E2E 测试中发现以下登录问题：

| 用户 | 角色 | 登录 API 结果 | 前端行为 | 预期行为 |
|------|------|--------------|----------|----------|
| fengliang | PRODUCTION_PREP | API 返回 200 + token | 停留在 /login | 重定向到 /dashboard |
| admin | SYS_ADMIN | API 返回 200 + token | 正常重定向到 /dashboard | 正常重定向 |
| taidongxu | TEAM_LEADER | API 返回 200 + token | 正常重定向到 /dashboard | 正常重定向 |
| hutingting | KEEPER | API 返回 200 + token | 正常重定向到 /dashboard | 正常重定向 |

**测试证据**：
```
>> POST http://localhost:8151/api/auth/login
<< 200 http://localhost:8151/api/auth/login
URL after 5s: http://localhost:8150/login   <-- 应该重定向到 /dashboard
```

**根本原因分析**：
- fengliang 的 API 响应包含正确的 token
- 但前端未能正确处理响应或存储 token
- 其他用户正常说明代码基本正确，可能是特定用户数据问题

---

## Required References / 必需参考

1. `frontend/src/pages/auth/LoginPage.vue` - 登录页面组件
2. `frontend/src/api/auth.js` - 认证 API 调用
3. `frontend/src/store/` - Pinia 状态管理（如果有）
4. `backend/routes/auth.py` - 后端登录 API
5. `test_runner/playwright_e2e.py` - 测试脚本中的登录逻辑

---

## Core Task / 核心任务

### 问题分析

1. 检查 `LoginPage.vue` 中的登录成功处理逻辑
2. 检查 token 存储逻辑（localStorage / sessionStorage）
3. 检查登录成功后的重定向逻辑
4. 分析 fengliang 用户数据与其他人有何不同

### fengliang 用户数据特征

从 API 响应看，fengliang 的特征：
- user_id: U_D93CFFC1EB164658
- role: production_prep_worker (非标准 role_code)
- permissions: ["order:transport_execute", "tool:location_view", "tool:search", "tool:view"]
- org_id: ORG_DEPT_001

### 可能的问题

1. **响应处理差异**：代码可能对特定角色有特殊处理
2. **token 存储失败**：某些用户数据导致 token 存储失败
3. **重定向条件判断**：某些用户数据导致重定向条件不满足
4. **权限检查提前拦截**：登录后立即进行权限检查失败

### 必须执行的修复

1. **诊断阶段**：
   - 在 LoginPage.vue 中添加调试日志（如果需要）
   - 检查登录成功后的完整处理流程

2. **修复阶段**：
   - 确保 token 正确存储到 localStorage
   - 确保重定向逻辑对所有用户一致

3. **验证阶段**：
   - 使用 Playwright 测试 fengliang 登录

---

## Required Work / 必需工作

- [ ] Step 1: 检查 `LoginPage.vue` 完整代码
- [ ] Step 2: 检查登录成功后的 token 存储逻辑
- [ ] Step 3: 检查重定向逻辑
- [ ] Step 4: 检查是否有针对特定角色的条件判断
- [ ] Step 5: 修复发现的问题
- [ ] Step 6: 验证修复：运行 playwright 测试 fengliang 登录

---

## Constraints / 约束条件

- **零退化原则**：不得破坏其他用户的登录功能
- **前端代码规范**：使用英文变量名，4空格缩进
- **不修改测试数据**：不要修改 fengliang 的用户数据

---

## Completion Criteria / 完成标准

1. fengliang 登录后成功重定向到 http://localhost:8150/dashboard
2. 其他用户（admin, taidongxu, hutingting）登录不受影响
3. token 正确存储在 localStorage
4. 可以使用 fengliang 的 token 访问受保护资源
