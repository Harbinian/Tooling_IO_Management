# Bug Fix: E2E 测试登录和 RBAC 权限失败

## 任务编号
- **类型编号**: 10181
- **任务类型**: Bug 修复
- **Primary Executor**: Claude Code
- **优先级**: P1

## 上下文

### 问题来源
`test_reports/HUMAN_E2E_STEP10_REPORT_20260401_210000.md`

### 问题描述
E2E 测试基础设施存在两个主要问题：

1. **登录 API 行为不一致**
   - Smoke test 和 workflow test 调用登录 API 返回 401
   - RBAC test 中用户可以成功登录
   - API 直接调用 `login_name` 参数可以成功

2. **RBAC 权限不匹配**
   - 24项 RBAC 测试中 8 项失败
   - `TEAM_LEADER -> order:create: expected=ALLOW, actual=DENY (status=400)`
   - `KEEPER -> keeper_confirm: expected=DENY, actual=ALLOW (status=400)`
   - `PRODUCTION_PREP -> transport_execute: expected=ALLOW, actual=DENY (status=400)`

### 影响
- 无法完成完整的3轮回归测试
- E2E 测试无法验证系统稳定性

## 必需参考

1. `test_runner/api_e2e.py` - API E2E 测试代码
2. `test_runner/playwright_e2e.py` - Playwright E2E 测试代码
3. `backend/routes/auth_routes.py` - 认证路由
4. `backend/services/auth_service.py` - 认证服务
5. `docs/RBAC_PERMISSION_MATRIX.md` - RBAC 权限矩阵
6. `docs/API_SPEC.md` - API 规范

## 核心任务

### 1. 调查登录 API 不一致问题

**现象分析**:
```
[1/4] Testing login API...
   [WARN] Login failed, stopping smoke test

# 但 RBAC 测试中:
[Step 1] Precondition: Login all test users
   [OK] Logged in taidongxu as TEAM_LEADER (user_id=U_8546A79BA76D4FD2)
```

**可能原因**:
- Smoke test 和 RBAC test 调用登录 API 的方式不同
- 参数名称不一致（`login_name` vs `username`）
- 测试数据或环境差异

### 2. 分析 RBAC 权限不匹配

**失败的测试项**:
| # | 角色 | 操作 | 预期 | 实际 | 状态码 |
|---|------|------|------|------|--------|
| 8 | TEAM_LEADER | order:create | ALLOW | DENY | 400 |
| 9 | TEAM_LEADER | order:submit | DENY | ALLOW | 404 |
| 11 | TEAM_LEADER | order:final_confirm | DENY | ALLOW | 404 |
| 12 | TEAM_LEADER | order:delete | DENY | ALLOW | 404 |
| 18 | KEEPER | keeper_confirm | DENY | ALLOW | 400 |
| 19 | KEEPER | final_confirm | DENY | ALLOW | 404 |
| 22 | PRODUCTION_PREP | pre-transport | ALLOW | DENY | 400 |
| 23 | PRODUCTION_PREP | transport-start | DENY | ALLOW | 404 |

**需要调查**:
- 测试预期是否正确（是否与实际 RBAC 矩阵一致）
- API 权限判断逻辑是否正确
- 是否存在参数传递错误

## 必需工作

### Step 1: 检查 api_e2e.py 的登录逻辑

读取 `test_runner/api_e2e.py`，找到：
1. Smoke test 的登录调用方式
2. RBAC test 的登录调用方式
3. 对比两者参数差异

### Step 2: 检查认证 API 实现

读取 `backend/routes/auth_routes.py` 和 `backend/services/auth_service.py`：
1. 确认登录 API 接受的参数名称
2. 确认认证逻辑

### Step 3: 验证 RBAC 测试预期

读取 `docs/RBAC_PERMISSION_MATRIX.md`：
1. 确认 TEAM_LEADER 是否有 order:create 权限
2. 确认 KEEPER 是否有 keeper_confirm 权限
3. 确认 PRODUCTION_PREP 是否有 transport_execute 权限

### Step 4: 修复问题

根据调查结果：
1. 修复 api_e2e.py 中的登录参数（如果不一致）
2. 修复 RBAC 测试的预期值（如果预期错误）
3. 或修复后端 API 权限逻辑（如果确实有问题）

### Step 5: 验证修复

运行 `python test_runner/api_e2e.py` 确认：
1. Login 不再返回 401
2. RBAC 测试通过率提高

## 约束条件

1. **不破坏现有功能** - 只修复测试代码，不修改后端逻辑（除非确认后端有 bug）
2. **使用正确的参数名** - 登录 API 使用 `login_name` 而非 `username`
3. **保持测试隔离** - 确保测试使用独立的测试数据

## 完成标准

1. **登录 API 调用正确** - Smoke test 和 RBAC test 都能成功登录
2. **RBAC 测试通过率 >= 90%** - 24项测试中至少22项通过
3. **无回归** - 现有功能不受影响

## 验收测试

```bash
# 1. 运行 API E2E 测试
python test_runner/api_e2e.py

# 预期结果:
# - Login 不再返回 401
# - RBAC 测试通过率 >= 90%

# 2. 运行 Playwright E2E 测试 (如果浏览器可用)
python test_runner/playwright_e2e.py

# 预期结果:
# - 快速冒烟测试 PASS
# - 完整工作流测试 PASS
# - RBAC 权限测试 PASS
```

## 报告要求

完成修复后，输出：
1. 发现的问题根本原因
2. 采取的修复措施
3. 验证结果
4. 遗留问题（如果有）
