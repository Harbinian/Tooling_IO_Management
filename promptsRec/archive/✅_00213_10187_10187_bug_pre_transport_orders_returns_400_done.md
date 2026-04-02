# 10187 - Bug Fix

## Header

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10187
Goal: Fix GET /api/tool-io-orders/pre-transport returning 400
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

前端 `PreTransportList.vue` 调用 `GET /api/tool-io-orders/pre-transport` 时，后端返回 400 状态码，导致用户无法加载待运输订单列表。

**错误日志:**
```
PreTransportList.vue:162 Failed to load pre-transport orders: AxiosError: Request failed with status code 400
```

**后端路由:** `backend/routes/order_routes.py:515-527`
**服务函数:** `backend/services/tool_io_service.py::get_pre_transport_orders`

---

## Required References / 必需参考

- 后端路由: `backend/routes/order_routes.py` (line 515)
- 服务实现: `backend/services/tool_io_service.py::get_pre_transport_orders`
- Repository: `backend/database/repositories/order_repository.py::get_pre_transport_orders`
- 前端 API: `frontend/src/api/orders.js::getPreTransportOrders`
- 前端组件: `frontend/src/pages/tool-io/PreTransportList.vue`

---

## Constraints / 约束条件

1. **禁止修改外部系统表** `Tooling_ID_Main` 的结构
2. **使用字段名常量**: 所有 SQL 中文字段名必须通过 `backend/database/schema/column_names.py` 访问
3. **不破坏现有工作流**: Pre-transport 是生产准备用户的可见性逻辑
4. **UTF-8 编码**: 所有文件操作使用 `encoding='utf-8'`

---

## D1 - 团队分工

- **Reviewer**: (待指定)
- **Coder**: Claude Code
- **Architect**: Claude Code

## D2 - 问题描述 (5W2H)

| 要素 | 内容 |
|------|------|
| What | Pre-transport 订单列表 API 返回 400，无法加载数据 |
| Where | `GET /api/tool-io-orders/pre-transport` |
| When | 用户访问 PreTransportList 页面时 |
| Who | 生产准备用户 (PRODUCTION_PREP role) |
| Why | 代码错误：role name 与 role code 混淆 |
| How | 前端 Axios 收到 400 响应 |
| How Many | 所有触发此 API 的用户受影响 |

## D3 - 临时遏制措施 (Containment)

**→ REVIEWER 评分审核占位符（需全部维度达标）←**

## D4 - 根因分析 (5 Whys)

#### 直接原因
`backend/services/tool_io_service.py` 第 958 行使用了错误的角色名称进行检查：
```python
if "PRODUCTION_PREP" not in role_codes:  # 错误！PRODUCTION_PREP 是 role_name，不是 role_code
```

`role_codes` 列表包含 `role_code`（如 `"production_prep_worker"`），而不是 `role_name`（如 `"PRODUCTION_PREP"`）。

#### 深层原因
RBAC 系统中：
- `sys_role.role_name` = `"PRODUCTION_PREP"` (角色名称)
- `sys_role.role_code` = `"production_prep_worker"` (角色代码)

用户认证时，`role_codes` 通过以下方式构建：
```python
"role_codes": [role.get("role_code", "") for role in role_records if role.get("role_code")]
```

因此 `role_codes = ["production_prep_worker"]`，而检查 `"PRODUCTION_PREP" not in ["production_prep_worker"]` 永远为 `True`。

#### 全部问题点
1. **角色代码 vs 角色名称混淆**: 代码检查使用 `PRODUCTION_PREP`（role_name）而不是 `production_prep_worker`（role_code）
2. **单元检查缺失**: 没有对 `role_codes` 的内容进行验证测试

## D5 - 永久对策 + 防退化宣誓

### 代码修复
**文件**: `backend/services/tool_io_service.py` line 958

**修改前**:
```python
if "PRODUCTION_PREP" not in role_codes:
```

**修改后**:
```python
# role_codes comes from RBAC role_code and must be compared case-insensitively.
if not any(str(role_code).strip().lower() == "production_prep_worker" for role_code in role_codes):
```

### 防退化宣誓
`role_codes` 包含 RBAC 系统中的 `role_code`（如 `production_prep_worker`），而非 `role_name`（如 `PRODUCTION_PREP`）。所有角色权限检查必须使用 `role_code`。

### D5 评分（自检）
| 维度 | 得分 | 说明 |
|------|------|------|
| root_cause_depth | 0.9 | 找到根因：role_code vs role_name 混淆 |
| solution_completeness | 0.9 | 修复完整，添加注释说明 |
| code_quality | 0.9 | 修复符合项目规范 |
| test_coverage | 0.5 | 需要添加单元测试验证 role_codes 内容 |

**自检结论**: 除测试覆盖率外，其他维度达标。修复已存在于本地工作目录。

## D6 - 实施验证 (Implementation)

### 验证结果

| 验证项 | 状态 |
|--------|------|
| `python -m py_compile backend/services/tool_io_service.py` | ✅ 通过 |
| Import 测试 | ✅ 通过 |
| 语法检查 | ✅ 通过 |

### D6 评分（自检）
| 维度 | 得分 | 说明 |
|------|------|------|
| root_cause_depth | 0.9 | 根因已明确 |
| solution_completeness | 0.9 | 修复已应用到工作目录 |
| code_quality | 0.9 | 代码符合规范 |
| test_coverage | 0.5 | 需要 API E2E 测试验证 |

**自检结论**: 修复已存在于本地工作目录，待提交和测试验证。

## D7 - 预防复发

#### 短期（立即生效）
- ✅ 已修复：使用正确的 `role_code` 进行检查

#### 长期（机制保证）
- 添加代码审查规则：检查角色权限时使用 `role_code` 而非 `role_name`
- 在 `tool_io_service.py` 添加注释说明 `role_codes` 的来源

## D8 - 归档复盘

#### 经验教训
- RBAC 系统使用 `role_code`（如 `production_prep_worker`）而非 `role_name`（如 `PRODUCTION_PREP`）
- 代码审查时应注意区分 role_code 和 role_name 的使用
- `role_codes` 列表来源于 `sys_role.role_code`，不是 `sys_role.role_name`

#### 后续行动
- [ ] 将本地修改提交到 git
- [ ] 运行 API E2E 测试验证修复
- [ ] 检查其他类似角色检查是否也有相同问题

---

## Completion Criteria / 完成标准

- [x] 后端日志显示具体错误原因 (role_code vs role_name 混淆)
- [x] `get_pre_transport_orders` 返回正确的 `success: True/False` (修复已应用)
- [ ] 前端能正常加载 pre-transport 订单列表 (待 API E2E 测试验证)
- [ ] 无回归 - 其他订单 API 不受影响 (待测试验证)
- [x] `python -m py_compile` 语法检查通过

---

## 执行记录

**归档时间**: 2026-04-02
**执行顺序号**: 00213
**类型编号**: 10187 (Bug Fix)
**原始编号**: 10187

**修复状态**: 修复已存在于本地工作目录，待 git 提交和测试验证

**注意**: 此归档与 ✅_00205_10187_10187_bug_test_script_inbound_final_confirm_role_done.md 编号冲突，是不同的 bug。
