# Bug Fix: E2E 测试登录 API 不一致和 RBAC 权限不匹配

## 任务编号
- **类型编号**: 10184
- **任务类型**: Bug 修复
- **Primary Executor**: Claude Code
- **优先级**: P1
- **依赖**: 10181 (部分完成，需继续修复遗留问题)

## 上下文

### 问题来源
`promptsRec/archive/🔶_00191_10181_10181_fix_e2e_login_and_rbac_test_failures_done.md`
`test_reports/HUMAN_E2E_STEP10_REPORT_20260401_210000.md`

### 遗留问题描述
任务 10181 已通过 commit `d8b8f4a` 修复部分问题，但仍有以下遗留问题：

1. **登录 API 行为不一致**
   - Smoke test 和 workflow test 调用登录 API 返回 401
   - RBAC test 中用户可以成功登录
   - 可能原因：参数名称不一致或测试环境差异

2. **Admin 用户登录失败**
   - RBAC 测试中 admin 用户登录失败
   - 错误: `[FAIL] Failed to login admin`

3. **RBAC 权限不匹配** (24项测试中约8项失败)
   | # | 角色 | 操作 | 预期 | 实际 | 状态码 |
   |---|------|------|------|------|--------|
   | 8 | TEAM_LEADER | order:create | ALLOW | DENY | 400 |
   | 18 | KEEPER | keeper_confirm | DENY | ALLOW | 400 |
   | 22 | PRODUCTION_PREP | pre-transport | ALLOW | DENY | 400 |

### 影响
- 无法完成完整的 E2E 回归测试
- 测试基础设施不可靠

## 必需参考

1. `test_runner/api_e2e.py` - API E2E 测试代码（重点：登录逻辑和 RBAC 测试矩阵）
2. `test_runner/playwright_e2e.py` - Playwright E2E 测试代码
3. `backend/routes/auth_routes.py` - 认证路由
4. `backend/services/auth_service.py` - 认证服务
5. `docs/RBAC_PERMISSION_MATRIX.md` - RBAC 权限矩阵
6. `docs/API_SPEC.md` - API 规范
7. `backend/database/schema/column_names.py` - 字段名常量

## 核心任务

### 1. 调查登录 API 不一致问题

**需要对比分析**:
- `api_e2e.py` 中 smoke_test 的登录调用方式
- `api_e2e.py` 中 rbac_test 的登录调用方式
- `auth_routes.py` 中登录 API 的参数接受逻辑

**检查点**:
- 参数名称: `login_name` vs `username`
- 请求体格式
- Headers 设置
- 错误响应处理

### 2. 分析 RBAC 权限不匹配

**需要验证**:
- `RBAC_TEST_MATRIX` 中的预期值是否与 `docs/RBAC_PERMISSION_MATRIX.md` 一致
- 后端 API 实际权限判断逻辑
- 错误响应码（400 vs 403）的使用场景

### 3. 修复 Admin 用户登录问题

**检查点**:
- `TEST_USERS` 中 admin 的密码配置
- 后端 admin 账号的实际密码
- 认证服务中 admin 用户的处理逻辑

## 必需工作

### Step 1: 检查登录 API 调用差异

读取 `test_runner/api_e2e.py`:
1. 找到 `quick_smoke_test` 函数中的登录调用
2. 找到 `run_rbac_test` 函数中的登录调用
3. 对比两者的请求参数、URL、headers

### Step 2: 检查认证 API 实现

读取 `backend/routes/auth_routes.py`:
1. 确认登录 endpoint 的参数名称
2. 确认认证逻辑
3. 确认错误响应码

### Step 3: 验证 RBAC 测试矩阵

读取 `docs/RBAC_PERMISSION_MATRIX.md` 和 `api_e2e.py` 中的 `RBAC_TEST_MATRIX`:
1. 确认每个测试用例的预期值是否正确
2. 修正不匹配的预期值（如有）

### Step 4: 修复问题

根据调查结果：
1. 统一登录 API 调用方式
2. 修正 RBAC 测试预期值
3. 或修复后端 API 权限逻辑（如果确实有问题）

### Step 5: 验证修复

运行 `python test_runner/api_e2e.py`:
1. 确认 smoke_test 登录成功
2. 确认 rbac_test 通过率 >= 90%

## 约束条件

1. **不破坏现有功能** - 只修复测试代码，不修改后端逻辑（除非确认后端有 bug）
2. **保持测试隔离** - 确保测试使用独立的测试数据
3. **使用正确的参数名** - 登录 API 使用 `login_name` 而非 `username`
4. **RBAC 测试通过率目标** - >= 90% (24项中至少22项通过)

## 完成标准

1. **登录 API 调用一致** - smoke_test 和 rbac_test 都能成功登录
2. **Admin 用户可登录** - admin 账号在 RBAC 测试中能成功登录
3. **RBAC 测试通过率 >= 90%** - 24项测试中至少22项通过
4. **无回归** - 现有功能不受影响

## 验收测试

```bash
# 运行 API E2E 测试
python test_runner/api_e2e.py

# 预期结果:
# - Login smoke test PASS
# - RBAC test pass rate >= 90%
# - Admin user login PASS
```
