# Prompt 10194: 修复 RBAC 权限不匹配问题

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 1
Goal: 修复 RBAC 测试中 8 项权限预期与实际不符的问题
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

E2E RBAC 测试显示 24 项测试中约 8 项失败：

| 角色 | 权限 | 预期 | 实际 |
|------|------|------|------|
| TEAM_LEADER | order:create | ALLOW | DENY (400) |
| KEEPER | keeper_confirm | DENY | ALLOW (400) |
| PRODUCTION_PREP | transport_execute | ALLOW | DENY (400) |

### 5W2H 问题陈述

- **What**: RBAC 权限测试 8 项失败，返回 400 状态码
- **Where**: `test_runner/api_e2e.py` RBAC 测试套件
- **When**: 每次运行 RBAC 测试时
- **Who**: 受影响角色: TEAM_LEADER, KEEPER, PRODUCTION_PREP
- **Why**: 未知，可能是测试数据错误、权限矩阵文档错误、或实现 Bug
- **How**: 通过对比 API 响应与预期，识别差异

---

## D3: 临时遏制措施 (Containment)

### 临时措施

在根因明确前，**暂时跳过失败的 RBAC 测试用例**，避免阻塞 CI：

```python
# 在 api_e2e.py 中标记跳过
@pytest.mark.skip(reason="待排障 RBAC 权限不一致问题")
def test_team_leader_order_create():
    ...
```

### 验证

标记后运行 `python test_runner/api_e2e.py --mode rbac`，确保其他测试不受影响。

---

## D4: 根因分析 (5 Whys)

### 排查步骤

1. **读取 RBAC 测试代码**
   - 定位 `test_rbac_permissions()` 函数
   - 提取失败案例的完整请求

2. **对比请求结构**
   - 成功案例 vs 失败案例的 HTTP 请求差异
   - 检查字段名、headers、body 结构

3. **检查 API 响应**
   - 400 错误返回的具体错误信息
   - 是参数验证失败？还是权限检查失败？

4. **验证权限矩阵**
   - 对照 `docs/RBAC_PERMISSION_MATRIX.md`
   - 确认预期权限是否符合文档

5. **检查后端实现**
   - 读取 `backend/services/rbac_service.py`
   - 追踪权限判断逻辑

### 根因假设

| # | 假设 | 验证方法 |
|---|------|---------|
| 1 | 测试用例字段名错误 | 对比成功/失败请求 |
| 2 | 权限矩阵文档错误 | 对比实现代码 |
| 3 | 后端 RBAC 实现错误 | 追踪权限判断逻辑 |
| 4 | API 路由映射错误 | 检查路由配置 |

---

## D5: 永久对策 + 防退化宣誓

### 修复方案

根据根因，选择以下方案：

**方案 A: 修正测试用例**
- 如果文档和实现一致，修正 `api_e2e.py` 中的测试数据

**方案 B: 修正后端实现**
- 如果实现与文档不符，修正 `rbac_service.py`
- 同时更新 `RBAC_PERMISSION_MATRIX.md`

**方案 C: 修正权限矩阵文档**
- 如果需要变更权限策略，更新文档后再改代码

### 防退化措施

- 添加单元测试验证 RBAC 逻辑
- 在 `docs/RBAC_PERMISSION_MATRIX.md` 中添加变更记录

---

## D6: 实施验证 (Implementation)

### 验证步骤

1. 运行完整 RBAC 测试套件
2. 确认所有用例通过（或按 D3 约定跳过）
3. 运行 API E2E 完整测试，确保无回归

### 验证命令

```bash
python test_runner/api_e2e.py --mode rbac
```

**通过标准**: 所有 RBAC 测试用例通过，无 400 错误

---

## Required References / 必需参考

- `test_runner/api_e2e.py` - RBAC 测试代码
- `backend/services/rbac_service.py` - RBAC 服务实现
- `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵文档（权威来源）
- `docs/API_SPEC.md` - API 规范

---

## Required Work / 必需工作

- [ ] D3: 临时跳过失败用例，确保 CI 不阻塞
- [ ] D4: 完成根因分析（5 Whys），明确问题归属
- [ ] D5: 制定永久对策，确认权威来源
- [ ] D6: 实施修复并验证
- [ ] 更新 RBAC 测试覆盖

---

## Constraints / 约束条件

- **权威来源**: 以 `docs/RBAC_PERMISSION_MATRIX.md` 为准
- **如需变更文档**: 必须先更新文档，再修改代码
- **完成标准**: **所有受影响用例必须全部通过**，不允许残留失败

---

## Completion Criteria / 完成标准

1. **根因明确**: D4 完成并记录根因结论
2. **所有 RBAC 测试通过**: 24/24 通过率 100%
3. **无回归**: API E2E 其他测试仍正常
4. **如涉及文档变更**: 同步更新 `RBAC_PERMISSION_MATRIX.md`
5. **移除临时跳过**: D3 的 skip 标记已移除

---

## Reviewer 节点

D3、D5、D6 完成后必须通知 reviewer 评分审核，通过后才能继续。
