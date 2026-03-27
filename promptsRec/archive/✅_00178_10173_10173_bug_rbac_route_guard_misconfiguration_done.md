# BUG 修复: RBAC路由守卫配置错误

## 任务编号
- **执行顺序号**: 00178
- **类型编号**: 10173
- **任务类型**: Bug修复任务 (10001-19999)
- **优先级**: P1

## 问题描述

### 症状
Playwright E2E测试中RBAC权限测试失败：
```
❌ [taidongxu] rbac_taidongxu_/keeper: 访问/keeper -> FAIL
   预期:deny 实际:allow

❌ [hutingting] rbac_hutingting_/create: 访问/create -> FAIL
   预期:deny 实际:allow

❌ [fengliang] rbac_fengliang_/tool-io: 访问/tool-io -> FAIL
   预期:deny 实际:allow
```

### 预期行为（根据RBAC设计）
| 角色 | 页面 | 预期结果 |
|------|------|----------|
| TEAM_LEADER | /keeper | DENY |
| KEEPER | /create | DENY |
| PRODUCTION_PREP | /tool-io | DENY |

### 根本原因
前端路由守卫（Vue Router navigation guard）未正确实现角色访问控制。

## 前置依赖
- 无

## 修复方案

### 1. 检查当前路由守卫实现

检查 `frontend/src/router/` 目录下的：
- router/index.ts 或 router.js
- 路由守卫配置（beforeEach, beforeEnter等）
- 角色权限定义

### 2. 对照RBAC文档

参考以下文档确认正确的权限矩阵：
- `docs/RBAC_PERMISSION_MATRIX.md`
- `docs/RBAC_DESIGN.md`

### 3. 修复路由守卫

确保以下路由守卫正确实现：
- TEAM_LEADER 不能访问 /keeper
- KEEPER 不能访问 /create
- PRODUCTION_PREP 不能访问 /tool-io

### 4. 验证修复

运行一轮Playwright E2E测试：
```bash
cd E:/CA001/Tooling_IO_Management
python test_runner/playwright_e2e.py
```

确认以下RBAC测试通过：
- rbac_taidongxu_/keeper ✅
- rbac_hutingting_/create ✅
- rbac_fengliang_/tool-io ✅

## 约束条件
- 遵循项目的RBAC权限矩阵文档
- 不破坏其他已正常工作的路由守卫
- 保持路由配置的结构清晰

## 完成标准
1. 上述3个RBAC测试全部通过
2. 其他RBAC测试不受影响

## 报告输出
写入 `test_reports/BUGFIX_10173_RBAC_ROUTE_GUARD_REPORT_YYYYMMDD.md`
